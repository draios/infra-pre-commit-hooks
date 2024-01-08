import argparse
from git import Repo
from collections import defaultdict
from typing import Sequence, Dict, List
import os

fallback_key = "fallback"


def matching_upstream_args(
    filter_args: List, upstream_args: Dict, fallback_args: Dict
) -> bool:
    upstream_from_filter = set(map(lambda x: x[0], filter_args))
    upstream_from_upstreams = set(upstream_args.keys())
    upstream_from_fallback = set(fallback_args.keys())

    return (
        upstream_from_upstreams == upstream_from_fallback
    ) and upstream_from_filter.issubset(upstream_from_upstreams)


def parse_filter_args(raw_filters: List) -> List:
    filters = []

    for raw_filter in raw_filters:
        filters.append(raw_filter.split())
    return filters


def parse_upstream_args(raw_upstreams: List) -> Dict:
    upstreams = {}
    for upstream in raw_upstreams:
        splitted_upstream = upstream.split()
        upstreams[splitted_upstream[0]] = splitted_upstream[1]
    return upstreams


def build_data_structures(
    filter_args: List, upstream_args: Dict, fallback_args: Dict
) -> Dict:
    configs = {}

    for upstream_name, upstream_dir in upstream_args.items():
        configs[upstream_name] = {"dir": upstream_dir, "config": []}
        for file_filter in filter(lambda x: x[0] == upstream_name, filter_args):
            new_filter = {}
            new_filter["suffix"] = file_filter[1]
            # Split ,
            new_filter["exts"] = file_filter[2].split(",")
            new_filter["dir"] = file_filter[3]
            configs[upstream_name]["config"].append(new_filter)

        fallback_filter = {
            "suffix": fallback_key,
            "exts": [""],
            "dir": fallback_args[upstream_name],
        }
        configs[upstream_name]["config"].append(fallback_filter)
    return configs


def get_suffix(filename: str, filters: Dict) -> str:
    for file_filter in filters:
        if any([filename.lower().endswith(ext) for ext in file_filter["exts"]]):
            return file_filter["suffix"]


def write_patch(filepath: str, content: str):
    with open(filepath, "w") as f:
        print(content, file=f)
    print(f"{filepath} updated")


def create_directory(directory: str):
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"{directory} created")


def is_same_content(filename: str, content: str) -> bool:
    try:
        with open(filename, "r") as f:
            file = f.read()
            return file == (content + "\n")
    except FileNotFoundError:
        return False


def write_patch_suffix_upstream(
    upstream_name: str, file_filter: Dict, suffix: str, diffs: Dict
) -> int:
    if len(diffs[suffix]) > 0:
        content = "\n".join(diffs[suffix])
        filename = f"{file_filter['dir']}/{upstream_name}_{suffix}.patch"
        create_directory(file_filter["dir"])
        if not is_same_content(filename, content):
            write_patch(filename, content)
            return 1
    return 0


def write_patch_upstream(
    upstream_name: str, file_filter: Dict, suffix: str, diffs: Dict
) -> int:
    writes = 0
    writes += write_patch_suffix_upstream(upstream_name, file_filter, suffix, diffs)
    writes += write_patch_suffix_upstream(
        upstream_name, file_filter, f"{suffix}_deleted", diffs
    )
    return writes


def build_patches(configs: Dict) -> int:
    new_patches = 0
    for upstream_name in configs.keys():
        diffs = defaultdict(list)
        repo = Repo(configs[upstream_name]["dir"])
        hcommit = repo.head.commit

        for diff in hcommit.diff(None):
            base_key = get_suffix(diff.a_path, configs[upstream_name]["config"])

            if base_key is None:
                base_key = fallback_key

            key = f"{base_key}_deleted" if (diff.b_mode) == 0 else base_key
            diffs[key].append(repo.git.diff("HEAD", "--", diff.a_path))

        for file_filter in configs[upstream_name]["config"]:
            new_patches += write_patch_upstream(
                upstream_name, file_filter, file_filter["suffix"], diffs
            )
    return new_patches


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--filters", dest="raw_filters", action="append", nargs="*", default=[]
    )
    parser.add_argument(
        "--upstreams", action="append", dest="upstreams", nargs="+", required=True
    )
    parser.add_argument(
        "--fallbacks", dest="raw_fallbacks", action="append", nargs="+", required=True
    )
    args = parser.parse_args(argv)
    if len(args.raw_filters) > 0:
        filter_args = parse_filter_args(args.raw_filters[0])
    else:
        filter_args = []
    upstream_args = parse_upstream_args(args.upstreams[0])
    fallback_args = parse_upstream_args(args.raw_fallbacks[0])

    if not matching_upstream_args(filter_args, upstream_args, fallback_args):
        print("Fallbacks and upstreams don't match")
        exit(1)

    configs = build_data_structures(filter_args, upstream_args, fallback_args)
    writes = build_patches(configs)
    return writes


if __name__ == "__main__":
    raise SystemExit(main())

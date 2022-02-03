#!/usr/bin/env python

import os
import re
import argparse
from sys import argv
from collections import OrderedDict
from typing import Sequence


output = {}
nl = "\n"


def extract_info(batsfile):
    """
    Extract information from test
    """
    k = open(batsfile, "r")
    # Thanks to @panepan83
    myreg = re.compile('^@test\s+"([^"]+)"\s+{([\s\S]*?)}\s*(?=(\n@|\Z))', re.MULTILINE)
    myreg_comment = re.compile("((\s*#.*\n)+)")

    for m in myreg.finditer(k.read()):
        t, b = m.group(1, 2)
        try:
            c = " ".join(myreg_comment.search(b).group(1).replace("\n", "").replace("#", "").split())
            if t[0].isdigit():
                output[t] = c
        except AttributeError:
            pass


def do_readme(readmefile: str):
    """
    Check if README.md already exist
    and trucate the file so we can append
    the new version
    """
    if os.path.isfile(readmefile):
        if os.stat(readmefile).st_size != 0:
            f = open(readmefile, "r+")
            f.truncate(0)
            f.close()


def write_readme(readmefile: str, content: str):
    """Append contents"""
    with open(readmefile, "a") as f:
        f.write(content)
        f.close()


def do_the_magic(directory):
    """
    Search for all bats files and extract docs
    If header.md is present will be prepended
    before the tests markdown
    """
    for root, dirs, files in os.walk(directory):
        r = root + "/../README.md"
        do_readme(r)
        for file in files:
            if file == "header.md":
                h = open(root + "/" + file, "r")
                write_readme(r, h.read())
                h.close()
        # Some base base markdown
        write_readme(r, f"{nl}## Tests{nl}")
        # Extract values from tests, we need to repeat the loop here 'cause
        # we need to prepend the header and title before the bats tests docs
        for file in files:
            if file.endswith(".bats"):
                extract_info(root + "/" + file)
        # Sort tests by number and append them in markdown
        sd = {k: v for k, v in sorted(output.items(), key=lambda item: item[0])}
        for k, v in sd.items():
            write_readme(r, f"{nl}### {k}{nl}")
            write_readme(r, f"{v}{nl}")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("filenames", nargs="*", help="Bats tests files")
    a = parser.parse_args(argv)

    dirs = []
    # Avoid to process a directory twice
    # in case of multiple bats files modified
    for filename in a.filenames:
        if os.path.realpath(filename) not in dirs and filename.endswith(".bats"):
            dirs.append(os.path.dirname(filename))

    # Main loop
    retval = 0
    for dir in dirs:
        # In case the script will modify a dir we need
        # to print the list of dirs modified
        print(f"{dir}{nl}")
        try:
            do_the_magic(dir)
        except Exception as e:
            print(e)
            retval = 1
    return retval


if __name__ == "__main__":
    raise SystemExit(main())

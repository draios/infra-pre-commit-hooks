# Sysdig opinionated pre-commit hooks

Internal note: this is a public repo

## create-bats-readme

Sysdig opinionated automatically bats tests README generator.

Automatically recognizes when a `.bats` file has been changed and create the README sourcing all the bats files present on that dir.
It's based on our directory convention and on commented lines under the test name (like docstring in python).

```yaml
repos:
  - repo: https://github.com/draios/infra-pre-commit-hooks
    rev: 0.0.1
    hooks:
      - id: create-bats-readme
```

Prerequisites:

* each bats test definition must be numbered like `1.2`, `3.5`, `4.3` etc. If
  you have a pre/post steps you can just use the name you want, will be ignored.

* you need to add the doc under the test definition in one or more commented
  lines, each commented lines will be backported into the final README file.

Optional:

* if `header.md` is present will be prepended before the tests markdown

example:

```shell
@test "1.1 Helm: install my foobar chart" {
    # Install my fantastic foobar chart        ---> MULTILINE DESC
    # and this decription will be backported   ---> MULTILINE DESC
    # in the result markdown                   ---> MULTILINE DESC

    run helm install foobar
    assert_success
}
```

## conftest-check

Sysdig opinionated validation hooks (by using conftest)

Needs 2 argument:

* `--policy` or `-p` the dir or git repo (soonTM) where the conftest policies are stored

* `--dirs` or `-d` the directory where the files that need to be validate are stored

```yaml
repos:
  - repo: https://github.com/draios/infra-pre-commit-hooks
    rev: 0.0.1
    hooks:
      - id: conftest-check
        args: [-p=mypolicydir, -d=mytargetfiles]
```

## create-patch-files

This hook will create the patch files for the upstream repos that you have configured inside the hook.

The hook has 2 required parameters and 1 optional parameter:

* `--upstreams`: Defines the position of the upstream repo, you can pass multiple upstream like this `--upstreams foo /foo bar /bar`. This will tell the hook that there are 2 upstreams called `foo` and `bar`, `foo` is in directory `/foo` and `bar` is in directory `/bar`
* `--filters`: Defines multiple filters for the upstreams repos, you can filter files by extensions and put their patch in a given directory like this: `--filters foo scripts sh,shell /foo/scripts`. This example will apply the filter to the `foo` upstream and tags all the files ending with `sh` or `shell` with the tag `scripts`, all the patch files will be placed in `/foo/scripts`.
* `--fallbacks`: Define where to put the patchfiles for a given upstream if no filters are matched, it is passed like this: `--fallbacks foo /foo/fall`. In this example, every patch file from the upstream `foo` that do not match a filter, will be placed in `/foo/fall`.

TLDR:

* `--upstreams upstream_name upstream_directory`
* `--filters upstream_name tag extensions directory`
* `--fallbacks upstream_name directory`

Each upstream needs a fallback, to get all the patch files!

The patch files' name will be as follows:

* `{upstream_name}_{tag}.patch`: for a filtered patch.
* `{upstream_name}_{tag}_deleted.patch`: for a filtered patch which has deleted files in it.
* `{upstream_name}_fallback.patch`: For a fallback patch file.
* `{upstream_name}_fallback_deleted.patch`: For a fallback patch file which has deleted files in it

example:

```yaml
repos:
  - repo: https://github.com/draios/infra-pre-commit-hooks
    rev: 0.0.1
    hooks:
      - id: create_patch_files
        args:
          - --upstream
          - foo /foo
          - bar /bar
          - --filters
          - foo scripts sh,shell /foo/scripts
          - --fallbacks
          - foo /foo/fallback
          - bar /bar/fallback
```

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

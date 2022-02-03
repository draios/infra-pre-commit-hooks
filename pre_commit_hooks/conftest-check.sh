#!/usr/bin/env bash

set -e

CONFTEST=$(command -v conftest)
conftest_ignore="kustomization*|Taskfile*"
declare -i RC=0
_p=""
_d=""

check_deps() {
    local depend=("conftest" "git")
    for d in "${depend[@]}"; do
        command -v "$d" >/dev/null 2>&1 || { echo "$d is not present in your path, aborting"; exit 1; }
    done
}

# From https://github.com/gruntwork-io/pre-commit/blob/master/hooks/shellcheck.sh
parse_arguments() {
    while (($# > 0)); do
        # Grab param and value splitting on " " or "=" with parameter expansion
        local PARAMETER="${1%[ =]*}"
        local VALUE="${1#*[ =]}"
        if [[ "$PARAMETER" == "$VALUE" ]]; then VALUE="$2"; fi
        shift
        case "$PARAMETER" in
            -p*|--policy*)
                _p="$VALUE"
                ;;
            -d*|--dirs*)
                _d="$VALUE"
                ;;
            -*)
                printf "Error: Unknown option: %s /n" "$PARAMETER" >&2
                exit 1
                ;;
            *)
                files="$files $PARAMETER"
                ;;
        esac
    done
}

pull_policy() {
    #TODO: check if we need to pull policies from git repo
    #for now let's assume that the policies are stored inside
    #the repo
    true
}

check_deps
parse_arguments "$@"

dirs="$(echo "$files" | xargs -n1 dirname | sort -u | uniq)"

for dir in $dirs; do
    if [[ "${dir##"$_d"}" != "$dir" ]]; then
        $CONFTEST test --ignore="${conftest_ignore}" --policy "$_p" "$dir" || RC="$?"
    fi
done

exit $RC

#!/usr/bin/env bash
# One league iteration at a time: an iteration claims its number on GitHub
# before it starts, so two never start from the same ledger.
#
#   scripts/claim-iteration.sh claim [--base REF] [--by TEXT]
#   scripts/claim-iteration.sh status [--base REF]
#   scripts/claim-iteration.sh release N CLAIM
#
# The claim is the branch claude/league-iteration-N on origin, pointing at an
# empty commit on origin/main whose message says who claimed it and when. The
# push creates the branch only if it doesn't exist, which GitHub decides
# atomically, so of two sessions claiming the same number one wins.
#
# N is one more than the last "## Iteration N" of the ledger at --base
# (origin/main by default, fetched first; a session that goes on from its own
# unmerged iteration passes its branch). The claim commit is always on
# origin/main, so a claim pushes nothing of the iteration's work.
#
# claim:   prints "N CLAIM" (the claim commit) and exits 0, or names who holds
#          N and exits 2.
# status:  prints the next N and who holds it, if anyone; exits 0 when it is
#          free, 2 when it is claimed.
# release: deletes the claim, only if the branch still points at CLAIM.
#
# The finished iteration replaces the claim commit on the same branch:
#
#   git push --force-with-lease=refs/heads/claude/league-iteration-N:CLAIM \
#       origin HEAD:refs/heads/claude/league-iteration-N
#
# The claim holds until main has the iteration's ledger entry (its pull request
# merged) or it is released. CLAIM_PUSH_URL, when set, is where the claim is
# pushed (the automated iteration's App token); fetches always use origin.
set -euo pipefail

usage() {
  sed -n '5,7p' "$0" | sed 's/^# *//' >&2
  exit 64
}

cmd=${1:-}
[ -n "$cmd" ] || usage
shift
base=origin/main
by=""
while [ $# -gt 0 ]; do
  case $1 in
    --base) base=$2; shift 2 ;;
    --by) by=$2; shift 2 ;;
    -h | --help) usage ;;
    *) break ;;
  esac
done
push_url=${CLAIM_PUSH_URL:-origin}

branch_of() { echo "claude/league-iteration-$1"; }

next_number() {
  local last
  last=$(git show "$1:ledger/iterations.md" | sed -nE 's/^## Iteration ([0-9]+)([^0-9].*)?$/\1/p' | sort -n | tail -1)
  [ -n "$last" ] || { echo "no '## Iteration N' entry in the ledger at $1" >&2; exit 1; }
  echo $((last + 1))
}

# The commit the remote branch points at, or nothing.
remote_head() {
  git ls-remote origin "refs/heads/$(branch_of "$1")" | cut -f1
}

describe_holder() {
  local n=$1 sha=$2
  git fetch -q origin "refs/heads/$(branch_of "$n")" 2>/dev/null || true
  if git cat-file -e "$sha^{commit}" 2>/dev/null; then
    git log -1 --format="%h %s%n%b" "$sha" | sed -n '1,4s/^/  /p' >&2
  fi
}

git fetch -q origin main

case $cmd in
  status)
    n=$(next_number "$base")
    held=$(remote_head "$n")
    if [ -z "$held" ]; then
      echo "iteration $n is free"
      exit 0
    fi
    echo "iteration $n is claimed: $(branch_of "$n")"
    describe_holder "$n" "$held"
    exit 2
    ;;

  claim)
    n=$(next_number "$base")
    ref="refs/heads/$(branch_of "$n")"
    [ -n "$by" ] || by="the worktree $(basename "$(git rev-parse --show-toplevel)")"
    when=$(date -u +%Y-%m-%dT%H:%M:%SZ)
    claim=$(git commit-tree "origin/main^{tree}" -p origin/main \
      -m "Claim league iteration $n" \
      -m "By: $by
At: $when
Base: $(git rev-parse --short "$base") ($base)

This empty commit holds the iteration's number while it runs. The iteration's
own commit replaces it on this branch (scripts/claim-iteration.sh).")
    # An empty expected value: the branch must not exist yet.
    if git push -q --force-with-lease="$ref:" "$push_url" "$claim:$ref" 2>/dev/null; then
      echo "claimed iteration $n as $(branch_of "$n")" >&2
      echo "$n $claim"
      exit 0
    fi
    held=$(remote_head "$n")
    if [ -z "$held" ]; then
      echo "the claim push failed and nobody holds iteration $n: check access to $push_url" >&2
      exit 1
    fi
    echo "iteration $n is already claimed: $(branch_of "$n")" >&2
    describe_holder "$n" "$held"
    exit 2
    ;;

  release)
    [ $# -eq 2 ] || usage
    n=$1
    claim=$2
    ref="refs/heads/$(branch_of "$n")"
    git push -q --force-with-lease="$ref:$claim" "$push_url" ":$ref"
    echo "released iteration $n" >&2
    ;;

  *) usage ;;
esac

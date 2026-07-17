#!/usr/bin/env bash
# git-dd-enforce: in Datadog git repos, blocks the vanilla git operations that
# git dd replaces with a faster mega-repo-aware equivalent.
#
# Only two shapes are enforced, both with an unambiguous git-dd replacement
# regardless of context:
#   git fetch / git pull            -> git dd sync
#   git rebase (origin/)main|master|prod (bare form only) -> git dd sync-and-rebase
#
# Branch creation, local switch/checkout, interactive rebase, --onto rebases
# and rebases onto non-default branches (stacked PRs) are intentionally left
# alone: git dd has no equivalent for those, or the equivalent (git dd
# new-branch) can't express "branch off my current branch instead of main."

if ! command -v jq &>/dev/null; then exit 0; fi

INPUT=$(cat)
CMD=$(echo "$INPUT" | jq -r '.tool_input.command // empty')
CWD=$(echo "$INPUT" | jq -r '.cwd // empty')

if [ -z "$CMD" ] || [ -z "$CWD" ]; then exit 0; fi

block() {
  jq -n --arg r "$1" '{continue: false, stopReason: $r}'
  exit 0
}

# Only enforce inside repos whose origin/datadog remote is a Datadog GitHub repo.
REMOTES=$(git -C "$CWD" remote -v 2>/dev/null)
if [ -z "$REMOTES" ]; then exit 0; fi
if ! echo "$REMOTES" | grep -qiE 'github\.com[:/](datadog|ddoghq)/'; then exit 0; fi

if echo "$CMD" | grep -qE '(^|[;&|]\s*)(git|dd-git)\s+(fetch|pull)\b'; then
  block "git fetch/pull is blocked in Datadog repos. Run 'git dd sync' instead — it updates the main branch, prunes merged branches and cleans up stale refs in one step."
fi

if echo "$CMD" | grep -qE '(^|[;&|]\s*)(git|dd-git)\s+rebase\s+(origin/)?(main|master|prod)\s*($|[;&|])'; then
  block "git rebase onto the main branch is blocked in Datadog repos. Run 'git dd sync-and-rebase' instead — it syncs the main branch first, then rebases your current branch on it."
fi

exit 0

#!/usr/bin/env bash
# repo-checkout-guard: blocks mutations to a DataDog repo's main checkout
# outside its own .worktrees/ subtree, so parallel agents can never collide
# on a shared checkout. Reads (grep, cat, find, git status/log) are allowed;
# only mutating command shapes and any Edit/Write/MultiEdit are blocked.
# Companion to worktree-create.sh/worktree-remove.sh.
# See docs/Claude Code Multi-Repo Worktree Guardrails.md in the vault.

if ! command -v jq &>/dev/null; then exit 0; fi

DD_REPOS_ROOT="$HOME/go/src/github.com/DataDog"
[ -d "$DD_REPOS_ROOT" ] || exit 0

INPUT=$(cat)
TOOL=$(echo "$INPUT" | jq -r '.tool_name // empty')

block() {
  jq -n --arg r "$1" '{continue: false, stopReason: $r}'
  exit 0
}

is_main_checkout_path() {
  case "$1" in
  "$DD_REPOS_ROOT"/*/.worktrees/*) return 1 ;;
  "$DD_REPOS_ROOT"/*) return 0 ;;
  *) return 1 ;;
  esac
}

case "$TOOL" in
Edit | Write | MultiEdit)
  FILE=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')
  [ -n "$FILE" ] || exit 0
  if is_main_checkout_path "$FILE"; then
    block "Blocked: $FILE is in a DataDog repo's main checkout, not a worktree. Get a worktree first (repo/branch name via the worktree skill), then edit inside .worktrees/<branch>/ instead."
  fi
  ;;
Bash)
  CMD=$(echo "$INPUT" | jq -r '.tool_input.command // empty')
  [ -n "$CMD" ] || exit 0
  # Verb and path are checked independently (not adjacently) since `git -C
  # <path> commit` puts flags between the git subcommand and the path.
  if echo "$CMD" | grep -qE '(^|[[:space:];&|])(add|commit|checkout|switch|reset|merge|rebase|stash|clean|rm|mv|tee)([[:space:]]|$)' \
    || echo "$CMD" | grep -qE 'cp[[:space:]]+[^|;&]*-f|sed[[:space:]]+-i'; then
    MATCH=$(echo "$CMD" | grep -oE "$DD_REPOS_ROOT/[A-Za-z0-9_./-]+" | head -1)
    if [ -n "$MATCH" ] && is_main_checkout_path "$MATCH"; then
      block "Blocked: this command mutates $MATCH, a DataDog repo's main checkout, not a worktree. Get a worktree first, then run mutating commands inside .worktrees/<branch>/ instead."
    fi
  fi
  CWD=$(echo "$INPUT" | jq -r '.cwd // empty')
  if [ -n "$CWD" ] && is_main_checkout_path "$CWD"; then
    block "Blocked: this command's working directory $CWD is a DataDog repo's main checkout, not a worktree. Get a worktree first."
  fi
  ;;
esac

exit 0

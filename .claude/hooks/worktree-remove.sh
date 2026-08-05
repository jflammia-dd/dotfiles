#!/usr/bin/env bash
# worktree-remove: WorktreeRemove hook. Unlocks and removes the worktree
# WorktreeCreate made. Refuses (leaves it in place) if the worktree is
# dirty, since `git worktree remove` without --force does that by default.
# See docs/Claude Code Multi-Repo Worktree Guardrails.md in the vault.

if ! command -v jq &>/dev/null; then exit 0; fi

INPUT=$(cat)
WORKTREE_PATH=$(echo "$INPUT" | jq -r '.worktree_path // empty')

[ -n "$WORKTREE_PATH" ] || exit 0
[ -d "$WORKTREE_PATH" ] || exit 0

MAIN_REPO=$(git -C "$WORKTREE_PATH" rev-parse --path-format=absolute --git-common-dir 2>/dev/null)
[ -n "$MAIN_REPO" ] || exit 0
MAIN_REPO=$(dirname "$MAIN_REPO")

git -C "$MAIN_REPO" worktree unlock "$WORKTREE_PATH" 2>/dev/null || true
git -C "$MAIN_REPO" worktree remove "$WORKTREE_PATH" 2>/dev/null || true

exit 0

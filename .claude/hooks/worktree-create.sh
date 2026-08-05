#!/usr/bin/env bash
# worktree-create: WorktreeCreate hook. Routes to one of several DataDog
# repos under ~/go/src/github.com/DataDog (repos live outside the Obsidian
# vault launch directory, so native single-repo worktree detection can't
# find them). The repo is encoded as the first "/"-segment of the requested
# worktree name: "dd-source/justin.flammia/SEC-12345-fix" creates a
# worktree in dd-source on branch justin.flammia/SEC-12345-fix.
# See docs/Claude Code Multi-Repo Worktree Guardrails.md in the vault.

set -euo pipefail

if ! command -v jq &>/dev/null; then
  echo "worktree-create: jq is required" >&2
  exit 1
fi

INPUT=$(cat)
NAME=$(echo "$INPUT" | jq -r '.name // empty')

if [ -z "$NAME" ]; then
  echo "worktree-create: no name provided" >&2
  exit 1
fi

REPO="${NAME%%/*}"
BRANCH="${NAME#*/}"

if [ "$REPO" = "$NAME" ] || [ -z "$BRANCH" ]; then
  echo "worktree-create: name must be '<repo>/<branch>', got '$NAME'" >&2
  exit 1
fi

DD_REPOS_ROOT="$HOME/go/src/github.com/DataDog"
REPO_DIR="$DD_REPOS_ROOT/$REPO"

if [ ! -d "$REPO_DIR/.git" ]; then
  echo "worktree-create: no repo at $REPO_DIR" >&2
  exit 1
fi

WORKTREE_DIR="$REPO_DIR/.worktrees/$BRANCH"

if [ -e "$WORKTREE_DIR" ]; then
  echo "worktree-create: $WORKTREE_DIR already exists (collision on repo+branch)" >&2
  exit 1
fi

# Local-only ignore so .worktrees/ never shows up as untracked clutter,
# without touching the repo's tracked .gitignore.
EXCLUDE_FILE="$REPO_DIR/.git/info/exclude"
grep -qxF '.worktrees/' "$EXCLUDE_FILE" 2>/dev/null || echo '.worktrees/' >>"$EXCLUDE_FILE"

# baseRef "head": branch from local HEAD only, never fetch origin. Run
# `git dd sync-and-rebase` beforehand for a worktree off current main.
git -C "$REPO_DIR" worktree add -b "$BRANCH" "$WORKTREE_DIR" HEAD >&2

git -C "$REPO_DIR" worktree lock "$WORKTREE_DIR" --reason "held by Claude Code session" >&2 || true

if [ "$REPO" = "dd-source" ]; then
  SHARED_OUTPUT_BASE="$HOME/.cache/bazel-output-bases/dd-source-shared"
  mkdir -p "$SHARED_OUTPUT_BASE"
  echo "$SHARED_OUTPUT_BASE" >"$WORKTREE_DIR/.bazel-shared-output-base"
fi

echo "$WORKTREE_DIR"

#!/usr/bin/env bash
# worktree-sweep: SessionStart hook. Removes unlocked worktrees under any
# DataDog repo's .worktrees/ that are either merged+clean or idle 14+ days
# with no activity and no working-tree changes. Locked worktrees (in use by
# a live session) and dirty or recently-active unmerged worktrees are never
# touched. Backstop for WorktreeRemove not firing on a crash.
# See docs/Claude Code Multi-Repo Worktree Guardrails.md in the vault.

DD_REPOS_ROOT="$HOME/go/src/github.com/DataDog"
IDLE_SECONDS=$((14 * 24 * 60 * 60))
NOW=$(date +%s)

[ -d "$DD_REPOS_ROOT" ] || exit 0

for REPO_DIR in "$DD_REPOS_ROOT"/*/; do
  REPO_DIR="${REPO_DIR%/}"
  [ -d "$REPO_DIR/.git" ] || continue
  [ -d "$REPO_DIR/.worktrees" ] || continue

  DEFAULT_BRANCH=$(git -C "$REPO_DIR" rev-parse --abbrev-ref origin/HEAD 2>/dev/null | sed 's@^origin/@@')
  [ -n "$DEFAULT_BRANCH" ] || DEFAULT_BRANCH="main"

  RECORD=""
  while IFS= read -r LINE; do
    if [ -z "$LINE" ]; then
      WT_PATH=$(printf '%s' "$RECORD" | awk '/^worktree /{print substr($0,10)}')
      LOCKED=$(printf '%s' "$RECORD" | grep -c '^locked')
      RECORD=""
      [ -n "$WT_PATH" ] || continue
      case "$WT_PATH" in
      */.worktrees/*) ;; # only ever touch worktrees we created
      *) continue ;;      # skip the main checkout entry
      esac
      [ "$LOCKED" -eq 0 ] || continue
      [ -d "$WT_PATH" ] || continue

      DIRTY=$(git -C "$WT_PATH" status --porcelain 2>/dev/null)
      [ -z "$DIRTY" ] || continue

      BRANCH=$(git -C "$WT_PATH" rev-parse --abbrev-ref HEAD 2>/dev/null)
      LAST_COMMIT=$(git -C "$WT_PATH" log -1 --format=%ct 2>/dev/null || echo 0)

      MERGED=1
      git -C "$REPO_DIR" merge-base --is-ancestor "$BRANCH" "$DEFAULT_BRANCH" 2>/dev/null && MERGED=0

      IDLE=0
      if [ "$LAST_COMMIT" -gt 0 ] && [ $((NOW - LAST_COMMIT)) -ge "$IDLE_SECONDS" ]; then IDLE=1; fi

      if [ "$MERGED" -eq 0 ] || [ "$IDLE" -eq 1 ]; then
        git -C "$REPO_DIR" worktree remove "$WT_PATH" 2>/dev/null
      fi
    else
      RECORD="$RECORD
$LINE"
    fi
  done < <(git -C "$REPO_DIR" worktree list --porcelain 2>/dev/null; echo)

  git -C "$REPO_DIR" worktree prune 2>/dev/null
done

exit 0

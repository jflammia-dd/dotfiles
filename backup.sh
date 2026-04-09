#!/usr/bin/env bash
# Sync ~/.claude/ config into this repo and push to GitHub.
# Run manually at any time, or let launchd run it daily.
set -euo pipefail

DOTFILES="$(cd "$(dirname "$0")" && pwd)"
CLAUDE="$HOME/.claude"

# Sync home dotfiles
echo "Syncing home dotfiles ..."
for f in .zshrc .zshenv .zprofile .gitconfig; do
  [ -f "$HOME/$f" ] && cp "$HOME/$f" "$DOTFILES/$f"
done

# Sync git config (global ignore)
mkdir -p "$DOTFILES/.config/git"
[ -f "$HOME/.config/git/ignore" ] && cp "$HOME/.config/git/ignore" "$DOTFILES/.config/git/ignore"

# Sync gitsign config (public files only — signing-key is a private key and never synced)
if [ -d "$HOME/.config/gitsign" ]; then
  mkdir -p "$DOTFILES/.config/gitsign"
  rsync -a \
    --exclude='signing-key' \
    --exclude='signing-key.pub' \
    --exclude='.install_id' \
    "$HOME/.config/gitsign/" "$DOTFILES/.config/gitsign/"
fi

echo "Syncing ~/.claude/ ..."

rsync -a --no-links \
  --exclude='.credentials.json' \
  --exclude='.credentials.json.bak' \
  --exclude='history.jsonl' \
  --exclude='*.jsonl' \
  --exclude='cache/' \
  --exclude='debug/' \
  --exclude='downloads/' \
  --exclude='file-history/' \
  --exclude='image-cache/' \
  --exclude='ide/' \
  --exclude='paste-cache/' \
  --exclude='session-env/' \
  --exclude='sessions/' \
  --exclude='shell-snapshots/' \
  --exclude='skill-workspaces/' \
  --exclude='statsig/' \
  --exclude='tasks/' \
  --exclude='telemetry/' \
  --exclude='todos/' \
  --exclude='usage-data/' \
  --exclude='backups/' \
  --exclude='plugins/' \
  --exclude='projects/' \
  --exclude='plans/' \
  --exclude='skills/find-skills' \
  --exclude='skills/first-principles-decomposer' \
  --exclude='skills/slackfmt' \
  --exclude='skills/*-workspace/' \
  --exclude='security_warnings_state_*.json' \
  --exclude='stats-cache.json' \
  --exclude='.ccstatusline-version-cache' \
  --exclude='settings.json.bak' \
  --exclude='settings.json.orig' \
  --exclude='*.bak' \
  --exclude='*.orig' \
  --exclude='__pycache__/' \
  --exclude='*.pyc' \
  "$CLAUDE/" "$DOTFILES/.claude/"

# Memory files live nested inside projects/ — sync them separately
find "$CLAUDE/projects" -type d -name "memory" 2>/dev/null | while read mem_dir; do
  rel="${mem_dir#"$CLAUDE/"}"
  dest="$DOTFILES/.claude/$rel"
  mkdir -p "$dest"
  rsync -a "$mem_dir/" "$dest/"
done

cd "$DOTFILES"

# Guard: refuse to commit if any hardcoded secret patterns are present
SECRET_HITS=$(grep -rn \
  -e "github_pat_[A-Za-z0-9_]\{20,\}" \
  -e "ghp_[A-Za-z0-9]\{36\}" \
  -e "figd_[A-Za-z0-9_-]\{20,\}" \
  -e "sk-[A-Za-z0-9]\{20,\}" \
  --include="*.sh" --include="*.zsh" --include="*.zshrc" --include="*.zshenv" \
  --include="*.zprofile" --include="*.json" --include="*.py" \
  . 2>/dev/null | grep -v "Binary" || true)
if [ -n "$SECRET_HITS" ]; then
  echo "ERROR: Possible secret found in tracked files. Aborting backup."
  echo "$SECRET_HITS"
  exit 1
fi

if git diff --quiet && git diff --cached --quiet && [ -z "$(git ls-files --others --exclude-standard)" ]; then
  echo "Nothing changed. No backup needed."
  exit 0
fi

git add -A
git commit -m "dotfiles backup $(date '+%Y-%m-%d %H:%M')"
git push
echo "Backup pushed: $(date)"

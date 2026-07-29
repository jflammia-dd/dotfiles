#!/usr/bin/env bash
# Run this ONCE on an existing machine to switch dotfiles from real files
# to symlinks pointing at this repo. Creates a timestamped backup first.
#
# Usage:
#   ./migrate.sh             # apply changes (backs up first)
#   ./migrate.sh --dry-run   # preview only, no changes made
#
# On a fresh machine with no existing dotfiles, use install.sh instead.
set -euo pipefail

DOTFILES="$(cd "$(dirname "$0")" && pwd)"
DRY_RUN=false
source "$DOTFILES/lib/owned-agent-skills.sh"

if [[ "${1:-}" == "--dry-run" ]]; then
  DRY_RUN=true
  echo "[DRY RUN] No changes will be made."
  echo ""
fi

# Collect all tracked files
tracked=()
while IFS= read -r df; do
  tracked+=("$df")
done < <(find "$DOTFILES" \
           \( -name ".git" -prune \) -o \
           \( -path "$DOTFILES/.agents" -prune \) -o \
           \( -type f \
              -path "$DOTFILES/.*" \
              ! -name ".gitignore" \
              -print \) \
         | sort)

if [ ${#tracked[@]} -eq 0 ]; then
  echo "ERROR: No tracked dotfiles found in $DOTFILES"
  exit 1
fi

echo "Tracked files in repo: ${#tracked[@]}"
echo ""

# Categorise each file
to_replace=()   # real file exists, will be replaced with symlink
to_update=()    # already a symlink, will be retargeted
to_create=()    # does not exist yet, will be created

for df in "${tracked[@]}"; do
  link="${df/$DOTFILES/$HOME}"
  if [ -L "$link" ]; then
    to_update+=("$df")
  elif [ -e "$link" ]; then
    to_replace+=("$df")
  else
    to_create+=("$df")
  fi
done

# Report
if [ ${#to_replace[@]} -gt 0 ]; then
  echo "Will replace (backup first):"
  for df in "${to_replace[@]}"; do
    echo "  ${df/$DOTFILES/$HOME}"
  done
  echo ""
fi

if [ ${#to_update[@]} -gt 0 ]; then
  echo "Already symlinks (will retarget if pointing elsewhere):"
  for df in "${to_update[@]}"; do
    link="${df/$DOTFILES/$HOME}"
    current_target="$(readlink "$link")"
    if [ "$current_target" = "$df" ]; then
      echo "  OK $link"
    else
      echo "  RETARGET $link  ($current_target -> $df)"
    fi
  done
  echo ""
fi

if [ ${#to_create[@]} -gt 0 ]; then
  echo "Will create (no existing file):"
  for df in "${to_create[@]}"; do
    echo "  ${df/$DOTFILES/$HOME}"
  done
  echo ""
fi

if $DRY_RUN; then
  echo "Owned cross-harness agent skills:"
  restore_owned_agent_skills true
  echo ""
  echo "Dry run complete. Run without --dry-run to apply."
  exit 0
fi

# Back up every real file that will be replaced
if [ ${#to_replace[@]} -gt 0 ]; then
  BACKUP="$HOME/.dotfiles-backup-$(date +%Y%m%d-%H%M%S)"
  echo "Creating backup at $BACKUP ..."
  for df in "${to_replace[@]}"; do
    link="${df/$DOTFILES/$HOME}"
    dest="$BACKUP/${link#"$HOME/"}"
    mkdir -p "$(dirname "$dest")"
    cp -a "$link" "$dest"
  done
  echo "Backup created."
  echo ""
fi

# Create symlinks
echo "Creating symlinks ..."
for df in "${tracked[@]}"; do
  link="${df/$DOTFILES/$HOME}"
  mkdir -p "$(dirname "$link")"
  ln -sf "$df" "$link"
  echo "  $link -> $df"
done

echo ""
echo "Restoring owned cross-harness agent skills ..."
restore_owned_agent_skills false

echo ""
echo "Done."
if [ ${#to_replace[@]} -gt 0 ]; then
  echo ""
  echo "Previous files backed up to: $BACKUP"
  echo "Delete once you have verified everything works:"
  echo "  rm -rf $BACKUP"
fi

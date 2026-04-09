#!/usr/bin/env bash
# Run this ONCE on an existing machine to switch ~/.claude/ from real files
# to symlinks pointing at this repo. Creates a timestamped backup first.
#
# On a fresh machine, use install.sh instead.
set -euo pipefail

DOTFILES="$(cd "$(dirname "$0")" && pwd)"
BACKUP="$HOME/.claude-backup-$(date +%Y%m%d-%H%M%S)"

echo "Creating safety backup at $BACKUP ..."
rsync -a "$HOME/.claude/" "$BACKUP/"
echo "Backup created."

echo ""
echo "Creating symlinks from $DOTFILES to $HOME ..."
find "$DOTFILES" -type f -path "$DOTFILES/.*" | while read -r df; do
  link="${df/$DOTFILES/$HOME}"
  link_dir="$(dirname "$link")"
  mkdir -p "$link_dir"
  if [ -e "$link" ] && [ ! -L "$link" ]; then
    echo "  replacing: $link"
  elif [ -L "$link" ]; then
    echo "  updating:  $link"
  else
    echo "  linking:   $link"
  fi
  ln -sf "$df" "$link"
done

echo ""
echo "Done. Your previous ~/.claude/ is backed up at:"
echo "  $BACKUP"
echo ""
echo "You can delete the backup once you've verified everything works:"
echo "  rm -rf $BACKUP"

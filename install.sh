#!/usr/bin/env bash
# Fresh machine setup: symlink dotfiles and configure scheduled backup.
# On an existing machine with files already in place, use migrate.sh instead.
set -euo pipefail

DOTFILES="$(cd "$(dirname "$0")" && pwd)"

echo "Symlinking dotfiles from $DOTFILES ..."
find "$DOTFILES" \
    \( -name ".git" -prune \) -o \
    \( -type f \
       -path "$DOTFILES/.*" \
       ! -name ".gitignore" \
       -print \) \
  | while read -r df; do
  link="${df/$DOTFILES/$HOME}"
  mkdir -p "$(dirname "$link")"
  ln -sf "$df" "$link"
  echo "  $link"
done

# Install Oh My Zsh if not already installed
if [ ! -d "$HOME/.oh-my-zsh" ]; then
  RUNZSH=no sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
fi

# Install zsh plugins
ZSH_CUSTOM="${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}"

if [ ! -d "$ZSH_CUSTOM/plugins/zsh-syntax-highlighting" ]; then
  git clone https://github.com/zsh-users/zsh-syntax-highlighting.git "$ZSH_CUSTOM/plugins/zsh-syntax-highlighting"
fi

if [ ! -d "$ZSH_CUSTOM/plugins/zsh-autosuggestions" ]; then
  git clone https://github.com/zsh-users/zsh-autosuggestions.git "$ZSH_CUSTOM/plugins/zsh-autosuggestions"
fi

if [ ! -d "$ZSH_CUSTOM/plugins/fzf-tab" ]; then
  git clone https://github.com/Aloxaf/fzf-tab.git "$ZSH_CUSTOM/plugins/fzf-tab"
fi

# Install daily backup LaunchAgent
PLIST_SRC="$DOTFILES/launchd/com.justin.dotfiles-backup.plist"
PLIST_DEST="$HOME/Library/LaunchAgents/com.justin.dotfiles-backup.plist"
if [ -f "$PLIST_SRC" ]; then
  mkdir -p "$HOME/Library/LaunchAgents"
  cp "$PLIST_SRC" "$PLIST_DEST"
  launchctl load "$PLIST_DEST" 2>/dev/null || true
  echo "Daily backup LaunchAgent installed (runs at 3pm)."
fi

echo ""
echo "Setup complete. Run ./backup.sh anytime to push a manual backup."

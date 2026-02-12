#!/usr/bin/env bash
set -euo pipefail

DOTFILES_PATH="$HOME/dotfiles"

# Symlink dotfiles to the home directory
find "$DOTFILES_PATH" -type f -path "$DOTFILES_PATH/.*" |
while read df; do
  link=${df/$DOTFILES_PATH/$HOME}
  mkdir -p "$(dirname "$link")"
  ln -sf "$df" "$link"
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

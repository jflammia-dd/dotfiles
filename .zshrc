# Auto-attach to tmux on SSH login
if [ -n "$SSH_CONNECTION" ] && [ -z "$TMUX" ]; then
  tmux attach -t default 2>/dev/null || tmux new -s default
fi

# Path to your Oh My Zsh installation.
export ZSH="$HOME/.oh-my-zsh"

ZSH_THEME="robbyrussell"

plugins=(
  git
  fzf-tab
  zsh-syntax-highlighting
  zsh-autosuggestions
  kubectl
)

source $ZSH/oh-my-zsh.sh

# Preferred editor
export EDITOR='nvim'
export VISUAL='nvim'
export GIT_EDITOR='nvim'

# Aliases
alias ll='ls -lah'
alias vim='nvim'
alias vi='nvim'

export DATADOG_ROOT="$HOME/dd"

# If you come from bash you might have to change your $PATH.
# export PATH=$HOME/bin:$HOME/.local/bin:/usr/local/bin:$PATH

# fix for bashcompinit leaking nobareglobqual and breaking oh-my-zsh's (N) glob checks (2026-08-05)
setopt bareglobqual

# Path to your Oh My Zsh installation.
export ZSH="$HOME/.oh-my-zsh"

# Set name of the theme to load --- if set to "random", it will
# load a random theme each time Oh My Zsh is loaded, in which case,
# to know which specific one was loaded, run: echo $RANDOM_THEME
# See https://github.com/ohmyzsh/ohmyzsh/wiki/Themes
ZSH_THEME="robbyrussell"

# Set list of themes to pick from when loading at random
# Setting this variable when ZSH_THEME=random will cause zsh to load
# a theme from this variable instead of looking in $ZSH/themes/
# If set to an empty array, this variable will have no effect.
# ZSH_THEME_RANDOM_CANDIDATES=( "robbyrussell" "agnoster" )

# Uncomment the following line to use case-sensitive completion.
# CASE_SENSITIVE="true"

# Uncomment the following line to use hyphen-insensitive completion.
# Case-sensitive completion must be off. _ and - will be interchangeable.
# HYPHEN_INSENSITIVE="true"

# Uncomment one of the following lines to change the auto-update behavior
# zstyle ':omz:update' mode disabled  # disable automatic updates
# zstyle ':omz:update' mode auto      # update automatically without asking
# zstyle ':omz:update' mode reminder  # just remind me to update when it's time

# Uncomment the following line to change how often to auto-update (in days).
# zstyle ':omz:update' frequency 13

# Uncomment the following line if pasting URLs and other text is messed up.
# DISABLE_MAGIC_FUNCTIONS="true"

# Uncomment the following line to disable colors in ls.
# DISABLE_LS_COLORS="true"

# Uncomment the following line to disable auto-setting terminal title.
# DISABLE_AUTO_TITLE="true"

# Uncomment the following line to enable command auto-correction.
# ENABLE_CORRECTION="true"

# Uncomment the following line to display red dots whilst waiting for completion.
# You can also set it to another string to have that shown instead of the default red dots.
# e.g. COMPLETION_WAITING_DOTS="%F{yellow}waiting...%f"
# Caution: this setting can cause issues with multiline prompts in zsh < 5.7.1 (see #5765)
# COMPLETION_WAITING_DOTS="true"

# Uncomment the following line if you want to disable marking untracked files
# under VCS as dirty. This makes repository status check for large repositories
# much, much faster.
# DISABLE_UNTRACKED_FILES_DIRTY="true"

# Uncomment the following line if you want to change the command execution time
# stamp shown in the history command output.
# You can set one of the optional three formats:
# "mm/dd/yyyy"|"dd.mm.yyyy"|"yyyy-mm-dd"
# or set a custom format using the strftime function format specifications,
# see 'man strftime' for details.
# HIST_STAMPS="mm/dd/yyyy"

# Would you like to use another custom folder than $ZSH/custom?
# ZSH_CUSTOM=/path/to/new-custom-folder

# Which plugins would you like to load?
# Standard plugins can be found in $ZSH/plugins/
# Custom plugins may be added to $ZSH_CUSTOM/plugins/
# Example format: plugins=(rails git textmate ruby lighthouse)
# Add wisely, as too many plugins slow down shell startup.
plugins=(
  git
  fzf-tab
  zsh-syntax-highlighting
  zsh-autosuggestions
  kubectl
)

source $ZSH/oh-my-zsh.sh

# User configuration

# export MANPATH="/usr/local/man:$MANPATH"

# You may need to manually set your language environment
# export LANG=en_US.UTF-8

# Preferred editor for local and remote sessions
export EDITOR='nvim'
export VISUAL='nvim'
export GIT_EDITOR='nvim'

# Compilation flags
# export ARCHFLAGS="-arch $(uname -m)"

# Set personal aliases, overriding those provided by Oh My Zsh libs,
# plugins, and themes. Aliases can be placed here, though Oh My Zsh
# users are encouraged to define aliases within a top-level file in
# the $ZSH_CUSTOM folder, with .zsh extension. Examples:
# - $ZSH_CUSTOM/aliases.zsh
# - $ZSH_CUSTOM/macos.zsh
# For a full list of active aliases, run `alias`.
#
# Aliases
 alias zshconfig="vim ~/.zshrc"
 alias ohmyzsh="vim ~/.oh-my-zsh"

alias ls='eza'
alias ll='eza -l --header --icons'
alias la='eza -la --header --icons'
alias tree='eza --tree'

alias ccstatus='npx -y ccstatusline@latest'
alias cat='bat'
alias grep='rg'

eval "$(zoxide init zsh)"

# grpcurl alias for siem-entity-api
alias grpc-siem='grpcurl -plaintext \
  -import-path $HOME/dd/dd-source/domains/cloud-security-platform/apps/apis/siem-entity-api/entitiespb \
  -import-path /opt/homebrew/include \
  -import-path $HOME/.local/share/proto-include \
  -proto entities.proto'

# Use Neovim instead of Vim
alias vim='nvim'
alias vi='nvim'

# Homebrew
autoload -Uz compinit
compinit

# git dd
autoload -Uz _git_dd

export DATADOG_ROOT="$HOME/dd"
export PATH="$DATADOG_ROOT/devtools/bin:$PATH"

# gh authenticates via its own keyring (run `gh auth login` to set up).
# The Figma MCP uses OAuth via https://mcp.figma.com/mcp.
# Neither needs tokens injected from the shell.

# Claude code
#export CLAUDE_CODE_NO_FLICKER=1

# https://datadoghq.atlassian.net/wiki/spaces/ENG/pages/2291499908/Go#macOS-Development
export PKG_CONFIG_PATH="$(brew --prefix)/opt/openssl/lib/pkgconfig:$PKG_CONFIG_PATH"
export PKG_CONFIG_PATH="$(brew --prefix)/lib/pkgconfig:$PKG_CONFIG_PATH"
export CPATH="$(brew --prefix)/include:$CPATH"
export LIBRARY_PATH="$(brew --prefix)/lib:$LIBRARY_PATH"


# Claude Code runs directly (no `script` wrapper). The wrapper was removed
# 2026-06-04 because macOS `script` does not forward SIGWINCH, which froze the
# TUI at its launch size and corrupted rendering on every resize. See
# docs/Ghostty Rendering Corruption.md in the Datadog vault.

#THIS MUST BE AT THE END OF THE FILE FOR SDKMAN TO WORK!!!
export SDKMAN_DIR="$HOME/.sdkman"
[[ -s "$HOME/.sdkman/bin/sdkman-init.sh" ]] && source "$HOME/.sdkman/bin/sdkman-init.sh"
export PYENV_ROOT="$HOME/.pyenv"
[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init - zsh)"
#compdef gt
###-begin-gt-completions-###
#
# yargs command completion script
#
# Installation: gt completion >> ~/.zshrc
#    or gt completion >> ~/.zprofile on OSX.
#
_gt_yargs_completions()
{
  local reply
  local si=$IFS
  IFS=$'
' reply=($(COMP_CWORD="$((CURRENT-1))" COMP_LINE="$BUFFER" COMP_POINT="$CURSOR" gt --get-yargs-completions "${words[@]}"))
  IFS=$si
  _describe 'values' reply
}
compdef _gt_yargs_completions gt
###-end-gt-completions-###



# dd-curl: wraps dd-auth + curl for easy Datadog API calls
# See: https://datadoghq.atlassian.net/wiki/spaces/~630fbeeb8d88ec800fbe6546/pages/5271783161
dd-curl() {
  local url host
  local -a auth=(dd-auth)
  for url in "$@"; do [[ $url == http*://* ]] && break; url=""; done
  if [[ -n $url ]]; then
    host=${url#*://}; host=${host%%[/:]*}; host=${host#api.}
    [[ $host == datadoghq.eu ]] && host=app.datadoghq.eu
    [[ $host == datad0g.com ]] && host=dd.datad0g.com
    [[ $host != datadoghq.com ]] && auth+=(--domain "$host")
  fi

  "${auth[@]}" -- bash -c '
    curl -sS \
      -H "Accept: application/json" \
      -H "DD-API-KEY: $DD_API_KEY" \
      -H "DD-APPLICATION-KEY: $DD_APP_KEY" \
      "$@"
  ' _ "$@"
}

# Trajectory - AI coding agent observability
export PATH="/Users/justin.flammia/.trajectory/bin:$PATH"

# Per-repo GitHub account selection via direnv (see ~/.config/direnv/lib/).
eval "$(direnv hook zsh)"

# Disable high-context web search confirmation gate (prevents stuck sessions from concurrent confirm prompts)
export PI_RESEARCH_WEB_CONFIRM_HIGH_CONTEXT=false

# pi-patch-layer wrapper: intercepts pi update --extensions to re-apply patches
export PATH="$HOME/.pi/agent/patches/bin:$PATH"

eval "$(/opt/dogbrew/bin/dogbrew init zsh)"

# Colima Docker socket
export DOCKER_HOST="unix://$HOME/.colima/default/docker.sock"
export TESTCONTAINERS_DOCKER_SOCKET_OVERRIDE=/var/run/docker.sock

# Ensure PI_CLIENT_SESSION_ID always has a value (prevents pi subagent auth failures)
export PI_CLIENT_SESSION_ID="${PI_CLIENT_SESSION_ID:-unknown}"

# Force-refresh ddtool token when pi auth errors occur
alias pi-auth-refresh='ddtool auth login --datacenter us1.ddbuild.io --force && echo "Token refreshed"'

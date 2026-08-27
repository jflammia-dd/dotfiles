source /Users/justin.flammia/.privilegesalias

eval "$(/opt/homebrew/bin/brew shellenv zsh)"

# Created by `pipx` on 2026-01-28 16:09:38
export PATH="$PATH:/Users/justin.flammia/.local/bin"


# Added by Toolbox App
export PATH="$PATH:/Users/justin.flammia/Library/Application Support/JetBrains/Toolbox/scripts"

export PYENV_ROOT="$HOME/.pyenv"
[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init - zsh)"

# Added by Obsidian
export PATH="$PATH:/Applications/Obsidian.app/Contents/MacOS"

eval "$(/opt/dogbrew/bin/dogbrew init zsh)"

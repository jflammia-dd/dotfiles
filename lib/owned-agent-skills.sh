#!/usr/bin/env bash

# Shared backup and restore helpers for explicitly owned cross-harness skills.
# The caller must set DOTFILES and may override HOME in tests.

owned_agent_skills_manifest() {
  printf '%s\n' "$DOTFILES/.agents/owned-skills.txt"
}

validate_owned_agent_skill_name() {
  local skill="$1"
  if [[ ! "$skill" =~ ^[A-Za-z0-9][A-Za-z0-9._-]*$ ]]; then
    echo "ERROR: Invalid owned agent skill name in manifest: $skill" >&2
    return 1
  fi
}

sync_owned_agent_skills() {
  local manifest
  manifest="$(owned_agent_skills_manifest)"
  if [ ! -f "$manifest" ]; then
    echo "ERROR: Owned agent skill manifest is missing: $manifest" >&2
    return 1
  fi

  local skill src dest
  while IFS= read -r skill || [ -n "$skill" ]; do
    [[ -z "$skill" || "$skill" =~ ^[[:space:]]*# ]] && continue
    validate_owned_agent_skill_name "$skill"

    src="$HOME/.agents/skills/$skill"
    dest="$DOTFILES/.agents/skills/$skill"
    if [ ! -d "$src" ] || [ -L "$src" ]; then
      echo "ERROR: Allowlisted agent skill is missing or not a real directory: $src" >&2
      echo "The existing backup was left untouched." >&2
      return 1
    fi

    mkdir -p "$dest"
    rsync -a --no-links --delete --delete-excluded \
      --exclude='.git/' \
      --exclude='.env' \
      --exclude='.env.*' \
      --exclude='.credentials.json' \
      --exclude='credentials.json' \
      --exclude='*.token' \
      --exclude='*.pem' \
      --exclude='*.key' \
      --exclude='.DS_Store' \
      --exclude='__pycache__/' \
      --exclude='*.pyc' \
      --exclude='cache/' \
      --exclude='node_modules/' \
      --exclude='.venv/' \
      "$src/" "$dest/"
    echo "  backed up owned agent skill: $skill"
  done < "$manifest"
}

restore_owned_agent_skills() {
  local dry_run="${1:-false}"
  local manifest
  manifest="$(owned_agent_skills_manifest)"
  if [ ! -f "$manifest" ]; then
    echo "ERROR: Owned agent skill manifest is missing: $manifest" >&2
    return 1
  fi

  local skill src dest adapter adapter_target current_target
  while IFS= read -r skill || [ -n "$skill" ]; do
    [[ -z "$skill" || "$skill" =~ ^[[:space:]]*# ]] && continue
    validate_owned_agent_skill_name "$skill"

    src="$DOTFILES/.agents/skills/$skill"
    dest="$HOME/.agents/skills/$skill"
    adapter="$HOME/.claude/skills/$skill"
    adapter_target="../../.agents/skills/$skill"

    if [ ! -d "$src" ]; then
      echo "ERROR: Backup for allowlisted agent skill is missing: $src" >&2
      return 1
    fi

    if [ -L "$dest" ]; then
      echo "WARNING: Keeping symlink at canonical agent skill path: $dest" >&2
    elif [ -d "$dest" ]; then
      if ! diff -qr "$src" "$dest" >/dev/null 2>&1; then
        echo "WARNING: Keeping existing agent skill with local differences: $dest" >&2
      else
        echo "  existing owned agent skill is current: $skill"
      fi
    elif [ -e "$dest" ]; then
      echo "WARNING: Keeping non-directory at canonical agent skill path: $dest" >&2
    elif $dry_run; then
      echo "  would restore owned agent skill: $dest"
    else
      mkdir -p "$dest"
      rsync -a --no-links \
        --exclude='.git/' \
        --exclude='.env' \
        --exclude='.env.*' \
        --exclude='.credentials.json' \
        --exclude='credentials.json' \
        --exclude='*.token' \
        --exclude='*.pem' \
        --exclude='*.key' \
        --exclude='.DS_Store' \
        --exclude='__pycache__/' \
        --exclude='*.pyc' \
        --exclude='cache/' \
        --exclude='node_modules/' \
        --exclude='.venv/' \
        "$src/" "$dest/"
      echo "  restored owned agent skill: $skill"
    fi

    if [ -L "$adapter" ]; then
      current_target="$(readlink "$adapter")"
      if [ "$current_target" = "$adapter_target" ]; then
        echo "  Claude adapter is current: $skill"
      else
        echo "WARNING: Keeping existing Claude adapter target: $adapter -> $current_target" >&2
      fi
    elif [ -e "$adapter" ]; then
      echo "WARNING: Keeping existing non-symlink Claude skill: $adapter" >&2
    elif $dry_run; then
      echo "  would create Claude adapter: $adapter -> $adapter_target"
    else
      mkdir -p "$(dirname "$adapter")"
      ln -s "$adapter_target" "$adapter"
      echo "  created Claude adapter: $skill"
    fi
  done < "$manifest"
}

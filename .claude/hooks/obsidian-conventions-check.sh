#!/usr/bin/env bash
# obsidian-conventions-check.sh
# PreToolUse hook for Write and Edit tools. Validates files written to the
# Obsidian vault against the vault conventions. Blocks writes that violate.
#
# Checks:
# 1. File is inside the vault root (any directory, any depth)
# 2. Frontmatter exists with date_created and tags
# 3. Frontmatter exists with date_created and tags
# 4. Wikilinks in frontmatter are quoted YAML list items, not unquoted or comma-joined
#
# Hook protocol: reads JSON on stdin, writes JSON decision on stdout.
# Input: {"tool": "Write"|"Edit", "input": {"path": "...", "content": "..."}}
# Output: {"decision": "approve"|"block", "message": "..."}

set -euo pipefail

# Resolve vault root from the Obsidian CLI, with a fallback
VAULT_ROOT="$(obsidian vault info=path </dev/null 2>/dev/null || echo "")"
if [[ -z "$VAULT_ROOT" ]]; then
  VAULT_ROOT="$HOME/Documents/Datadog"
fi
# Read the hook input
input=$(cat)
tool=$(echo "$input" | python3 -c "import sys,json; print(json.load(sys.stdin).get('tool',''))" 2>/dev/null || echo "")
file_path=$(echo "$input" | python3 -c "import sys,json; print(json.load(sys.stdin).get('input',{}).get('path',''))" 2>/dev/null || echo "")
content=$(echo "$input" | python3 -c "import sys,json; print(json.load(sys.stdin).get('input',{}).get('content',''))" 2>/dev/null || echo "")

# Only check Write and Edit tools
if [[ "$tool" != "Write" && "$tool" != "Edit" ]]; then
  echo '{"decision":"approve"}'
  exit 0
fi

# Only check files inside the vault
if [[ "$file_path" != "$VAULT_ROOT"/* ]]; then
  echo '{"decision":"approve"}'
  exit 0
fi

# Resolve the path relative to vault root
rel_path="${file_path#$VAULT_ROOT/}"

# For Edit tool, we may not have full content — skip content checks
if [[ "$tool" == "Edit" ]]; then
  echo '{"decision":"approve"}'
  exit 0
fi

# Check 2: Must have frontmatter with date_created and tags
if [[ "$content" != ---* ]]; then
  echo '{"decision":"block","message":"obsidian-conventions: vault notes must have frontmatter starting with ---. Add date_created and tags fields."}'
  exit 0
fi

# Extract frontmatter
fm_end=$(echo "$content" | awk 'NR==1{next} /^---$/{print NR; exit}' 2>/dev/null || echo "0")
if [[ "$fm_end" == "0" || -z "$fm_end" ]]; then
  echo '{"decision":"block","message":"obsidian-conventions: frontmatter is not closed with a second ---. Add closing --- after frontmatter fields."}'
  exit 0
fi

fm_content=$(echo "$content" | sed -n "2,$((fm_end-1))p")

if ! echo "$fm_content" | grep -q "date_created:"; then
  echo '{"decision":"block","message":"obsidian-conventions: frontmatter must include date_created field."}'
  exit 0
fi

if ! echo "$fm_content" | grep -q "tags:"; then
  echo '{"decision":"block","message":"obsidian-conventions: frontmatter must include tags field (YAML list)."}'
  exit 0
fi

# Check 3: No unquoted wikilinks in frontmatter
# Unquoted [[ in YAML is a flow sequence start — will break parsing
if echo "$fm_content" | grep -qE '^\s*[A-Za-z_]+:\s*\[\[' ; then
  echo '{"decision":"block","message":"obsidian-conventions: unquoted [[wikilinks]] in frontmatter break YAML parsing. Quote each link and use YAML list format: relates_to:\n  - \"[[Note Name]]\"."}'
  exit 0
fi

# Check 4: No comma-joined wikilinks in a single frontmatter string
if echo "$fm_content" | grep -qE '\[\[.*\]\].*\[\[.*\]\]' | grep -v '^\s*-' ; then
  echo '{"decision":"block","message":"obsidian-conventions: multiple wikilinks in a single frontmatter string are not parsed correctly. Use YAML list format with one quoted link per line."}'
  exit 0
fi

echo '{"decision":"approve"}'

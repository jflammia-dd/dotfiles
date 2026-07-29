#!/usr/bin/env bash
# em-dash-check: scans Write, Edit, and MultiEdit tool output for em dashes (U+2014)
# and double-hyphen (--) used as dash substitutes.
# Fires PostToolUse. Injects a warning into context if a violation is found
# so Claude can correct the output before the user sees it.

if ! command -v jq &>/dev/null; then
  exit 0
fi

INPUT=$(cat)
TOOL=$(echo "$INPUT" | jq -r '.tool_name // ""')

# Only check Write, Edit, and MultiEdit calls
case "$TOOL" in
  Write|Edit|MultiEdit) ;;
  *) exit 0 ;;
esac

# Extract file path and skip code files — only scan prose files (.md, .txt, etc.)
if [ "$TOOL" = "Write" ] || [ "$TOOL" = "Edit" ]; then
  FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // ""')
  EXT="${FILE_PATH##*.}"
  case "$EXT" in
    sh|bash|py|go|js|ts|jsx|tsx|java|rb|rs|c|cpp|h|hpp|json|yaml|yml|toml|xml|html|htm|css|scss|sql|swift|kt|scala|r|m|pl|php)
      exit 0 ;;
  esac
elif [ "$TOOL" = "MultiEdit" ]; then
  FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // ""')
  EXT="${FILE_PATH##*.}"
  case "$EXT" in
    sh|bash|py|go|js|ts|jsx|tsx|java|rb|rs|c|cpp|h|hpp|json|yaml|yml|toml|xml|html|htm|css|scss|sql|swift|kt|scala|r|m|pl|php)
      exit 0 ;;
  esac
fi

# Extract the written/changed content
if [ "$TOOL" = "Write" ]; then
  CONTENT=$(echo "$INPUT" | jq -r '.tool_input.content // ""')
elif [ "$TOOL" = "Edit" ]; then
  CONTENT=$(echo "$INPUT" | jq -r '.tool_input.new_string // ""')
else
  # MultiEdit: collect all new_string values from the edits array
  CONTENT=$(echo "$INPUT" | jq -r '[.tool_input.edits[]?.new_string // ""] | join("\n")')
fi

VIOLATIONS=""

# Check for em dash (—, U+2014)
if echo "$CONTENT" | grep -q '—'; then
  LINES=$(echo "$CONTENT" | grep -n '—' | head -5 | sed 's/^/  /')
  VIOLATIONS="${VIOLATIONS}Em dash (—) detected. Restructure the sentence to remove it. Do not simply swap the em dash for another punctuation mark.\n${LINES}\n"
fi

# Check for double-hyphen (--) used as dash substitute in prose.
# Exclude code blocks and YAML/config lines (lines starting with optional spaces then #, //, or word: --).
PROSE=$(echo "$CONTENT" | grep -v '^\s*[#/]' | grep -v '^\s*\w\+:' | grep -v '```')
if echo "$PROSE" | grep -q ' -- '; then
  LINES=$(echo "$PROSE" | grep -n ' -- ' | head -5 | sed 's/^/  /')
  VIOLATIONS="${VIOLATIONS}Double-hyphen ( -- ) used as dash substitute in prose. Restructure the sentence to remove it. Do not simply swap the dashes for another punctuation mark.\n${LINES}\n"
fi

if [ -n "$VIOLATIONS" ]; then
  MSG="Writing style violation in output:\n${VIOLATIONS}"
  jq -n --arg msg "$MSG" \
    '{"hookSpecificOutput":{"hookEventName":"PostToolUse","additionalContext":$msg}}'
fi

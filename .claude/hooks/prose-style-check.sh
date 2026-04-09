#!/usr/bin/env bash
# prose-style-check: scans Write, Edit, and MultiEdit tool output for common
# punctuation violations in prose files:
#   1. Comma before coordinating conjunction (and/or/but) joining independent clauses
#      or as an Oxford comma — both are banned in Justin's voice.
# Fires PostToolUse. Injects a warning into context if violations are found.

if ! command -v jq &>/dev/null; then
  exit 0
fi

INPUT=$(cat)
TOOL=$(echo "$INPUT" | jq -r '.tool_name // ""')

case "$TOOL" in
  Write|Edit|MultiEdit) ;;
  *) exit 0 ;;
esac

# Extract file path and skip code files — only scan prose files
if [ "$TOOL" = "Write" ] || [ "$TOOL" = "Edit" ]; then
  FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // ""')
elif [ "$TOOL" = "MultiEdit" ]; then
  FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // ""')
fi
EXT="${FILE_PATH##*.}"
case "$EXT" in
  sh|bash|py|go|js|ts|jsx|tsx|java|rb|rs|c|cpp|h|hpp|json|yaml|yml|toml|xml|html|htm|css|scss|sql|swift|kt|scala|r|m|pl|php)
    exit 0 ;;
esac

# Extract the written/changed content
if [ "$TOOL" = "Write" ]; then
  CONTENT=$(echo "$INPUT" | jq -r '.tool_input.content // ""')
elif [ "$TOOL" = "Edit" ]; then
  CONTENT=$(echo "$INPUT" | jq -r '.tool_input.new_string // ""')
else
  CONTENT=$(echo "$INPUT" | jq -r '[.tool_input.edits[]?.new_string // ""] | join("\n")')
fi

VIOLATIONS=""

# Check for comma before coordinating conjunction (covers Oxford comma and
# comma-before-and/or/but-joining-clauses — both banned).
# Pattern: ", and " or ", or " or ", but " in prose lines.
# Exclude lines that look like code, YAML, or markdown list items.
PROSE_LINES=$(echo "$CONTENT" | grep -v '^\s*[-*#>]' | grep -v '^\s*//' | grep -v '^\s*\w\+:')
if echo "$PROSE_LINES" | grep -qiE ',\s+(and|or|but)\s'; then
  LINES=$(echo "$PROSE_LINES" | grep -inE ',\s+(and|or|but)\s' | head -5 | sed 's/^/  /')
  VIOLATIONS="${VIOLATIONS}Comma before coordinating conjunction (and/or/but) detected. This violates both the Oxford comma rule and the no-comma-before-conjunction rule. Remove the comma.\n${LINES}\n"
fi

if [ -n "$VIOLATIONS" ]; then
  MSG="Writing style violation in output:\n${VIOLATIONS}"
  jq -n --arg msg "$MSG" \
    '{"hookSpecificOutput":{"hookEventName":"PostToolUse","additionalContext":$msg}}'
fi

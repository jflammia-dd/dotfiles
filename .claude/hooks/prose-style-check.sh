#!/usr/bin/env bash
# prose-style-check: scans Write, Edit, and MultiEdit tool output for prose style
# violations in Justin's voice. Checks performed in a single pass:
#   1. Em dash (U+2014) — banned; restructure the sentence
#   2. Double-hyphen ( -- ) as dash substitute in prose — banned
#   3. Oxford comma / comma before coordinating conjunction — banned
# Fires PostToolUse. Skips code file extensions. Injects a warning into context
# when violations are found so Claude can correct before the user sees the output.

if ! command -v jq &>/dev/null; then
  exit 0
fi

INPUT=$(cat)
TOOL=$(echo "$INPUT" | jq -r '.tool_name // ""')

case "$TOOL" in
  Write|Edit|MultiEdit) ;;
  *) exit 0 ;;
esac

# Extract file path and skip code files — only scan prose files (.md, .txt, etc.)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // ""')
EXT="${FILE_PATH##*.}"
case "$EXT" in
  sh|bash|py|go|js|ts|jsx|tsx|java|rb|rs|c|cpp|h|hpp|json|yaml|yml|toml|xml|html|htm|css|scss|sql|swift|kt|scala|r|m|pl|php)
    exit 0 ;;
esac

# Extract the written/changed content — one pass covers all three tool types
if [ "$TOOL" = "Write" ]; then
  CONTENT=$(echo "$INPUT" | jq -r '.tool_input.content // ""')
elif [ "$TOOL" = "Edit" ]; then
  CONTENT=$(echo "$INPUT" | jq -r '.tool_input.new_string // ""')
else
  CONTENT=$(echo "$INPUT" | jq -r '[.tool_input.edits[]?.new_string // ""] | join("\n")')
fi

VIOLATIONS=""

# 1. Em dash (—, U+2014)
if echo "$CONTENT" | grep -q '—'; then
  LINES=$(echo "$CONTENT" | grep -n '—' | head -5 | sed 's/^/  /')
  VIOLATIONS="${VIOLATIONS}Em dash (—) detected. Restructure the sentence to remove it. Do not simply swap the em dash for another punctuation mark.\n${LINES}\n"
fi

# 2. Double-hyphen ( -- ) as dash substitute in prose.
# Skip lines that look like code comments, YAML keys, or fenced code blocks.
PROSE=$(echo "$CONTENT" | grep -v '^\s*[#/]' | grep -v '^\s*\w\+:' | grep -v '```')
if echo "$PROSE" | grep -q ' -- '; then
  LINES=$(echo "$PROSE" | grep -n ' -- ' | head -5 | sed 's/^/  /')
  VIOLATIONS="${VIOLATIONS}Double-hyphen ( -- ) used as dash substitute in prose. Restructure the sentence to remove it.\n${LINES}\n"
fi

# 3. Oxford comma / comma before coordinating conjunction (and/or/but).
# Skip code comments, YAML keys, fenced code and blockquotes. Markdown list items are
# deliberately NOT skipped: bullets are where most prose actually lives, and excluding
# them let nine violations sit in CLAUDE.md unnoticed for months.
PROSE_LINES=$(echo "$CONTENT" | grep -v '^\s*>' | grep -v '^\s*//' | grep -v '^\s*\w\+:' | grep -v '```')
if echo "$PROSE_LINES" | grep -qiE ',\s+(and|or|but)\s'; then
  LINES=$(echo "$PROSE_LINES" | grep -inE ',\s+(and|or|but)\s' | head -5 | sed 's/^/  /')
  VIOLATIONS="${VIOLATIONS}Comma before coordinating conjunction (and/or/but) detected. This violates both the Oxford comma rule and the no-comma-before-conjunction rule. Remove the comma.\n${LINES}\n"
fi

if [ -n "$VIOLATIONS" ]; then
  MSG="Writing style violation in output:\n${VIOLATIONS}"
  jq -n --arg msg "$MSG" \
    '{"hookSpecificOutput":{"hookEventName":"PostToolUse","additionalContext":$msg}}'
fi

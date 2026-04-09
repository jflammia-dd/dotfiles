#!/usr/bin/env bash
# session-start-check: fires at session start (SessionStart).
# Checks for a pending-remember marker left by the previous session's
# SessionEnd hook and surfaces it as additionalContext if present.

if ! command -v jq &>/dev/null; then exit 0; fi

MARKER="$HOME/.claude/.pending-remember"
[ -f "$MARKER" ] || exit 0

MSG=$(cat "$MARKER")
rm -f "$MARKER"

jq -n --arg msg "$MSG" \
  '{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":$msg}}'

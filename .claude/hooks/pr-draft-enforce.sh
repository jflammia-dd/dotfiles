#!/usr/bin/env bash
# pr-draft-enforce: auto-injects --draft into gh pr create commands that omit it.
# Enforces the global rule that all PRs must start as drafts.
# This hook only normalizes. It does NOT auto-allow.
# The permission system and downstream hooks decide approval.

if ! command -v jq &>/dev/null; then exit 0; fi

INPUT=$(cat)
CMD=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

if [ -z "$CMD" ]; then exit 0; fi

# Only act on gh pr create commands
if ! echo "$CMD" | grep -qE '(^|; *|&& *|\|\| *)gh pr create( |$)'; then exit 0; fi

# Already has --draft, nothing to do
if echo "$CMD" | grep -q -- '--draft'; then exit 0; fi

# Inject --draft after every occurrence of "gh pr create"
UPDATED=$(echo "$CMD" | sed -E 's/(gh pr create)/\1 --draft/g')

ORIGINAL_INPUT=$(echo "$INPUT" | jq -c '.tool_input')
UPDATED_INPUT=$(echo "$ORIGINAL_INPUT" | jq --arg cmd "$UPDATED" '.command = $cmd')

# No permissionDecision. Normalization only; let downstream decide approval.
jq -n \
  --argjson updated "$UPDATED_INPUT" \
  '{
    "hookSpecificOutput": {
      "hookEventName": "PreToolUse",
      "updatedInput": $updated
    }
  }'

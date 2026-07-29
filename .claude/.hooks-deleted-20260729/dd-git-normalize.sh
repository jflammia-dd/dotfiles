#!/usr/bin/env bash
# dd-git-normalize: rewrites dd-git → git before RTK's hook runs.
# dd-git is a Datadog git wrapper with an identical subcommand interface.
# Normalizing here lets RTK's rewrite registry handle token optimization
# without needing to know about dd-git.
#
# This hook only rewrites the command name — it does NOT auto-allow.
# The permission system and downstream hooks (rtk-rewrite.sh) decide approval.
#
# This hook must run BEFORE rtk-rewrite.sh in settings.json.

if ! command -v jq &>/dev/null; then
  exit 0
fi

INPUT=$(cat)
CMD=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

if [ -z "$CMD" ]; then
  exit 0
fi

# Check if dd-git appears anywhere in the command before doing work.
if ! echo "$CMD" | grep -qE '(^|; *|&& *|\|\| *)dd-git '; then
  exit 0
fi

NORMALIZED=$(echo "$CMD" | sed -E 's/(^|; *|&& *|\|\| *)dd-git /\1git /g')

ORIGINAL_INPUT=$(echo "$INPUT" | jq -c '.tool_input')
UPDATED_INPUT=$(echo "$ORIGINAL_INPUT" | jq --arg cmd "$NORMALIZED" '.command = $cmd')

# No permissionDecision — let the permission system and downstream hooks decide.
jq -n \
  --argjson updated "$UPDATED_INPUT" \
  '{
    "hookSpecificOutput": {
      "hookEventName": "PreToolUse",
      "updatedInput": $updated
    }
  }'

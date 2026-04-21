#!/usr/bin/env bash
set -euo pipefail

# Rewrites bzl commands to prepend /opt/homebrew/bin to PATH.
#
# The modern-python plugin installs a python3 shim that blocks all bare python3
# invocations. bzl calls python3 internally to run tools/bazel. The shim exits 1,
# breaking bzl. Prepending /opt/homebrew/bin makes the real python3 reachable
# before the shim.

input=$(cat)
cmd=$(echo "$input" | jq -r '.tool_input.command // empty')

[[ -z "$cmd" ]] && exit 0

# Match if 'bzl' appears as a word (preceded by start, space, semicolon, or &&)
if printf '%s' "$cmd" | grep -qE '(^|[[:space:];]|&&[[:space:]]*)bzl[[:space:]]'; then
    # Wrap in subshell so the PATH export applies to the full command including cd
    new_cmd="( export PATH=\"/opt/homebrew/bin:/opt/homebrew/sbin:\${PATH}\"; $cmd )"
    jq -n --arg cmd "$new_cmd" \
        '{"hookSpecificOutput": {"hookEventName": "PreToolUse", "updatedInput": {"command": $cmd}}}'
fi

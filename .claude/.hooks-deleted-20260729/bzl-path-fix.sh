#!/usr/bin/env bash
set -euo pipefail

# Rewrites bzl and rapid.sh commands to prepend /opt/homebrew/bin to PATH.
#
# The modern-python plugin installs a python3 shim that blocks all bare python3
# invocations. bzl calls python3 internally to run tools/bazel. The shim exits 1,
# breaking bzl. rapid.sh (Rapid CLI wrapper) also shells out to bzl internally.
# Prepending /opt/homebrew/bin makes the real python3 reachable before the shim,
# and the export is inherited by all child processes of the rewritten command.

input=$(cat)
cmd=$(echo "$input" | jq -r '.tool_input.command // empty')

[[ -z "$cmd" ]] && exit 0

# Match bzl as a word, or rapid.sh anywhere in the command (including full paths).
if printf '%s' "$cmd" | grep -qE '(^|[[:space:];]|&&[[:space:]]*)bzl[[:space:]]' || \
   printf '%s' "$cmd" | grep -qF 'rapid.sh '; then
    # Wrap in subshell so the PATH export applies to the full command including cd
    new_cmd="( export PATH=\"/opt/homebrew/bin:/opt/homebrew/sbin:\${PATH}\"; $cmd )"
    jq -n --arg cmd "$new_cmd" \
        '{"hookSpecificOutput": {"hookEventName": "PreToolUse", "updatedInput": {"command": $cmd}}}'
fi

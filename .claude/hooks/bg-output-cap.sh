#!/bin/bash
# ponytail: caps background Bash task output at 2GiB via ulimit -f so a runaway/interactive
# process (e.g. a CLI stuck prompting on empty stdin) hits SIGXFSZ instead of filling the disk.
input=$(cat)
bg=$(echo "$input" | jq -r '.tool_input.run_in_background // false')
if [ "$bg" != "true" ]; then
  echo '{}'
  exit 0
fi
cmd=$(echo "$input" | jq -r '.tool_input.command')
echo "$input" | jq -c --arg cmd "ulimit -f 4194304; $cmd" \
  '{hookSpecificOutput: {hookEventName: "PreToolUse", updatedInput: (.tool_input + {command: $cmd})}}'

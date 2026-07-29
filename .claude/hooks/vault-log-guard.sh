#!/usr/bin/env bash
# vault-log-guard: protects the Obsidian vault's append-only operational ledger
# at Documents/Datadog/docs/log.md from shell commands that would overwrite,
# truncate, reorder or relocate it.
#
# Why this exists as a global hook rather than a hookify rule: hookify globs
# `.claude/hookify.*.local.md` relative to the working directory, so the vault's
# `protect-vault-log` rule only fires when cwd is the vault. A shell command run
# from any other directory could still target the file by absolute path.
#
# Division of labour with the permission layer. The deny rule
# `Edit(//Users/justin.flammia/Documents/Datadog/docs/log.md)` covers Claude's
# file tools plus the Bash file commands Claude Code recognizes. It does not
# cover shell redirection, which the docs describe as an arbitrary subprocess.
# That gap is what this script closes.
#
# Reads are deliberately untouched: the sanctioned append path is to read the
# tail, append with an append-only tool, then read the tail again to verify.

if ! command -v jq &>/dev/null; then exit 0; fi

INPUT=$(cat)
CMD=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

if [ -z "$CMD" ]; then exit 0; fi

block() {
  jq -n --arg r "$1" '{continue: false, stopReason: $r}'
  exit 0
}

# Matches the ledger by relative or absolute path. Anchored on the trailing
# path segment so either spelling is caught.
LOG='(^|[[:space:]"'"'"'/])docs/log\.md'

# Destructive shapes: output redirection, tee, in-place editors, copy/move onto
# the file, and truncation.
if echo "$CMD" | grep -qE ">[[:space:]]*[^|;&]*${LOG}"; then
  block "Writing to docs/log.md via shell redirection is blocked. It is an append-only operational ledger. Read the current tail, append with an append-only tool (obsidian append preferred) or the /log workflow, then read the tail again to verify."
fi

if echo "$CMD" | grep -qE '(^|[;&|]|[[:space:]])(tee|truncate)[[:space:]]' && echo "$CMD" | grep -qE "$LOG"; then
  block "This command would overwrite or truncate docs/log.md, an append-only operational ledger. Use an append-only tool (obsidian append preferred) or the /log workflow instead."
fi

if echo "$CMD" | grep -qE '(sed|perl)[[:space:]]+(-[a-zA-Z]*i|-i)' && echo "$CMD" | grep -qE "$LOG"; then
  block "In-place editing of docs/log.md is blocked. It is an append-only operational ledger, so rewriting history in it requires an explicit request from Justin."
fi

if echo "$CMD" | grep -qE '(^|[;&|]|[[:space:]])(cp|mv|rm)[[:space:]]' && echo "$CMD" | grep -qE "$LOG"; then
  block "Copying over, moving or removing docs/log.md is blocked. It is an append-only operational ledger. If it looks missing or damaged, stop and tell Justin before any reconstruction."
fi

exit 0

#!/usr/bin/env bash
# git-commit-message-guard: blocks a `git commit` that carries no message on the
# command line, so the exact literal message is always visible in the transcript
# before the commit runs.
#
# Promoted from the vault's hookify rule `git-commit-requires-message`, which
# only loaded when the working directory was the vault: hookify globs
# `.claude/hookify.*.local.md` relative to cwd with no parent or home fallback,
# so it never fired in dd-source where the commits actually happen.
#
# Deliberately global rather than Datadog-scoped, for two reasons. The CLAUDE.md
# Git Rule requiring the message text up front is unconditional, and a commit
# with no -m opens $EDITOR, which hangs a non-interactive shell regardless of
# which repo it runs in.

if ! command -v jq &>/dev/null; then exit 0; fi

INPUT=$(cat)
CMD=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

if [ -z "$CMD" ]; then exit 0; fi

block() {
  jq -n --arg r "$1" '{continue: false, stopReason: $r}'
  exit 0
}

# Matches `git commit` / `dd-git commit` at the start of a command or after a
# shell separator, when no message-bearing flag appears anywhere in the command.
if echo "$CMD" | grep -qE '(^|[;&|]\s*)(git|dd-git)\s+commit\b' \
   && ! echo "$CMD" | grep -qE '(-m\b|-F\b|--message\b|--file\b)'; then
  block "This 'git commit' passes no message, so it would open an editor or silently reuse a prior message via --amend/-C. Show the exact, literal commit message text in the conversation first, then re-run with that text via -m (or a heredoc with -F - for multi-line messages). Do not amend or reuse a previous message without writing and showing a new one."
fi

exit 0

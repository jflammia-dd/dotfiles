#!/usr/bin/env bash
# run-codex-subtask.sh — safe delegation bridge from Claude Code to Codex
#
# Usage:
#   run-codex-subtask.sh read-only    <prompt-file>
#   run-codex-subtask.sh write        <prompt-file>
#
# The prompt is read from a file (not a shell argument) to avoid quoting fragility.

set -euo pipefail

MODE="${1:-}"
PROMPT_FILE="${2:-}"

if [[ -z "$MODE" || -z "$PROMPT_FILE" ]]; then
    echo "Usage: run-codex-subtask.sh <read-only|write> <prompt-file>" >&2
    exit 1
fi

if [[ ! -f "$PROMPT_FILE" ]]; then
    echo "Prompt file not found: $PROMPT_FILE" >&2
    exit 1
fi

case "$MODE" in
    read-only)
        codex exec \
            --cd "$PWD" \
            --skip-git-repo-check \
            --sandbox read-only \
            --color never \
            --ephemeral \
            - < "$PROMPT_FILE"
        ;;
    write)
        # --full-auto sets sandbox=workspace-write and approval=on-request
        codex exec \
            --cd "$PWD" \
            --skip-git-repo-check \
            --full-auto \
            --color never \
            --ephemeral \
            - < "$PROMPT_FILE"
        ;;
    *)
        echo "Unknown mode '$MODE'. Use 'read-only' or 'write'." >&2
        exit 1
        ;;
esac

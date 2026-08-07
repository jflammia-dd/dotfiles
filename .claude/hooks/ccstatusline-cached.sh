#!/usr/bin/env bash
# ccstatusline: renders the Claude Code status line via the globally installed binary.
# ponytail: dropped the npx-based auto-update check (npm view + npx both hit the network
# on every prompt), which caused UserPromptSubmit hook timeouts whenever the VPN was flaky.
# Update manually with `npm update -g ccstatusline` when needed.
command -v ccstatusline >/dev/null 2>&1 && exec ccstatusline "$@"

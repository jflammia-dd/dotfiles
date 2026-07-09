#!/usr/bin/env bash
# Codex CLI runs this via its `notify` setting, passing a JSON event as $1.
# We bark when a turn completes (Codex finished / needs you).
# Fails silently if the pet isn't running, so it never blocks Codex.
EVENT="${1:-}"
case "$EVENT" in
  *agent-turn-complete*)
    curl --silent --max-time 1 http://127.0.0.1:4242/bark >/dev/null 2>&1 || true
    ;;
  *)
    : # other event types — ignore
    ;;
esac
exit 0

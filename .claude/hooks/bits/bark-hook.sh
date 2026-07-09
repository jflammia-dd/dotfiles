#!/usr/bin/env bash
# Makes Bits bark (loud) when Claude finishes a task or needs your attention.
# Fails silently if the pet isn't running, so it never blocks your agent.
curl --silent --max-time 1 http://127.0.0.1:4242/bark >/dev/null 2>&1 || true

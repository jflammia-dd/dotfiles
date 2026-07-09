#!/usr/bin/env bash
# Gently wakes Bits (perk up + wiggle) when you submit a message.
# Fails silently if the pet isn't running, so it never blocks your message.
curl --silent --max-time 1 http://127.0.0.1:4242/wake >/dev/null 2>&1 || true

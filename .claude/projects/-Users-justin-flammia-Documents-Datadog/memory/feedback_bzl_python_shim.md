---
name: bzl python3 shim issue in Claude Code sessions
description: bzl run works in Claude Code sessions; bzl build and rapid run may still fail due to the modern-python shim
type: feedback
originSessionId: 7da81963-1801-4858-a15d-eb928abdeb37
---
`bzl run` (e.g. `bzl run //domains/language_tools/apps/whoisthis:whoisthis`) works fine in Claude Code sessions. The user confirmed this directly on 2026-05-18.

`bzl build` and `rapid run` (full Bazel builds) may still fail due to the `trailofbits/modern-python` shim intercepting `python3`. For those, stripping the shim from PATH first may help:
```bash
CLEAN_PATH=$(echo $PATH | tr ':' '\n' | grep -v "modern-python\|\.claude/plugins" | tr '\n' ':' | sed 's/:$//') && PATH="/opt/homebrew/bin:$CLEAN_PATH" bzl run //:gazelle
```

**How to apply:** Always attempt `bzl run` directly first. Only fall back to the PATH-stripping workaround or asking the user to run it manually if the command actually fails.

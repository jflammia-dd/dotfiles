---
name: bzl-works-in-claude-code-sessions
description: "bzl build, bzl run and bzl test all work normally in Claude Code sessions; the python shim assumption was incorrect"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 97902f2c-fd3f-411c-91ce-4b32851f6f82
---

`bzl build`, `bzl run` and `bzl test` all work normally inside Claude Code sessions. The assumption that `bzl build`/`rapid run` fail due to the `trailofbits/modern-python` shim intercepting `python3` was incorrect and has been disproved.

**How to apply:** Run `bzl` commands directly without any PATH workarounds. Do not fall back to asking the user to run commands in their own terminal.

**Why:** The user explicitly corrected this on 2026-05-20 and confirmed bzl works as expected.

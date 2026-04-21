---
name: bzl python3 shim issue in Claude Code sessions
description: bzl and rapid run fail inside Claude Code sessions due to modern-python plugin shim intercepting python3
type: feedback
originSessionId: 7da81963-1801-4858-a15d-eb928abdeb37
---
`bzl build`, `rapid run` and any Bazel command fails inside Claude Code sessions with "ERROR: Use `uv run python3 tools/bazel` instead of `python3 tools/bazel`".

**Why:** The `trailofbits/modern-python` Claude plugin installs a `python3` shim at the front of PATH. The shim intercepts every direct `python3` call and redirects it to `uv run`. `bzl` calls `python3 tools/bazel` internally and hits the shim instead of real Python.

**How to apply:** Never chase this error inside a Claude Code session. It is not a code problem. All Bazel builds (`bzl build`, `bzl test`) and `rapid run` must be executed in the user's own terminal (Ghostty), not through Claude Code. The build succeeds correctly there. CI also validates the build independently.

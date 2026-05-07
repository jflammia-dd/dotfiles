---
name: bzl python3 shim issue in Claude Code sessions
description: bzl and rapid run fail inside Claude Code sessions due to modern-python plugin shim intercepting python3
type: feedback
originSessionId: 7da81963-1801-4858-a15d-eb928abdeb37
---
`bzl build`, `rapid run` and any Bazel command fails inside Claude Code sessions with "ERROR: Use `uv run python3 tools/bazel` instead of `python3 tools/bazel`".

**Why:** The `trailofbits/modern-python` Claude plugin installs a `python3` shim at the front of PATH. The shim intercepts every direct `python3` call and redirects it to `uv run`. `bzl` calls `python3 tools/bazel` internally and hits the shim instead of real Python.

**How to apply:** For Gazelle (`bzl run //:gazelle`), strip the shim from PATH first and it works inside Claude Code:
```bash
CLEAN_PATH=$(echo $PATH | tr ':' '\n' | grep -v "modern-python\|\.claude/plugins" | tr '\n' ':' | sed 's/:$//') && PATH="/opt/homebrew/bin:$CLEAN_PATH" bzl run //:gazelle
```
For full Bazel builds (`bzl build`, `rapid td update -t`), this workaround is insufficient and the build still fails. Those must be run in the user's own terminal. Use the clean-PATH trick for Gazelle-only operations.

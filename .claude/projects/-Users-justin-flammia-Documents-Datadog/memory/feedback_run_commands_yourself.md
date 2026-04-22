---
name: Run commands yourself, don't delegate to the user
description: When the user asks Claude to run a command or check something, do it directly. Never tell the user to run it themselves.
type: feedback
originSessionId: 7da81963-1801-4858-a15d-eb928abdeb37
---
When asked to run a command or check a result, do it directly using available tools. Never respond by telling the user to run it themselves.

**Why:** It creates unnecessary friction and defeats the purpose of an agentic session.

**How to apply:** If a tool limitation prevents running a command (e.g. bzl in Claude Code sessions due to the python3 shim), try an alternative approach (e.g. plain `go test` instead of `bzl test`) before giving up. Only surface the limitation if truly no workaround exists.

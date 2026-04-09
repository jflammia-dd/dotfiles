---
name: 1Password shell secrets removed
description: Neither gh nor Figma MCP need tokens injected from the shell; both handle auth independently
type: feedback
originSessionId: 42e75a7a-f348-41a5-b64b-9159e8aa2f8d
---
The `op read` calls for `GITHUB_PERSONAL_ACCESS_TOKEN`, `GH_TOKEN` and `FIGMA_TOKEN` were removed from `.zshrc` entirely.

**Why:** Neither tool actually needed them. `gh` authenticates via its own keyring (OAuth token managed by `gh auth login`). The Figma MCP is a remote HTTP server at `https://mcp.figma.com/mcp` that uses OAuth, not a local process reading `FIGMA_TOKEN`. The 1Password shell plugin (`plugins.sh`) was also removed since it was injecting `GH_TOKEN` on every `gh` call, causing a biometric prompt per invocation.

**How to apply:** Do not re-add `op read` calls to shell startup files for these tools. If `gh` auth breaks, run `gh auth login`. If Figma MCP auth breaks, Claude Code will prompt for re-auth via the MCP OAuth flow.

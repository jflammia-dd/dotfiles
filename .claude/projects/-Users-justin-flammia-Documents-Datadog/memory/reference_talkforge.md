---
name: reference-talkforge
description: "Internal Datadog tool for planning conference talks and other content, built by the advocacy team"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 4b0950bd-b2a0-477c-ba8d-404328729f21
  modified: 2026-08-07T19:20:37.090Z
---

`https://datadog.talkforge.app/` is an internal Datadog tool (Google Workspace SSO sign-in required, VPN not confirmed necessary) built by James Eastham (advocacy team, `james.eastham@datadoghq.com`), announced 2026-08-07 in Slack channel C08V7DFTUMS. Despite the name it plans any content, not just conference talks: YouTube videos, product demo outlines, internal eng demos or brown bags. Codified from practices of about 20 Datadog developer advocates with hundreds of talks between them.

The `/talks` dashboard offers three entry points, each feeding a chat-based Talk Assistant that ends in a structured outline: start from scratch, import a transcript or record your voice. It can also generate title/abstract suggestions and a Datadog-branded slide deck. Full MCP support is available for terminal-based planning: `claude mcp add --transport http talkforge https://datadog.talkforge.app/mcp --scope user`. It is also available through the company ChatGPT subscription (sign in there). Support runs through the `#talkforge-support` Slack channel, plus a feedback form linked in the app sidebar. James is actively soliciting feedback, ping him directly after trying it.

MCP is set up 2026-08-07 for both harnesses using native HTTP, no `npx mcp-remote` wrapper: Claude Code via `claude mcp add --transport http talkforge https://datadog.talkforge.app/mcp --scope user` (in `~/.claude.json`), Codex via `[mcp_servers.talkforge]` / `url = "https://datadog.talkforge.app/mcp"` in `~/.codex/config.toml`, matching how `datadog-mcp`/`ddci-mcp-prod`/`odp` are already configured there. OAuth-gated, first tool call in a session pops browser consent.

Why: Justin flagged it 2026-08-07 as worth remembering for future conference talk prep.

How to apply: surface this tool when Justin is prepping a conference talk, planning any content (talk, demo, video), looking for a talk idea or asking about talk structure/best practices. It's already wired into both Claude Code and Codex as an MCP server, so just use its tools directly rather than the browser.

---
name: reference_datadog_saas_mcp_config
description: "Datadog SaaS MCP servers (Jira/Confluence, Gmail, Calendar, Workspace) must be configured as native HTTP, not npx mcp-remote"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 1590f239-016c-465a-82dc-2244d54e4f8a
  modified: 2026-07-23T16:22:11.432Z
---

The Datadog-hosted SaaS MCP servers (repo `DataDog/itops-saas-ai-mcp`, owned by the SaaS AI / EITAI team) are `datadog-atlassian`, `datadog-gmail`, `datadog-google-calendar`, `datadog-google-workspace` on `*-834963730936.us-central1.run.app/mcp`.

Canonical config page (updated May 2026): [Saas AI Remote MCP Servers](https://datadoghq.atlassian.net/wiki/spaces/EITAI/pages/6298928130/Saas+AI+Remote+MCP+Servers). The recommended Claude Code config is native HTTP:

```json
{ "type": "http", "url": "https://<server>-834963730936.us-central1.run.app/mcp" }
```

Or `claude mcp add --transport http --scope user <name> <url>`. Auth is Google/Atlassian OAuth via a FastMCP OAuthProxy over Streamable HTTP; first use opens a browser consent. Cloud-ID/domain-locked to datadoghq.

Do NOT configure these as `npx mcp-remote <url>` (stdio). That is the outdated transport: it spawns npx (node cold-start + npm resolution) plus an mcp-remote proxy process on every session start, adding real startup latency. Native HTTP connects directly and in parallel.

For Jira/Confluence specifically, prefer the official `atlassian@claude-plugins-official` plugin over `datadog-atlassian`: it reaches the same `datadoghq` site with a broader toolset and is what CLAUDE.md already mandates (`mcp__plugin_atlassian_atlassian__*`). The deprecated option ("don't do this anymore") is the older `uvx mcp-atlassian` community server with a personal API token. Note: the Datadog SaaS suite was pilot-closed / pre-GA as of mid-2026.

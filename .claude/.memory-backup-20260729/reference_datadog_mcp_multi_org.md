---
name: reference_datadog_mcp_multi_org
description: "Datadog MCP server URLs by org: mcp.datad0g.com for staging org 2, mcp.datadoghq.com for production/dogfood"
metadata: 
  node_type: memory
  type: reference
  originSessionId: bb441f31-7fab-4b02-85ca-9a8e40b49233
---

Two separate MCP server domains for two environments:

| MCP name | Server URL | Environment |
|---|---|---|
| `datadog-mcp` | `mcp.datadoghq.com` | Production + dogfood (`ddstaging.datadoghq.com`, org 197728) |
| `datadog-staging` | `mcp.datad0g.com` | Staging org 2 (`dd.datad0g.com`) |

Both are registered in `agents/capabilities/mcp-servers.json` and `~/.claude.json`.

Key facts:
- These are separate OAuth sessions. `/mcp` must be run for each.
- The domain difference is fundamental: `mcp.datadoghq.com` OAuth opens `app.datadoghq.com` and cannot reach staging org 2. The "two entries same URL" trick only works for switching between prod and dogfood orgs.
- Use `mcp__datadog-staging__*` tools for staging org 2 queries (Vault audit logs, per-org data indexed in org 2's log store).
- `@org_id:2` filtering on `datadog-mcp` only works for logs with `org_id` as a custom attribute (e.g., ERS resolution logs). It does not reach org 2's own log indexes.
- To rebuild the staging entry: `claude mcp add datadog-staging --transport http https://mcp.datad0g.com/api/unstable/mcp-server/mcp`
- Never edit `~/.claude/plugins/marketplaces/datadog-claude-plugins/iir/.mcp.json` to add MCPs. Plugin caching silently ignores the change. Use `claude mcp add` which writes to `~/.claude.json` directly.

Doc: [[Datadog MCP - Multi-Org Setup]]

---
name: reference_atlassian_mcp_contentformat_param
description: "The official Atlassian remote MCP's format parameter is contentFormat, not bodyFormat; wrong name silently falls back to markdown instead of erroring"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 34af4833-cda8-447f-bcde-c6f82cc699fa
  modified: 2026-08-12T18:03:38.289Z
---

The official Atlassian remote MCP server (`mcp.atlassian.com/v1/mcp/authv2`, same server behind Claude Code's `atlassian@claude-plugins-official` plugin and Pi's `atlassian` MCP entry in `~/.pi/agent/mcp.json`) takes `contentFormat` on `getConfluencePage`/`updateConfluencePage`, with enum values `html`, `markdown`, `adf`. There is no `bodyFormat` parameter.

**Why:** Pi's `/ueba-sync-recap` run passed `bodyFormat: "html"` and got markdown back with no error, then concluded the tool "only supports markdown or adf" and asked whether a different, more limited Atlassian tool was in play. It wasn't a missing capability, it was an unrecognized field name silently falling back to a default format instead of failing loudly. Confirmed 2026-08-12 when correcting the param name fixed it.

**How to apply:** Any harness (Pi, Claude Code, other) hitting this same server should use `contentFormat`, not `bodyFormat`, when the task needs the HTML round-trip (e.g. [[ueba-sync-recap]]'s surgical Confluence edit, which depends on `data-local-id`/`data-annotation-id` attributes that only survive the HTML format). If a format-sensitive Confluence edit comes back in the wrong format, check the parameter name before assuming the tool lacks the format entirely.

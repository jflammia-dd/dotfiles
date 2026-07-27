---
name: atlassian-mcp-comment-timeout
description: "getJiraIssue/searchJiraIssuesUsingJql hang ~60s on media-heavy comments; known upstream bug, no fix"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 5e5cf8e9-9c9e-429c-b19d-4d5056663f94
  modified: 2026-07-27T12:15:49.019Z
---

`getJiraIssue` (and `searchJiraIssuesUsingJql`) can stall until the client's 60s timeout when the issue's `comment` field (or description) contains roughly 7+ `media`/`mediaSingle`/`mediaGroup` ADF nodes (images, attachments, previews). Reliable failure above ~10-15 media nodes.

Root cause (confirmed via upstream issue, not guessed): the server fully hydrates every media reference (Media API metadata, signed URLs, previews) server-side before responding, regardless of `responseContentFormat` (markdown or ADF) or how narrow `fields` is. Even `fields: ["comment"]` alone still triggers it. This is a known, open, unresolved bug: [atlassian/atlassian-mcp-server#145](https://github.com/atlassian/atlassian-mcp-server/issues/145). No maintainer fix or opt-out exists as of 2026-07.

No workaround eliminates it. Symptoms are inconsistent (a stalled call sometimes succeeds on plain retry) rather than a hard permanent failure per issue.

How to apply:
- If `getJiraIssue` with `fields` including `comment` times out or backgrounds, don't conclude the MCP server itself is broken. Check whether the issue's comments contain images/attachments first, then retry once or twice before escalating.
- Fetching without `comment` is unaffected and fast, so pull issue metadata (status, description, etc.) and comments as separate calls if speed matters.
- Do not try `-comment` exclusion syntax or the generic `fetch` ARI tool as workarounds; both were tested upstream and don't help (`fetch` returns empty stubs for nested comment ARIs).
- `cloudId` accepts either the site hostname (e.g. `datadoghq.atlassian.net`) or the resolved UUID from `getAccessibleAtlassianResources`. That was not the cause of the slowness in this incident, so don't misdiagnose it as a `cloudId` format issue.

---
name: Rich formatting in Jira comments
description: Which MCP tool to use when posting Jira comments that need rendered markdown (bold, code blocks, lists)
type: feedback
originSessionId: c81bf2b9-a173-4be3-a1cb-bea71ce61e1c
---
Use `mcp__plugin_atlassian_atlassian__addCommentToJiraIssue` with `contentFormat: "markdown"` for any Jira comment that needs rendered formatting. This converts markdown to ADF before posting, so bold, code blocks and bullet lists render correctly in the Jira UI.

`mcp__datadog-atlassian__add_comment` accepts plain text only. It converts text to ADF but does not process markdown, so `**bold**` and ` ```code``` ` appear as literal characters.

**Why:** Confirmed working 2026-05-05. The distinction matters any time a comment contains code snippets, terminal output or structured content.

**How to apply:** Default to `addCommentToJiraIssue` with `contentFormat: "markdown"` whenever the comment contains anything beyond plain prose.

#!/bin/bash
# Blocks the plain-text Datadog Atlassian MCP tools and redirects to the
# plugin tool that supports contentFormat: "markdown" for proper ADF rendering.
INPUT=$(cat)
TOOL=$(echo "$INPUT" | jq -r '.tool_name // empty')

if [ "$TOOL" = "mcp__datadog-atlassian__add_comment" ]; then
  echo '{"continue": false, "stopReason": "Use mcp__plugin_atlassian_atlassian__addCommentToJiraIssue with contentFormat: \"markdown\" instead. The datadog-atlassian tool posts plain text only — bold, code blocks and lists will appear as literal characters."}'
else
  echo '{"continue": false, "stopReason": "Use mcp__plugin_atlassian_atlassian__editJiraIssue with contentFormat: \"markdown\" instead. The datadog-atlassian tool posts plain text only — bold, code blocks and lists will appear as literal characters."}'
fi

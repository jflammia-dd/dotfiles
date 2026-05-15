#!/usr/bin/env bash
# jira-formatting-guard: enforces that text published to Atlassian (Jira and
# Confluence) renders as rich content rather than literal markdown.
#
# 1. Blocks the legacy mcp__datadog-atlassian__* write tools which post plain
#    text only. Redirects callers to the plugin tools.
# 2. On the plugin tools, blocks calls that omit contentFormat: "markdown" or
#    "adf". Without that field the body is sent as plain text and the bold,
#    code blocks, lists and links appear as literal characters in the UI.

if ! command -v jq &>/dev/null; then
  exit 0
fi

INPUT=$(cat)
TOOL=$(echo "$INPUT" | jq -r '.tool_name // empty')

block() {
  jq -n --arg r "$1" '{continue: false, stopReason: $r}'
  exit 0
}

case "$TOOL" in
  mcp__datadog-atlassian__add_comment)
    block "Use mcp__plugin_atlassian_atlassian__addCommentToJiraIssue with contentFormat: \"markdown\" instead. The datadog-atlassian tool posts plain text only. Bold, code blocks and lists will appear as literal characters in the Jira UI."
    ;;
  mcp__datadog-atlassian__update_issue|mcp__datadog-atlassian__update_page)
    block "Use the plugin Atlassian tool with contentFormat: \"markdown\" instead. The datadog-atlassian tools post plain text only. Bold, code blocks and lists will appear as literal characters in the UI."
    ;;
  mcp__plugin_atlassian_atlassian__addCommentToJiraIssue|\
mcp__plugin_atlassian_atlassian__editJiraIssue|\
mcp__plugin_atlassian_atlassian__createJiraIssue|\
mcp__plugin_atlassian_atlassian__createConfluencePage|\
mcp__plugin_atlassian_atlassian__updateConfluencePage|\
mcp__plugin_atlassian_atlassian__createConfluenceFooterComment|\
mcp__plugin_atlassian_atlassian__createConfluenceInlineComment)
    FORMAT=$(echo "$INPUT" | jq -r '.tool_input.contentFormat // ""')
    case "$FORMAT" in
      markdown|adf) exit 0 ;;
      *)
        block "Set contentFormat: \"markdown\" (or \"adf\") on this Atlassian publish call. Without it the body is sent as plain text. Bold, code blocks, lists and links render as literal characters in the Jira or Confluence UI."
        ;;
    esac
    ;;
  *)
    exit 0
    ;;
esac

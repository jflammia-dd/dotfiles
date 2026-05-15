#!/usr/bin/env bash
# local-process-language-check: blocks Atlassian publish operations whose body
# contains private workflow vocabulary that should never appear in shared
# artifacts. Policy: agents/policies/published-artifacts.md
#
# Fires PreToolUse. Exits cleanly to allow the call. Returns a stopReason
# response to block it.

if ! command -v jq &>/dev/null; then
  exit 0
fi

INPUT=$(cat)
TOOL=$(echo "$INPUT" | jq -r '.tool_name // ""')

# Tools that publish text to systems other people read. Extend as needed.
case "$TOOL" in
  mcp__plugin_atlassian_atlassian__addCommentToJiraIssue) FIELD="commentBody" ;;
  mcp__plugin_atlassian_atlassian__editJiraIssue) FIELD="fields" ;;
  mcp__plugin_atlassian_atlassian__createJiraIssue) FIELD="description" ;;
  mcp__plugin_atlassian_atlassian__createConfluencePage) FIELD="body" ;;
  mcp__plugin_atlassian_atlassian__updateConfluencePage) FIELD="body" ;;
  mcp__plugin_atlassian_atlassian__createConfluenceFooterComment) FIELD="body" ;;
  mcp__plugin_atlassian_atlassian__createConfluenceInlineComment) FIELD="body" ;;
  *) exit 0 ;;
esac

# Extract the body. For editJiraIssue, the description may sit inside the
# fields object as fields.description or fields.summary; jq -- handles missing
# keys without erroring.
if [ "$FIELD" = "fields" ]; then
  CONTENT=$(echo "$INPUT" | jq -r '
    (.tool_input.fields.description // "")
    + "\n"
    + (.tool_input.fields.summary // "")
  ')
else
  CONTENT=$(echo "$INPUT" | jq -r --arg f "$FIELD" '.tool_input[$f] // ""')
fi

if [ -z "$CONTENT" ]; then
  exit 0
fi

# Forbidden patterns. Case-insensitive grep. Each pattern is a literal phrase
# that is highly unlikely to appear in legitimate published copy.
PATTERNS=(
  'done.gate'
  'integration gate'
  'no per.ticket PR'
  'per the PoC'
  'per the [Jj]ira [Ll]ifecycle'
  'per the lifecycle'
  'per the workflow'
  'kickoff comment'
  'PoC branch is the integration'
  '/jira-start'
  '/jira-close'
  '/jira-block'
  '/jira-update'
  'feedback_[a-z_]+\.md'
  'MEMORY\.md'
  '/Users/justin\.flammia/'
)

HITS=""
for pat in "${PATTERNS[@]}"; do
  if echo "$CONTENT" | grep -qiE "$pat"; then
    LINE=$(echo "$CONTENT" | grep -niE "$pat" | head -1)
    HITS="${HITS}  - ${LINE}\n"
  fi
done

if [ -n "$HITS" ]; then
  REASON=$(printf 'Blocked: published artifact contains local-process language. These phrases describe a personal workflow and do not belong in Jira or Confluence text. Rewrite to describe the work, drop the workflow framing, then retry.\n\nMatches:\n%b\nPolicy: agents/policies/published-artifacts.md' "$HITS")
  # JSON-encode the reason via jq -Rs.
  jq -n --arg r "$REASON" '{continue: false, stopReason: $r}'
  exit 0
fi

exit 0

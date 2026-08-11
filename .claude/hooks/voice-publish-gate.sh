#!/usr/bin/env bash
# voice-publish-gate: runs style_check.py over the body of an Atlassian publish
# call. Closes the gap that let a Jira comment ship with two commas before
# "and": prose-style-check.sh only sees Write and Edit output, so anything
# published through the Atlassian MCP was never checked.
#
# Fires PreToolUse. Exits cleanly to allow the call. Returns a stopReason
# response to block it.
#
# Block vs warn. A create or comment payload is entirely text authored in this
# session, so violations are always newly introduced and the call is blocked.
# An update payload carries the whole existing page or description, most of
# which predates this session, so a block there would fire on years-old prose
# nobody is editing. Those calls warn instead, naming only what to look at.
#
# Escape hatch: export VOICE_GATE_OFF=1 before launching Claude. It has to come
# from the shell environment, so a tool call cannot set it to route around the
# gate.
#
# Rules and calibration: agents/skills/justins-voice/SKILL.md

if ! command -v jq &>/dev/null; then
  exit 0
fi

[ -n "${VOICE_GATE_OFF:-}" ] && exit 0

CHECKER="$HOME/.claude/skills/justins-voice/style_check.py"
# Fail open. A missing or broken linter must not block every publish.
[ -f "$CHECKER" ] || exit 0

INPUT=$(cat)
TOOL=$(echo "$INPUT" | jq -r '.tool_name // ""')

case "$TOOL" in
  mcp__plugin_atlassian_atlassian__addCommentToJiraIssue) FIELD="commentBody"; TARGET="jira"; MODE="block" ;;
  mcp__plugin_atlassian_atlassian__createJiraIssue)       FIELD="description"; TARGET="jira"; MODE="block" ;;
  mcp__plugin_atlassian_atlassian__createConfluencePage)  FIELD="body"; TARGET="confluence"; MODE="block" ;;
  mcp__plugin_atlassian_atlassian__createConfluenceFooterComment) FIELD="body"; TARGET="confluence"; MODE="block" ;;
  mcp__plugin_atlassian_atlassian__createConfluenceInlineComment) FIELD="body"; TARGET="confluence"; MODE="block" ;;
  mcp__plugin_atlassian_atlassian__updateConfluencePage)  FIELD="body"; TARGET="confluence"; MODE="warn" ;;
  mcp__plugin_atlassian_atlassian__editJiraIssue)         FIELD="fields"; TARGET="jira"; MODE="warn" ;;
  *) exit 0 ;;
esac

if [ "$FIELD" = "fields" ]; then
  CONTENT=$(echo "$INPUT" | jq -r '
    (.tool_input.fields.description // "") + "\n" + (.tool_input.fields.summary // "")')
else
  CONTENT=$(echo "$INPUT" | jq -r --arg f "$FIELD" '.tool_input[$f] // ""')
fi

[ -z "${CONTENT// /}" ] && exit 0

# markdown lints as-is. adf arrives as JSON and html as tags, so both get
# reduced to their text and checked with phrase rules only. Structural rules
# such as KEY-UNLINKED read markdown link syntax that no longer exists after
# that reduction and would fire on every correctly linked key.
FORMAT=$(echo "$INPUT" | jq -r '.tool_input.contentFormat // "markdown"')
PHRASE_ONLY=""
case "$FORMAT" in
  markdown) ;;
  adf)
    PHRASE_ONLY="--phrase-only"
    CONTENT=$(printf '%s' "$CONTENT" | jq -r 'try ([.. | objects | select(.type=="text") | .text] | join(" ")) catch .' 2>/dev/null || printf '%s' "$CONTENT")
    ;;
  *)
    PHRASE_ONLY="--phrase-only"
    CONTENT=$(printf '%s' "$CONTENT" | sed -e 's/<[^>]*>/ /g' -e 's/&gt;/>/g' -e 's/&lt;/</g' -e 's/&amp;/\&/g')
    ;;
esac

REPORT=$(printf '%s' "$CONTENT" | python3 "$CHECKER" --stdin --target "$TARGET" $PHRASE_ONLY 2>/dev/null)
[ -z "$REPORT" ] && exit 0

if [ "$MODE" = "warn" ]; then
  REASON=$(printf 'Style check on this %s payload found issues. This is a warning, not a block, because the payload carries existing content as well as your edit. Check whether any of these are in the text you added. If they are, fix them and retry. If they are pre-existing, proceed.\n\n%s\n\nRules: agents/skills/justins-voice/SKILL.md' "$TOOL" "$REPORT")
  jq -n --arg r "$REASON" '{hookSpecificOutput: {hookEventName: "PreToolUse", permissionDecision: "ask", permissionDecisionReason: $r}}'
  exit 0
fi

REASON=$(printf 'Blocked: this content has not passed the style check. Every line here was written this session, so each violation is yours to fix. Correct the text and retry.\n\n%s\n\nIf a violation is a false positive, say so with the rule id rather than editing rules.json to silence it. Rules: agents/skills/justins-voice/SKILL.md' "$REPORT")
jq -n --arg r "$REASON" '{continue: false, stopReason: $r}'
exit 0

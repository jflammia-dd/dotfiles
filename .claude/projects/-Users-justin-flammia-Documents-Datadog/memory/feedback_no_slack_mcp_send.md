---
name: Never send Slack messages via MCP
description: The Slack MCP appends "Sent using Claude" attribution to every message it sends, which is never allowed. Always use pbcopy+slackfmt instead.
type: feedback
originSessionId: cbbce9e1-84ca-4d75-974d-1f1cad151355
---
Never use the Slack MCP to send messages. The MCP automatically appends "Sent using Claude" attribution, which the user has explicitly prohibited in all mediums.

**Why:** Claude attribution is never acceptable in any medium the user sends to colleagues.

**How to apply:** Always format Slack content with `echo "..." | npx @slackfmt/cli@latest` and nothing else. `slackfmt` copies to clipboard itself. Never pipe its output to `pbcopy` because that overwrites the formatted content with the literal text "Copied to clipboard!". The user pastes manually. Do not use `slack_send_message` or `slack_send_message_draft` for any outbound message.

---
name: Slack mention format
description: Use "@First Name Last Name" for Slack @-mentions in message drafts, never <@slack_id> syntax
type: feedback
originSessionId: 1c23090d-f3ac-49ec-afd9-a92499a4579b
---
Use `@First Name Last Name` when @-mentioning people in Slack message drafts. Never use the `<@SLACK_ID>` syntax.

**Why:** The `<@id>` format is not what users type or expect to see in a draft they'll paste manually.

**How to apply:** When composing Slack messages (via slackfmt or pbcopy), always use the person's display name in `@First Last` format.

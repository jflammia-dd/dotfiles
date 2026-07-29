---
name: feedback_slack_link_rendering
description: Markdown links can paste into Slack as literal brackets; use bare URLs for manual-paste messages
metadata: 
  node_type: memory
  type: feedback
  originSessionId: c6a0443d-d3a9-4dcd-8d25-a96d32b57751
  modified: 2026-07-23T20:04:11.066Z
---

When Justin manually pastes a Slack message, markdown links `[text](url)` can arrive as literal text: the anchor shows as `[text]` and only the bare URL inside the parentheses auto-links. This happens when the slackfmt rich-text clipboard does not survive the paste, so Slack receives plain markdown.

**Why:** Observed live on a UEBA thread update. slackfmt is meant to convert markdown to Slack rich text, but rich-text paste fidelity is unreliable, and the fallback (plain markdown) renders as brackets-plus-parens.

**How to apply:** For Slack messages Justin will paste by hand, use bare full URLs inline (Slack auto-links them reliably with no rich-text dependency). A bare full URL is clickable and satisfies [[feedback_clickable_links]] (that rule bans bare IDs like "DGV-70", not full URLs). Reserve markdown anchor-text links for when rich-text paste is confirmed to render. Still run content through [[slackfmt]] for bold/lists/code. Related: [[feedback_no_slack_mcp_send]].

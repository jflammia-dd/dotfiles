---
name: feedback-clickable-links
description: Every Jira, Confluence, Slack and PR reference is a rendered markdown link, never a bare ID
metadata:
  type: feedback
---

Every reference to a Jira issue, Confluence page, Slack message or pull request is a
rendered markdown link with descriptive anchor text. Never a bare ID, never a bare URL
in prose.

**Why:** a bare key like SEC-34246 forces the reader to search for it. A link with
descriptive anchor text tells them what it is before they click. It also works from any
surface (Jira, Confluence, GitHub, a doc) without them reconstructing the URL.

**How to apply:**
- Jira: `[SEC-34246: email cross-trust resolution](https://datadoghq.atlassian.net/browse/SEC-34246)`
- Confluence and GitHub: standard markdown `[descriptive text](url)`
- Slack: the native `<url|text>` form, since Slack does not render markdown links
- Anchor text describes the target, so prefer the ticket summary over the bare key
- Applies in prose, tables and list items alike

Platform-specific link syntax is covered in [[feedback-slack-link-rendering]]. Code
references have their own rule in [[feedback-code-deeplinks]].

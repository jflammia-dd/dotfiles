---
name: Epic description style
description: Jira epic descriptions should not list child ticket numbers in the prose
type: feedback
originSessionId: 41e20ba3-699a-49bc-bcb0-a343d113c563
---
Do not reference child ticket numbers (e.g. SEC-30832, SEC-30880) in the prose of a Jira epic description. The epic view already shows all child tickets. The description should explain what the epic is and why it exists, in plain prose. Ticket enumeration in the body is redundant and defeats the purpose of the epic structure.

**Why:** User called this out explicitly after an epic description update listed current priorities as a numbered ticket list.

**How to apply:** When writing or updating a Jira epic description, describe phases and goals in prose only. No ticket numbers, no bulleted ticket lists, no "current priorities" sections enumerating SEC-IDs.

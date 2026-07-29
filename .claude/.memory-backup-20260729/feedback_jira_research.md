---
name: Document research findings in Jira tickets
description: Add implementation research to Jira tickets so followers understand the reasoning
type: feedback
originSessionId: 7da81963-1801-4858-a15d-eb928abdeb37
---
Before writing code for a ticket, add a Jira comment documenting the key research findings: what APIs were found, what field names matter, what design decisions were made and why.

**Why:** People following the work in Jira need context to understand the implementation choices. Raw code changes don't explain why specific fields, clients or patterns were chosen.

**How to apply:** After researching a ticket's implementation, add a comment to the Jira issue covering the concrete findings (field names, import paths, filter syntax, design constraints). Write it at the level a Datadog engineer unfamiliar with the specific system could follow.

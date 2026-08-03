---
name: feedback-no-local-vault-links-jira
description: "never link to local Obsidian vault files in Jira/Confluence comments, summarize instead"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: bb43d5ec-5318-453d-8830-a3da00497d71
  modified: 2026-08-03T15:49:25.614Z
---

Never link to local Obsidian vault markdown files in Jira comments (or any externally-shared artifact). Vault files live only on Justin's machine, so a link is dead for any other developer reading the ticket.

Why: caught when drafting a SEC-34257 audit comment that cited vault doc paths as sources for retention-estimate inputs.

How to apply: when a comment needs to reference vault-sourced data (numbers, decisions, prior analysis), inline a terse summary of the fact itself instead of a path or link. Reserve links for things reachable by any Datadog employee (GitHub, Confluence, Jira). This applies everywhere the same class of mistake could recur: PR descriptions, Slack messages, any cross-referenced artifact.

---
name: jira-reference-issues-in-dev-work
description: "Canonical Atlassian guidance on referencing Jira issue keys in commits and PRs so the Development panel auto-links"
metadata:
  node_type: memory
  type: reference
  originSessionId: ea0492c0-e69e-42cf-a798-97f2498649d1
---

Canonical source: [Reference issues in your development work](https://support.atlassian.com/jira-software-cloud/docs/reference-issues-in-your-development-work/) (Atlassian Jira Software Cloud docs).

Rules:

- Commit: include the key in the subject, e.g., `[SEC-31588] <conventional commit subject>`.
- PR title: include the key, e.g., `[SEC-31588] <subject>`.
- Do NOT include the issue key in branch names. Datadog engineering has its own branch-naming convention. Commits and PR titles carry the key for Jira auto-linking; branches do not need it.
- Keys are case-sensitive. Use `SEC-31588`, not `sec-31588`.
- Crucible reviews: title starts with the key.
- Smart Commits (`#close`, `#time 1h`, `#comment ...`) are referenced separately and require admin enablement. Do not assume they work without checking.

Why: Jira's Development panel auto-populates from text containing the key. Putting the key in the commit subject and PR title gives Jira everything it needs without polluting branch names.

How to apply: Use the existing Datadog conventions (codified in CLAUDE.md Git Rules) for commit and PR formats. Follow Datadog engineering's branch-naming convention separately.

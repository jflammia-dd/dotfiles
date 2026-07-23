---
name: code-comment-references-need-deeplinks
description: "Bare Jira/Confluence/PR IDs in Go (or other) source code comments must be full deeplinks, not bare numbers"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 1166dd41-c837-44c4-9acb-dcb6a70b794a
  modified: 2026-07-21T17:52:28.836Z
---

Any Jira, Confluence, PR or other external reference written inside a source code comment must be a full URL, never a bare ID like "Confluence 5278466430" or "SEC-12345" alone. Resolve the real link (fetch the page/issue if needed to confirm it exists) and inline the URL in the comment.

**Why:** A bare ID is a dead end for the next engineer reading the comment in an editor, which has no ID-resolution tooling the way Jira/Confluence UIs do. This surfaced in `record_writer.go`, which carried `(Confluence 5278466430)` instead of a link; fixed to the full `https://datadoghq.atlassian.net/wiki/pages/viewpage.action?pageId=<id>` deeplink.

**How to apply:** Applies to comments in code files specifically, distinct from [[feedback_clickable_links]] (bare IDs in vault docs/Jira/Confluence prose) and [[feedback_code_deeplinks]] (file+line references inside docs needing GitHub links). When writing or editing a code comment that cites an external doc or ticket, use the `https://datadoghq.atlassian.net/wiki/pages/viewpage.action?pageId=<id>` form for Confluence (works without knowing the space key) and standard `https://datadoghq.atlassian.net/browse/<KEY>` for Jira. If multiple comments in the same file cite the same source, consolidate to one citation and have the others reference it, rather than repeating (and risking drift on) the same link.

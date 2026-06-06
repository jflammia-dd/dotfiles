---
name: feedback-no-iterative-thinking-in-output
description: "Never include iterative thinking or before/after comparisons in any output (code, config, docs, Confluence, Slack or anything else)"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 43ba118d-87bd-4895-ba7e-37bb2786d919
---

Comments, documentation and all other output must state intent only.

**Why:** Iterative thinking (what changed, what was wrong before, how this improves on the old approach) is conversational context. It does not belong in artifacts that outlive the session.

**How to apply:** Strip any phrasing that implies a before state or comparison: "instead of X", "now Y", "reduces N to 1", "skips its own per-query mint", "falls back to", "no longer does X". If the sentence only makes sense knowing the old behavior, rewrite it around the intent.

Applies everywhere: code comments, commit messages, Confluence pages, Jira comments, Slack messages, config files, docs.

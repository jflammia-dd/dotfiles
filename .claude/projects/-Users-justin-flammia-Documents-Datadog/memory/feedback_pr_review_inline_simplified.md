---
name: feedback_pr_review_inline_simplified
description: "PR review comments must be inline (anchored to specific lines via a GitHub review), and must use the simplified conversational version, not the full technical draft"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: f2b9c6f8-a59b-4fc4-8f6b-8754c48b063d
  modified: 2026-08-05T22:30:40.899Z
---

When posting drafted PR review comments to GitHub, two requirements apply.

1. Post as inline comments anchored to specific line(s) of code, as part of a GitHub review (`gh api repos/<owner>/<repo>/pulls/<number>/reviews` with a `comments` array carrying `path`/`line`/`side`), not as general top-level PR comments via `gh pr comment`.
2. Use the simplified plain-language version shown in conversation for approval (the "simple version" recap), not the longer technical draft with links and full reasoning. The detailed draft is for Justin's own understanding while approving; the posted comment should be the short version.

Why: caught after posting two full-length top-level comments on PR #40254 (ddoghq/dd-source) that were neither inline nor simplified. Justin deleted them manually and corrected the approach. Justin flagged this as a recurring issue, not a first-time mistake, so treat it as a standing rule rather than a one-off correction.

How to apply: any time a PR review flow (see [[pr_review skill]] usage) reaches the posting step, confirm the target comment is anchored to a line/range via a review payload and pull the short summary sentence(s) already shown for approval, not the fuller markdown draft.

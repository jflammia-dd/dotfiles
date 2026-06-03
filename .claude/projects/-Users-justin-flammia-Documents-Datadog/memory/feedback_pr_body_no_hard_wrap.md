---
name: feedback_pr_body_no_hard_wrap
description: Never hard-wrap prose in PR descriptions posted via gh CLI; GitHub renders hard newlines as line breaks within paragraphs
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 9f90ac39-4013-48f7-8793-5741d1f64bef
---

Never use heredocs or any multi-line string that hard-wraps prose at 80 characters when posting PR descriptions via `gh pr create` or `gh pr edit`.

**Why:** GitHub's markdown renderer treats hard newlines within a paragraph as line breaks, producing broken mid-sentence wrapping in the rendered description.

**How to apply:** Keep prose paragraphs as single unwrapped lines in the shell command. Use `gh pr edit --body "..."` with the summary as one long line. Only use actual newlines between distinct blocks (headings, list items, blank lines between paragraphs).

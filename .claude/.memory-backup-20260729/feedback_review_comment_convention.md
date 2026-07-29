---
name: feedback_review_comment_convention
description: "Justin's inline review-comment convention for Claude-generated Obsidian notes (highlight + HTML comment)"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: a2026cdb-e4a4-45cf-a08f-1a7f1f1022a7
---

Justin flags feedback inline on Claude-generated notes using `==highlighted text==` for the span plus an adjacent `<!-- REVIEW: comment -->` HTML comment, since Obsidian has no Confluence/Google-Docs-style selection-anchored comments.

Why: he wanted a way to anchor comments to specific text during review without a native feature for it; HTML comments render invisibly in Obsidian preview/reading view but are visible in the raw markdown any tool reads, and `==...==` gives a visible "selection" analog.

How to apply: when asked to address review comments in a vault note, grep for `REVIEW:`, resolve each against its adjacent highlight or paragraph, make the edit, then strip both the comment and highlight markers. Full convention documented at `agents/skills/obsidian/references/vault-conventions.md`.

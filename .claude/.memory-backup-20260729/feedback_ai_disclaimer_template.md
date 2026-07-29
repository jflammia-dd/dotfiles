---
name: feedback-ai-disclaimer-template
description: "Standard opt-in AI disclaimer text for published documents, and where it's wired into policy/skill"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 26a60a50-5f26-4907-9d34-9ec3d85b8007
  modified: 2026-07-22T18:16:20.120Z
---

Justin has a standard disclaimer he opts into adding at the top of some published documents, disclosing they were AI-drafted:

```
🤖 *AI Disclaimer: This document was drafted with Claude based on [source material]. I have reviewed it for accuracy before publishing.*
```

Fill in `[source material]` per document (for example, "PoC code and notes kept locally", "meeting transcripts and Slack threads"). Keep the rest of the wording fixed.

Why: this is a deliberate, opt-in authorship disclosure, distinct from the local-process-language ban on casually mentioning "Claude"/"the agent" in published artifacts (see [[feedback_no_claude_attribution]] and `agents/policies/published-artifacts.md`, which now documents this as an explicit exception).

How to apply: never add this automatically. When publishing a doc (`obsidian-to-confluence` skill, step 1c), ask whether Justin wants it added; default to no. If yes, insert as the first line after the H1 heading, before any Review Status table.

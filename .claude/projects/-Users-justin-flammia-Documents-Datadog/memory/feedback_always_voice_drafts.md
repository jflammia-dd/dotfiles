---
name: feedback-always-voice-drafts
description: run every drafted reply (PR/Confluence/Slack/Jira) through justins-voice before showing it, without being asked
metadata:
  type: feedback
---

Apply the `justins-voice` skill to every drafted human-facing reply (PR comments, Confluence, Slack, Jira) by default, before presenting it. Do not wait for the user to ask.

Why: user had to explicitly request voice pass and a follow-up correction ("no catch openers") on the same thread; said directly "I don't want to have to correct you each time." AGENTS.md/CLAUDE.md already mandates invoking justins-voice for any human-facing writing task, this confirms it applies to short PR reply drafts too, not just documents.

How to apply: draft, then silently pass through justins-voice rules (no Oxford commas, no em dashes, no colons in narrative, active voice, no evaluative openers like "good/fair catch", less-is-more brevity) before it ever reaches the user. See [[feedback_no_catch_acknowledgment]].

---
name: feedback-measure-whole-context-surface-first
description: Before optimising any always-on context, measure every contributor to it. The skill listing usually dwarfs CLAUDE.md
metadata:
  type: feedback
---

Before trimming any part of always-on context, measure **every** contributor to it and rank
them. Do not start with the file that looks biggest.

**Why:** during the 2026-07 config migration, roughly five hours went into carefully trimming
a 3,158-token `CLAUDE.md` while the registered skill listing sat unmeasured at 14,366 tokens
per turn, more than four times larger. One measurement pass at the start would have reordered
the entire sequence. The migration plan listed the skill surface as a late minor step and that
ordering was followed instead of verified.

**How to apply:**
- Measure first, in this order of usual size: registered skill descriptions, then MCP tool
  definitions, then the memory index, then `CLAUDE.md` and any imported files.
- Count skill descriptions by walking `~/.claude/skills/*/SKILL.md` (follow symlinks) plus
  `skills/*/SKILL.md` under each **enabled** plugin in the marketplaces tree. Do not recurse
  the plugin cache, which holds duplicate versions and inflates the count wildly.
- Use `/context` for the authoritative live figure, since MCP tool schemas may be deferred
  and therefore invisible from inside a session.
- Drive skill decisions from actual usage: grep session transcripts under
  `~/.claude/projects/**/*.jsonl` for `"name":"Skill"` and count the `skill` argument. In 589
  sessions only 38 of 158 skills had ever been invoked.

Related: [[project-corporate-ai-gateway-model-defaults]]

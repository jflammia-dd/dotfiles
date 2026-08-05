---
name: feedback_skill_creator_symlink
description: Skills created by skill-creator land in .agents/skills/ but may not be symlinked into .claude/skills/, leaving them invisible to Claude sessions
metadata: 
  node_type: memory
  type: feedback
  originSessionId: e280c5fe-f1d8-42ec-be9c-fb9e6d5bb3ce
---

Skills created by `skill-creator` are written to `~/.agents/skills/<name>/` but are not automatically symlinked into `~/.claude/skills/`. Without the symlink, the skill won't appear in the available-skills list and can't be invoked.

**Why:** Discovered 2026-06-01 when `wrap-up` skill was missing from the list despite having been created in a prior session.

**How to apply:** If a user says a skill they created isn't showing up, check `~/.agents/skills/` for it and create the symlink: `ln -s ../../.agents/skills/<name> ~/.claude/skills/<name>`.

**Tool name correction (2026-08-05):** there is no skill literally named `skill-creator` installed in this environment. The skill-creation tool is `write-a-skill` (`~/.claude/skills/write-a-skill`). If a user says "use the skill creator," confirm which skill they mean rather than assuming the name, then verify with `find ~/.claude/skills ~/.agents/skills -maxdepth 1 -iname "*<guess>*"` before invoking.

**Vault-specific symlink pattern:** for skills authored in the Datadog Obsidian vault, canonical content lives at `agents/skills/<name>/SKILL.md` in the vault, symlinked as `~/.claude/skills/<name> -> ../../Documents/Datadog/agents/skills/<name>` (confirmed via `pr-review`'s existing symlink). Register new vault skills in `agents/capabilities/skills.json` and `AGENTS.md`'s skill list too, not just the symlink.

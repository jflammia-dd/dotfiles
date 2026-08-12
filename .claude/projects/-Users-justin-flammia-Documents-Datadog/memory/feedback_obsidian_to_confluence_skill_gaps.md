# obsidian-to-confluence Skill: Broken Symlinks and Missing Codification

## Broken symlinks

The `obsidian-to-confluence` skill's script symlinks at `~/.claude/skills/obsidian-to-confluence/scripts/` are broken. They point to `~/dotfiles/.claude/skills/obsidian-to-confluence/scripts/` but the actual `.py` files are missing from that location. Only `__pycache__` bytecode exists, so the skill may still work via cached imports but the source is unavailable for inspection or modification. The dotfiles git repo has commit history referencing these files but they were removed at some point.

## Missing codification (UPDATED 2026-08-11)

The skill's SKILL.md has been updated to codify the five workflow gaps identified during the ADR-0004 publishing session. The following steps were added:

1. **Step 1d: Strip Obsidian-only metadata** — vault-local callouts (e.g., `> [!info] Not yet published to Confluence`) must be removed before conversion.
2. **Step 1e: Resolve wikilinks to Confluence URLs** — `[[WikiLink]]` references to already-published notes should be replaced with proper Confluence page links before conversion.
3. **Step 1f: Use native frontmatter for ADR pages** — ADRs should use the Atlassian MCP's `createConfluencePage` with HTML content format to get native status pills, date nodes, and mentions in the frontmatter table.
4. **Step 10: Cross-reference updates** — when publishing a document that supersedes/amends existing ones, update the existing pages' frontmatter tables (Status, Superseded by, Refined by, Amended by).

The broken symlinks for the Python scripts remain unresolved. The SKILL.md is updated but the script source files at `dotfiles/.claude/skills/obsidian-to-confluence/scripts/` are still missing.

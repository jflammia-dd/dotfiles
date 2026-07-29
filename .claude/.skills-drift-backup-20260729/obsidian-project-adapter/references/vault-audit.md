# Full Vault Audit

Run when the user asks to "audit the vault", "check vault organization", or similar. Use the Explore subagent for thoroughness since this touches every part of the vault.

## Areas to Cover

**1. Directory structure and file counts**
- Use `obsidian files` and `obsidian folders` to get counts per directory.
- Flag directories that are empty or underutilized relative to their stated purpose.
- Note if any directory is serving multiple unrelated purposes and may benefit from sub-organization.

**2. Obsidian configuration**
- Read `.obsidian/app.json` for settings like `newFileLocation`, `attachmentFolderPath`, `promptDelete`.
- Read `.obsidian/community-plugins.json` and check which plugins are installed.
- Flag plugins that are installed but never used (e.g., Dataview with zero queries in the vault).
- To disable a plugin: remove it from `.obsidian/community-plugins.json` AND delete its directory under `.obsidian/plugins/`. Both steps are needed; a plugin directory without a config entry is already disabled but wastes space.
- Note any settings that conflict with the vault's organizational structure.

**3. Template consistency**
- Read all templates in `templates/`.
- Compare template frontmatter fields against actual notes created from those templates.
- Flag drift: fields that appear in notes but not the template (or vice versa).
- Check if template body sections match what users actually write in practice.

**4. Wiki-link health**
- Run `obsidian unresolved format=json counts verbose` to find broken links.
- Categorize unresolved links: missing person profiles, missing concept stubs, typos/misspellings, alias mismatches, backslash-escaped pipes (`\|` instead of `|`), and attachment path issues.
- Run `obsidian orphans` and `obsidian deadends` for graph connectivity.
- Check for shorthand references that should use display aliases (e.g., `[[Syed]]` instead of `[[Syed Ashrafulla|Syed]]`).

**5. Tag usage**
- Run `obsidian tags counts sort=count format=json` to see all tags and their frequency.
- Identify tag clusters (related tags forming a coherent group) vs. one-off tags with no pattern.
- Check if the `tags:` frontmatter field in templates is being populated or left empty in practice.

**6. Frontmatter completeness (people directory)**
- Read all files in `people/` and check which frontmatter fields are populated vs. empty.
- Report people profiles with missing core fields (team, org, role, email, location).
- Flag profiles with placeholder values (e.g., no last name, nickname as manager).
- This is informational only. Empty profiles are valid per the graph-first philosophy.

**7. Content type analysis (docs directory)**
- Read filenames and scan content in `docs/` to categorize files by type: reference docs, ticket work, technical research, personal/meta, living dashboards.
- Flag if the directory is mixing too many content types and may benefit from categorization.

**8. Date and naming consistency**
- Check `notes/` filenames against their frontmatter `date` fields for mismatches.
- Verify naming conventions are followed across directories.

**9. Most-linked targets**
- Use `obsidian backlinks` across key files to identify the most-referenced people and concepts.
- This reveals the vault's actual centers of gravity, which may differ from what the user expects.

## Output Format

Present findings grouped by category with clear actionable vs. informational labels:

- **Fix** — broken links, formatting errors, config issues (things that are objectively wrong)
- **Consider** — structural suggestions, unused plugins, template drift (judgment calls)
- **FYI** — usage statistics, most-linked targets, content type breakdown (awareness only)

End with a prioritized list of recommended actions, ordered by impact.

## Documenting Audit Results

After completing an audit, create a doc note at `docs/YYYY-MM-DD - Vault Audit.md` with:
- Frontmatter: `date` and `tags: [productivity]`
- Findings grouped under `## Fix`, `## Consider`, and `## FYI` headers
- Each actionable item as a task: `- [ ] **Description** — Details #todo`
- This creates trackable tasks visible in the TODO dashboard

After implementing fixes, mark tasks as `[x]` with a brief note of what was done. This provides a record of vault maintenance over time.

## Updating the Skill After Audits

After completing an audit, review whether lessons learned should be captured in SKILL.md. Common updates include:
- New entries in Common Pitfalls (formatting issues discovered)
- Changes to the vault structure table (directories added, merged, or removed)
- Updated canonical field names or template fields
- New guidance in audit areas based on patterns found

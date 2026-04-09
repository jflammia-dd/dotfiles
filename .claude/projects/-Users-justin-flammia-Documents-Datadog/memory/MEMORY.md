# Memory Index

## User Profile
- Justin Flammia, Cloud SIEM team, K9 security org at Datadog
- Based in NYC (America/New_York timezone)
- Has been working in Go for several months; comfortable with the language in the Datadog monorepo context
- Email: justin.flammia@datadoghq.com
- Git branch naming convention: `justin.flammia/<ticket>-<description>`
- When doing PR code reviews, show the comment for approval before posting to the PR

## Jira/Atlassian Notes
- MCP `addCommentToJiraIssue` does NOT render `[~accountId:xxx]` mentions — they show as literal text. Avoid inline mentions in Jira comments; let the user add them manually.
- Jira comment editor accepts **markdown** (not wiki markup). Pasting markdown renders correctly in the UI. No markdown toggle needed; just paste directly.
- When preparing Jira comments for clipboard, always use markdown format (not Jira wiki markup like `h2.`, `{{code}}`, `[text|url]`).

## ERS / Temporal Husky
- **Per-event temporal resolution** (the core ERS problem): For each security signal, resolve the entity's state at that signal's timestamp. If a user's role changed at 3pm, a signal at 2pm should see the old role and a signal at 4pm should see the new role.
- Research note: `journal/Temporal Husky - Event-Entity Joins.md`
- `redaplinfra` (GA, production reads) is the only active track for SIEM entity data. `siementity` (INTERNAL) stopped receiving data on Jan 30, 2026 when the crawler's direct EVP send was removed (PR #346014). Do NOT use `siementity` for testing or validation.
- BeagleSQL table `siem_entity_identity` maps to the dead `siementity` track. `redaplinfra` is only queryable via Trino or gRPC. Always test against `redaplinfra`.
- Temporal versioning on `redaplinfra` works. The composite version formula `(payload.version << 48) + timestampMilli` produces unique values per write even with version=0. The "Temporal Husky Versioning Gap" executive summary (March 2026) was retracted; its root cause analysis was wrong.

## Obsidian Vault Notes
- [Notes vs docs placement](feedback_notes_vs_docs.md): "open a note" = `notes/YYYY-MM-DD - Description.md`; `docs/` is for durable reference material only


- **Person enrichment**: Run whoisthis first (team, org, role, Slack ID), then Slack profile (deep-link), then Playwright for start date. See CLAUDE.md for full workflow.
- [Inactive/departed people](feedback_person_inactive_status.md) — whoisthis returning null = likely departed; set `status: inactive` + `tags: [departed]`; proactively flag to user
- [Slack title is unreliable](feedback_slack_title_unreliable.md) — never use Slack title for the `role` field; it's user-editable and often satirical
- **whoisthis enrichment**: Datadog email format drops hyphens from hyphenated last names (e.g., Howard-Flanders → `paul.howardflanders@datadoghq.com`). Some first names are non-obvious spellings (Jenifer not Jennifer). Always verify whoisthis results against the filename and rename if needed.
- **Null whoisthis results** may mean the person departed Datadog, not just a wrong email. Check with the user.
- **Zhong Ren**: whoisthis returns null even with correct email. Likely departed Datadog (Slack deactivated per user).

## Active Documents
- [UEBA doc intent](ueba-doc-intent.md) — UEBA Engineering Landscape doc frames ambiguous work into actionable tracks; open questions become next steps, not blockers
- [Entity Resolution RFC](project_er_proposal.md) — Complete draft RFC at `docs/Entity Resolution - Design Proposal.md`; not yet published to Confluence; Phase 1 (GW→AWS) is the dependency for the User Entity Roll-up project

## Investigation Methodology
- [Verify data sources before comparing results](feedback_investigation_methodology.md) — when two sources show different results, first check if both are live and receiving the same data before theorizing about application logic

## Office Tracking
- [Week boundary rule](feedback_office_week_boundaries.md) — weeks are full Mon-Fri units owned by the month containing the Monday; no partial weeks at month boundaries
- [WFH recording convention](feedback_wfh_recording.md) — only record WFH for notable deviations (bad weather, transit issues, illness); routine WFH is not recorded
- Office tracking is now a single yearly file: `office tracking/2026 - In-Office Tracking.md`
- Slash commands: `/office`, `/wfh [reason]`, `/pto [type]` handle entry + compliance recalc automatically

## Obsidian Plugin Dependencies
- [Templater plugin](project_obsidian_templater.md) — required for Person template first-name alias auto-population; uses `<% tp.file.title.split(' ')[0] %>` syntax
- [Dataview plugin](project_obsidian_dataview.md) — required for dynamic tenure callout on all people notes; uses `dataviewjs` blocks; JS enabled must be on in Dataview settings

## Obsidian Formatting
- [Mermaid newlines](feedback_mermaid_newlines.md) — use `<br/>` inside Mermaid node labels, not `\n`

## Credentials & Tokens
- [Confluence API token](confluence-api-token.md) — expires 2027-03-22; stored in macOS Keychain under `confluence-api-token`

## Key Files
- [GoLand Setup](goland-setup.md) — GoLand configuration for dd-source
- [dd-source Development](dd-source-dev.md) — Repository structure, builds, tools
- [siem-entity-api](siem-entity-api.md) — Project-specific notes
- EVP query stack reference: `docs/EVP Storage and Query Patterns.md` — covers Beagle, DDSQL, Malamute, DataFusion, Trino, Caniche, Substrait and Husky with two execution paths

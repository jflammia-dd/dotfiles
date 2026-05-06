# Memory Index

## User Profile
- Justin Flammia, Cloud SIEM team, K9 security org at Datadog
- Based in NYC (America/New_York timezone)
- Has been working in Go for several months; comfortable with the language in the Datadog monorepo context
- Email: justin.flammia@datadoghq.com
- Git branch naming convention: `justin.flammia/<ticket>-<description>`
- When doing PR code reviews, show the comment for approval before posting to the PR

## Jira/Atlassian Notes
- [Epic description style](feedback_epic_description_style.md): no ticket numbers in epic prose; describe phases and goals only


- MCP `addCommentToJiraIssue` does NOT render `[~accountId:xxx]` mentions. They show as literal text. Avoid inline mentions in Jira comments; let the user add them manually.
- [Rich formatting in Jira comments](feedback_jira_rich_formatting.md): use `addCommentToJiraIssue` with `contentFormat: "markdown"` for any comment with bold, code blocks or lists; `add_comment` does not render markdown
- Jira comment editor accepts **markdown** (not wiki markup). Pasting markdown renders correctly in the UI. No markdown toggle needed; just paste directly.
- When preparing Jira comments for clipboard, always use markdown format (not Jira wiki markup like `h2.`, `{{code}}`, `[text|url]`).

## ERS Project Structure
- [Three-track structure](project_ers_three_track_structure.md): Entity Context (ingestion + sideplane), ERS (resolution) and Risk Insights Entity Rollup (Shariq's Caniche view). Each track has distinct milestones for the same IdP.
- [ERS Delivery Plan](../docs/ERS - Delivery Plan.md) and [Project Overview](../docs/Entity Context and ERS - Project Overview.md) are the canonical planning docs as of 2026-05-05.

## Document Conventions
- [Don't replace existing docs](feedback_dont_replace_existing_docs.md): when asked to write a new document, create a new file; never overwrite the existing one
- [Documents define their own terminology](feedback_documents_define_own_terminology.md): leadership docs should not borrow phase/wave/cohort labels from external plans; define terms within the doc

## ERS / Temporal Husky
- **Per-event temporal resolution** (the core ERS problem): For each security signal, resolve the entity's state at that signal's timestamp. If a user's role changed at 3pm, a signal at 2pm should see the old role and a signal at 4pm should see the new role.
- Research note: `journal/Temporal Husky - Event-Entity Joins.md`
- **Current production state:** `redaplinfra` is the active track for all SIEM entity data (`siem_entity_identity` resource type). All code today (ERS `EmailExactStrategy`, `secmon-public-api` entity context handlers) reads from `redaplinfra`. This is correct and should not be changed until the migration below completes.
- **History:** The full track timeline is `siementity` → `redaplinfra` → `siementity`. Originally, SIEM wrote directly to `siementity` using custom dedup in `siem-entity-api`. PR [#346014](https://github.com/DataDog/dd-source/pull/346014) switched writes to flow through REDAPL's Iris dedup pipeline, landing on `redaplinfra`. `siementity` stopped receiving data Jan 30, 2026 but the track was never deleted. The current migration is back to `siementity`, the same physical track, but now powered by the REDAPL pipeline (Iris dedup, Temporal Husky versioning) instead of the old custom direct-write approach.
- **New decision (made 2026-04-24):** Migrate entity data back to `siementity`. Reason: `redaplinfra` has only 3-day Temporal Husky retention (subject to other producers' scope settings); `siementity` has its own dedicated 90-day retention scope. `siementity` is the correct spelling (all lowercase, one word).
- **Migration status (as of 2026-04-27, NOT yet complete):** PR [#134486](https://github.com/DataDog/logs-backend/pull/134486) merged 4/27, flipping `siementity` from INTERNAL to GA. 2-intake-deploy waiting period running. The double-write code change (`resource-processor-temporal-husky` writing to `siementity`) is owned by redapl-compute (Aniruddha Atale); firm date by 4/28 EOD, estimated ~1 sprint. Conservative design partner launch: 5/24.
- **`siementity`-worker** already exists at `dd-source/domains/evp-workers/apps/siementity-worker`. Takes `TemporalResource` protobuf, writes to Temporal Husky scope `"siementity"`. Cloud SIEM owns this worker.
- **Future target (post-migration):** The REDAPL pipeline and Iris dedup are unchanged. The only difference is that `resource-processor-temporal-husky` writes SIEM data to `siementity` instead of `redaplinfra`. Practical impact on ERS: (1) reads in `EmailExactStrategy` and entity context handlers must point at `siementity`; (2) ERS's RecordWriter (Phase 3) writes to REDAPL via `RedaplAsyncIntakeClient.SendBatch()` the same way `siem-entity-crawler` does, and REDAPL routes that output to `siementity`.
- Temporal versioning formula `(payload.version << 48) + timestampMilli` is implemented in `siementity-worker/src/worker.ts:128`. The "Temporal Husky Versioning Gap" executive summary (March 2026) was retracted; root cause analysis was wrong.

- [No profile for manager refs](feedback_no_profile_for_manager_refs.md): Don't create vault profiles for people who only appear as a `manager:` field in someone else's profile

## Obsidian Vault Notes
- [log.md wiki-link convention](feedback_log_wiki_links.md): use `[[Page Title]]` wiki-links (not bare paths) when referencing vault docs in docs/log.md

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
- [Verify data sources before comparing results](feedback_investigation_methodology.md). When two sources show different results, first check if both are live and receiving the same data before theorizing about application logic.

## Work OS Interaction Style
- [/now should be interactive](feedback_now_interactive.md): one item at a time with action prompts; never a wall of text

## Confluence Workflow
- [Confluence edit approval](feedback_confluence_edit_approval.md). Show verbatim before/after and get explicit approval before applying any page edit. Never apply after a dry-run without pausing.
- [Review comment workflow](feedback_review_comment_workflow.md). One comment at a time. Pre-load context and draft. Move items to Responded immediately after posting.
- [Tool limitations](feedback_tool_limitations.md). Before claiming a tool can't do something, check whether a Python/ADF API approach can. confluence-write.py can't inject link marks but Python ADF scripts can.

## Office Tracking
- [Week boundary rule](feedback_office_week_boundaries.md) — weeks are full Mon-Fri units owned by the month containing the Monday; no partial weeks at month boundaries
- [WFH recording convention](feedback_wfh_recording.md) — only record WFH for notable deviations (bad weather, transit issues, illness); routine WFH is not recorded
- Office tracking is now a single yearly file: `office tracking/2026 - In-Office Tracking.md`
- Slash commands: `/office`, `/wfh [reason]`, `/pto [type]` handle entry + compliance recalc automatically

## Obsidian Plugin Dependencies
- [Templater plugin](project_obsidian_templater.md) — required for Person template first-name alias auto-population; uses `<% tp.file.title.split(' ')[0] %>` syntax
- [Dataview plugin](project_obsidian_dataview.md) — required for dynamic tenure callout on all people notes; uses `dataviewjs` blocks; JS enabled must be on in Dataview settings

## Obsidian Formatting
- [Mermaid newlines](feedback_mermaid_newlines.md): use `<br/>` inside Mermaid node labels, not `\n`
- [Diagram rendering](feedback_diagram_rendering.md): edit `attachments/*.mmd` source files then run `mmdc -i ... -o ...` to regenerate the PNG

## Shell & Credentials
- [1Password shell secrets removed](feedback_op_shell_secrets.md): gh and Figma MCP handle auth independently; no op read calls needed in .zshrc

## Credentials & Tokens
- [Confluence API token](confluence-api-token.md) — expires 2027-03-22; stored in macOS Keychain under `confluence-api-token`

## Ghostty
- [Ghostty Settings Editor](reference_ghostty_settings_editor.md): no config key to set editor for Settings menu; use `ghostty +edit-config` with `$EDITOR` instead

## Internal Resources
- [Presentation template](reference_presentation_template.md). Official internal Google Slides asset library (backgrounds, graphics, template)

## Dev Environment
- [bzl python3 shim issue](feedback_bzl_python_shim.md): `bzl build`/`rapid run` always fail inside Claude Code sessions due to modern-python plugin intercepting `python3`. Run Bazel commands in your own terminal.

## ERS PoC
- [Branching strategy](project_ers_branching.md): single branch `justin.flammia/SEC-30573-entity-resolution-poc` for all PoC work; topic branches off epic only when parallel contributors need isolation
- [Local dev workflow](project_ers_local_dev.md): `DD_ENV=dev rapid run -s entity-resolution` then `grpcurl -plaintext localhost:8080 grpc.health.v1.Health/Check`; statsd warning is expected

- [Run commands yourself](feedback_run_commands_yourself.md): always run commands directly; never tell the user to run something themselves
- [Document research in Jira](feedback_jira_research.md): add a Jira comment with research findings before writing code, so followers understand the reasoning

## Work Cadence
- [ERS PoC work cadence](feedback_work_cadence.md): ticket-by-ticket flow, no push without approval, no Claude attribution, workflow prefs in Obsidian only (not repo docs)

## Obsidian Doc Management
- [Retire stale docs](feedback_retire_stale_docs.md): Delete superseded docs outright; don't archive or add "superseded" headers. Flag stale docs proactively.
- [Zoom file handling](feedback_zoom_file_handling.md): Move Zoom summary files to `attachments/` immediately on ingest; don't leave them in ~/Downloads.

## Writing Rules
- [No TH abbreviation](feedback_no_TH_abbreviation.md): Always write "Temporal Husky" in full, never "TH". Hard rule, not a suggestion.
- [Slack intro style](feedback_slack_intro_style.md): Cold Slack messages use "I'm from [team]" and "I want to understand" for personal framing; "we" for team-level concerns.
- [Always use clickable links](feedback_clickable_links.md): Every Jira ticket, Confluence page, Slack thread, GitHub PR must be a rendered markdown link in conversation. Never a bare ID.
- [Code references must be GitHub deeplinks](feedback_code_deeplinks.md): File path + line number references in docs must link to the exact line on GitHub (`DataDog/dd-source`, `main` branch). Never plain text.

## Slack Workflow
- [Never send via Slack MCP](feedback_no_slack_mcp_send.md): MCP appends "Sent using Claude" attribution; always use pbcopy+slackfmt so user pastes manually
- [Slack mention format](feedback_slack_mention_format.md): use `@First Name Last Name` in drafts, never `<@slack_id>` syntax

## PR and Commit Conventions
- [No Claude attribution in PRs](feedback_no_claude_attribution.md): never add "Generated with Claude Code" or co-author trailers unless explicitly asked
- [PR approval required before publishing](feedback_pr_approval_required.md): always show draft title+body in conversation and get explicit approval before `gh pr create` or any PR description update, even for draft PRs

## PUP / SQL Queries
- [Always print and copy PUP queries](feedback_pup_query_display.md): print as code block AND pbcopy every time; clipboard may be overwritten

## Key Files
- [GoLand Setup](goland-setup.md) — GoLand configuration for dd-source
- [dd-source Development](dd-source-dev.md) — Repository structure, builds, tools
- [siem-entity-api](siem-entity-api.md) — Project-specific notes
- EVP query stack reference: `docs/EVP Storage and Query Patterns.md` — covers Beagle, DDSQL, Malamute, DataFusion, Trino, Caniche, Substrait and Husky with two execution paths

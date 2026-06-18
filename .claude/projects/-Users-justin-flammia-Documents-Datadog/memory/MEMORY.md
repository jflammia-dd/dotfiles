# Memory Index

## Learning
- [Reference Tables teach workspace](reference_tables_teach_workspace.md): `/teach` workspace at `~/teach/reference-tables/`. Product-feature fluency. Lesson 1 done.

## User Profile
- Justin Flammia, Cloud SIEM team, K9 security org at Datadog
- Based in NYC (America/New_York timezone)
- Has been working in Go for several months; comfortable with the language in the Datadog monorepo context
- Email: justin.flammia@datadoghq.com
- Git branch naming convention: `justin.flammia/<ticket>-<description>`
- When doing PR code reviews, show the comment for approval before posting to the PR
- [code-review skill auto-posts without approval](feedback_code_review_skill_no_autopost.md): do NOT use the `code-review:code-review` skill; perform reviews manually and present findings for approval first

## Jira/Atlassian Notes
- [Epic description style](feedback_epic_description_style.md): no ticket numbers in epic prose; describe phases and goals only
- [PoC done gate](feedback_poc_done_gate.md): for tickets on a PoC branch, Done = commit lands on the PoC branch (not PR-to-main). Acceptance criteria still verified before transition.


- MCP `addCommentToJiraIssue` does NOT render `[~accountId:xxx]` mentions. They show as literal text. Avoid inline mentions in Jira comments; let the user add them manually.
- [SEC project requires component](feedback_jira_sec_component_required.md): every `createJiraIssue` against SEC must pass `additional_fields: {"components": [{"id": "10488"}]}` for Cloud SIEM tickets. Schema does not advertise this; first attempt without it returns HTTP 400.
- [Referencing Jira issues in dev work](reference_jira_dev_work.md): canonical Atlassian doc + Datadog conventions for putting the issue key in branches, commits and PR titles. Keys are case-sensitive, uppercase.
- [Rich formatting in Jira comments](feedback_jira_rich_formatting.md): use `addCommentToJiraIssue` with `contentFormat: "markdown"` for any comment with bold, code blocks or lists; `add_comment` does not render markdown
- Jira comment editor accepts **markdown** (not wiki markup). Pasting markdown renders correctly in the UI. No markdown toggle needed; just paste directly.
- When preparing Jira comments for clipboard, always use markdown format (not Jira wiki markup like `h2.`, `{{code}}`, `[text|url]`).

## ERS Architecture Principles
- [AWS within-trust not shipped](feedback_aws_within_trust_not_shipped.md): CloudTrail assume-role walk is in-flight Q3 work, not GA; email matching via EmailExactStrategy is the only out-of-the-box resolution path across all four CSPs
- [No outbound API calls](feedback_ers_no_outbound_api.md): ERS must read only from data already ingested into Datadog. No calls to AWS, PAM tools, IdPs or any external service. Missing datasets mean ingestion work is needed, not a design workaround.
- [Best-effort resolution](feedback_ers_best_effort.md): ERS resolves as far as available data allows and stops cleanly. INDETERMINATE (data gap, useful intermediate actor) vs UNRESOLVED (no progress or guardrail exit). unsupported_gap always maps to UNRESOLVED. actor_class uses UNKNOWN not INDETERMINATE.

## ERS Commitments
- [Q2 delivery commitment](project_ers_q2_commitment.md): federation + role chain resolution in production behind feature flag for org 2 by June 30, PoC state; confirmed with Corey Finley 2026-06-08

## ERS Project Structure
- [Three-track structure](project_ers_three_track_structure.md): Entity Context (ingestion + sideplane), ERS (resolution) and Risk Insights Entity Rollup (Shariq's Caniche view). Each track has distinct milestones for the same IdP.
- [ERS Delivery Plan](../docs/ERS - Delivery Plan.md) and [Project Overview](../docs/Entity Context and ERS - Project Overview.md) are the canonical planning docs as of 2026-05-05.
- [Risk Insights Caniche join vs siementity/ERS](project_risk_insights_caniche_vs_siementity.md): goal is to replace the email-match resolution CTE in risk_insights_risk_scores with ERS entity_resolution records, keeping cloud-inventory decoration/findings as-is. risk_insights_* is the LIVE serving set (API GetViewNames), *_v3 is legacy. Grilled design + prod-org-2 runtime evidence captured in the note.

## Document Conventions
- [Don't replace existing docs](feedback_dont_replace_existing_docs.md): when asked to write a new document, create a new file; never overwrite the existing one
- [Documents define their own terminology](feedback_documents_define_own_terminology.md): leadership docs should not borrow phase/wave/cohort labels from external plans; define terms within the doc

## ERS / Temporal Husky
- **Per-event temporal resolution** (the core ERS problem): For each security signal, resolve the entity's state at that signal's timestamp. If a user's role changed at 3pm, a signal at 2pm should see the old role and a signal at 4pm should see the new role.
- Research note: `journal/Temporal Husky - Event-Entity Joins.md`
- **Current production state (as of 2026-05-07): MIGRATION COMPLETE.** Both sides are done. The REDAPL double-write to `siementity` is deployed. Antara's [dd-source#432500](https://github.com/DataDog/dd-source/pull/432500) flipped the `secmon-public-api` entity context handler to default to `siementity`. Full use of the `siementity` track is now enabled. The `siem-redaplinfra-killswitch` FF exists as an emergency fallback only.
- **History:** The full track timeline is `siementity` → `redaplinfra` → `siementity`. Originally, SIEM wrote directly to `siementity` using custom dedup in `siem-entity-api`. PR [#346014](https://github.com/DataDog/dd-source/pull/346014) switched writes to flow through REDAPL's Iris dedup pipeline, landing on `redaplinfra`. `siementity` stopped receiving data Jan 30, 2026 but the track was never deleted. The current migration is back to `siementity`, the same physical track, but now powered by the REDAPL pipeline (Iris dedup, Temporal Husky versioning) instead of the old custom direct-write approach.
- **New decision (made 2026-04-24):** Migrate entity data back to `siementity`. Reason: `redaplinfra` has only 3-day Temporal Husky retention (subject to other producers' scope settings); `siementity` has its own dedicated 90-day retention scope. `siementity` is the correct spelling (all lowercase, one word).
- **Migration status (complete as of 2026-05-07):** Double-write confirmed deployed. Entity context handler default flipped to `siementity` by Antara ([dd-source#432500](https://github.com/DataDog/dd-source/pull/432500)). Track is live end to end. ERS PoC session confirmed working against `siementity` only.
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

## Balto Runtime Config
- [CINDY trigger pattern](feedback_balto_cindy_trigger.md): `balto migrate` creates proposals without a reviewer; must call `UpdateConfiguration` with `ReviewConfig` via a `bzl run` tool to trigger CINDY Slack approval notifications
- [#k9-siem-ueba channel](reference_k9_siem_ueba_channel.md): `C0B0QRZLCKX` is the UEBA engineering channel used for Balto CINDY notifications for ERS services

## PR Review
- [Codex comments invisible to get-pr-comments.sh](feedback_pr_comments_codex_blind_spot.md): Codex posts as plain PR comments not GraphQL review threads; always also run `gh api "repos/DataDog/dd-source/pulls/<N>/comments"` after any PR review

## Observability as Code
- [Cloud SIEM dashboards live in logs-ops](reference_cloud_siem_dashboards_logs_ops.md): 28 dashboards + 120 monitors in logs-ops cloud-siem domain (not terraform-config/k9-app), deployed via Bazel monitoring_module across gov/prod/staging. Guide: `docs/Dashboards as Code at Datadog.md`

## Active Documents
- [UEBA doc intent](ueba-doc-intent.md) — UEBA Engineering Landscape doc frames ambiguous work into actionable tracks; open questions become next steps, not blockers
- [Entity Resolution RFC](project_er_proposal.md) — Complete draft RFC at `docs/Entity Resolution - Design Proposal.md`; not yet published to Confluence; Phase 1 (GW→AWS) is the dependency for the User Entity Roll-up project
- [UEBA Q3 integration framing](project_ueba_q3_integration_framing.md) — seven Q3 sources, end-to-end-over-depth tenet, partner-delivery prioritization, ownership; docs `UEBA Q3 Goal Framing.md` + `UEBA Q3 Deliverables and Ownership.md`

## Investigation Methodology
- [Verify data sources before comparing results](feedback_investigation_methodology.md). When two sources show different results, first check if both are live and receiving the same data before theorizing about application logic.

## Work OS Interaction Style
- [/now should be interactive](feedback_now_interactive.md): one item at a time with action prompts; never a wall of text

## Confluence Workflow
- [Confluence edit approval](feedback_confluence_edit_approval.md). Show verbatim before/after and get explicit approval before applying any page edit. Never apply after a dry-run without pausing.
- [Confluence edit safety](feedback_confluence_edit_safety.md): Fetch live ADF before ANY edit. Surgical changes to fetched content only. Never regenerate from Obsidian for an existing page. Verify node count after PUT.
- [Review comment workflow](feedback_review_comment_workflow.md). One comment at a time. Pre-load context and draft. Move items to Responded immediately after posting.
- [Tool limitations](feedback_tool_limitations.md). Before claiming a tool can't do something, check whether a Python/ADF API approach can. confluence-write.py can't inject link marks but Python ADF scripts can.
- [Don't suggest resolving comments](feedback_confluence_comment_resolution.md): threads stay open after replying so others can follow the discussion

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

## EVP / Data Tools
- [EVP Explorer = Events UI](reference_evp_explorer_events_ui.md): when user asks for "EVP Explorer" or a GUI to browse track data, they mean Events UI at `dd.datad0g.com/internal/events-ui/`; siementity link: `?track=siementity&query_type=list`

## Internal Resources
- [Presentation template](reference_presentation_template.md). Official internal Google Slides asset library (backgrounds, graphics, template)
- [Datadog MCP multi-org setup](reference_datadog_mcp_multi_org.md): `mcp.datad0g.com` for staging org 2; `mcp.datadoghq.com` for prod/dogfood; separate OAuth sessions; use `claude mcp add` not plugin files

## Skills
- [skill-creator symlink gap](feedback_skill_creator_symlink.md): skills created by `skill-creator` land in `~/.agents/skills/` but are not auto-symlinked into `~/.claude/skills/`; create the symlink manually if a skill is missing

## Dev Environment
- [bzl works in Claude Code](feedback_bzl_python_shim.md): `bzl build`, `bzl run` and `bzl test` all work normally in-session; the python3 shim assumption was wrong.
- [Proto regen must use Bazel](feedback_proto_regen_bazel.md): never use local `protoc` to regenerate `.pb.go` files; use `bzl run //path:file.pb.go_snapshot_test_update` targets instead
- [DDCI MCP auth at session start](feedback_ddci_mcp_auth.md): authenticate mcp__ddci-mcp-prod before any CI debugging; Datadog MCP queries hit staging and return nothing
- [Datadog MCP env switching](feedback_datadog_mcp_env_switch.md): when a query needs a different org (cross-org 404 naming a target org, or a prod resource while bound to staging), ask Justin to re-auth the Datadog MCP for that env and keep going; don't give up

## GitHub Resolution
- [GitHub actor resolution finding](project_github_actor_resolution.md): email-bearing GitHub activity resolves (~96%); audit-log logins don't (absent from IdP data); login resolution needs GitHub-to-IdP linkage, gated on customer SSO/SCIM. Full doc: `docs/GitHub Actor Resolution in UEBA.md`
- [retriever-cli cloud_siem queries](reference_retriever_cli_cloud_siem.md): qualify views as `cloud_siem.*`, quote case-sensitive columns, `--customer-auth=skip` for employee reads, staging env org 2 on `us1.staging.dog`; Risk Insights not materialized in dogfood/prod-org-2
- [Deep-dive reproduction block](feedback_deep_dive_reproduction_block.md): always include the exact queries/commands in deep-dive and research docs (keep in published Confluence version); reproducibility + credibility; scrub only AI-tooling references

## ERS PoC
- [Branching strategy](project_ers_branching.md): single branch `justin.flammia/SEC-30573-entity-resolution-poc` for all PoC work; topic branches off epic only when parallel contributors need isolation
- [Local dev workflow](project_ers_local_dev.md): `DD_ENV=dev rapid run -s siem-entity-resolution-api` then `grpcurl -plaintext localhost:8080 grpc.health.v1.Health/Check`; statsd warning is expected
- [Staging test drive](project_ers_staging_td.md): active TD is `suzuki-x-90`; endpoint `rapid-td-suzuki-x-90.us1.staging.dog:443`; service renamed from `entity-resolution` to `siem-entity-resolution-api` on 2026-05-20

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
- [Include customer demand data](feedback_include_customer_demand_data.md): pull grounded named customer/design-partner demand into planning/positioning docs to strengthen the case; never fabricate where a source has none

## Slack Workflow
- [Never send via Slack MCP](feedback_no_slack_mcp_send.md): MCP appends "Sent using Claude" attribution; always use pbcopy+slackfmt so user pastes manually
- [Slack mention format](feedback_slack_mention_format.md): use `@First Name Last Name` in drafts, never `<@slack_id>` syntax

## PR and Commit Conventions
- [No Claude attribution in PRs](feedback_no_claude_attribution.md): never add "Generated with Claude Code" or co-author trailers unless explicitly asked
- [PR approval required before publishing](feedback_pr_approval_required.md): always show draft title+body in conversation and get explicit approval before `gh pr create` or any PR description update, even for draft PRs
- [No hard-wrapping in PR body prose](feedback_pr_body_no_hard_wrap.md): keep prose paragraphs as single unwrapped lines in `gh pr create`/`gh pr edit`; hard newlines render as line breaks in GitHub

## PUP / SQL Queries
- [Always print and copy PUP queries](feedback_pup_query_display.md): print as code block AND pbcopy every time; clipboard may be overwritten
- [Use retriever-cli for queries](feedback_retriever_cli_queries.md): run/test all Trino and DDSQL queries with retriever-cli; share via `retriever-cli link --execution-engine <engine> --query "..."` to generate a PUP URL

## ERS Prod Deployment
- [siem-entity-resolution-api prod deploy command](project_siem_era_prod_deploy_cmd.md): exact `rapid release` command for us1-only prod deploy, expected ~35-45 min total

## Rapid / Mosaic
- [Mosaic URL patterns](reference_mosaic_urls.md): allDeployments tab tracks rollout per DC; change-request URL only tracks the CI bundle generation job
- [rapid.json deployment gap](feedback_rapid_json_deployment_gap.md): rapid.json-only changes don't trigger Conductor redeployment; must run `rapid release` manually to force CNAB regeneration
- [Rapid prod deployment](feedback_rapid_prod_deployment.md): wrapper script injects RAPID_INVOKER=claude_code and blocks prod; user must run `rapid release --env prod --branch main` directly in a clean terminal

## Key Files
- [GoLand Setup](goland-setup.md) — GoLand configuration for dd-source
- [dd-source Development](dd-source-dev.md) — Repository structure, builds, tools
- [siem-entity-api](siem-entity-api.md) — Project-specific notes
- EVP query stack reference: `docs/EVP Storage and Query Patterns.md` (covers Beagle, DDSQL, Malamute, DataFusion, Trino, Caniche, Substrait and Husky with two execution paths)
- Query stack mental model + PUP guide: `docs/Datadog Query Stack Reference.md` (name decoder, layer diagram, when to use each PUP engine)

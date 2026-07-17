# Memory Index

## Learning
- [Reference Tables teach workspace](reference_tables_teach_workspace.md): `/teach` workspace at `~/teach/reference-tables/`, product-feature fluency. Lesson 1 done.

## User Profile
- Justin Flammia, Cloud SIEM team, K9 security org at Datadog. NYC (America/New_York). Email justin.flammia@datadoghq.com.
- Comfortable in Go within the Datadog monorepo.
- Git branch convention: `justin.flammia/<ticket>-<description>`
- [code-review skill auto-posts without approval](feedback_code_review_skill_no_autopost.md): do NOT use the `code-review:code-review` skill; review manually, present findings for approval first.
- [NYC conference room booking preference](user_nyc_conference_room_preference.md): order is 29th floor, then 30th, then rest of Bank A, then Bank B.

## NYC Office
- [Elevator bank floor groupings](reference_nyc_office_elevator_banks.md): Bank A = 28-43 (Justin's floor 29 included); Bank B = 17-18, 44-51. Confirmed from the panel photo.

## Jira/Atlassian Notes
- [Cloud SIEM Jira conventions](reference_cloud_siem_jira_conventions.md): Goal→Initiative(SECPRODK9)→Epic(SEC)→Story/Task; epics immutable + outcome-oriented; relationships in native fields only (parent + is-blocked-by DAG); sprints+priority; sparse labels; no sizing. Note: [[Cloud SIEM - Jira Conventions and Patterns]].
- [Epic description style](feedback_epic_description_style.md): no ticket numbers in epic prose, describe phases and goals only.
- [PoC done gate](feedback_poc_done_gate.md): on a PoC branch, Done = commit lands on the branch (not PR-to-main); acceptance criteria still verified.
- [SEC project requires component](feedback_jira_sec_component_required.md): `createJiraIssue` against SEC needs `additional_fields: {"components": [{"id": "10488"}]}` or returns HTTP 400.
- [Transition Jira to In Review on PR open](feedback_transition_jira_on_pr_open.md): do this automatically after every `gh pr create`, never wait to be asked.
- [Referencing Jira issues in dev work](reference_jira_dev_work.md): issue key in branches, commits, PR titles; keys case-sensitive uppercase.
- [Rich formatting in Jira comments](feedback_jira_rich_formatting.md): use `addCommentToJiraIssue` with `contentFormat: "markdown"`; `add_comment` does not render markdown.

## ERS Architecture Principles
- [AWS within-trust not shipped](feedback_aws_within_trust_not_shipped.md): CloudTrail assume-role walk is Q3 in-flight, not GA; EmailExactStrategy is the only out-of-the-box path across all four CSPs.
- [No outbound API calls](feedback_ers_no_outbound_api.md): ERS reads only already-ingested Datadog data; missing datasets mean ingestion work, not a design workaround.
- [Best-effort resolution](feedback_ers_best_effort.md): resolve as far as data allows, stop cleanly. INDETERMINATE (data gap) vs UNRESOLVED (no progress/guardrail exit); unsupported_gap maps to UNRESOLVED; actor_class uses UNKNOWN.

## ERS Commitments
- [Q2 delivery commitment](project_ers_q2_commitment.md): federation + role chain resolution in prod behind FF for org 2 by June 30, PoC state; confirmed with Corey Finley 2026-06-08.

## ERS Project Structure
- [Three-track structure](project_ers_three_track_structure.md): Entity Context (ingestion + sideplane), ERS (resolution), Risk Insights Entity Rollup (Shariq's Caniche view); distinct milestones per IdP.
- [ERS Jira structure](reference_ers_jira_structure.md): ERS build under KR2 SECPRODK9-1302; strategy epics SEC-33707/8/9/13 + new "Resolve Email Address Actors to the Human" epic (replaces PoC SEC-30573, which is being closed); SEC-33721 is the KR1 consumer roll-up. Logical ticket list + DAG in [[ERS - Jira Structure and Backlog Mapping]].
- [ERS Delivery Plan](../docs/ERS - Delivery Plan.md) and [Project Overview](../docs/Entity Context and ERS - Project Overview.md): canonical planning docs (2026-05-05).
- [ERS epic fact-check + ticket-shaping process](reference_ers_epic_process.md): repeatable per-epic process (fact-check → report → apply), refined on Azure + AWS; apply to GCP/foundation/IdP cohorts before touching Jira.
- [ERS foundation skeleton-first](project_ers_foundation_skeleton.md): freeze seams + file locations in a stubbed skeleton (quick-follow after the scaffolds + protos) before the provider lanes start; lanes block on the stub, real impl matures in parallel.
- [Risk Insights Caniche join vs siementity/ERS](project_risk_insights_caniche_vs_siementity.md): replace the email-match resolution CTE in risk_insights_risk_scores with ERS entity_resolution records, keep cloud-inventory decoration/findings. risk_insights_* is LIVE serving set, *_v3 legacy.

## Document Conventions
- [Don't replace existing docs](feedback_dont_replace_existing_docs.md): new document = new file, never overwrite.
- [Documents define their own terminology](feedback_documents_define_own_terminology.md): don't borrow phase/wave/cohort labels from external plans; define terms in the doc.

## ERS / Temporal Husky
- **Per-event temporal resolution** (core ERS problem): resolve each signal's entity state at that signal's timestamp (2pm signal sees old role, 4pm sees new).
- Research note: `journal/Temporal Husky - Event-Entity Joins.md`
- [siementity migration](project_siementity_migration.md): COMPLETE 2026-05-07. Timeline siementity → redaplinfra → siementity; read/write impact on ERS, worker, versioning formula in the file.
- [No profile for manager refs](feedback_no_profile_for_manager_refs.md): don't create vault profiles for people appearing only as a `manager:` field.

## Obsidian Vault Notes
- [log.md wiki-link convention](feedback_log_wiki_links.md): use `[[Page Title]]` wiki-links, not bare paths, in docs/log.md.
- [Review comment convention](feedback_review_comment_convention.md): `==highlight==` + `<!-- REVIEW: ... -->` to flag inline feedback on generated notes; grep/resolve/strip when addressing.
- [Notes vs docs placement](feedback_notes_vs_docs.md): "open a note" = `notes/YYYY-MM-DD - Description.md`; `docs/` is durable reference only.
- [Inactive/departed people](feedback_person_inactive_status.md): whoisthis null = likely departed; set `status: inactive` + `tags: [departed]`, flag to user.
- [Slack title is unreliable](feedback_slack_title_unreliable.md): never use Slack title for `role`, it's user-editable.
- **Zhong Ren**: whoisthis returns null even with correct email; likely departed (Slack deactivated).
- [Transcript ingest skill gap](project_transcript_ingest_skill_gap.md): no vault skill handles raw Zoom transcripts; `ingest-zoom-meeting` excludes them and points to a nonexistent skill.

## Balto Runtime Config
- [CINDY trigger pattern](feedback_balto_cindy_trigger.md): `balto migrate` creates proposals without a reviewer; call `UpdateConfiguration` with `ReviewConfig` via `bzl run` to trigger CINDY Slack notifications.
- [#k9-siem-ueba channel](reference_k9_siem_ueba_channel.md): `C0B0QRZLCKX`, UEBA eng channel for Balto CINDY notifications.

## PR Review
- [Codex comments invisible to get-pr-comments.sh](feedback_pr_comments_codex_blind_spot.md): Codex posts plain PR comments, not review threads; also run `gh api "repos/DataDog/dd-source/pulls/<N>/comments"`.

## Observability as Code
- [Cloud SIEM dashboards live in logs-ops](reference_cloud_siem_dashboards_logs_ops.md): 28 dashboards + 120 monitors in logs-ops cloud-siem domain, Bazel monitoring_module across gov/prod/staging. Guide: `docs/Dashboards as Code at Datadog.md`.

## Active Documents
- [UEBA doc intent](ueba-doc-intent.md): UEBA Engineering Landscape frames ambiguous work into tracks; open questions become next steps.
- [Entity Resolution RFC](project_er_proposal.md): draft at `docs/Entity Resolution - Design Proposal.md`, not yet on Confluence; Phase 1 (GW→AWS) is the User Entity Roll-up dependency.
- [UEBA Q3 integration framing](project_ueba_q3_integration_framing.md): seven Q3 sources, end-to-end-over-depth, partner-delivery priority. Docs `UEBA Q3 Goal Framing.md`, `UEBA Q3 Deliverables and Ownership.md`.
- [ERS prod redesign domain model](project_ers_prod_redesign_domain_model.md): clean-slate read-path design; locked decisions + open questions in the doc.

## Investigation Methodology
- [Verify data sources before comparing results](feedback_investigation_methodology.md): when sources differ, first confirm both are live on the same data before theorizing about logic.

## Work OS Interaction Style
- [/now should be interactive](feedback_now_interactive.md): one item at a time with action prompts, never a wall of text.

## Confluence Workflow
- [Confluence edit approval](feedback_confluence_edit_approval.md): show verbatim before/after, get explicit approval; never apply straight after a dry-run.
- [Confluence edit safety](feedback_confluence_edit_safety.md): fetch live ADF before any edit, surgical changes only, never regenerate from Obsidian, verify node count after PUT.
- [Review comment workflow](feedback_review_comment_workflow.md): one comment at a time, pre-load context and draft, move to Responded after posting.
- [Tool limitations](feedback_tool_limitations.md): check a Python/ADF approach before claiming a tool can't do it; ADF scripts can inject link marks.
- [Don't suggest resolving comments](feedback_confluence_comment_resolution.md): threads stay open after replying so others can follow.

## Office Tracking
- [Week boundary rule](feedback_office_week_boundaries.md): full Mon-Fri weeks owned by the month containing the Monday, no partial weeks.
- [WFH recording convention](feedback_wfh_recording.md): record WFH only for notable deviations (weather, transit, illness), not routine.
- Single yearly file `office tracking/2026 - In-Office Tracking.md`; `/office`, `/wfh [reason]`, `/pto [type]` handle entry + compliance recalc.

## Obsidian Plugin Dependencies
- [Templater plugin](project_obsidian_templater.md): Person template first-name alias auto-population, `<% tp.file.title.split(' ')[0] %>`.
- [Dataview plugin](project_obsidian_dataview.md): dynamic tenure callout on people notes via `dataviewjs`; JS must be enabled.

## Obsidian Formatting
- [Mermaid newlines](feedback_mermaid_newlines.md): `<br/>` in Mermaid node labels, not `\n`.
- [Diagram rendering](feedback_diagram_rendering.md): edit `attachments/*.mmd`, run `mmdc -i ... -o ...` to regenerate the PNG.

## Shell & Credentials
- [1Password shell secrets removed](feedback_op_shell_secrets.md): gh and Figma MCP auth independently, no `op read` in .zshrc.

## Credentials & Tokens
- [Confluence API token](confluence-api-token.md): expires 2027-03-22, in macOS Keychain under `confluence-api-token`.

## Ghostty
- [Ghostty Settings Editor](reference_ghostty_settings_editor.md): no config key for the Settings-menu editor; use `ghostty +edit-config` with `$EDITOR`.

## tmux / NeoVim
- [tmux extended-keys for Ctrl-Space](feedback_tmux_extended_keys_ctrl_space.md): `set -g extended-keys on` for Ctrl-modified keys to reach nvim; default off collapses Ctrl-Space to NUL.

## EVP / Data Tools
- [EVP Explorer = Events UI](reference_evp_explorer_events_ui.md): "EVP Explorer" means Events UI at `dd.datad0g.com/internal/events-ui/`; siementity `?track=siementity&query_type=list`.

## Internal Resources
- [Presentation template](reference_presentation_template.md): official internal Google Slides asset library.
- [Internal Excalidraw](reference_excalidraw_internal.md): use `https://excalidraw.static-app.us1.prod.dog/` for drawing tool requests, not excalidraw.com.
- [Datadog MCP multi-org setup](reference_datadog_mcp_multi_org.md): `mcp.datad0g.com` staging org 2, `mcp.datadoghq.com` prod/dogfood; separate OAuth; use `claude mcp add`.

## Skills
- [skill-creator symlink gap](feedback_skill_creator_symlink.md): skill-creator skills land in `~/.agents/skills/`, not auto-symlinked into `~/.claude/skills/`; symlink manually.

## Dev Environment
- [bzl works in Claude Code](feedback_bzl_python_shim.md): `bzl build/run/test` work in-session; the python3 shim assumption was wrong.
- [Proto regen must use Bazel](feedback_proto_regen_bazel.md): never local `protoc` for `.pb.go`; use `bzl run //path:file.pb.go_snapshot_test_update`.
- [DDCI MCP auth at session start](feedback_ddci_mcp_auth.md): auth mcp__ddci-mcp-prod before CI debugging, or Datadog MCP hits staging and returns nothing.
- [Datadog MCP env switching](feedback_datadog_mcp_env_switch.md): on a cross-org 404 or a prod resource while bound to staging, ask Justin to re-auth the Datadog MCP for that env and continue.

## GitHub Resolution
- [GitHub actor resolution finding](project_github_actor_resolution.md): email-bearing GitHub activity resolves ~96%; audit-log logins don't (absent from IdP), gated on customer SSO/SCIM. Doc: `docs/GitHub Actor Resolution in UEBA.md`.
- [retriever-cli cloud_siem queries](reference_retriever_cli_cloud_siem.md): qualify views `cloud_siem.*`, quote case-sensitive columns, `--customer-auth=skip` for employee reads, staging org 2 on `us1.staging.dog`; Risk Insights not materialized in dogfood/prod-org-2.
- [Deep-dive reproduction block](feedback_deep_dive_reproduction_block.md): include exact queries/commands in deep-dive and research docs (keep in Confluence version); scrub only AI-tooling references.

## ERS PoC
- [Branching strategy](project_ers_branching.md): single branch `justin.flammia/SEC-30573-entity-resolution-poc`; topic branches only for parallel contributors.
- [Local dev workflow](project_ers_local_dev.md): `DD_ENV=dev rapid run -s siem-entity-resolution-api`, then `grpcurl -plaintext localhost:8080 grpc.health.v1.Health/Check`; statsd warning expected.
- [Staging test drive](project_ers_staging_td.md): TD `suzuki-x-90`, endpoint `rapid-td-suzuki-x-90.us1.staging.dog:443`; service renamed to `siem-entity-resolution-api` 2026-05-20.
- [Run commands yourself](feedback_run_commands_yourself.md): always run commands directly, never tell the user to run something.
- [Document research in Jira](feedback_jira_research.md): add a Jira comment with research findings before writing code.

## Work Cadence
- [ERS PoC work cadence](feedback_work_cadence.md): ticket-by-ticket flow; workflow prefs live in Obsidian, not repo docs.

## Obsidian Doc Management
- [Retire stale docs](feedback_retire_stale_docs.md): delete superseded docs outright, no archive/"superseded" headers; flag stale docs proactively.
- [Zoom file handling](feedback_zoom_file_handling.md): don't move Zoom source files to attachments; vault notes are the artifact, source is ephemeral.
- [Check vault before asking user](feedback_check_vault_before_asking.md): check with obsidian tools before asking whether a vault file exists.

## Writing Rules
- [No TH abbreviation](feedback_no_TH_abbreviation.md): always write "Temporal Husky" in full, never "TH".
- [Slack intro style](feedback_slack_intro_style.md): cold Slack uses "I'm from [team]" / "I want to understand"; "we" for team-level concerns.
- [Always use clickable links](feedback_clickable_links.md): every Jira/Confluence/Slack/PR reference is a rendered markdown link, never a bare ID.
- [Code references must be GitHub deeplinks](feedback_code_deeplinks.md): file+line references in docs link to the exact line on GitHub (`DataDog/dd-source`, `main`).
- [Include customer demand data](feedback_include_customer_demand_data.md): pull grounded named customer/design-partner demand into planning docs; never fabricate.

## Slack Workflow
- [Never send via Slack MCP](feedback_no_slack_mcp_send.md): MCP appends "Sent using Claude"; use pbcopy+slackfmt for manual paste.
- [Slack mention format](feedback_slack_mention_format.md): `@First Name Last Name` in drafts, never `<@slack_id>`.

## PR and Commit Conventions
- [No Claude attribution in PRs](feedback_no_claude_attribution.md): never add "Generated with Claude Code" or co-author trailers unless asked.
- [PR approval required before publishing](feedback_pr_approval_required.md): show draft title+body and get explicit approval before `gh pr create` or description update, even drafts.
- [No hard-wrapping in PR body prose](feedback_pr_body_no_hard_wrap.md): keep prose paragraphs as single unwrapped lines in `gh pr create`/`edit`.
- [PR publish needs its own approval](feedback_pr_publish_requires_separate_approval.md): creating a draft PR is not approval to publish it; always pass `--draft` explicitly and verify with `gh pr view`; hook-wiring gap (settings.json vs settings.local.json) caused a real incident.

## PUP / SQL Queries
- [Always print and copy PUP queries](feedback_pup_query_display.md): print as a code block AND pbcopy every time.
- [Use retriever-cli for queries](feedback_retriever_cli_queries.md): run/test Trino and DDSQL with retriever-cli; share via `retriever-cli link --execution-engine <engine> --query "..."`.

## ERS Prod Deployment
- [siem-entity-resolution-api prod deploy command](project_siem_era_prod_deploy_cmd.md): exact `rapid release` command for us1-only prod deploy, ~35-45 min.

## git-dd
- [git-dd adoption](project_git_dd_adoption.md): all Datadog repos, `justin.flammia` prefix only, devflow refspecs kept, hard-block hook (fetch/pull/rebase-onto-main only) via `~/.claude/settings.json` not hookify.

## Rapid / Mosaic
- [Mosaic URL patterns](reference_mosaic_urls.md): allDeployments tab tracks per-DC rollout; change-request URL tracks only the CI bundle job.
- [rapid.json deployment gap](feedback_rapid_json_deployment_gap.md): rapid.json-only changes don't trigger Conductor; run `rapid release` to force CNAB regeneration.
- [Rapid prod deployment](feedback_rapid_prod_deployment.md): wrapper injects RAPID_INVOKER=claude_code and blocks prod; user runs `rapid release --env prod --branch main` in a clean terminal.

## Key Files
- [GoLand Setup](goland-setup.md): GoLand config for dd-source.
- [dd-source Development](dd-source-dev.md): repo structure, builds, tools.
- [siem-entity-api](siem-entity-api.md): project-specific notes.
- EVP query stack: `docs/EVP Storage and Query Patterns.md` (Beagle, DDSQL, Malamute, DataFusion, Trino, Caniche, Substrait, Husky).
- Query stack mental model + PUP guide: `docs/Datadog Query Stack Reference.md`.

# Memory Index

## Learning
- [Reference Tables teach workspace](reference_tables_teach_workspace.md): `/teach` workspace at `~/teach/reference-tables/`, product-feature fluency. Lesson 1 done.
- [EVP temporal queries teach workspace](reference_evp_temporal_queries_teach_workspace.md): `~/teach/evp-temporal-queries/`, Temporal Husky AS-OF fluency from SEC-34246. Lesson 1 done.

## Claude Code Environment
- [Corporate AI gateway model defaults](project_corporate_ai_gateway_model_defaults.md): default Sonnet 5 @ 256k via Datadog gateway, cost-conscious; size always-on context for 256k, avoid Opus-only mechanisms.
- [Measure the whole context surface first](feedback_measure_whole_context_surface_first.md): skill listing usually dwarfs CLAUDE.md (14.4k vs 3.2k tokens); rank every contributor before trimming any.
- [deny costs tokens, ask does not](feedback_deny_vs_ask_token_asymmetry.md): deny forces model round-trips, ask is a UI prompt; reserve deny for what would never be approved.
- [dotfiles cron rsyncs ~/.claude](reference_dotfiles_cron_rsync_backup.md): "dotfiles backup" commits understate their contents; check git status before assuming work is uncommitted.
- [Datadog SaaS MCP config](reference_datadog_saas_mcp_config.md): atlassian/gmail/calendar/workspace must be native `type: http`, never `npx mcp-remote`; canonical EITAI page; prefer official atlassian plugin.
- [Startup hooks / slow startup](reference_claude_startup_hooks.md): marketplace-auto-update plugin caused ~75s block; replaced with throttled background hook; don't re-add the plugin.
- [ccstatusline npx hook timeout](reference_ccstatusline_npx_hook_timeout.md): npx-based ccstatusline hook stalled on VPN flakiness, causing 30s UserPromptSubmit timeouts; fixed by installing the binary globally and dropping npx.
- [Matt Pocock skills migration](project_mattpocock_skills_migration.md): consolidated onto the official claude-plugins-official marketplace plugin, globally scoped; retired legacy manual installs and three vault forks (grill-me, grill-with-docs, handoff); wrap-up stays custom.
- [Atlassian MCP comment timeout](reference_atlassian_mcp_comment_timeout.md): getJiraIssue hangs ~60s on media-heavy comments, known unfixed upstream bug (#145), not a broken MCP; retry.
- [DataDog repo layout](reference_datadog_repo_layout.md): real repo checkouts live under `~/go/src/github.com/DataDog/`, not near the vault; stray nested `logs-backend` clone found and removed.
- [isolation:worktree cross-repo limitation](reference_isolation_worktree_limitation.md): Agent tool's isolation:worktree can't target a repo outside the parent session's directory or set the worktree name; use WorktreeCreate/WorktreeRemove hooks instead.
- [Commit hook pipeline](reference_commit_hook_pipeline.md): three PreToolUse Bash hooks gate every commit, message-exists, prose-style, subject-format, in that order.

## User Profile
- Justin Flammia, Cloud SIEM team, K9 security org at Datadog. NYC (America/New_York). Email justin.flammia@datadoghq.com.
- Comfortable in Go within the Datadog monorepo.
- [Staff engineer standard-setting authority](user_staff_engineer_standard_setting.md): one of two staff engineers on Cloud SIEM backend, can set team conventions directly.
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

## ERS
- Architecture: [no outbound API calls](feedback_ers_no_outbound_api.md) (missing datasets mean ingestion work, not a workaround), [best-effort resolution](feedback_ers_best_effort.md) (INDETERMINATE = data gap, UNRESOLVED = no progress, actor_class UNKNOWN), [AWS within-trust not shipped](feedback_aws_within_trust_not_shipped.md) (EmailExactStrategy is the only out-of-the-box path across all four CSPs).
- Structure: [three-track](project_ers_three_track_structure.md) (Entity Context, ERS, Risk Insights Entity Rollup), [Jira structure](reference_ers_jira_structure.md) (KR2 SECPRODK9-1302, epics SEC-33707/8/9/13, KR1 roll-up SEC-33721), [epic fact-check process](reference_ers_epic_process.md), [foundation skeleton-first](project_ers_foundation_skeleton.md), [Caniche join vs siementity](project_risk_insights_caniche_vs_siementity.md) (risk_insights_* is LIVE, *_v3 legacy).
- Canonical plans: [ERS Delivery Plan](../docs/ERS - Delivery Plan.md), [Project Overview](../docs/Entity Context and ERS - Project Overview.md) (2026-05-05). Ticket DAG in [[ERS - Jira Structure and Backlog Mapping]].
- Commitments: [Q2 delivery](project_ers_q2_commitment.md) (federation + role chain in prod behind FF for org 2 by June 30, PoC state; confirmed with Corey Finley 2026-06-08).
- PR workflow: [request-ers reviewer suggestion](feedback_request_ers_pr_suggestion.md) (suggest `gh request-ers` at draft-PR creation under SECPRODK9-1302, never auto-run, once per PR).
- [SEC-32487 is PoC-scoped](project_sec_32487_poc_scoped.md): manual-CD gate on siem-entity-resolution-api doesn't carry over to the productionized service; drain-timeout question still open on its own merits.
- [ERS reviewer group dual-org identities](reference_ers_reviewer_group_dual_org.md): `gh request-ers` only works in `ddoghq` org; use `gh request-ers-dd` for `DataDog`-org repos (e.g. logs-ops); always verify via `requested_reviewers` API since mismatched handles fail silently.
- [DDSQL unknown-provider precedent](reference_ddsql_unknown_provider_precedent.md): `cloud_siem_risk_insights_risk_scores_signals.ddsql` CASE mapping is the existing convention for missing/unknown enum-like values; check it before inventing a new fallback.

## Document Conventions
- [Don't replace existing docs](feedback_dont_replace_existing_docs.md): new document = new file, never overwrite.
- [Documents define their own terminology](feedback_documents_define_own_terminology.md): don't borrow phase/wave/cohort labels from external plans; define terms in the doc.

## ERS / Temporal Husky
- **Per-event temporal resolution** is the core ERS problem: each signal resolves against entity state at its own timestamp (2pm signal sees old role, 4pm sees new). Research note `journal/Temporal Husky - Event-Entity Joins.md`.
- [siementity migration](project_siementity_migration.md) COMPLETE 2026-05-07 (timeline, read/write impact on ERS and worker, versioning formula in the file); [no profile for manager refs](feedback_no_profile_for_manager_refs.md).

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
- [Inline + simplified when posting](feedback_pr_review_inline_simplified.md): post drafted review comments as line-anchored inline review comments, using the short approved version not the full draft. Recurring correction, not a one-off.

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

## Jira/Confluence Comment Content
- [No local vault links in Jira](feedback_no_local_vault_links_jira.md): summarize vault-sourced facts inline instead, since local file paths are dead links for other devs.

## Confluence Workflow
- Edits: [approval first](feedback_confluence_edit_approval.md) (verbatim before/after, never straight after a dry-run), [edit safety](feedback_confluence_edit_safety.md) (fetch live ADF, surgical only, never regenerate from Obsidian, verify node count after PUT), [tool limitations](feedback_tool_limitations.md) (check a Python/ADF approach before claiming a tool can't do it).
- Comments: [one at a time](feedback_review_comment_workflow.md) (pre-load context, move to Responded after posting), [don't suggest resolving](feedback_confluence_comment_resolution.md) (threads stay open so others can follow).

## Office Tracking
- [Week boundary rule](feedback_office_week_boundaries.md): full Mon-Fri weeks owned by the month containing the Monday, no partial weeks.
- [WFH recording convention](feedback_wfh_recording.md): record WFH only for notable deviations (weather, transit, illness), not routine.
- Single yearly file `docs/2026 - In-Office Tracking.md`; `/office`, `/wfh [reason]`, `/pto [type]` handle entry + compliance recalc.

## Obsidian Plugin Dependencies
- [Templater plugin](project_obsidian_templater.md): Person template first-name alias auto-population, `<% tp.file.title.split(' ')[0] %>`.
- [Dataview plugin](project_obsidian_dataview.md): dynamic tenure callout on people notes via `dataviewjs`; JS must be enabled.

## Obsidian Formatting
- [Mermaid newlines](feedback_mermaid_newlines.md): `<br/>` in Mermaid node labels, not `\n`.
- [Diagram rendering](feedback_diagram_rendering.md): edit `attachments/*.mmd`, run `mmdc -i ... -o ...` to regenerate the PNG.

## Credentials & Tokens
- [Confluence API token](confluence-api-token.md): expires 2027-03-22, in macOS Keychain under `confluence-api-token`.

## EVP / Data Tools
- [EVP Explorer = Events UI](reference_evp_explorer_events_ui.md): "EVP Explorer" means Events UI at `dd.datad0g.com/internal/events-ui/`; siementity `?track=siementity&query_type=list`.

## Internal Resources
- [Talkforge](reference_talkforge.md): `datadog.talkforge.app`, AI content-planning tool (talks/demos/videos) from Datadog's advocacy team; has MCP support.
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
- [Ground connectivity diagnosis empirically](feedback_ground_connectivity_diagnosis_empirically.md): never repeat a tool's self-reported error (e.g. "not connected to appgate") as fact; verify via ifconfig/netstat/nc first.
- [1Password SSH signing needs biometric approval](reference_1password_ssh_signing_biometric.md): git commit signing fails with "agent" errors when Justin isn't at the keyboard to approve Touch ID; not a network/AppGate issue, just retry once he confirms.

## GitHub Resolution
- [GitHub actor resolution finding](project_github_actor_resolution.md): email-bearing GitHub activity resolves ~96%; audit-log logins don't (absent from IdP), gated on customer SSO/SCIM. Doc: `docs/GitHub Actor Resolution in UEBA.md`.
- [retriever-cli cloud_siem queries](reference_retriever_cli_cloud_siem.md): qualify views `cloud_siem.*`, quote case-sensitive columns, `--customer-auth=skip` for employee reads, staging org 2 on `us1.staging.dog`; Risk Insights not materialized in dogfood/prod-org-2.
- [Deep-dive reproduction block](feedback_deep_dive_reproduction_block.md): include exact queries/commands in deep-dive and research docs (keep in Confluence version); scrub only AI-tooling references.

## ERS PoC / Ops
- [Branching](project_ers_branching.md) (single branch `justin.flammia/SEC-30573-entity-resolution-poc`), [local dev](project_ers_local_dev.md) (`DD_ENV=dev rapid run -s siem-entity-resolution-api`), [staging TD](project_ers_staging_td.md) (`suzuki-x-90`, `rapid-td-suzuki-x-90.us1.staging.dog:443`), [prod deploy](project_siem_era_prod_deploy_cmd.md) (us1-only `rapid release`, ~35-45 min).
- [Run commands yourself](feedback_run_commands_yourself.md), [document research in Jira](feedback_jira_research.md) before writing code, [ticket-by-ticket cadence](feedback_work_cadence.md).

## Obsidian Doc Management
- [Retire stale docs](feedback_retire_stale_docs.md): delete superseded docs outright, no archive/"superseded" headers; flag stale docs proactively.
- [Zoom file handling](feedback_zoom_file_handling.md): don't move Zoom source files to attachments; vault notes are the artifact, source is ephemeral.
- [Check vault before asking user](feedback_check_vault_before_asking.md): check with obsidian tools before asking whether a vault file exists.

## Writing Rules
- Voice: [always voice-pass drafts](feedback_always_voice_drafts.md) by default, [full scrub on revision](feedback_voice_full_scrub_on_revision.md) (re-check the whole draft, not just the flagged spot), [no comma before conjunction](feedback_comma_before_conjunction.md) (actively scan, not a background rule), [no "good catch" openers](feedback_no_catch_acknowledgment.md).
- Links: [always clickable](feedback_clickable_links.md) (never a bare ID), [code refs as GitHub deeplinks](feedback_code_deeplinks.md) (`DataDog/dd-source`, `main`), [full URLs in code comments](feedback_code_comment_references.md).
- Content: [no TH abbreviation](feedback_no_TH_abbreviation.md) (write "Temporal Husky"), [Slack intro style](feedback_slack_intro_style.md) ("I'm from [team]", "we" for team concerns), [include customer demand data](feedback_include_customer_demand_data.md) (grounded and named, never fabricated).

## Slack Workflow
- [Slack mention format](feedback_slack_mention_format.md): `@First Name Last Name` in drafts, never `<@slack_id>`.
- [Plain narrative style](feedback_slack_plain_narrative_style.md): Slack messages are flowing prose, no bold "Where we stand"/"open tension" section labels.

## PR and Commit Conventions
- [Dotfiles repo exempt from JIRA tag](feedback_dotfiles_repo_no_jira_tag.md): `~/dotfiles` commits skip `[SEC-XXXXX]`/`[NOJIRA]`, it's personal config not Datadog work; other style rules still apply.
- [Dotfiles backup runs unsigned](project_dotfiles_backup_unsigned_commits.md): `commit.gpgSign=false` local override in `~/dotfiles/.git/config` so the 3pm launchd job can commit headless past 1Password Touch ID.
- [Standard AI disclaimer for published docs](feedback_ai_disclaimer_template.md): opt-in 🤖 disclaimer template, offer during `obsidian-to-confluence` publish, default no.
- [No hard-wrapping in PR body prose](feedback_pr_body_no_hard_wrap.md): keep prose paragraphs as single unwrapped lines in `gh pr create`/`edit`.
- [PR creation SOP](feedback_pr_single_commit_sop.md): before review, squash draft-phase commits to one and run the PR description through justins-voice, simplified, in GitHub markdown.

## PUP / SQL Queries
- [Always print and copy PUP queries](feedback_pup_query_display.md): print as a code block AND pbcopy every time.
- [Use retriever-cli for queries](feedback_retriever_cli_queries.md): run/test Trino and DDSQL with retriever-cli; share via `retriever-cli link --execution-engine <engine> --query "..."`.

## git-dd
- [git-dd adoption](project_git_dd_adoption.md): all Datadog repos, `justin.flammia` prefix only, devflow refspecs kept, hard-block hook (fetch/pull/rebase-onto-main only) via `~/.claude/settings.json` not hookify.
- [gh-shim for dual-org auth](reference_gh_shim_dual_org.md): auto-swaps `GH_CONFIG_DIR` for `ddoghq` vs `DataDog` orgs; beta tool, replaces manual `gh auth switch` chaining once installed.
- [logs-ops missing branch-prefix refspec](reference_logs_ops_missing_branch_prefix.md): `gh pr create` needs explicit `--head`/`--base` there since it lacks the `git-dd add-branch-prefix` setup other repos have.

## Rapid / Mosaic
- [Mosaic URL patterns](reference_mosaic_urls.md): allDeployments tab tracks per-DC rollout; change-request URL tracks only the CI bundle job.
- [rapid.json deployment gap](feedback_rapid_json_deployment_gap.md): rapid.json-only changes don't trigger Conductor; run `rapid release` to force CNAB regeneration.
- [Confirm Rapid staging deploy](reference_confirm_rapid_staging_deploy.md): find the squash-merged commit on main (not the branch SHA), compare against Conductor's `lastDeployedSha`/`currentHeadSha` via the read-only status script.
- [Rapid prod deployment](feedback_rapid_prod_deployment.md): wrapper injects RAPID_INVOKER=claude_code and blocks prod; user runs `rapid release --env prod --branch main` in a clean terminal.

## Key Files
- [dd-source Development](dd-source-dev.md): repo structure, builds, tools.
- [siem-entity-api](siem-entity-api.md): project-specific notes.
- EVP query stack: `docs/EVP Storage and Query Patterns.md` (Beagle, DDSQL, Malamute, DataFusion, Trino, Caniche, Substrait, Husky).
- Query stack mental model + PUP guide: `docs/Datadog Query Stack Reference.md`.

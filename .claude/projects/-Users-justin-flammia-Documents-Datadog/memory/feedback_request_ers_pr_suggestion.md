---
name: request-ers-pr-suggestion
description: suggest the gh request-ers alias when creating a draft PR for a SECPRODK9-1302 ticket, never auto-run it
metadata:
  type: feedback
---

When creating a draft PR for a Jira ticket confirmed under the SECPRODK9-1302 initiative ([[reference_ers_jira_structure]]), suggest running the local `gh` alias `request-ers` to request review from the ERS/entity-resolution reviewer team. Reference it by name (`gh request-ers <PR>`), not by a hardcoded reviewer list, since Justin can change the alias's expansion at any time with `gh alias set --clobber`. If the current reviewer names matter in the moment, check `gh alias list` rather than trust a memorized list.

Determining whether a ticket is "under" SECPRODK9-1302: leaf tickets referenced in branches/commits/PRs (e.g. `SEC-34246`) never mention the epic or initiative directly. Check the leaf ticket's Jira parent chain (`getJiraIssue` with `fields: ["parent"]`, walking up if needed) to confirm it climbs to SECPRODK9-1302, rather than matching against a static epic list, since new epics get added under the initiative over time. Cache confirmed tickets so the same ticket isn't requeried every session.

Why: Justin owns four specific ERS domain reviewers (Shariq Syed, Chelsea Xu, Romain Kirszbaum, Kaitlyn Fa as of 2026-07-27) via this alias, and wants them requested consistently for this initiative's work without manual reviewer selection each time.

How to apply:
- Suggest (never auto-run) `gh request-ers` only once, at the moment a draft PR is created for a confirmed SECPRODK9-1302 ticket. Do not suggest it again after later pushes to the same PR, since re-running it re-requests review from people who already reviewed.
- Do not suggest it at the draft-to-published step. Justin does that manually after eyeballing the draft in the GitHub UI, and it isn't part of this suggestion's trigger.
- Do not suggest it for cloud-security-platform or siem-entity-* work outside SECPRODK9-1302. The alias is scoped to this initiative only, not a general-purpose reviewer default.
- If Justin asks to actually invoke `request-ers` (or any `gh` alias), verify the target PR first before running it, per his standing instruction on all `gh` aliases.

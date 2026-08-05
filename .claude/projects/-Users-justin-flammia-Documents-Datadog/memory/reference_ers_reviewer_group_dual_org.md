---
name: reference_ers_reviewer_group_dual_org
description: ERS reviewer group has separate GitHub identities per org (ddoghq vs DataDog); two gh aliases route to the right one
metadata: 
  node_type: memory
  type: reference
  originSessionId: 25a1e736-5755-4d77-8482-9ee23b3c69c8
  modified: 2026-08-04T18:39:25.183Z
---

The four ERS reviewers exist as different GitHub accounts in the two orgs that host relevant repos. `gh request-ers` (existing alias) only works in the `ddoghq` org, e.g. `ddoghq/dd-source`. It silently drops unmatched reviewers with no error when run against a `DataDog`-org repo like `DataDog/logs-ops`, so a "success" output there does not mean the reviewers landed. Always check `gh api repos/<owner>/<repo>/pulls/<n>/requested_reviewers` after requesting to confirm, rather than trusting the alias's exit status alone.

Mapping (ddoghq handle → DataDog handle → display name):
- `shariq-syed_ddog` → `shariqrsyed` → Shariq Syed
- `chelsea-xu_ddog` → `chelsea-xu-dd` → Chelsea Xu
- `romain-kirszbaum_ddog` → `Fedessi8187` → Romain Kirszbaum (no name resemblance, easy to misidentify)
- `kaitlyn-fa_ddog` → `kxfa` → Kaitlyn Fa

For a `DataDog`-org repo, use the new alias `gh request-ers-dd <PR-number>` (added 2026-08-04, same shape as `request-ers` but with the DataDog-org handles). Requires the `jflammia-dd` `gh` account active, same as any other `DataDog`-org PR operation. See [[project_ers_jira_structure]] and the dual-account note in [[project_ers_branching]] for the broader dual-`gh`-account setup this fits into.

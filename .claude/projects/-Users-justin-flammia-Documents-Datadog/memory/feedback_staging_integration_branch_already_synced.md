---
name: feedback_staging_integration_branch_already_synced
description: "Never run ddr devflow integrate --pr for a PR that's already in the merge queue; the staging integration branch picks it up via routine main-sync"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 2b268d54-117a-4e6e-8ae8-1704fd9bd296
  modified: 2026-08-11T13:59:45.353Z
---

Before running `ddr devflow integrate --pr <url> -d` against `siem-entity-resolution-staging` (or any per-service Rapid integration branch), check whether the PR already landed there through the branch's routine sync from `main`. If it did, do not integrate it again.

**Why:** On 2026-08-10, PR ddoghq/dd-source#49009 was already integrated into `siem-entity-resolution-staging` automatically (at merge-queue time, before any devflow command was run). Running `ddr devflow integrate --pr ... -d` afterward reapplied the same diff on top of a branch that already had it, producing a literal duplicate Go struct declaration (`ResolutionRequestFields` at two line numbers in the same file) and breaking the build. Reverting via `ddr devflow code revert-integration -b <branch> --pr <url>` and then re-running the same `integrate --pr` command reproduced the exact same failure a second time, since the branch still had the change through main-sync and the redundant integrate step re-added it again.

**How to apply:** Before integrating a PR into a Rapid/Conductor integration branch, check the branch's recent commit history (`gh api "repos/<owner>/<repo>/commits?sha=<branch>&path=<changed-file>"`) for a prior "integrating [...] (PR <number>, ...)" entry for the same PR. If found, skip `integrate` entirely and just trigger the deploy directly against the branch's current tip: `ddr devflow deploy -b <branch> -s <service1> -s <service2> -t staging`. Reserve `integrate --pr ... -d` for PRs that have never touched that integration branch. See [[project_siem_era_prod_deploy_cmd]] for the separate, unrelated prod-deploy command and its own constraints.

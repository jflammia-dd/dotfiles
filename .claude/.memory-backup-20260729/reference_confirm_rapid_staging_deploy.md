---
name: confirm-rapid-staging-deploy
description: How to verify a specific merged commit is actually deployed to staging for a Conductor-managed Rapid service
metadata: 
  node_type: memory
  type: reference
  originSessionId: 1166dd41-c837-44c4-9acb-dcb6a70b794a
  modified: 2026-07-22T13:34:36.435Z
---

To confirm a specific commit is live in a Rapid service's staging deployment (continuous Conductor deploy, `service.datadog.yaml`'s `datadoghq.com/sdp.conductor` target):

1. Find the actual squash-merged commit on `main`, not the feature branch's own commit SHA. This repo squash-merges PRs, so the branch's commits never land on `main` verbatim, only a new commit with the same diff and a different SHA does. Search by PR number or title:
   ```bash
   git log --oneline --all --grep="<PR number or title>"
   ```
2. Get the latest Conductor run for the service (read-only status, not a deploy action):
   ```bash
   <conductor-skill-path>/scripts/get_conductor_status.sh <service> --target staging
   ```
   Read `lastDeployedSha` (live before this run started) and `currentHeadSha` (what this run is deploying).
3. Check ancestry: `git merge-base --is-ancestor <squash-commit-sha> <lastDeployedSha-or-currentHeadSha>`. An ancestor of `lastDeployedSha` is the strongest confirmation, since it was already live before the current run even began.

A service's own staging logs also carry a `version` tag (`v<pipeline-id>-<short-sha>`) as a quick spot-check. Resolve that short SHA only after `git dd sync`/`git fetch`. A stale local clone makes a genuinely valid SHA look unresolvable and reads like a real discrepancy when it isn't.

**Why:** Confirmed empirically during SEC-34246 staging validation (worked out the hard way: first mistook the branch's own commit for what should appear on `main`, then mistook a short SHA prefix in a log line for unresolvable because of a stale local fetch). The "don't use the conductor skill for Rapid services" warning applies to its deploy/rollback action commands only. Rapid services still route through the same underlying Conductor/railyard system for staging, so the read-only status script is fine and is the only way to get deployment history, since the `rapid` CLI itself has no such command.

**How to apply:** Any time "is my merge actually deployed to staging yet" comes up for a Rapid/Conductor service. Full worked example with exact commands: [[SEC-34246 - Worker Staging Validation Test Plan]] (vault doc, "Confirming the deployed revision" section).

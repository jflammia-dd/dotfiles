---
name: ERS PoC git branching strategy
description: Decided branching approach for ERS PoC development in dd-source
type: project
originSessionId: 7da81963-1801-4858-a15d-eb928abdeb37
---
Single long-running branch for all PoC work: `justin.flammia/SEC-30573-entity-resolution-poc`.

**Why:** PoC work doesn't merge to main during development. You deploy the branch directly to staging with `rapid release` or `rapid td create`. Per-ticket branches would require rebasing between tickets to keep the staging deployment current, which is friction for no benefit. Jira tickets track what got built; commit messages track what changed. Branch topology doesn't need to do that job during a solo PoC.

**When contributors join:** Short-lived topic branches off the epic branch for any parallel ticket work. They merge back to the epic branch when done. No structural change needed until two people are working different tickets simultaneously.

**How to apply:** All PoC commits go on `justin.flammia/SEC-30573-entity-resolution-poc`. Always use `git-dd`, not vanilla git. No push without explicit approval. When the PoC graduates to production PRs, cut them from the epic branch using the PR sequencing strategy in [[Running a PoC at Datadog]].

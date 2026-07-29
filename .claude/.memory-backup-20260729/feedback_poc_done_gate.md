---
name: poc-done-gate
description: "When a Jira ticket's work happens on a PoC branch, the Done gate is the commit landing on the PoC branch, not a PR merging to main"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: ea0492c0-e69e-42cf-a798-97f2498649d1
---

Tickets whose implementation lands on a shared PoC branch (for example `justin.flammia/SEC-30573-entity-resolution-poc`) reach Done as soon as the commit lands on that branch. There is no per-ticket PR to merge.

**Why:** PoC work integrates into the PoC branch directly. That branch IS the integration point. Waiting for a PR-to-main merge would stall every PoC ticket on a gate that does not apply.

**How to apply:** When closing a Jira ticket whose work is on a PoC branch, link the closing comment to the commit on the PoC branch (not a PR). The To Do → In Progress → Done sequence still requires acceptance criteria verification. The canonical lifecycle rule lives in [[jira-lifecycle-plan]].

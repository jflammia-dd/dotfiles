---
name: ers-poc-git-branching-strategy
description: ERS PoC branch is dead; all work is now directly off main
metadata: 
  node_type: memory
  type: project
  originSessionId: fdfa1da7-e87f-454c-8d43-688f1128761d
---

The PoC branch `justin.flammia/SEC-30573-entity-resolution-poc` is dead. All ERS work now happens directly off `main` in dd-source. Feature branches are short-lived, cut from `main` and targeting `main` via PR.

**Why:** The PoC graduated to production. The PoC branch served its purpose during exploratory development; it no longer exists as an active development surface.

**How to apply:** Never reference or suggest the PoC branch. When working on ERS tickets, cut a new branch from `main` named `justin.flammia/<TICKET>-<description>`. All PRs target `main`. Deploy to staging via Rapid test drive or `rapid release` as normal.

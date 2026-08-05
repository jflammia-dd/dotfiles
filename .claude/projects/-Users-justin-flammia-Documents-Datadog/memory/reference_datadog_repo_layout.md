---
name: reference-datadog-repo-layout
description: "Real DataDog git repo checkouts live under ~/go/src/github.com/DataDog/, not near the Obsidian vault"
metadata: 
  node_type: memory
  type: reference
  originSessionId: bcb61b40-d3ee-404d-b859-ba85bb2cd4a1
  modified: 2026-08-05T18:23:37.317Z
---

The working checkouts of DataDog repos (dd-source, logs-ops, cloud-inventory, dd-go, dogweb, k8s-resources, datastores, terraform-config, consul-config, datacenter-config, infrastructure-resources, architecture, devtools, images, web-ui, bits-pet, k9-iw-ocsf-ai-pipeline-generation) are siblings under `~/go/src/github.com/DataDog/`.

The Obsidian vault at `Documents/Datadog` is a separate, unrelated directory tree. It is not a git repo itself and the repos above are not nested inside it.

One exception found and removed: a stray `logs-backend` clone was nested directly inside the vault at `Documents/Datadog/logs-backend/.git`. It was verified clean (on `prod`, up to date with origin) and deleted during [[Claude Code Multi-Repo Worktree Guardrails]] because its presence collided with Claude Code's own nested-repo detection for multi-repo workspaces.

**How to apply:** any task that needs to locate a DataDog repo checkout on this machine should look under `~/go/src/github.com/DataDog/<repo>`, not near the vault. See [[reference_isolation_worktree_limitation]] for why this separation matters for Claude Code's native worktree tooling specifically.

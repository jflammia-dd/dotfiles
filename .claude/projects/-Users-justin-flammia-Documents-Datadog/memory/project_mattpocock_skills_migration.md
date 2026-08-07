---
name: project_mattpocock_skills_migration
description: "2026-08-07 migration of Matt Pocock's skills from manual/local installs to the official claude-plugins-official marketplace plugin, plus retirement of three vault forks"
metadata: 
  node_type: memory
  type: project
  originSessionId: 779e6f9c-1e4b-415e-8cc7-2642e5728113
  modified: 2026-08-07T14:16:25.790Z
---

Consolidated all Matt Pocock skill sources onto `mattpocock-skills@claude-plugins-official`, installed globally (`scope: user`, enabled).

Why: a pre-marketplace manual install (27 skill dirs mirrored into `~/.agents/skills/`, symlinked from `~/.claude/skills/`) was shadowing the official plugin, and the plugin itself was misscoped to a single project (`~/Documents/UEBA`, disabled). No single global source of truth existed.

What changed:
- Uninstalled the misscoped local install, reinstalled at `scope: user` (global), version 1.2.3.
- Deleted 27 shadowing symlinks/dirs plus 3 orphaned duplicates (`grill-me`, `grill-with-docs`, `handoff` copies not currently active) under `~/.agents/skills/`. Left 13 unrelated skills untouched (`caveman`, `slackfmt`, `mcp-repair`, etc.) after confirming byte-for-byte they aren't Matt Pocock's work.
- Separately migrated three vault-customized forks (`agents/skills/{grill-me,grill-with-docs,handoff}` in the Datadog vault) to the official plugin versions, on explicit approval, accepting the loss of vault-specific behavior: `grill-with-docs` had a `CONTEXT.md`/ADR-integrated domain-modeling session the plugin stub doesn't have; `handoff` had a full checkpoint/list/load/clear lifecycle the plugin's one-shot write doesn't have.
- `wrap-up` has no official equivalent and stays as the vault's only remaining custom fork.
- Updated `agents/capabilities/skills.json` and `AGENTS.md` in the vault to drop the three retired entries (both the Claude Code and Codex registrations, per explicit decision to accept Codex losing these three skills entirely since Codex has no plugin-marketplace backfill).
- Added a dated addendum to `docs/2026-07-07 - Claude Code Context Optimization.md` noting its "vault-native" claim for `grill-me`/`handoff` no longer holds, without altering its historical analysis data.

How to apply: if new Matt Pocock skills appear or existing ones update, `claude plugin marketplace update claude-plugins-official` picks them up automatically at global scope. Don't reintroduce manual copies into `~/.agents/skills/` or per-project symlinks.

Codex parity decision (2026-08-07): explicitly decided against giving Codex the full Matt Pocock set. Upstream's own ADR (`.agents/adr/0002-ship-as-a-claude-code-plugin.md` in the plugin cache) confirms no native Codex plugin exists yet, Codex's manifest format can't express a curated subset of their bucketed skills layout, so they deferred it and point to `skills.sh` as the interim workaround. `skills.sh` is copy-based (writes real files into `.agents/skills/` plus a `skills-lock.json`), which is a fork under a different name, not a subscribe mechanism. Pointing Codex at Claude Code's plugin cache directly was also checked and rejected: the cache path is not stable (rotated across three directory names within minutes of installing, no `latest` pointer). Decision: accept the gap. Codex has none of Matt Pocock's skills until upstream ships a native Codex plugin. Revisit only when that lands, don't reach for `skills.sh` or a hand-rolled sync as a workaround in the meantime.

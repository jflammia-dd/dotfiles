---
name: reference_claude_startup_hooks
description: Why Claude Code session startup was slow and the marketplace-auto-update replacement hook
metadata: 
  node_type: memory
  type: reference
  originSessionId: 1590f239-016c-465a-82dc-2244d54e4f8a
  modified: 2026-07-23T16:56:41.263Z
---

Claude Code startup took ~55-85s to become responsive. Root cause (found via `claude -p ... --debug-file`): the `marketplace-auto-update@datadog-claude-plugins` plugin's SessionStart hook ran `claude plugin update` once per installed plugin (79 serial CLI spawns, ~75s). SessionStart hooks are awaited before the prompt is usable, so the whole startup blocked on it. MCP init was NOT the cause (all servers connect in ~6s in parallel; disabling MCP changed nothing).

Fix: uninstalled that plugin and rely on Claude Code's NATIVE plugin/marketplace auto-updater instead. SessionStart hooks cannot be async (they always block), so no hook is the right tool for this. Native auto-update runs in the background 0-10 min after startup, non-blocking, controlled by an `autoUpdate` flag per marketplace. The main `datadog-claude-plugins` marketplace already had `autoUpdate: true` in `~/.claude/plugins/known_marketplaces.json`, so the plugin was fully redundant. Enabled `autoUpdate: true` on the github-backed marketplaces via `extraKnownMarketplaces` in `~/.claude/settings.json` (official marketplaces default on; directory-source ones left alone). A short-lived bespoke background hook (`marketplace-auto-update-bg.sh`) was tried then removed in favor of this native path. Do not re-add the marketplace-auto-update plugin, it reintroduces the blocking loop and duplicates native auto-update. The plugin lives at `DataDog/claude-marketplace` (owner Mat Brown) if the upstream blocking-hook bug is worth reporting.

Secondary contributors also fixed: `npx mcp-remote` transport on the Datadog SaaS MCP servers (see [[reference_datadog_saas_mcp_config]]), a dead `k9-admin-mcp` test-drive endpoint and a duplicate `datadog-atlassian`. Also relevant: a 100%-full disk (`/System/Volumes/Data`) compounds startup because Claude Code atomically rewrites the ~93KB `~/.claude.json` on every start. Keep free space available.

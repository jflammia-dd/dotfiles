---
name: reference-isolation-worktree-limitation
description: "Claude Code's Agent tool isolation:worktree cannot target a repo outside the parent session's directory or set the worktree name"
metadata: 
  node_type: memory
  type: reference
  originSessionId: bcb61b40-d3ee-404d-b859-ba85bb2cd4a1
  modified: 2026-08-05T18:23:53.724Z
---

The `Agent` tool's `isolation: "worktree"` option (and the equivalent `isolation: worktree` field in subagent frontmatter) only isolates within whichever repo the parent session's launch directory already belongs to. Two confirmed gaps, verified against official Claude Code docs (v2.1.218+) rather than inferred:

1. The caller has no way to set the `name` passed to the underlying `WorktreeCreate` hook when dispatching via the `Agent` tool with `isolation: "worktree"`. It is auto-generated only.
2. Subagent frontmatter has no `cwd`/`workingDirectory` field. A subagent isolated this way always resolves against the parent session's launch directory, never a different repo.

Net effect: this mechanism cannot support dispatching subagents across multiple different repos from a session that isn't already rooted in one of them. It only works when the session's own launch directory is the target repo.

The actual documented mechanism for a non-git (or wrong-repo) launch directory is the `WorktreeCreate`/`WorktreeRemove` hook pair in `settings.json`. It receives `name` on stdin, returns an absolute path and can run `git worktree add` against any repo on disk regardless of the session's CWD.

**How to apply:** don't reach for `isolation: worktree` as the parallelism mechanism when work spans multiple repos outside the session's own directory. Use `WorktreeCreate`/`WorktreeRemove` hooks instead, as implemented in [[Claude Code Multi-Repo Worktree Guardrails]] and [[reference_datadog_repo_layout]].

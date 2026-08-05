---
name: reference-commit-hook-pipeline
description: "Three global PreToolUse hooks gate every git commit, each checking a different thing"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 8b3a3813-d6a6-4492-9764-fe499f3fb095
  modified: 2026-08-05T19:35:11.608Z
---

Three hooks fire on `PreToolUse` for the `Bash` matcher in `~/.claude/settings.json`, in this order, each checking something distinct about a `git`/`dd-git commit`:

1. `git-commit-message-guard.sh`, checks that a message exists at all (blocks commits with no `-m`/`-F`, which would open `$EDITOR` or silently reuse a prior message).
2. `voice-git-gate.sh`, checks prose style of the message (em dashes, Oxford commas, via `~/.claude/skills/voice/style_check.py`). Also covers `gh pr create/edit/comment/review`.
3. `commit-format-guard.sh`, checks structure of the subject line against `docs/Git Commit Message Standards.md` in the Datadog vault: `[TICKET]`/`[NOJIRA]` bracket, no trailing period, no `type(scope):` prefix, 50/72 char soft/hard limits.

How to apply: when debugging a blocked commit or adding a fourth commit-related check, read all three scripts first so the new one doesn't duplicate an existing check. Escape hatches: `VOICE_GATE_OFF=1`, `COMMIT_FORMAT_GATE_OFF=1`. See [[project_git_dd_adoption]] for the related `git dd` fetch/pull/rebase block, a separate hook.

---
name: feedback-deny-vs-ask-token-asymmetry
description: A permission deny costs model round-trips, an ask costs almost none. Reserve deny for what would never be approved
metadata:
  type: feedback
---

A `deny` rule costs tokens. An `ask` rule costs almost none.

When a deny fires, the error returns to the model, which has to notice it, re-plan and report
back. Then Justin overrides and it retries: two or three model round-trips per occurrence.
When an `ask` fires it is a UI prompt handled outside the model. One keystroke and the tool
runs, with no extra turn.

**Why:** this inverts the intuitive design goal. The aim is not to make overrides easy, it is
to **minimise how often a block fires at all**. So `deny` belongs only on actions that would
essentially never be approved from inside Claude Code. `ask` belongs on everything that
usually would be.

**How to apply:**
- `deny` for rare and irreversible: force-push, PR publish, merge, close, release create,
  public comment and review posts, outbound email send.
- `ask` for medium-frequency and reversible: plain push, issue mutation, destructive local git,
  Confluence and Jira writes.
- No new rule at all for high-frequency actions that already have gates. `git commit` has
  three. `transitionJiraIssue` is required to be automatic.
- A `deny` on an MCP tool makes any `PreToolUse` guard on that tool unreachable, since deny is
  evaluated before the tool runs. That is why Atlassian writes are `ask`: it preserves the
  formatting and language guards.
- Permission `deny` rules cannot read environment variables, so an override gesture such as
  `ALLOW_MUTATE=1` can only be honoured by a hook, never by a deny entry.

Related: [[feedback-measure-whole-context-surface-first]]

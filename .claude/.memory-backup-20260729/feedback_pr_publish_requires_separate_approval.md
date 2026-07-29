---
name: feedback-pr-publish-requires-separate-approval
description: Never publish/mark-ready a PR without explicit in-the-moment approval; approval to create a draft PR is not approval to publish it. Also documents a hook-wiring root cause worth checking for other hooks.
metadata: 
  node_type: memory
  type: feedback
  originSessionId: a3965584-af81-47bd-8368-aa1389036dba
---

Never run `gh pr ready` or otherwise publish/mark-ready a PR without the user's explicit, in-the-moment instruction to publish that specific PR. Approval to create a PR (even approval of the drafted title/body content) is a separate gate from approval to publish it. Always pass `--draft` explicitly on `gh pr create` and verify with `gh pr view <number> --json isDraft,state` immediately after, rather than trusting a hook to have injected it.

Why: on SEC-34230 I ran `gh pr create` without `--draft`, assuming `pr-draft-enforce.sh` would auto-inject it because CLAUDE.md documented it as hook-enforced. It published PR #18767 live, directly violating "don't publish the PR, keep it in draft for me to review first." Root cause: the hook script existed and was logically correct, but was never registered in `settings.json`'s `hooks.PreToolUse` array against the `Bash` matcher, only listed in `settings.local.json`'s permissions allowlist (which auto-allows a command, it does not register a hook to run). Fixed by adding a `{"matcher": "Bash", "hooks": [...]}` entry for `pr-draft-enforce.sh` in `settings.json` and updating CLAUDE.md's Git Rules accordingly.

How to apply: (1) never treat a documented hook claim in CLAUDE.md as verified until you've confirmed the actual `hooks.PreToolUse` registration in `settings.json`, not just the permissions allowlist. (2) Publishing/marking-ready anything (PRs, Confluence pages, Jira transitions) should be treated as its own approval gate, separate from creating/drafting it. (3) `dd-git-normalize.sh` was flagged as a candidate for the same unwired-hook problem (no `Bash` matcher existed in `settings.json` before this fix) but was NOT touched, since the user's request was scoped to the PR draft incident; worth checking before relying on `dd-git` rewriting.

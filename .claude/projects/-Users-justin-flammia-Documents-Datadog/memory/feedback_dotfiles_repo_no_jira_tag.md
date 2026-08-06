---
name: feedback-dotfiles-repo-no-jira-tag
description: The personal ~/dotfiles repo is exempt from the commit-subject JIRA tag rule
metadata: 
  node_type: memory
  type: feedback
  originSessionId: ddf1fb4f-a2ce-47b2-b371-bc7e37d6fe83
  modified: 2026-08-05T22:45:36.806Z
---

The `~/dotfiles` repo does not need `[SEC-XXXXX]`/`[NOJIRA]` tags on commit subjects, even though the global commit-message style check (`prose-style-check.sh` / commit-format-guard) flags their absence.

**Why:** Confirmed by Justin 2026-08-05 after a dotfiles commit (`ea8ba71`) tripped the style check for missing a tag. Dotfiles is a personal config repo, not Datadog engineering work, so the Jira-tag convention in [[project_git_dd_adoption]] and the global commit rules doesn't apply there.

**How to apply:** When committing to `~/dotfiles`, don't add a `[NOJIRA]` tag or treat the style check's tag warning as something to fix. Other style rules (no local-process language, no semicolons joining clauses, etc.) still apply normally; only the ticket-tag requirement is waived for this repo.

---
name: pr-creation-sop
description: "Standing SOP for finalizing a PR before review: single commit, and a description run through justins-voice, simplified, in GitHub markdown"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 1166dd41-c837-44c4-9acb-dcb6a70b794a
  modified: 2026-07-22T01:26:17.917Z
---

Two requirements the user made explicit standing SOP for every PR (SEC-34239 PR #27433 session), both applied before asking whether to request review.

**1. Single commit.** While a PR is still in draft, fold every incremental commit made during that draft phase into one commit. A PR should reach "ready for review" with exactly one commit, not a series of small fixup commits accumulated while iterating.

Mechanically: `git reset --soft <merge-base-with-main>` then one fresh commit combining the subject and the PR description body (this repo squash-merges, so the PR description becomes the final commit anyway). Force-push with `--force-with-lease`. Re-run the test suite and confirm `git status` is clean before pushing, since a partially-staged commit is how a prior mistake happened (new tests left unstaged, missing from the commit).

**2. PR description formatting.** Run the description through the `justins-voice` skill, keep it short (not verbose section-by-section prose), and write it in GitHub-flavored markdown so it renders with real structure: numbered lists for a set of changes, `code` spans for identifiers, bold only as list-item labels, not for emphasis in running text. The same simplified body becomes the squashed commit's message per point 1, so getting this right once covers both.

**Why:** This is a deliberate override of the global default (new commits over amending); it's scoped specifically to the pre-review draft phase, not a general license to rewrite history. Once a PR is out for review, don't retroactively squash reviewer-visible history without being asked. The formatting requirement exists because a first draft tends to read as verbose, headed prose (a "What/Why/Changes/Testing/Notes" wall of paragraphs) when a shorter, list-heavy, markdown-rich version communicates the same content faster for a reviewer scanning on GitHub.

**How to apply:** Before telling the user a PR is ready for review, (a) check `git log --oneline origin/main..HEAD`; squash if more than one commit, and (b) re-read the current PR body for verbosity and markdown richness, tightening it the same way before the final squash. Combine with [[feedback_pr_body_no_hard_wrap]] and [[feedback_pr_publish_requires_separate_approval]]: marking ready-for-review is still its own separate approval gate from "create this PR" and from "squash to one commit."

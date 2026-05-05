---
name: Always get approval before publishing PR descriptions
description: Never publish a PR description (even to a draft PR) without showing the user a draft first and getting explicit approval
type: feedback
originSessionId: c81bf2b9-a173-4be3-a1cb-bea71ce61e1c
---
Always show the PR title and body as a draft in the conversation and wait for explicit approval before running `gh pr create` or editing an existing PR description. This applies to draft PRs too.

**Why:** The user caught a published PR description that referenced internal PoC work no external reader would understand, and contained Claude attribution. Both slipped through because the PR was created without prior review.

**How to apply:** Write the proposed PR title and body in the conversation as a code block or quoted text. Ask the user to confirm before calling any `gh` command that publishes or updates a PR description.

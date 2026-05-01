---
name: Use gh not gt for single PRs
description: When to use gh vs gt for GitHub operations in dd-source
type: feedback
originSessionId: a78207aa-e334-41ca-9a4a-40f2208e4d25
---
Use `gh` (GitHub CLI) for all standard GitHub operations including creating PRs, pushing and reviewing. `gt` (Graphite) is only appropriate when working with stacked PRs.

**Why:** gt adds unnecessary complexity for single-branch work. gh is the correct tool for the common case.

**How to apply:** Default to `gh` for all GitHub interactions. Only reach for `gt` when explicitly working with a stacked PR chain.

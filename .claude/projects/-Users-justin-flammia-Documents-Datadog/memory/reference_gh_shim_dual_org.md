---
name: reference-gh-shim-dual-org
description: "gh-shim tool auto-switches gh auth between ddoghq and DataDog orgs, replacing manual gh auth switch chaining"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 7828ebc5-5cd9-4841-a308-95dbcd285183
  modified: 2026-08-05T22:07:50.965Z
---

`gh-shim` (Confluence: [gh-shim](https://datadoghq.atlassian.net/wiki/spaces/FF/pages/6965592110)) solves the `ddoghq`/`DataDog` dual-org `gh` auth problem directly. It detects whether a `gh` invocation is in a `ddoghq` context and swaps `GH_CONFIG_DIR` to a separate config (`~/.config/gh-shim-ddoghq`) for that call, so the correct account is always active without manual switching.

Install: authenticate in both orgs with `DataDog` as the active account, install `dogbrew`, then `dogbrew install gh-shim` and `gh-shim install` (restart shell or `eval "$(gh-shim init)"` after). Currently in beta as of 2026-07-31.

Why: previously worked around the same problem by chaining `gh auth switch --user <account> && gh ...` in a single Bash invocation, because switching in one call didn't reliably persist to the next tool call. `gh-shim` replaces that workaround once installed.

How to apply: before manually chaining `gh auth switch`, check whether `gh-shim` is installed (`which gh-shim`, or check `PATH` for the shim). If installed, just run plain `gh` commands. Fall back to the chained `gh auth switch && gh ...` pattern only if not installed.

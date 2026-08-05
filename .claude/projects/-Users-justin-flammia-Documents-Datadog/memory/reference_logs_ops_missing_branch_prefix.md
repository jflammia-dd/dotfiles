---
name: reference-logs-ops-missing-branch-prefix
description: "logs-ops clone lacks the justin.flammia/* branch-prefix refspec, so gh pr create needs explicit --head/--base"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 7828ebc5-5cd9-4841-a308-95dbcd285183
  modified: 2026-08-05T22:08:02.336Z
---

`DataDog/logs-ops` local clone's `remote.origin.fetch` only includes `+refs/heads/master:refs/remotes/origin/master`. Other repos configured via `git-dd add-branch-prefix` also fetch `justin.flammia/*` refs so `gh pr create` can resolve the local branch to a remote tracking ref automatically. Without that refspec, `gh pr create` fails with "must first push the current branch to a remote, or use the --head flag" even after a successful push.

Why: `logs-ops` was never run through the same `git-dd` branch-prefix setup as other repos.

How to apply: on a `logs-ops` PR, if `gh pr create` errors this way, pass `--head justin.flammia/<branch> --base master` explicitly rather than debugging the push. Consider running `git-dd add-branch-prefix` in that clone to fix it at the source.

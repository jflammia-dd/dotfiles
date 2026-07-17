---
name: project-git-dd-adoption
description: "git-dd adoption decisions for dd-source (scope, branch prefix strategy, enforcement hook design)"
metadata: 
  node_type: memory
  type: project
  originSessionId: 7a957bf0-c1c8-48c4-b571-75e265558a8f
---

Adopted `git dd` across all Datadog GitHub repos (not just dd-source), per the doc at https://datadoghq.atlassian.net/wiki/spaces/FF/pages/5695472050/git+dd. Confirmed 2026-07-16.

Key facts from the doc that shaped the design:
- `git dd` is a narrow set of commands (`sync`, `switch`, `sync-and-rebase`, `new-branch`, `prune`, `doctor`, `add-branch-prefix`) layered on vanilla git, not a wholesale replacement. The doc explicitly says `git dd switch` is NOT a replacement for `git switch`.
- Known anti-pattern (Known Issues page, dd-source-specific): git before 3.0 stores refs on the filesystem, so two tracked branches where one is a subpath of the other, or differ only in case, cause `cannot lock ref ... exists` collisions. Risk scales with the number of branch prefixes tracked.
- `add-branch-prefix` deletes non-matching remote refs and adds devflow safety refspecs (`fix-merge-*`, `devflow-copy-of-*`) by default; kept those on (needed for devflow-generated branch checkouts, e.g. integration branches).

Decisions:
- Branch prefix tracked: `justin.flammia` only. Coworker branches via ad hoc `git dd switch coworker/branch`, not standing prefixes, to keep ref-collision surface low.
- Devflow safety refspecs: kept on (not disabled via `git-dd.use-default-devflow-refspecs false`).
- Enforcement: hard block, not auto-rewrite or warn-only, because the git-dd mappings aren't 1:1 (e.g. `git checkout -b` can't be forced through `git dd new-branch` without breaking [[project_ers_branching|stacked-branch workflows]] since that command always branches off a freshly-synced main).
- Enforcement scope: only `git fetch`/`git pull` (→ `git dd sync`) and bare `git rebase` onto `main`/`master`/`prod` (→ `git dd sync-and-rebase`). Branch creation, interactive rebase, `--onto` rebases, and rebases onto non-default branches (stacking) are intentionally exempt.

Implementation:
- Hook: `~/.claude/hooks/git-dd-enforce.sh`, registered in `~/.claude/settings.json` under the existing `matcher: "Bash"` block (same block as `pr-draft-enforce.sh`). Global, not per-project. Deliberately NOT done via hookify, because hookify's `config_loader.py` only globs `.claude/hookify.*.local.md` relative to the process cwd, with no `~/.claude` fallback, so a hookify rule would only fire when Claude Code's cwd is a repo that has that rule file, and dd-source's `.claude/` is shared/tracked (unlike `settings.local.json`, which is gitignored there), so adding one would risk pushing a personal rule to the whole team.
- Scoping check inside the hook: matches on `origin`/`datadog` remote pointing at `github.com[:/](datadog|ddoghq)/`, not a hardcoded repo name, so it covers all Datadog repos per the adopted scope.
- `~/.claude/CLAUDE.md` Git Rules section updated with the `git dd` usage rules and the stacked-PR rebase caveat.

Onboarding already completed on this machine: `git-dd` installed via Homebrew, `git dd add-branch-prefix justin.flammia` run in `~/go/src/github.com/DataDog/dd-source` (only checkout; the linked worktree at `~/tools/siem-entity-cli` is locked/detached, not an active dev worktree so it needed no config).

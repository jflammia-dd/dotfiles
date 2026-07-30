---
name: reference-dotfiles-cron-rsync-backup
description: The dotfiles cron backup rsyncs ~/.claude into the repo before committing, so its commit messages understate what they contain
metadata:
  type: reference
---

The `dotfiles backup <date>` commits in `~/dotfiles` are produced by a cron job that
**rsyncs `~/.claude` into the repo and then commits**, roughly daily at 15:00.

**Why this matters:** the commit message says "dotfiles backup" but the commit may contain a
full session's worth of config work. During the 2026-07 migration, commit `739c0a9`, labelled
`dotfiles backup 2026-07-29 15:00`, actually carried hook deletions, `MEMORY.md` edits and 136
scratch backup files. `git log --oneline` gives no hint of that.

**How to apply:**
- Never trust a `dotfiles backup` commit message to describe its contents. Read the stat.
- Check `git status` before assuming session work is uncommitted. The cron may already have
  taken it, which is why a file edited an hour ago can show no diff.
- Any scratch or backup directory created under `~/.claude` will be committed unless
  `.gitignore` excludes it. Dated dot-prefixed patterns are now excluded
  (`.claude/.memory-backup-*/`, `.claude/.skills-drift-backup-*/`, `.claude/.hooks-deleted-*/`).
- A separate cleanup process deletes `*.bak` files under `~/.claude`, so ad-hoc `.bak` copies
  are not a durable safety net. Use git history instead.
- Note `~/.claude/settings.json` and `settings.local.json` are real files in `~/.claude`, not
  symlinks into dotfiles, so they reach the repo only via this rsync.

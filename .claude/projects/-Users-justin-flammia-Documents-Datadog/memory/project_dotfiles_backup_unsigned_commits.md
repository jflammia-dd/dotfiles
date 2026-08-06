---
name: project-dotfiles-backup-unsigned-commits
description: dotfiles repo has commit.gpgSign=false locally so the 3pm launchd backup job can commit headless
metadata: 
  node_type: memory
  type: project
  originSessionId: ddf1fb4f-a2ce-47b2-b371-bc7e37d6fe83
  modified: 2026-08-06T00:20:30.126Z
---

`~/dotfiles/.git/config` has a local `[commit] gpgSign = false`, overriding the global `commit.gpgsign = true`. Global signing and every other repo are unaffected, this is a repo-local override only.

**Why:** The `com.justin.dotfiles-backup` launchd job (`~/dotfiles/backup.sh`, daily 3pm) failed on 2026-08-05 with `Couldn't sign message (signer): communication with agent failed?` because 1Password's SSH agent needs Touch ID approval to sign and nothing is at the keyboard when launchd fires. See [[reference_1password_ssh_signing_biometric]] for the underlying signing-agent behavior. Justin chose to disable signing for this repo specifically (over a dedicated non-biometric key or dropping `git push` from the job) since dotfiles is a personal config repo already exempt from other conventions, see [[feedback_dotfiles_repo_no_jira_tag]].

**How to apply:** Commits to `~/dotfiles` (including the daily automated backup) will show as unverified on GitHub going forward. That's an accepted tradeoff, not a bug to fix. If the job fails again with a signing-related error, check whether this local override survived (e.g. a `.git/config` reset) before re-diagnosing the 1Password agent.

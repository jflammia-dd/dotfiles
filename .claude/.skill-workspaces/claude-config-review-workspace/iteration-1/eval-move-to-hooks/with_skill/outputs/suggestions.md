# Claude Config Review: Should Anything Move to Hooks or Other Tools?

**Date**: 2026-04-03
**Scope**: Global CLAUDE.md, RTK.md, settings.json, all hooks, memory

---

## Summary

The overall config is in good shape. The hook layer is well-utilized with four active hooks covering RTK token rewriting, dd-git normalization, PR draft enforcement, and writing-task detection. Most rules in CLAUDE.md correctly document behaviors that are already enforced by hooks. A few items are worth tightening.

---

## Findings

**1. REDUNDANT (minor) - Git commit / push approval text duplicates what permissions already enforce**

In CLAUDE.md, Git Rules:

> "ALWAYS get explicit approval before running any commit command or creating a PR. Never auto-submit. (`git commit` and `git push` are not in the allow list and will prompt for approval.)"

The parenthetical correctly notes this is enforced by the permissions system (neither `git commit` nor `git push` appear in `permissions.allow`). The rule is not wrong, but the text is doing double duty: the parenthetical is advisory documentation of a hook-layer behavior. This is fine as written, but the full instruction could be trimmed to one sentence since the enforcement is already guaranteed.

**Proposed change**: Shorten to "Get explicit approval before committing or creating a PR - enforced by permissions." No structural change needed.

---

**2. WELL-PLACED - PR draft enforcement**

> "PRs are hook-enforced as drafts. `pr-draft-enforce.sh` auto-injects `--draft` into every `gh pr create` command."

This is the correct pattern: the hook is the enforcement mechanism, and CLAUDE.md merely documents that the hook exists. No change needed.

---

**3. WELL-PLACED - dd-git normalization**

> "ALWAYS prefer `dd-git` over `git`. Fall back to `git` only if `dd-git` is unavailable or fails."
> "RTK handles token optimization transparently. `dd-git` commands are normalized to `git` by `dd-git-normalize.sh`..."

The instruction tells Claude which tool to prefer; the hook silently normalizes the output. Both layers are doing distinct jobs. No change needed.

---

**4. WELL-PLACED - RTK hook usage**

The RTK.md content is appropriately split: meta commands that Claude must invoke directly (`rtk gain`, `rtk discover`) are documented in RTK.md, while all other commands are handled transparently by `rtk-rewrite.sh`. The hook ordering in settings.json (dd-git-normalize first, then pr-draft-enforce, then rtk-rewrite) is correct - normalization runs before rewriting.

---

**5. WRONG LAYER (candidate) - "Always use `gh` for GitHub interactions"**

In CLAUDE.md:

> "ALWAYS use `gh` on the command line when interacting with GitHub."

This rule appears in both CLAUDE.md and in the global CLAUDE.md comment at the top of the system-reminder. It is advisory text today. There is no hook enforcing it. A PreToolUse hook on Bash could detect `curl https://api.github.com` or `curl api.github.com` patterns and block or rewrite them to `gh api` equivalents.

**Verdict**: The current pattern (text instruction) is reasonable for this rule because violations are rare and the `gh` CLI is high enough signal in Claude's training that the text rule is reliably followed. A hook would add marginal enforcement at the cost of complexity. **Keep as text, no change required.** Flag as a candidate only if violations are observed.

---

**6. WRONG LAYER - "Always rebase against parent branch before updating a PR" has no enforcement**

> "Whenever updating a PR, rebase against the parent branch first."

This is a text instruction with no hook backing. Unlike the draft-PR rule (which has pr-draft-enforce.sh), rebasing is not enforced anywhere. A PreToolUse hook could detect `gh pr create` or `git push` patterns and inject a warning or block if no rebase has occurred - but detecting "has the user rebased recently" is stateful and hard to implement reliably in a shell hook.

**Verdict**: Keep as text. A hook here would be difficult to implement correctly without false positives. The advisory nature is appropriate for a rule that requires judgment about the state of the branch.

---

**7. WRONG LAYER (actionable) - "Never use em dashes" has no enforcement**

Writing Rules:

> "NEVER use em dashes (—) in any written output, including comments, docs, messages, or prose."

This is a text instruction with no hook. A PostToolUse hook on Write/Edit tool calls could scan the written content for em dash characters (`—`, Unicode U+2014) and either block the write or inject a correction.

This is a strong hook candidate because:
- It is deterministic (em dash is a single Unicode character, unambiguous)
- It must apply with zero exceptions
- Text instructions can be forgotten mid-session, especially in long or complex conversations
- A PostToolUse hook on file writes would catch the most common violation path

**Proposed change**: Add a PostToolUse hook on Write/Edit that scans `tool_result` or `tool_input` content for `—` and outputs a warning (blocking or advisory). This upgrades a zero-exception rule from advisory to guaranteed.

---

**8. WRONG LAYER (strong candidate) - "Invoke justins-voice skill before writing content" is partially enforced**

Writing Rules:

> "ALWAYS invoke the `justins-voice` skill before drafting or editing documents, announcements or distributed written content. The hookify system handles detection; treat its trigger as a hard requirement."

The `justins-voice-detect.sh` UserPromptSubmit hook fires when writing-intent keywords are detected, injecting an `additionalContext` reminder. This is partial enforcement - it reminds Claude to invoke the skill but does not block the response from proceeding without it.

The hook's keyword exclusion list is broad: it skips prompts containing `review`, `optimize`, `debug`, `fix`, `check`, `analyze`, `suggest`, `explain`, `summarize`, `investigate`, `diagnose`, `look at`, `find`, `search`, `why`, `how`, `what`, or `show me`. A prompt like "write a summary of..." would match `write` first and inject the context, but a prompt like "can you help me revise this?" would also match `revise`.

**Verdict**: The current partial enforcement is the right architecture for this rule. A full block is not possible because the hook cannot verify whether the skill was already invoked earlier in the session. The current additionalContext injection is the correct mechanism. No structural change needed - but note the hook correctly documents "hard requirement" phrasing that aligns with CLAUDE.md's instruction.

---

**9. WELL-PLACED - Testing rules**

All five testing rules (TDD, read existing tests, cover both paths, update existing tests, no duplication) are appropriately in CLAUDE.md as advisory text. These are nuanced, judgment-based rules that cannot be mechanically enforced by hooks. The `superpowers:test-driven-development` skill reference is appropriate.

---

**10. MISSING PERMISSION - `dd-git` not in allow list**

`settings.json` does not include `Bash(dd-git:*)` or `Bash(git:*)` in `permissions.allow`. This means every `dd-git` or `git` command prompts the user for approval before the dd-git-normalize hook has a chance to rewrite it to `rtk git ...`. The RTK rewrite hook auto-allows rewrites it handles, but the initial `dd-git` or `git` commands that RTK does not rewrite (e.g., `git config`, `git log`) still require approval.

If `git` commands are frequently approved without concern, adding `Bash(git:*)` or specific safe git read commands to `permissions.allow` would reduce prompt fatigue without loosening security.

**Proposed change** (optional): Add `Bash(git log:*)`, `Bash(git diff:*)`, `Bash(git status:*)`, `Bash(git fetch:*)` to `permissions.allow` for read-only operations if approval prompts for these are frequent. Keep `git commit`, `git push`, `git reset --hard` out of the allow list.

---

## Classification Summary

| Rule | Current Layer | Status |
|------|--------------|--------|
| Always use `gh` for GitHub | Text | Well-placed |
| Prefer `dd-git` over `git` | Text + hook (dd-git-normalize.sh) | Well-placed |
| RTK token optimization | Text + hook (rtk-rewrite.sh) | Well-placed |
| PRs must be drafts | Text + hook (pr-draft-enforce.sh) | Well-placed |
| Get approval before commit/push | Text + permissions (absence from allow list) | Well-placed, minor wordsmithing opportunity |
| Rebase before PR updates | Text only | Well-placed (hook not feasible) |
| Never use em dashes | Text only | Hook candidate (PostToolUse on Write/Edit) |
| Invoke justins-voice for writing | Text + partial hook (justins-voice-detect.sh) | Well-placed for what hooks can guarantee |
| TDD and testing rules | Text only | Well-placed (judgment-based) |
| Read-only git commands | Not in allow list | Optional: add to permissions.allow to reduce fatigue |

---

## Prioritized Actions

**High value, low effort:**
1. Add a PostToolUse hook to detect em dashes in written content (item 7). This upgrades a zero-exception rule to genuine enforcement.

**Low value, optional:**
2. Add read-only git subcommands to `permissions.allow` if approval fatigue for `git log`, `git diff`, `git status` is noticeable (item 10).

**Informational, no action required:**
3. Items 1-6, 8-9 are correctly layered as-is.

# Suggestions: What Should Move from CLAUDE.md to Hooks or Other Tools

Reviewed files:
- `~/.claude/CLAUDE.md`
- `~/.claude/RTK.md`
- `~/.claude/settings.json`
- `~/.claude/hooks/*.sh` (4 hooks)
- `~/.claude/projects/-Users-justin-flammia/memory/MEMORY.md` (empty)

---

## Already Correctly Handled by Hooks

The following rules in CLAUDE.md are already backed by active hooks and are
working as intended:

| CLAUDE.md rule | Enforcing hook |
|---|---|
| Prefer `dd-git` over `git` | `dd-git-normalize.sh` (PreToolUse/Bash) |
| PRs must be created as drafts | `pr-draft-enforce.sh` (PreToolUse/Bash) |
| RTK handles token optimization transparently | `rtk-rewrite.sh` (PreToolUse/Bash) |
| Invoke `justins-voice` before writing prose | `justins-voice-detect.sh` (UserPromptSubmit) |

These rules can be trimmed in CLAUDE.md to a single sentence each
("This is hook-enforced") to reduce context overhead.

---

## Suggestions: Rules That Should Move to Hooks

### 1. "ALWAYS use `gh` on the command line when interacting with GitHub"

**Location:** CLAUDE.md (Git Rules, line 5) and CLAUDE.md header (imported from
the global CLAUDE.md preamble).

**Problem:** This is a behavioral enforcement rule stated as prose. Claude can
forget it or bypass it. A hook is more reliable.

**Suggestion:** Add a PreToolUse/Bash hook that inspects commands for GitHub
API calls made via tools other than `gh` (e.g., `curl https://api.github.com`
or `hub` commands) and either rewrites them or blocks with an explanation. The
prose rule can then become a one-liner note pointing at the hook.

---

### 2. "ALWAYS get explicit approval before running any commit command or creating a PR. Never auto-submit."

**Location:** CLAUDE.md (Git Rules, line 8).

**Problem:** This is partially enforced by the permissions allow-list (neither
`git commit` nor `git push` are in `settings.json` `allow`), but that is
implicit. The protection is real, but fragile: adding those commands to the
allow-list in the future would silently break the rule. There is no hook
actively enforcing the "ask first" policy.

**Suggestion:** Add a PreToolUse/Bash hook that matches `git commit` and
`git push` commands, and outputs a `permissionDecision: "ask"` response with a
clear reason string (`"Explicit approval required before committing or
pushing"`). This makes the policy durable regardless of the allow-list.

---

### 3. "Whenever updating a PR, rebase against the parent branch first."

**Location:** CLAUDE.md (Git Rules, line 11).

**Problem:** This is a workflow instruction with no enforcement mechanism.
Claude follows it only if it reads and remembers the rule. It fires on a
specific trigger (updating a PR) but nothing intercepts the trigger.

**Suggestion:** Add a PreToolUse/Bash hook that detects `gh pr edit` or
`git push` targeting an existing PR branch (heuristic: branch name is not
`main`/`master`/`develop`) and injects `additionalContext` reminding Claude to
rebase first. Alternatively, the `pr-draft-enforce.sh` hook could be extended
to also check for rebase freshness via `git status --short` and emit a warning
if the branch is behind its upstream.

---

### 4. TDD rule: "Use the `superpowers:test-driven-development` skill when implementing any feature or bugfix."

**Location:** CLAUDE.md (Testing Rules, line 20).

**Problem:** Skill invocation rules are exactly what the `justins-voice-detect.sh`
pattern was built for. The writing hook detects writing-intent prompts and
injects a reminder; the same pattern applies here for coding-intent prompts.
The rule currently relies on Claude reading and remembering the instruction
every session.

**Suggestion:** Add a UserPromptSubmit hook that detects implementation-intent
prompts (`implement`, `add feature`, `fix bug`, `build`, `create`, `develop`,
`write the code for`) and injects `additionalContext` reminding Claude to invoke
`superpowers:test-driven-development` first. Model this directly after
`justins-voice-detect.sh`.

---

### 5. "NEVER use em dashes in any written output"

**Location:** CLAUDE.md (Writing Rules, line 24).

**Problem:** This is a style constraint that cannot be enforced pre-generation
(Claude produces output before any PostToolUse hook sees it). However, a
PostToolUse hook on the `Write` tool (or any file-writing tool) could scan
newly written files for em dashes and emit a warning or block the write.

**Suggestion:** Add a PostToolUse hook on `Write`/`Edit` that greps the written
content for `—` (U+2014) and emits a `hookOutput` warning with the line numbers
containing em dashes. This would surface violations immediately rather than
relying on Claude's in-context recall.

---

## Suggestions: Rules That Are Fine as Prose (No Hook Needed)

These rules describe judgment-based or multi-step workflows where a hook would
be too blunt or cannot mechanically enforce the intent:

- TDD methodology details (what to test, naming conventions, coverage goals) -
  these are guidance, not triggers.
- "Rebase before PR update" - the reminder hook above (suggestion 3) is
  sufficient; full automated enforcement would require git state inspection that
  is too complex for a hook.
- RTK meta-command documentation in `RTK.md` - this is reference material, not
  a rule.

---

## Summary Table

| Rule | Current state | Recommendation |
|---|---|---|
| Use `gh` for GitHub | Prose only | Add PreToolUse hook to block/warn non-gh GitHub API calls |
| Explicit approval before commit/push | Implicit (not in allow-list) | Add PreToolUse hook with `permissionDecision: "ask"` |
| Rebase before PR update | Prose only | Add PreToolUse hook injecting rebase reminder on push/pr-edit |
| Use TDD skill for features/bugfixes | Prose only | Add UserPromptSubmit hook (mirror justins-voice-detect pattern) |
| No em dashes | Prose only | Add PostToolUse hook on Write/Edit scanning for U+2014 |
| PRs must be drafts | Hook-enforced (pr-draft-enforce.sh) | Keep as-is; trim prose to one line |
| dd-git normalization | Hook-enforced (dd-git-normalize.sh) | Keep as-is; trim prose to one line |
| RTK transparent rewrite | Hook-enforced (rtk-rewrite.sh) | Keep as-is; remove duplicative explanation from prose |
| justins-voice for writing | Hook-enforced (justins-voice-detect.sh) | Keep as-is; trim prose to one line |

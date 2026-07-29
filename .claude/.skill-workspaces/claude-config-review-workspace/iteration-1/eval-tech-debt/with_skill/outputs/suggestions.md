# Claude Config Review: Tech Debt Suggestions

**Reviewed:** 2026-04-03
**Scope:** `~/.claude/CLAUDE.md`, `~/.claude/RTK.md`, `~/.claude/settings.json`, `~/.claude/hooks/*.sh`, `~/.claude/projects/-Users-justin-flammia/memory/MEMORY.md`

---

## Findings

### 1. Dangling forward reference in RTK.md — STALE

**Issue:** RTK.md ends with "Refer to CLAUDE.md for full command reference." CLAUDE.md contains no RTK command reference. This sentence points nowhere useful and will confuse any session that reads it.

**Layer:** RTK.md content

**Proposed change:** Remove that closing line from RTK.md, or replace it with a note pointing to the RTK GitHub repo or `rtk --help`.

---

### 2. Git Rules duplicate hook-enforced behavior — WRONG LAYER (advisory redundancy)

**Issue:** Several sentences in the Git Rules section document behavior that is already 100% enforced by hooks:

- "RTK handles token optimization transparently. `dd-git` commands are normalized to `git` by `dd-git-normalize.sh`..." — enforced by `dd-git-normalize.sh`
- "PRs are hook-enforced as drafts. `pr-draft-enforce.sh` auto-injects `--draft` into every `gh pr create` command." — enforced by `pr-draft-enforce.sh`
- "ALWAYS prefer `dd-git` over `git`." — partially moot because `dd-git-normalize.sh` normalizes either direction; the rule has no behavioral effect

The skill's core principle applies here: CLAUDE.md is advisory; hooks are guarantees. Restating guaranteed behavior as text instructions adds noise without adding safety.

**Layer:** CLAUDE.md Git Rules

**Proposed change:** Collapse these to a single comment block:

```
# Hook enforcement summary (see ~/.claude/hooks/):
#   dd-git-normalize.sh  — normalizes dd-git → git for RTK
#   pr-draft-enforce.sh  — auto-injects --draft on gh pr create
#   rtk-rewrite.sh       — rewrites commands for token savings
```

Remove the prose sentences that restate what hooks already guarantee. Keep the rules about explicit approval before commit/push and rebasing before PR updates, as those are advisory (not hook-enforced).

---

### 3. `justins-voice-detect.sh` has a potential stdin bug — STALE / WRONG LAYER

**Issue:** The hook script reads the prompt with:

```bash
prompt=$(jq -r '.prompt // ""')
```

There is no `< /dev/stdin` or `cat` piping the hook input into `jq`. On most shells, `jq` with no input source will block waiting for stdin from the terminal rather than reading the hook payload. This would cause the hook to hang or silently produce an empty prompt, meaning the writing detection never fires.

If this hook is working, it may be because Claude Code pipes stdin to the process automatically — but that behavior is not documented and should not be relied upon implicitly.

**Layer:** `~/.claude/hooks/justins-voice-detect.sh`

**Proposed change:** Change the prompt extraction to:

```bash
INPUT=$(cat)
prompt=$(echo "$INPUT" | jq -r '.prompt // ""')
```

This matches the pattern used by every other hook in the suite (`dd-git-normalize.sh`, `pr-draft-enforce.sh`, `rtk-rewrite.sh`) and is unambiguously correct.

---

### 4. `justins-voice-detect.sh` skip-list excludes verbs that produce written output — WRONG LAYER

**Issue:** The hook's skip-list aggressively skips prompts containing words like `review`, `optimize`, `analyze`, `check`, `suggest`, `summarize`. Many writing tasks start with those verbs:

- "Review and rewrite this doc" — skipped
- "Optimize the wording of this announcement" — skipped
- "Suggest edits to my Confluence page" — skipped

The CLAUDE.md rule says "ALWAYS invoke `justins-voice` before drafting or editing documents, announcements or distributed written content." The hook misses a significant class of editing prompts.

**Layer:** `~/.claude/hooks/justins-voice-detect.sh`

**Proposed change:** Move the skip logic after the writing-trigger match, not before it. Only skip if the prompt matches the skip-list AND does not match the writing trigger. Alternatively, add `edit|update|improve|polish|refine` to the writing trigger pattern so editing requests still fire the hook.

---

### 5. `dd-git-normalize.sh` auto-allows all dd-git commands including destructive ones — WRONG LAYER

**Issue:** `dd-git-normalize.sh` outputs `"permissionDecision": "allow"` after rewriting `dd-git` to `git`. This means any `dd-git` command — including `dd-git push --force` or `dd-git reset --hard` — is auto-allowed without the user seeing a prompt. The intent was to normalize the command name for RTK, not to grant blanket permission.

The RTK hook (`rtk-rewrite.sh`) does not auto-allow by default; it lets Claude Code's native permission system decide unless a rewrite was found. The normalize hook should behave the same way.

**Layer:** `~/.claude/hooks/dd-git-normalize.sh`

**Proposed change:** Remove `"permissionDecision": "allow"` from the normalize hook's output. Just emit the `updatedInput` with the normalized command and let Claude Code's permission system (and then RTK's hook) decide whether to allow or prompt. This matches the safer pattern in `rtk-rewrite.sh` for exit code 3 (ask-rule path).

---

### 6. Memory file is empty — WELL-PLACED but unused

**Issue:** `~/.claude/projects/-Users-justin-flammia/memory/MEMORY.md` contains only a `# Memory Index` header with no entries. This is not a bug, but it suggests the `remember` skill (which is enabled in `settings.json`) is not being used to persist session context.

**Layer:** Memory system

**Proposed change:** No structural change needed. Consider using `/remember` at the end of productive sessions to capture active work, key decisions, or ongoing context that would otherwise be re-derived from scratch next session. This is especially useful when working across multiple long-running features or investigations.

---

### 7. CLAUDE.md rule "ALWAYS use `gh` on the command line" is duplicated — REDUNDANT

**Issue:** The rule "ALWAYS use `gh` on the command line when interacting with GitHub" appears in both CLAUDE.md and the system-reminder (global user instructions injected by the harness). It loads twice every session.

**Layer:** CLAUDE.md Git Rules

**Proposed change:** Remove the duplicate from CLAUDE.md (it is already covered by the injected global instructions). If the intent is belt-and-suspenders, at minimum annotate it as a reminder rather than a rule: `# gh is always preferred over GitHub web — already enforced globally`.

---

### 8. RTK.md "Hook-Based Usage" section understates what the hook actually does — STALE

**Issue:** RTK.md says: "All other commands are automatically rewritten by the Claude Code hook. Example: `git status` → `rtk git status` (transparent, 0 tokens overhead)."

The hook (`rtk-rewrite.sh`) is version 3 and uses `rtk rewrite` with a full exit-code protocol including deny rules, ask rules, and auto-allow. The description in RTK.md is accurate for the happy path but does not mention that some commands can trigger an "ask" confirmation, or that the hook requires `rtk >= 0.23.0`. A reader troubleshooting unexpected prompts would not find the answer in RTK.md.

**Layer:** RTK.md

**Proposed change:** Add a short note: "Some commands trigger an ask-rule and will prompt for confirmation rather than auto-rewriting. This is intentional. Requires `rtk >= 0.23.0`." This prevents confusion when the hook asks instead of silently rewriting.

---

## Summary

| # | Item | Classification | Action |
|---|------|---------------|--------|
| 1 | Dangling "Refer to CLAUDE.md" in RTK.md | Stale | Remove or fix the reference |
| 2 | Git Rules re-state hook-enforced behavior | Redundant / Wrong layer | Collapse to a comment block |
| 3 | `justins-voice-detect.sh` stdin pattern | Wrong layer (potential bug) | Add `INPUT=$(cat)` pattern |
| 4 | `justins-voice-detect.sh` skip-list too broad | Wrong layer | Fix skip-list ordering |
| 5 | `dd-git-normalize.sh` auto-allows destructive commands | Wrong layer | Remove `permissionDecision: allow` |
| 6 | Memory file empty | Well-placed but unused | Use `/remember` more actively |
| 7 | `gh` rule duplicated from global instructions | Redundant | Remove from CLAUDE.md |
| 8 | RTK.md hook description understates ask-rule behavior | Stale | Add a clarifying note |

---

Want me to apply all of these, or go through them one at a time?

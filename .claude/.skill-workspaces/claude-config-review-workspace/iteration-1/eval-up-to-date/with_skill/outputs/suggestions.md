# Claude Config Review: Staleness Audit

**Date reviewed**: 2026-04-03
**Files reviewed**:
- `~/.claude/CLAUDE.md`
- `~/.claude/RTK.md`
- `~/.claude/settings.json`
- `~/.claude/hooks/dd-git-normalize.sh`
- `~/.claude/hooks/pr-draft-enforce.sh`
- `~/.claude/hooks/rtk-rewrite.sh`
- `~/.claude/hooks/justins-voice-detect.sh`
- `~/.claude/projects/-Users-justin-flammia/memory/MEMORY.md`

---

## Summary

The config is largely in good shape. The hook layer is well-structured with correct ordering. Two issues are worth addressing: one stale claim in RTK.md, and one stale/misleading line in CLAUDE.md about `dd-git`.

---

## Findings

### 1. STALE -- `dd-git` is not installed but CLAUDE.md still mandates it

**File**: `~/.claude/CLAUDE.md` (Git Rules section)

**Issue**: The rule says "ALWAYS prefer `dd-git` over `git`" and treats `dd-git` as the primary tool. But `dd-git` is not installed on this machine (`which dd-git` returns nothing). This means the rule cannot be followed as written. Any session where Claude follows it literally will immediately fall back anyway, making the preference instruction misleading noise.

The `dd-git-normalize.sh` hook is also wired but will never fire because no command will ever contain `dd-git` if the tool isn't present.

**Classification**: Stale

**Proposed change**: Either remove the `dd-git` preference entirely (since it's unavailable), or add a conditional note:

> ALWAYS prefer `dd-git` over `git` when available. If `dd-git` is not installed, use `git` directly. The `dd-git-normalize.sh` hook handles normalization transparently when `dd-git` is present.

If `dd-git` is a Datadog-internal tool only relevant in specific repos, consider moving this note to a project-level `CLAUDE.md` instead of the global one.

---

### 2. STALE -- RTK.md says "Refer to CLAUDE.md for full command reference" but no such reference exists

**File**: `~/.claude/RTK.md` (Hook-Based Usage section)

**Issue**: The last line reads "Refer to CLAUDE.md for full command reference." There is no RTK command reference section in `CLAUDE.md`. The only RTK mention in `CLAUDE.md` is one sentence about transparent normalization. The RTK.md file itself already contains the complete meta-command reference. The cross-reference is a dead end that sends readers in a circle.

**Classification**: Stale

**Proposed change**: Remove or replace that closing line. Options:

- Remove it entirely (RTK.md is self-contained).
- Replace with: "RTK operates transparently via hooks -- no additional commands needed for normal use."

---

### 3. WELL-PLACED -- Hook ordering is correct

`settings.json` runs hooks in order: `dd-git-normalize.sh` → `pr-draft-enforce.sh` → `rtk-rewrite.sh`. Normalization runs before the RTK rewrite, which is the required ordering. No change needed.

---

### 4. WELL-PLACED -- Commit/push approval enforced at the right layer

The rule "get explicit approval before running any commit command" is correctly implemented: `git commit` and `git push` are absent from `permissions.allow`, so Claude Code will prompt for approval. The text in CLAUDE.md is accurate and the enforcement matches.

---

### 5. WELL-PLACED -- PR draft enforcement is hook-backed

`pr-draft-enforce.sh` auto-injects `--draft` into every `gh pr create` call. The CLAUDE.md note accurately describes this as hook-enforced. No change needed.

---

### 6. WELL-PLACED -- `justins-voice` detection is hook-backed

`justins-voice-detect.sh` fires on `UserPromptSubmit` and injects a context reminder for writing tasks. The CLAUDE.md rule acknowledges this ("the hookify system handles detection; treat its trigger as a hard requirement"). Accurately described.

---

### 7. WELL-PLACED -- RTK version is current

RTK is installed at `0.34.3`. The hook's version guard requires `>= 0.23.0`, which is satisfied with significant headroom. No staleness here.

---

### 8. WELL-PLACED -- Memory file is empty (intentionally sparse)

`~/.claude/projects/-Users-justin-flammia/memory/MEMORY.md` contains only a `# Memory Index` header with no entries. This is correct -- global rules belong in `CLAUDE.md`, not memory. No duplication or misplacement.

---

### 9. INFORMATIONAL -- RTK.md cross-references itself redundantly

**File**: `~/.claude/RTK.md`

The "Hook-Based Usage" section says "All other commands are automatically rewritten by the Claude Code hook." This is accurate, but there are no other commands documented beyond the meta-commands above it. The section is a stub that adds no information. Low priority, but could be removed to tighten the file.

**Classification**: Minor -- not stale, but vestigial

---

## Recommended Actions (priority order)

1. **Fix CLAUDE.md**: Update or remove the `dd-git` preference rule since `dd-git` is not installed. If it is only relevant in the Datadog monorepo, move it to that project's `CLAUDE.md`.
2. **Fix RTK.md**: Remove or replace the dead "Refer to CLAUDE.md for full command reference" line.
3. **Optional**: Remove the stub "Hook-Based Usage" paragraph in RTK.md if it adds no value.

---

Want me to apply all of these, or go through them one at a time?

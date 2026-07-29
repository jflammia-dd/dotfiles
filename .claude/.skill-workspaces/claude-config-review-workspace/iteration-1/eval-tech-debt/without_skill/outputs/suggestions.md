# Claude Config Review: Optimization Suggestions

_Reviewed: 2026-04-03_

Files reviewed:
- `~/.claude/CLAUDE.md`
- `~/.claude/RTK.md`
- `~/.claude/settings.json`
- `~/.claude/hooks/rtk-rewrite.sh`
- `~/.claude/hooks/dd-git-normalize.sh`
- `~/.claude/hooks/justins-voice-detect.sh`
- `~/.claude/hooks/pr-draft-enforce.sh`
- `~/.claude/projects/-Users-justin-flammia/memory/MEMORY.md`

---

## Summary

The global config is well-structured and hook-enforced for critical workflows. No malware or obvious security issues found. Tech debt is mostly friction from:
1. Duplication between CLAUDE.md prose rules and hook enforcement
2. Stale or vague skill references that will rot as the skill list evolves
3. Missing rules that could be enforced by hooks but currently rely on prose
4. Settings.json maintenance issues as the plugin list grows

---

## Suggestions

### 1. CLAUDE.md: Remove prose rules already enforced by hooks

**Files affected:** `CLAUDE.md`, hooks

Three rules in CLAUDE.md are already enforced mechanically by hooks in `settings.json`:

| Rule | Enforced by |
|---|---|
| "PRs are hook-enforced as drafts" | `pr-draft-enforce.sh` |
| "`dd-git` commands are normalized to `git` by `dd-git-normalize.sh`" | `dd-git-normalize.sh` |
| "RTK handles token optimization transparently" | `rtk-rewrite.sh` |

These prose statements still have value as documentation for the model ("why is this happening"), but they can be tightened. Instead of describing the mechanism in detail, consolidate into a single line like:

> Hook enforcement is active for: draft PRs (`pr-draft-enforce.sh`), dd-git normalization (`dd-git-normalize.sh`), and RTK token optimization (`rtk-rewrite.sh`). These are automatic; no manual action needed.

This removes 4+ lines of redundant prose while keeping the "why" visible.

---

### 2. CLAUDE.md: The `superpowers:test-driven-development` skill reference may drift

**File:** `CLAUDE.md` line 20

```
- Use the `superpowers:test-driven-development` skill when implementing any feature or bugfix.
```

Skill names in CLAUDE.md that hard-code a path (`namespace:skill-name`) become stale when plugins or skills are renamed, replaced, or superseded. The skill list already shows `superpowers:test-driven-development` exists today, but this reference has no fallback and no verification step.

**Suggestion:** Reference skills by behavior rather than exact name, or add a comment noting the plugin source:

> Use the TDD skill (`superpowers:test-driven-development` from `claude-plugins-official`) when implementing features or bugfixes.

This makes it easier to update when the skill is renamed or moved.

---

### 3. CLAUDE.md: `justins-voice` skill enforcement is split and partially redundant

**File:** `CLAUDE.md` line 25-26, `hooks/justins-voice-detect.sh`, `settings.json`

The rule says:
> "The hookify system handles detection; treat its trigger as a hard requirement."

But the actual detection is in `justins-voice-detect.sh` (not hookify -- it is a manually written hook). The prose claim that "hookify system handles detection" is inaccurate -- hookify is a plugin for creating hooks, not the hook itself. This creates potential confusion.

Additionally, the hook fires on `UserPromptSubmit` but the CLAUDE.md rule says to invoke the skill "before drafting or editing documents." This is slightly inconsistent framing.

**Suggestions:**
- Correct the CLAUDE.md language: say "A PreToolUse hook detects writing tasks automatically" rather than attributing it to "the hookify system."
- Alternatively, if hookify was used to create the rule and manages the hook lifecycle, document that more precisely.

---

### 4. CLAUDE.md: No rule governing memory usage

**File:** `CLAUDE.md`, `MEMORY.md` (empty)

`MEMORY.md` is empty. There is no guidance in CLAUDE.md about when to write to memory, what format to use, or when to retrieve it. As Claude Code's `remember` plugin (`remember@claude-plugins-official`) is enabled in settings.json and the `remember:remember` skill is available, this is a missed opportunity.

**Suggestion:** Add a short rule to CLAUDE.md:

> Use the `remember:remember` skill to persist cross-session context (decisions, constraints, project state). Retrieve memory at the start of long-running tasks.

---

### 5. CLAUDE.md: No rule for when to use `codex-delegate` vs direct implementation

**File:** `CLAUDE.md`, `settings.json`

`codex@openai-codex` is enabled and `codex-delegate` is in the allowed Bash commands. However, there is no guidance in CLAUDE.md about when to delegate to Codex versus implementing directly. This will lead to inconsistent delegation decisions.

**Suggestion:** Add a delegation heuristic, e.g.:

> Use `codex-delegate` for parallelizable subtasks (code generation, search, transforms) where a second-agent pass improves coverage. Do not delegate for tasks requiring interactive approval or access to local state.

---

### 6. RTK.md: "Refer to CLAUDE.md for full command reference" points nowhere

**File:** `RTK.md` line 29

```
Refer to CLAUDE.md for full command reference.
```

CLAUDE.md contains no RTK command reference. This dangling reference is confusing -- either the content was removed or it was never added.

**Suggestion:** Either remove the line, or add a brief command reference table to CLAUDE.md under a `## RTK` section.

---

### 7. settings.json: `npx -y ccstatusline@latest` runs on every prompt -- latency risk

**File:** `settings.json` lines 42-47, 50-53

`npx -y ccstatusline@latest --hook` fires on both `PreToolUse` (Skill matcher) and every `UserPromptSubmit`. This means every prompt resolves an npm package from the network. If the npm registry is slow or unavailable, all prompts will stall.

**Suggestion:** Pin to a specific version instead of `@latest` to eliminate network resolution on every call:

```json
"command": "npx -y ccstatusline@1.2.3 --hook"
```

Check the current version with `npm info ccstatusline version` and pin it. Update periodically rather than auto-resolving every time.

---

### 8. settings.json: `statusLine` also runs `npx -y ccstatusline@latest` on every render

**File:** `settings.json` lines 68-72

Same issue as #7. The status line command re-fetches `@latest` on every status refresh.

```json
"statusLine": {
  "type": "command",
  "command": "npx -y ccstatusline@latest",
  "padding": 0
}
```

**Suggestion:** Pin the version here too, consistent with the hook.

---

### 9. settings.json: Large plugin list with no documented policy for additions/removals

**File:** `settings.json` `enabledPlugins` (lines 73-194)

The enabled plugin list has grown to 100+ entries. Several are explicitly set to `false` (disabled) -- `explanatory-output-style`, `inner-dev-loop-guild`, `squire`, `terraform`. There is no documented rationale for what is enabled vs disabled, and no cleanup policy.

**Suggestions:**
- Add a comment block above `enabledPlugins` (or a companion doc) explaining the enable/disable rationale for `false` entries so future-you knows whether they should stay disabled or were temporarily turned off.
- Consider using `claude-md-management:revise-claude-md` or `suggest-extensions:analyze-local` periodically to audit which plugins are actually used.

---

### 10. hooks/justins-voice-detect.sh: Missing `jq` dependency, reads raw `$prompt` from stdin incorrectly

**File:** `hooks/justins-voice-detect.sh` lines 5-22

The hook reads `prompt` as:
```bash
prompt=$(jq -r '.prompt // ""')
```

But it reads from stdin without capturing the full input first (`INPUT=$(cat)`). For hooks where multiple fields exist, reading stdin twice can silently produce empty output. Other hooks in this repo use the safer pattern:
```bash
INPUT=$(cat)
CMD=$(echo "$INPUT" | jq -r '.field // empty')
```

This hook also lacks the `jq` availability check that every other hook includes (`if ! command -v jq &>/dev/null; then exit 0; fi`).

**Suggestions:**
- Add a `jq` guard at the top (matching the pattern in the other 3 hooks).
- Capture stdin before parsing: `INPUT=$(cat); prompt=$(echo "$INPUT" | jq -r '.prompt // ""')`.

---

### 11. CLAUDE.md: Git Rules section mixes policy with implementation details

**File:** `CLAUDE.md` lines 3-11

The Git Rules section contains:
- Policy rules (user-facing behavior: "always get approval before commit")
- Implementation notes ("RTK handles token optimization transparently", "dd-git-normalize.sh" details)

Implementation notes are useful for debugging but add noise to the model's working context and will drift from reality as hooks evolve.

**Suggestion:** Move implementation notes to RTK.md or a `~/.claude/HOOKS.md` reference doc, keeping CLAUDE.md focused on behavioral policy. This reduces the context load for every conversation.

---

### 12. No session-start skill or context bootstrap rule

**File:** `CLAUDE.md`

The skill list includes `superpowers:using-superpowers` with the description "Use when starting any conversation - establishes how to find and use skills." There is no rule in CLAUDE.md that invokes this at session start, meaning its value is only realized when the user explicitly asks.

**Suggestion:** Consider adding a session-start rule:

> At the start of any complex multi-step task, invoke `superpowers:using-superpowers` to establish context for skill discovery.

Or, if this has been intentionally omitted to avoid overhead on short queries, document that decision so it is not revisited repeatedly.

---

## Low-Priority / Nice-to-Have

- **RTK.md**: The `⚠️ Name collision` warning about `reachingforthejack/rtk` is useful during initial setup but adds noise to every session. Consider moving it to a separate `~/.claude/SETUP-NOTES.md` and removing it from the always-injected RTK.md context.
- **MEMORY.md**: Currently empty. If the `remember` plugin is in use, audit whether memories are actually being written. If not, the plugin may not be configured or may need an explicit invocation rule (see suggestion #4).
- **settings.json**: The `confluence-api` plugin has a hardcoded scripts path in the allow list (`~/.claude/plugins/marketplaces/datadog-claude-plugins/confluence-api/scripts/**`). If the plugin moves or updates, this path silently breaks. Consider whether the plugin itself should manage this permission entry.

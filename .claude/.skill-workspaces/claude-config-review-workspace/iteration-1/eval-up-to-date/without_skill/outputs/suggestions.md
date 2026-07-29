# Global Claude Config Staleness Review

**Date assessed:** 2026-04-03

## Summary

The configuration is largely healthy and internally consistent. The hooks match the rules documented in CLAUDE.md, the RTK machinery is coherent, and the settings.json reflects the hook pipeline correctly. A handful of items are worth revisiting.

---

## CLAUDE.md

**File:** `~/.claude/CLAUDE.md`

### Potentially stale or inconsistent

1. **Duplicate GitHub rule.** The file opens with `@RTK.md` (which imports RTK.md) and then the Git Rules section begins with "ALWAYS use `gh` on the command line when interacting with GitHub." That rule is also stated verbatim inside CLAUDE.md itself (line 5). The same rule appears in both files, creating redundancy that can drift if one is updated without the other.

2. **`superpowers:test-driven-development` skill reference in Testing Rules.** The rule says "Use the `superpowers:test-driven-development` skill when implementing any feature or bugfix." The system prompt confirms that skill exists and is available. This is fine as-is, but verify the skill is still the right one — the superpowers suite has been reorganized (e.g., `superpowers:executing-plans` replaced `superpowers:execute-plan`). Confirm TDD guidance has not been folded into a different skill.

3. **`hookify` system reference in Writing Rules.** The rule says "The hookify system handles detection; treat its trigger as a hard requirement." This is backed by `justins-voice-detect.sh` (a `UserPromptSubmit` hook), which is accurate. However, the hook only fires on a narrow set of verbs (`write`, `draft`, `edit`, `revise`, `compose`, `rewrite`, `announce`, `announcement`) and specific doc-type keywords. If `justins-voice` coverage has expanded or the trigger list has changed, the CLAUDE.md rule and hook may have drifted. Worth spot-checking that the hook list matches current usage patterns.

---

## RTK.md

**File:** `~/.claude/RTK.md`

### Potentially stale

4. **"Refer to CLAUDE.md for full command reference."** The final line of RTK.md says "Refer to CLAUDE.md for full command reference." However, CLAUDE.md does not contain a RTK command reference -- the RTK commands are documented in RTK.md itself. This line appears to be vestigial from an earlier layout where the two files were merged or structured differently. It is mildly misleading.

5. **Version reference is unversioned.** The installation verification block says `rtk --version  # Should show: rtk X.Y.Z` with a literal placeholder. If there is a minimum supported version, this should state it explicitly (the hook already enforces `>= 0.23.0` at runtime). Aligning the doc to reflect the actual minimum would reduce ambiguity.

---

## settings.json

**File:** `~/.claude/settings.json`

### Potentially stale

6. **`"model": "sonnet[1m]"`** The configured model ID is `sonnet[1m]`. The current running model (per system context) is `claude-sonnet-4-6[1m]`. If `sonnet[1m]` still resolves correctly as an alias this is fine, but it is worth confirming the alias is still recognized rather than silently falling back to a different version.

7. **`"pup": true`** There is one plugin entry without a namespace: `"pup": true`. All other plugins use the `name@marketplace` convention. This may be intentional (a local or custom plugin), but if it was once a real marketplace plugin it could be stale and failing silently.

8. **Disabled plugins may be intentional, but worth auditing:**
   - `"explanatory-output-style@claude-plugins-official": false`
   - `"inner-dev-loop-guild@datadog-claude-plugins": false`
   - `"squire@datadog-claude-plugins": false`
   - `"terraform@claude-plugins-official": false`

   Disabled entries accumulate over time. If any were disabled temporarily (e.g., during testing), they may be safe to re-enable or remove.

9. **`codex@openai-codex` plugin + allow-list entry for `codex exec`** are present and consistent with each other. No staleness detected here.

---

## Hooks

**Directory:** `~/.claude/hooks/`

All four hook files are present and referenced correctly in `settings.json`. The hook pipeline order (dd-git-normalize → pr-draft-enforce → rtk-rewrite) matches the documentation in CLAUDE.md. No staleness detected in the hook implementations themselves.

### Minor observations

10. **`justins-voice-detect.sh` reads from stdin without capturing the full input blob.** The hook runs `jq -r '.prompt // ""'` but does not assign `$(cat)` to a variable first the way the other hooks do. This means the prompt is read once from stdin and if jq fails for any reason there is no fallback. This is a latent fragility rather than staleness, but worth noting.

---

## MEMORY.md

**File:** `~/.claude/projects/-Users-justin-flammia/memory/MEMORY.md`

The file contains only a `# Memory Index` header with no entries. This is either intentionally empty (memory was cleared or never populated for this project scope) or stale in the sense that session learnings that should have been recorded here were not. No action required unless you expected persisted memory to be here.

---

## Overall Verdict

| Area | Status |
|---|---|
| CLAUDE.md Git Rules | Minor redundancy with RTK.md; otherwise current |
| CLAUDE.md Testing Rules | Current, but verify `superpowers:test-driven-development` is still the right skill name |
| CLAUDE.md Writing Rules | Current; verify `justins-voice-detect.sh` trigger keywords match your usage |
| RTK.md | One stale/misleading cross-reference; version placeholder could be more specific |
| settings.json model | Unversioned alias -- confirm `sonnet[1m]` resolves to the intended model |
| settings.json plugins | `"pup"` entry lacks namespace; 4 disabled plugins worth auditing |
| Hooks | All 4 hooks are present, wired correctly, and functional |
| MEMORY.md | Empty; may be intentional |

No critical failures found. The highest-priority items are (6) confirming the model alias is current and (4) cleaning up the stale cross-reference in RTK.md.

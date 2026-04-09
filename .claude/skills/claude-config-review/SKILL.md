---
name: claude-config-review
description: Reviews global CLAUDE.md and memory files for optimization opportunities, tech debt, and misplaced rules. Researches current Claude Code best practices, identifies rules better enforced by hooks or permissions vs text instructions, flags stale or redundant content, and presents numbered suggestions for approval before applying any changes. Use proactively when the user asks to review, audit, optimize, clean up, elevate, improve, or check for tech debt in their Claude config, CLAUDE.md, global rules, or memory files. Also triggers on phrases like "make sure my Claude files are optimized", "elevate my Claude configuration", "are my Claude rules up to date", "clean up my global Claude setup", "is my CLAUDE.md good", or any request to review, improve or modernize Claude Code configuration. Also use when the user asks whether rules should be moved to hooks, skills, sub-files, or settings.json.
---

## What this skill does

Claude Code configuration accumulates tech debt over time. Rules get stale when the tooling they describe changes. Text instructions get added for things that hooks or permissions would enforce more reliably. Memories duplicate content already in CLAUDE.md. This skill surfaces those problems and suggests concrete fixes.

The core principle from Claude Code best practices: **CLAUDE.md is advisory, hooks are guarantees**. A rule that must happen with zero exceptions belongs in a hook or permission, not a text instruction.

## Step 1: Read the current state

Read all of these in parallel:

- `~/.claude/CLAUDE.md` and any `@`-referenced sub-files (e.g. `RTK.md`)
- `~/.claude/projects/<current-project>/memory/MEMORY.md` and all memory files it indexes
- `~/.claude/settings.json` — focus on `permissions.allow`, `permissions.deny` and `hooks`
- Every hook script referenced in `settings.json` hooks (read the actual `.sh` files)

## Step 2: Research current best practices

Use the `claude-code-guide` agent to answer: given the specific rules in this CLAUDE.md, which belong in hooks, which belong in `settings.json` permissions, and which are correctly placed as text? Ask about any tools or integrations mentioned (RTK, dd-git, etc.) to check whether tooling has changed since the rules were written.

Research in parallel with Step 3 if possible.

## Step 3: Categorize findings

For each rule or block in CLAUDE.md and each memory file, classify it as one of:

- **Stale** — describes a tool, version, or behavior that has changed or no longer exists
- **Redundant** — duplicates something already enforced by a hook, permission, or another rule
- **Wrong layer** — would be more reliably enforced as a PreToolUse/PostToolUse hook or a `permissions.deny` rule rather than text
- **Memory in CLAUDE.md** — content that belongs in memory files, or vice versa (memory files should not duplicate CLAUDE.md rules that load every session)
- **Well-placed** — correct as-is

The memory system guideline: do not store in memory what can be derived from reading the current project state. CLAUDE.md rules load every session and don't need memory reinforcement.

## Step 4: Present findings

Always present findings as a numbered list, even if there are only one or two items. For each item include:

1. What the issue is
2. Which layer it should move to (if applicable)
3. The specific change proposed

Use these categories as headers to group findings: **Bugs**, **Wrong layer**, **Stale**, **Redundant**, **Well-placed**. Always include a "Well-placed" group for things that are correct, so the review feels complete rather than only negative.

Be direct. If everything looks good, say so rather than inventing problems.

Do not apply any changes without explicit approval. End with: "Want me to apply all of these, or go through them one at a time?"

## Step 5: Adversarial review (optional)

After presenting findings, offer to run a Codex adversarial pass:

> "Want me to send this to Codex for an adversarial review? It will read the same files independently and try to challenge my findings and find anything I missed."

If the user agrees, use the `codex:codex-rescue` subagent with this prompt structure:

```
Adversarial review of a Claude Code configuration.

A Claude session reviewed these files and produced the following findings:
<paste the numbered findings list from Step 4>

Your job:
1. Challenge each finding. Is it actually correct? Are any false positives?
2. Find anything significant the review missed.
3. Flag any disagreements with the conclusions.

Files to review (read them yourself):
- ~/.claude/CLAUDE.md
- ~/.claude/RTK.md
- ~/.claude/settings.json
- ~/.claude/hooks/ (all .sh files)
- ~/.claude/projects/-Users-justin-flammia/memory/MEMORY.md

Be direct. If the original review was thorough and correct, say so.
```

Run the subagent in the foreground (`--wait`) so you can present its output inline.

After both reviews are complete, highlight where Codex agreed, where it disagreed, and any net-new findings it surfaced. Do not auto-apply Codex findings. Surface them as additional input for the user to weigh alongside Claude's own findings.

**Why `codex:rescue` and not `second-opinion`**: `second-opinion` is designed for git diffs of code files and explicitly excludes config review. `codex:rescue` runs an arbitrary task and is the right layer for this use case.

## Step 6: Apply approved changes

Apply only what the user approves. For hook changes:
- Write new hook scripts to `~/.claude/hooks/`
- Register them in `settings.json` `hooks` block in the correct position (hooks run in order)
- Make scripts executable with `chmod +x`
- Test each new hook by simulating its expected input before finishing

After applying, simplify any CLAUDE.md text rules that are now enforced at the hook layer — the text can note that enforcement is handled by the hook, but doesn't need to repeat the rule in full.

## Key patterns to look for

**Hook candidates** (deterministic, zero-exception rules):
- "Always create PRs as draft" → PreToolUse hook auto-injecting `--draft`
- "Never commit without approval" → PreToolUse hook or ensure command not in `permissions.allow`
- "Always use X tool instead of Y" → PreToolUse hook normalizing Y to X (like dd-git-normalize.sh)

**Permission candidates**:
- Hard blocks on dangerous commands → `permissions.deny`
- Frequently-run safe commands → `permissions.allow` to reduce prompt fatigue

**Sub-file candidates** (`@`-referenced from CLAUDE.md):
- Tool-specific docs that are long or frequently updated (like RTK.md) — keep CLAUDE.md short, pull detail into sub-files

**Memory candidates**:
- Project-specific context that changes (active work, decisions, who owns what)
- NOT: rules that apply every session — those belong in CLAUDE.md

## Hook ordering note

In `settings.json`, hooks under the same matcher run in sequence. Normalization hooks (like `dd-git-normalize.sh`) must run before rewrite hooks (like `rtk-rewrite.sh`) so downstream hooks see the normalized command. Keep this ordering in mind when registering new hooks.

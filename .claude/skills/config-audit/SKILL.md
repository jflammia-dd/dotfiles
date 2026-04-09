---
name: config-audit
description: >
  Periodic audit of Claude Code configuration to detect and fix drift. Use when you want to
  review CLAUDE.md, hooks, settings.json and memory files. Catches bugs in hook scripts,
  rules in the wrong enforcement layer, stale content and memory entries that duplicate CLAUDE.md.
  Run every few months or after a burst of config changes to keep the setup clean and efficient.
  Triggers on: "audit my config", "check my Claude setup", "review my hooks", "is my setup
  optimized", "review my Claude settings", "clean up my configuration", "config drift",
  "config health check", "review my settings.json".
---

# Claude Code Configuration Audit

Configuration accumulates debt over time: rules get stale, hooks develop edge-case bugs, memory
files start duplicating CLAUDE.md and new best practices emerge. This skill runs a full audit
and surfaces concrete fixes.

**Core principle:** CLAUDE.md guides behavior but does not enforce it. Hooks enforce behavior
regardless of whether Claude remembers the instruction. A rule that must hold with zero exceptions
belongs in a hook or permission, not in text.

---

## Step 1: Read the current state

Read all of these in parallel:

- `~/.claude/CLAUDE.md` and any `@`-referenced sub-files (e.g. RTK.md)
- `~/.claude/settings.json` (focus on `permissions.allow`, `permissions.deny`, and `hooks`)
- Every hook script referenced in `settings.json` (read the actual `.sh` files)
- The project memory index: `~/.claude/projects/<current-project>/memory/MEMORY.md` and all
  memory files it links to

---

## Step 2: Research current best practices

Use the `claude-code-guide` subagent to answer questions specific to what you found. Good
questions to ask based on common drift patterns:

- For any tool mentioned in CLAUDE.md rules: has the tool's interface changed in a way that
  makes the rule stale or misleading?
- For rules that look like zero-exception requirements: is there a hook type or
  `permissions.deny` entry that would enforce this more reliably than text?
- For `permissions.allow` entries: are these still meaningful given the current `defaultMode`
  setting? (Note: `allow` and `defaultMode` operate at different layers. Allow entries are
  not made redundant by `defaultMode: "auto"` but still worth auditing for entries that
  are no longer needed.)

Run this research in parallel with reading the files if possible.

---

## Step 3: Audit hook scripts for correctness

For each hook script, check:

**Logic bugs:**
- Does the tool-name matching cover all cases it should? If a hook handles `Write` and `Edit`
  but not `MultiEdit` (which shares the same tool_input structure), that's a gap.
- Does the hook correctly skip non-prose file types? Code extensions (.go, .py, .sh, .ts, etc.)
  often shouldn't be scanned for writing-style violations.
- Does the hook handle the case where `jq` or other dependencies are unavailable gracefully
  (exit 0 rather than error)?

**Ordering issues (PreToolUse hooks run in sequence):**
- Normalization hooks must run before rewrite hooks. If a hook normalizes command names
  (e.g., `dd-git` to `git`), it must appear before hooks that pattern-match on those commands.

**Coverage gaps:**
- PostToolUse hooks on Write/Edit/MultiEdit catch file-write violations but cannot catch
  violations in Claude's conversational output. Text rules in CLAUDE.md are still needed
  for prose responses. This is a known limitation, not a bug.

---

## Step 4: Audit CLAUDE.md for layer and clarity

For each rule in CLAUDE.md, classify it:

**Correct as text (advisory):**
- Rules that require conversational context or judgment (e.g., "get approval before committing")
- Rules that describe context and conventions rather than enforcing behavior
- Rules that explain why a hook or permission exists (keep these; they provide useful context)

**Should move to hook (zero-exception enforcement):**
- Rules that must always happen without exception and can be enforced mechanically
  (e.g., "always inject --draft", "never add Co-Authored-By")
- Check whether a hook already enforces it. If so, the CLAUDE.md text should acknowledge
  the hook rather than re-state the rule as an instruction.

**Should move to `permissions.deny` (hard block):**
- Rules that hard-block specific dangerous commands (force push, --no-verify, etc.)

**Stale or misleading:**
- Rules that describe a behavior that a hook immediately undoes (creating false cognitive load)
- Rules that reference tools, versions, or workflows that have changed
- Instructions whose effect is already achieved elsewhere, making the instruction misleading

---

## Step 5: Audit memory files

The guiding rule from CLAUDE.md itself: **do not write memories for rules already in CLAUDE.md**.

Memory files should hold:
- Project state and context (active work, decisions, who owns what)
- Discovered behavioral quirks (tool edge cases, API gotchas)
- User preferences discovered mid-session that are NOT already in CLAUDE.md
- Technical context that would be expensive to re-derive (schemas, data flow details)

Flag any memory entry that:
- Restates a rule already in CLAUDE.md (creates a redundant second source of truth)
- Describes a skill-level attribute (e.g., "new to Go") that may have gone stale
- References project state that has clearly changed (old RFCs, completed work, deprecated tracks)

---

## Step 6: Present findings

Group findings under these headers:

- **Bugs**: hook logic errors, coverage gaps, incorrect behavior
- **Wrong layer**: rules that belong in hooks/permissions instead of (or in addition to) text
- **Stale**: outdated content, misleading instructions, outdated context
- **Redundant**: memory entries that duplicate CLAUDE.md, allow entries that no longer add value
- **Well-placed**: correct as-is (always include this group so the review feels complete)

For each finding, state:
1. What the issue is
2. Which layer it should move to (if applicable)
3. The specific change proposed

End with: "Want me to apply all of these, or go through them one at a time?"

---

## Step 7: Apply approved changes

Apply only what the user approves. For hook changes:

1. Write updated hook scripts to `~/.claude/hooks/`
2. Register new hooks in `settings.json` in the correct position. Normalization hooks must
   come before rewrite hooks.
3. Make new scripts executable: `chmod +x <script>`
4. After adding hooks, verify the JSON in `settings.json` is valid

After applying, simplify any CLAUDE.md text rules that are now enforced at the hook layer.
The text can note that enforcement is handled by the hook, but doesn't need to re-state the
rule as an imperative instruction.

---

## Step 8: Adversarial Codex review (optional)

After presenting findings, offer:

> "Want me to send this to Codex for an adversarial review? It will read the same files
> independently and try to challenge my findings and find anything I missed."

If the user agrees, use the `codex:rescue` subagent with this prompt:

```
Adversarial review of a Claude Code configuration.

A Claude session reviewed these files and produced the following findings:
<paste the numbered findings list>

Your job:
1. Challenge each finding. Is it actually correct? Any false positives?
2. Find anything significant the review missed.
3. Flag any disagreements with the conclusions.

Files to review (read them yourself):
- ~/.claude/CLAUDE.md
- ~/.claude/settings.json
- ~/.claude/hooks/ (all .sh files)
- ~/.claude/projects/<current-project>/memory/MEMORY.md

Be direct. If the original review was thorough and correct, say so.
```

After both reviews complete, highlight where Codex agreed, disagreed, and any net-new findings.
Do not auto-apply Codex findings. Surface them as additional input for the user to weigh.

---

## Anti-patterns to watch for

These are the most common drift patterns, worth checking explicitly every run:

| Pattern | What to look for |
|---|---|
| Hook ordering bug | Normalization hook appears after the hook that needs normalized input |
| MultiEdit exclusion gap | File-type filtering applies to Write/Edit but not MultiEdit |
| Rule/hook contradiction | CLAUDE.md says "always X" but a hook immediately undoes X |
| Memory duplication | MEMORY.md restates a rule that's already in CLAUDE.md |
| Stale skill-level entry | Memory says "new to X" when the user has been using X for months |
| Missing deny rule | Zero-exception block is text-only with no `permissions.deny` backing |
| Orphaned allow entry | `permissions.allow` entry for a tool that's no longer used |
| PostToolUse coverage assumption | Assuming a PostToolUse hook catches conversational output (it doesn't) |

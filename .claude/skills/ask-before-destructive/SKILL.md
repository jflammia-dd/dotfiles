---
name: ask-before-destructive
description: >
  Before any destructive or irreversible operation — deleting files or directories,
  renaming skills, overwriting configs, removing packages, or resolving "collisions"
  — present the full plan using a structured approval mechanism with concrete options
  and wait for explicit user approval. Never assume a "skipped" or "duplicate" item is
  safe to delete. When in doubt, ask.
---

# Ask Before Destructive Changes

## What counts as destructive
- Deleting any file, directory, or symlink
- Renaming a skill (changing its `name` field) in a way that changes its identity
- Removing a package, hook, or skill directory — even one flagged as a "collision"
  or "skipped" by a validator
- Overwriting a file that has unique content not present elsewhere
- Any operation that cannot be cleanly undone with git or a trash/recycle bin

## The rule
1. STOP. Do not execute the destructive operation yet.
2. PRESENT the plan using `ask_user_question` (or equivalent structured mechanism).
   Each destructive action should be a concrete option the user can select. Include
   enough context in the option descriptions that the user understands exactly what
   will happen. Do not use freeform text as the primary approval path.
3. WAIT for explicit user selection. "I'll go ahead and..." is not approval — the
   user must actively choose an option.
4. Only then execute the approved option.

## How to present the choice
Use `ask_user_question` with one question per destructive action (or a single
question with all actions as options). Each option should be a distinct, mutually
exclusive choice. Recommended patterns:

- For each item to delete: option "Delete [path]" with description explaining what
  it contains and why it was flagged
- For collision resolution: one option per side ("Keep A, remove B" vs "Keep B,
  remove A" vs "Keep both, suppress the warning")
- For renames: "Rename to X" vs "Rename to Y" vs "Leave as-is"

If the user selects "Type something" (custom answer), treat that as explicit
direction and follow it.

## Special caution for skill collisions
A "collision" or "skipped" status does NOT mean the item is a redundant duplicate.
Packages are supersets of skills. A standalone skill may be the stale copy that
should be removed — OR it may be the canonical source the user deliberately kept.
Never assume. Ask which side is canonical before deleting either.

## What is NOT destructive (no approval needed)
- Editing the content of a file (adding frontmatter, fixing YAML, trimming text)
  as long as the original can be recovered from git or the edit is reversible
- Creating new files
- Reading or listing files

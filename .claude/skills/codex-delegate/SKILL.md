---
name: codex-delegate
description: >
  Delegation bridge from Claude Code to the local Codex CLI. Invoked either
  directly as /codex-delegate <task> or programmatically by dd-research on
  even-numbered verification passes. Never triggers based on conversation
  context alone. Passes a narrowly scoped coding or analysis task to Codex
  non-interactively and returns a concise summary.
allowed-tools:
  - Bash(~/.claude/skills/codex-delegate/scripts/run-codex-subtask.sh:*)
  - Bash(mktemp:*)
  - Bash(rm:*)
  - Bash(gh:*)
  - Bash(date:*)
  - Read
  - Grep
  - Glob
  - Edit
  - Write
---

# Codex Delegate

You are a delegation bridge. Your job is to translate a user-provided task
into a tight, self-contained Codex prompt, run it non-interactively via the
helper script, and return a concise summary of what Codex did.

You do NOT solve the task yourself. You delegate it.

---

## Step 1 — Classify the task

Decide whether Codex needs write access:

- **read-only**: analysis, explanation, search, review, or anything that
  should not modify files.
- **write**: implementing code, fixing bugs, adding tests, or any task that
  requires file edits.

When in doubt, use `read-only`. Ask the user if the mode is ambiguous.

**Fast path for pre-materialized prompts.** If the task arrives already containing
`## Style rules` and at least one `## Check` section — the prompt was assembled
upstream (e.g., by dd-research) and requires no further preparation. In that case:

1. Confirm mode is `read-only` (pre-materialized verification prompts are always read-only)
2. Skip Steps 2, 3, and 4 entirely
3. Go directly to Step 5 (write to temp file) and Step 6 (run as read-only)

Do not add domain conventions, do not search for the document, do not alter the
prompt in any way. The upstream skill is responsible for correctness; codex-delegate
is the executor, not the editor.

---

## Step 2 — Load domain conventions

Before locating the code or crafting the prompt, identify whether the task
touches a domain that has a skill. Skills encode conventions (file naming,
frontmatter schemas, tool commands, syntax rules) that Codex must follow to
produce correct output. Without them, Codex will guess.

**How to find relevant skills:**

Check both locations:
```
$PWD/.claude/skills/*/SKILL.md      ← project-level skills
~/.claude/skills/*/SKILL.md         ← global skills
```

Use Glob to discover what exists, then match based on the task domain:

| If the task involves...             | Look for this skill           | Extract these sections |
|-------------------------------------|-------------------------------|------------------------|
| Obsidian vault notes, frontmatter, meeting notes, people profiles | `$PWD/.claude/skills/obsidian/SKILL.md` | File naming, frontmatter schemas, wiki-link syntax, tool commands |
| Verifying a dd-research document (source table, citation checks, style) | `~/.claude/skills/dd-research/SKILL.md` — but only when the prompt was NOT assembled by dd-research; if the fast-path fires, Step 2 is skipped entirely | Source Hierarchy, Confidence Labeling, Output, Failure Modes (style items only) |
| Analyzing or writing Datadog Go/Java code | `~/.claude/skills/dd-research/SKILL.md` | Source Hierarchy, Exists ≠ Active Trap, Repo Discovery |
| Any other domain                    | Glob `$PWD/.claude/skills/` and scan names | Conventions and constraints only |

**What to do with the skill file:**

Read the relevant SKILL.md. Extract only the sections listed in the table above
for that domain. Do not dump the entire skill — extract the conventions, required
fields, file naming rules, tool commands, syntax constraints, and "do not" rules
that Codex needs to operate correctly in that domain.

Do not extract triggering logic, meta-instructions, or workflow descriptions
intended for Claude. Codex only needs the ruleset, not the process.

Encode the extracted content as a `## Domain conventions` block at the top of the
Codex prompt (before "What to do"). This is not optional context — it is the
ruleset Codex must follow.

If no skill matches the task domain, skip this step and continue.

---

## Step 3 — Locate the code (or the document)

Two distinct cases:

**Case A — Code analysis or implementation:** The task involves source code.
Check whether the relevant files are local first, then fall back to `gh`.

**Case B — Document review (e.g., called from dd-research verification pass):**
The "code" is the document being reviewed. Identify its absolute path.
Do not search GitHub — just confirm the file exists locally and use its
absolute path in the prompt. Always use absolute paths for documents; Codex
runs with its own working directory and relative paths will fail silently.

---

**For Case A: Check local availability first.** Use Glob or Grep to see if the relevant
files exist under `$PWD` or a known local repo path. If they do, tell Codex
the exact local path.

**If the code is not local, use `gh` to find it.** You have `gh` available.
Use it to locate and surface what Codex needs before delegating. Common
patterns:

```bash
# Read a specific file from a remote repo
gh api repos/ORG/REPO/contents/path/to/file.go \
  --jq '.content' | base64 -d

# View a PR's diff
gh pr view NUMBER --repo ORG/REPO

# Search for a file across repos (if org search is enabled)
gh search code "FunctionName" --repo ORG/REPO
```

Fetch what you can ahead of time and include the relevant excerpts directly
in the Codex prompt as inline context (under a `## Context` heading). This
is almost always faster and more reliable than telling Codex to shell out to
`gh` itself.

When the code is too large to inline, or when Codex needs to explore
interactively, tell Codex explicitly that `gh` is available and provide the
exact repo and path so it can fetch what it needs.

---

## Step 4 — Craft the Codex prompt

Restate the user's request as a tight, self-contained prompt structured as
follows. All sections that apply must be present.

1. **Domain conventions** (from Step 2, if a skill was found) — paste the
   extracted rules as a `## Domain conventions` block at the top. This tells
   Codex what constraints to operate under before it reads a single file.
2. **What to do** — one clear action (not a list of loose goals).
3. **Scope** — which files, packages, or directories are in play, and whether
   they are local or need to be fetched via `gh`. Be explicit.
4. **Context** — if the code isn't local, include a `## Context` block with
   the relevant excerpts you fetched in Step 3, or tell Codex exactly where
   to find it (`gh api repos/ORG/REPO/contents/path`).
5. **Success criteria** — what "done" looks like (e.g., "all existing tests
   pass", "the function returns X given Y", "no new files outside pkg/foo").
6. **Reporting requirement** — always append this verbatim at the end of
   your prompt:

   > After completing the task, report:
   > 1. What you changed (file paths and a one-line description each).
   > 2. What tests you ran and whether they passed.
   > 3. Any residual risks, caveats, or follow-up work needed.

Never use vague verbs like "improve", "clean up", or "refactor" without
specifying a concrete outcome. Never ask Codex to rewrite large swaths of
code unless that is exactly what the user wants.

---

## Step 5 — Write the prompt to a temp file

```
PROMPT_FILE=$(mktemp /tmp/codex-task-XXXXXX)
cat > "$PROMPT_FILE" << 'PROMPT_EOF'
<your crafted prompt here>
PROMPT_EOF
```

Writing to a file (rather than passing the prompt as a shell argument)
avoids quoting fragility.

---

## Step 6 — Run the helper script

For analysis-only tasks (read-only mode):
```
~/.claude/skills/codex-delegate/scripts/run-codex-subtask.sh read-only "$PROMPT_FILE"
```

For tasks requiring file edits (write mode):
```
~/.claude/skills/codex-delegate/scripts/run-codex-subtask.sh write "$PROMPT_FILE"
```

Then clean up:
```
rm "$PROMPT_FILE"
```

---

## Step 7 — Summarize for the user

After Codex finishes, present a concise summary covering:

- What Codex did (changes made, tests run, result).
- Any residual risks or follow-up items Codex flagged.
- Whether you recommend reviewing the diff before using the output.

Do not paste the raw Codex transcript unless the user asks for it.

---

## Step 8 — Retrospective (runs after every use)

This step is mandatory. It keeps the skill honest and makes it better over
time. Do not skip it, even when the task was trivial or successful.

### 8a — Write a log entry to LEARNINGS.md

Append one entry to `~/.claude/skills/codex-delegate/LEARNINGS.md` using
this format exactly:

```
## YYYY-MM-DD — <one-line task description>
- **Use case:** code-analysis | document-verification | write-task | other
- **Mode:** read-only | write
- **Domain skill loaded:** <name> | pre-materialized (dd-research) | none
- **Code location:** local | remote (<org/repo>) | mixed
- **Outcome:** success | partial | failed
- **What worked well:** <one sentence, or "nothing notable">
- **Friction or failure:** <one sentence describing any obstacle, or "none">
- **Proposed improvement:** <concrete change to SKILL.md or the script, or "none">
```

When fast-path fires (pre-materialized prompt from dd-research), set:
- **Use case:** document-verification
- **Domain skill loaded:** pre-materialized (dd-research)

Get the date from `date +%Y-%m-%d`. Append the entry; do not rewrite the
file from scratch.

### 8b — Scan for promotable patterns

Read the full LEARNINGS.md. Look for any observation that appears in 3 or
more entries — same friction, same workaround, same missing guidance. These
are candidates for promotion to SKILL.md.

**Use-case awareness:** Check the `Use case` field before grouping entries.
A pattern appearing 3 times in `document-verification` entries is a
verification-specific pattern. A pattern appearing across all use cases is
universal. Do not mix use cases when counting: 2 `code-analysis` + 1
`document-verification` = not a pattern, even if they describe similar friction.

Patterns worth promoting:
- A step that routinely needs adjustment (wrong order, missing info)
- A flag or command that keeps appearing as a fix for friction
- A domain mapping that belongs in the Step 2 table
- A safety rule that was nearly violated
- A prompt structure that consistently produced better Codex output

Patterns not worth promoting:
- One-off task-specific details
- Observations that contradict each other across entries
- Observations mixing different use cases
- Anything already covered in SKILL.md

### 8c — Apply improvements to SKILL.md (when warranted)

If a pattern qualifies, edit SKILL.md directly. Keep changes surgical:
- Add a row to the domain skill table in Step 2
- Add a clarifying sentence to an existing step
- Add a new safety rule
- Correct a flag or path that was wrong

Do not rewrite sections wholesale. Do not add more than 3–4 lines per
pattern. Do not log the change in LEARNINGS.md (the edit to SKILL.md is
self-evident). Note what you changed in the summary you return to the user.

---

## Safety rules (non-negotiable)

- Never pass `--dangerously-bypass-approvals-and-sandbox` to Codex.
- Never instruct Codex to modify files outside the current working directory
  tree. (Claude's own retrospective writes in Step 8 to
  `~/.claude/skills/codex-delegate/` are exempt from this rule.)
- Never run Codex interactively (no `codex` without `exec`).
- If the task seems too broad (e.g., "refactor the whole service"), ask the
  user to narrow it before proceeding.
- If the task involves credentials, secrets, or destructive operations,
  stop and ask the user to confirm before running anything.

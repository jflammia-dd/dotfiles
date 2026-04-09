---
name: edit-doc
description: Autonomous document editing with adversarial style enforcement and document coherence checking. Use this skill whenever Justin asks to edit, revise, rewrite, update, clean up, improve or change any document, paragraph, section or prose. This covers meeting notes, engineering docs, proposals, summaries, RFC sections, emails and any written content. The skill scans the full document before editing, makes the requested change, then checks for coherence impacts across the rest of the document (orphaned concepts, repetition, stale framing, broken pedagogical flow) before running the style gate. Never show a draft that hasn't passed the style gate. Trigger on phrases like "edit this", "rewrite this", "clean up this doc", "fix the writing", "update this paragraph", "revise this section" and similar requests about prose.
---

# Autonomous Document Editor

Three commitments before any output reaches the user:

1. The edit was made correctly and the style gate is clean.
2. The document's pedagogical arc is intact and the reader's mental model builds progressively through the full document, not just the edited section.
3. Any coherence issues the edit created or exposed are surfaced explicitly so the user can decide what to do.

---

## Step 0: Pre-edit document scan

Before touching any text, read the full document to understand its structure. This is not optional for documents with more than one section.

Build a mental map of:

- **Pedagogical arc**: What is the reader meant to understand at each stage? What does each section build on from the sections before it? Where does the document first introduce each key concept, system name, component, decision or constraint?
- **Framing**: Is there an introduction, overview, executive summary or "what this document covers" section? What promise does it make to the reader?
- **Dependencies**: Which sections depend on knowledge established in earlier sections?

This map is the reference point for the coherence check after the edit. Without it, coherence issues are invisible.

---

## Step 1: Make the edit

Apply the requested change. Add, restructure, remove or rewrite content as asked. Do the substantive work well before moving to coherence review.

---

## Step 2: Coherence check

After making the edit, check it against the document map built in Step 0. The goal is to find places where the edit has broken, orphaned or duplicated something in the rest of the document.

Run these five checks:

**Check 1: First-appearance integrity**
For every concept, term, system name, component, decision or constraint that the edited section introduces or meaningfully uses, ask: is this the first place in the document a reader would encounter it? If yes, does the edit give enough context for a reader who hasn't seen it before? If no, does an earlier section already introduce it correctly?

If a concept is used in the edit but never properly set up anywhere in the document, flag it. Name the concept, note where it first appears and suggest where to add an introduction.

**Check 2: Repetition**
Does the edited content cover ground already covered elsewhere in the document? Near-duplicate explanations, restated conclusions and repeated context are the most common artifacts of iterative editing. If the same ground appears in two places, flag both locations and recommend which to keep or how to consolidate.

**Check 3: Framing currency**
Read the document's introduction or overview section. Does it still accurately represent what the document covers? Would a reader of the opening have the right expectations for all sections, including the one just edited? If the edit adds something significant that the introduction doesn't prepare the reader for, flag it.

**Check 4: Backward dependencies**
Does the edited section assume knowledge that only appears later in the document? A reader progressing linearly should not need to know something from Section 4 to understand Section 2. If the edit creates a forward reference that leaves the reader without necessary context, flag it and recommend where to move or introduce the dependency.

**Check 5: Flow continuity**
Read the transitions from the section before the edit to the edited section, and from the edited section to the section that follows. Do they still work? Does the edited section connect to what came before and hand off naturally to what comes next, or has the edit created a seam?

### Coherence output format

For each issue found, record:

```
[Type]: [Issue description]
Location: [where in the document]
Recommended action: [specific suggestion]
```

Types: ORPHANED CONCEPT, REPETITION, STALE FRAMING, BACKWARD DEPENDENCY, BROKEN FLOW.

If no coherence issues are found, say so explicitly. That's a meaningful finding.

These findings are NOT automatically applied. They are surfaced for the user to act on. Structural decisions require judgment about intent. Surface them clearly and let the user decide.

---

## Step 3: Style gate loop (max 3 passes)

After the coherence check, scan for style violations and fix them. Repeat until a full pass finds zero violations or you have completed 3 passes.

### Rules

The full rule set lives in the `justins-voice` skill. Read that file before running the style gate:

```
~/.claude/skills/justins-voice/SKILL.md
```

The five categories to check in each pass:

1. **Em dashes and double-hyphens**: any em dash (U+2014) or `--` used as a substitute; restructure the sentence
2. **Oxford commas**: comma before "and"/"or" in a list of 3+ items; remove it
3. **Semicolons joining independent clauses**: split into two sentences or use a conjunction; semicolons in comma-containing lists are fine
4. **Colons joining independent clauses in narrative prose**: split or restructure; colons in headings and labels are fine
5. **Passive voice**: rewrite with a clear subject performing the action; passive is acceptable only when the actor is genuinely unknown or irrelevant

See justins-voice for high-risk patterns, edge cases and examples for each rule.

### Per-pass procedure

1. Read through the edited text top to bottom.
2. List every violation: rule, approximate location, offending text.
3. Fix all violations in one edit.
4. Record the count and breakdown by rule.
5. If zero violations found: stop. The document has passed.

### If violations remain after 3 passes

Do not present the document as clean. List exactly what remains, which rule it falls under and why it resists clean resolution.

---

## Step 4: Present output

Show the final edited section or document first. Follow it with two summary blocks.

```
---
Edit summary: [1-2 sentences on what was changed]
Style gate: passed in [N] pass(es)
Violations caught and fixed: [total] ([rule: count], ...)
Ambiguous (not fixed): [none | description with explanation]

Coherence findings:
[list of issues, or "None found"]
```

If the edit introduced zero style violations, say so.
If the coherence check found no issues, say so. A clean check is worth noting because it means the document's flow held.

---

## Scope

The style gate covers the edited or added text by default, plus sentences immediately adjacent to the edit. If the user asks to review the whole document, scan everything.

The coherence check always covers the whole document, regardless of how small the edit was. A one-sentence change can orphan a concept or create a gap in framing that spans the entire document.

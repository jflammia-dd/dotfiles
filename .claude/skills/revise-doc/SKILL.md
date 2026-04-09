---
name: revise-doc
description: "Composed workflow for revising technical documents that contain verified claims. Use when editing a section of a document that references code, schemas, configs, component behavior or design decisions. Any document where getting the technical facts wrong would be worse than leaving a gap. This skill combines verified-writing (checking existing and new claims against authoritative sources) with edit-doc (making the change, checking document coherence, running the style gate). Triggers on: 'update this technical doc', 'revise this RFC section', 'edit this design doc', 'update the data model section', or any request to modify a document where technical accuracy and document flow both matter."
---

# Technical Document Revision

Revising a technical document requires two things at once: the facts must be accurate and the document must still hold together as a coherent whole. This skill sequences both.

The three phases are: verify what's already there and what you're about to write, make the edit, then check that the document still works.

---

## Phase 1: Claim inventory and verification

Run `verified-writing` Phases 1 through 3 (claim inventory, source resolution and synthesis) before touching any text. The synthesis from verified-writing Phase 3 is the factual foundation for Phase 2 of this skill.

---

## Phase 2: Make the edit

Apply the requested change using only facts from Phase 1. Field types come from the source. Component names are exact. Design decisions trace to a document.

If a claim cannot be grounded in a verified source, either omit it or use `[TODO: verify: <what's missing>]`. Do not write a placeholder that sounds like a real fact.

---

## Phase 3: Coherence check

Run `edit-doc` Step 2 (coherence check) exactly. Collect any issues found for inclusion in the Phase 5 output block.

---

## Phase 4: Style gate

Run `edit-doc` Step 3 (style gate loop) exactly, including the humanizer pass at the end. Record violation counts and any remaining ambiguous cases for the Phase 5 output block.

---

## Phase 5: Unified output

Present the edited section or document. Follow it with a single combined summary block.

```
---
Edit summary: [1-2 sentences on what was changed]

Verification:
  Verified: [count] claims confirmed against sources
  Gaps: [count] claims could not be verified
  [list each gap with location and suggested source]
  Conflicts: [any source conflicts surfaced]

Coherence findings:
  [list of issues found, or "None found"]

Style gate: passed in [N] pass(es)
  Violations caught and fixed: [total] ([rule: count], ...)
  Ambiguous: [none | description]
```

The verification gaps section is the most important part of the output. Unverified claims in a document erode trust faster than style problems or structural issues. Surface them clearly.

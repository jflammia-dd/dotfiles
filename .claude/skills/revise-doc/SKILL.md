---
name: revise-doc
description: "Composed workflow for revising technical documents that contain verified claims. Use when editing a section of a document that references code, schemas, configs, component behavior or design decisions. Any document where getting the technical facts wrong would be worse than leaving a gap. This skill combines verified-writing (checking existing and new claims against authoritative sources) with edit-doc (making the change, checking document coherence, running the style gate). Triggers on: 'update this technical doc', 'revise this RFC section', 'edit this design doc', 'update the data model section', or any request to modify a document where technical accuracy and document flow both matter."
---

# Technical Document Revision

Revising a technical document requires two things at once: the facts must be accurate and the document must still hold together as a coherent whole. This skill sequences both.

The three phases are: verify what's already there and what you're about to write, make the edit, then check that the document still works.

---

## Phase 1: Claim inventory and verification

Before touching any text, identify every technical claim that needs verification. Follow the `verified-writing` skill's approach for this phase.

**Read the full document first.** Understand the document's current state, what it argues and where the sections being revised sit in the larger flow.

**Inventory two categories of claims:**

1. **Existing claims in sections being modified**: Do not assume existing prose is accurate. Scan the sections you are about to touch for technical assertions (field names, types, component names, behavioral descriptions, design rationale) and add them to the verification list.

2. **New claims being introduced**: Everything you plan to write that asserts a technical fact.

**For each claim, identify the authoritative source:**
- Source code first (proto definitions, Go/Java structs, schema files, tests)
- Configuration second (deploy.yaml, Helm values, feature flags)
- Design documents third (Confluence RFCs, Google Docs specs)

**Read the source before writing.** If a source cannot be located, do not guess. Surface the gap: "I couldn't locate [X]. Do you have a file path or Confluence URL?" Insert `[TODO: verify: <what's missing>]` as a placeholder in the draft.

**If sources conflict**, surface the conflict before writing. Do not pick one silently.

Produce a brief synthesis of verified facts before moving to the edit. This is what the prose will rest on.

---

## Phase 2: Make the edit

Apply the requested change using only facts from Phase 1. Field types come from the source. Component names are exact. Design decisions trace to a document.

If a claim cannot be grounded in a verified source, either omit it or use `[TODO: verify: <what's missing>]`. Do not write a placeholder that sounds like a real fact.

---

## Phase 3: Coherence check

After making the edit, check it against the rest of the document. Run the five coherence checks from the `edit-doc` skill:

1. **First-appearance integrity**: Every concept the edited section introduces or uses: is it properly set up somewhere in the document? If the edit is the first appearance, does it give enough context?

2. **Repetition**: Does the edited content cover ground already covered elsewhere?

3. **Framing currency**: Does the document's introduction or overview still accurately represent what the document covers?

4. **Backward dependencies**: Does the edited section assume knowledge that only appears later in the document?

5. **Flow continuity**: Do the transitions from the preceding section and to the following section still work?

---

## Phase 4: Style gate

Run up to 3 passes checking for style violations. Read `~/.claude/skills/justins-voice/SKILL.md` for the complete rule set.

Categories to check:

1. **Em dashes and double-hyphens**: restructure the sentence
2. **Oxford commas**: remove the comma before the final "and"/"or"
3. **Semicolons joining independent clauses**: split or use a conjunction
4. **Colons joining independent clauses in narrative prose**: split or restructure
5. **Passive voice**: rewrite with a clear subject performing the action

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

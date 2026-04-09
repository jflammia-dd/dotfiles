---
name: doc-audit
description: "Holistic health audit for a document that has accumulated many edits over time. Use when a document feels fragmented, when you want to check flow and coherence without making a specific edit, or when you're preparing to share a document that's been through many revisions. The skill reads the full document, simulates the reader's experience, maps the pedagogical arc, and surfaces structural issues with specific recommendations. Triggers on: 'audit this doc', 'review this document for flow', 'check if this doc holds together', 'is this doc coherent', 'document health check', or any request to assess a whole document rather than make a specific change."
---

# Document Health Audit

This skill reads a complete document and assesses its structural health. It does not make edits. It surfaces what is broken and why, so you can decide what to fix.

The audit has three phases: mapping the document's intended arc, simulating the reader's actual experience, and identifying where those two diverge.

---

## Phase 1: Document map

Read the entire document. Build a map of:

1. **Sections and their purpose**: What is each section trying to accomplish? What should the reader know or be able to do after reading it?

2. **Concept introduction sequence**: Where does each key concept, term, system name, design decision or constraint appear for the first time? Build a list: concept, first appearance location, whether it was properly introduced with context.

3. **Document-level claim**: What is the single thing the document is trying to establish or argue? If you cannot state it in two sentences, the document may lack a coherent center.

4. **Framing promise**: What does the opening (introduction, overview, abstract) promise the reader? Does it set accurate expectations for what follows?

---

## Phase 2: Reader journey simulation

Trace the document section by section, maintaining a model of what a reader knows at each point.

At the start, the reader knows nothing about the document's content. They bring only the domain knowledge appropriate for the document's audience.

For each section, record:

- **What the reader knows entering this section**: List the concepts and context established by prior sections.
- **What this section requires the reader to know**: List the concepts and context this section assumes as prerequisites.
- **Gap**: Is there anything this section requires that the reader does not yet have? If yes, that is a backward dependency.
- **What the reader knows leaving this section**: What new understanding has this section added?

Flags to set during simulation:

- **COLD CONCEPT**: A term or system appears without introduction. The reader has no frame for it.
- **PREREQUISITE GAP**: A section assumes knowledge that the document establishes only later.
- **STRANDED KNOWLEDGE**: A section establishes something the document never uses again. Either it belongs elsewhere or it was left over from a previous version.
- **ASSUMED CONTEXT**: The document assumes the reader knows something that should be explained, either because the audience may not know it or because the document made a specific choice about it that needs justification.

---

## Phase 3: Structural issues

After the simulation, identify the following:

**Fragmentation**
Does any topic appear in multiple disconnected places? Look for concepts, constraints or arguments that are introduced, then revisited later in ways that feel like separate additions rather than a unified explanation. Each complete idea should live in one place; references elsewhere should be brief pointers, not re-explanations.

**Stale framing**
Compare the opening section's promise to what the document actually delivers. Does the introduction still accurately represent the document's scope and argument? Introductions become stale faster than any other section because they are written first and edited last.

**Transition quality**
For each section boundary, read the last paragraph of the outgoing section and the first paragraph of the incoming section. Does the transition actively hand off? Does it tell the reader why the next section follows from what they just read? A missing or passive transition ("The next section covers X") is a flag.

**Proportionality**
Are any sections disproportionately long relative to their importance? A section that takes three times as much space as others to make an equivalent point is a signal that it is either over-explaining or doing multiple jobs. A section that is shorter than expected may have dropped important content in an edit.

**Orphaned content**
Does any passage feel like it arrived from a different version of the document? Signs: it repeats something said elsewhere, it uses terminology inconsistently with the rest of the document, it addresses a question the document hasn't raised, or it seems to answer an objection that the document no longer makes.

---

## Output format

Present findings in this order:

**Health summary** (3-5 sentences): The overall state of the document. What is working. What is most broken. The one thing to fix first.

**Reader journey gaps** (from Phase 2):
Each gap on its own line, using this format:

```
[Flag type]
Section: [section name]
Issue: [what's missing or assumed]
Recommendation: [specific action]
```

**Structural issues** (from Phase 3):
Each issue on its own line, using this format:

```
[Issue type]
Location: [section or section boundary]
Issue: [description]
Recommendation: [specific action]
```

**Priority order**: Surface the issues that most damage the reader's ability to build an accurate model first. A cold concept that a reader hits on page one is more urgent than a proportionality issue in a late section.

If the document is in good shape, say so plainly and note what is working well. A clean audit result is meaningful information.

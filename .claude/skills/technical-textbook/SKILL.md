---
name: technical-textbook
description: Reviews and rewrites technical documentation to read like a pedagogical textbook — for readers who need concepts defined before mechanics and motivation before implementation. Use when someone says "make this read like a textbook", "accessible to someone new", "don't gloss over anything", "I want this to build up the reader's mental model", or asks for a document review aimed at new engineers or onboarding. Also invoke proactively whenever a technical document is shared or being reviewed and you notice it jumps into implementation before establishing why the system exists, uses acronyms without defining them, or explains mechanics before the reader has any reason to care. If in doubt, use this skill when editing or reviewing any engineering doc, runbook, architecture writeup, or design document.
---

Technical documents fail new readers in predictable ways: terms appear before they're defined, mechanics are explained before the reader has any reason to care about them, vague equivalences substitute for actual detail ("GCP and Azure have equivalent fields") and style violations make the prose feel assembled rather than written. This skill catches all four categories systematically.

The organizing principle throughout: at every point in a document, a reader should be able to answer "what is this?" before they're told "how does it work?" Take any sentence and ask whether all the nouns in it have been defined for the reader by that point. Good pedagogical writing moves from abstract to concrete, from motivation to mechanism, from concept to example — each section makes the next one easier to absorb.

## Before you do anything: read the full document

Read the entire document before writing a single word of feedback or making any edits. The most impactful problems are structural — a concept used on page 3 that should have been defined on page 1 — and you can only identify those patterns after reading everything. Resist the urge to flag issues as you go; finish the read-through first.

While reading, maintain an internal log of:

- Every term used before it is defined *(Phase 3)*
- Every section that explains how something works before explaining why it exists *(Phase 1)*
- Every place where you, as a new reader, would ask a question the text doesn't answer *(Phase 3)*
- Examples that introduce new concepts — they should only confirm ones already established *(Phases 1 and 2)*
- Acronyms that appear without expansion on first use *(Phase 3)*
- Diagrams, tables or examples that are too dense or require prior knowledge to read *(Phase 2)*
- Tables whose purpose isn't clear from their headers *(Phase 2)*
- Diagrams that use labels not yet introduced in the prose *(Phase 2)*

## Phase 1: Structural assessment

Structural problems have the highest leverage. A well-written sentence in the wrong section still confuses.

**Section ordering.** For a reader encountering a system for the first time, the natural learning order is:

1. What is this system and why does it exist? (motivation)
2. What vocabulary does the reader need to follow the rest? (concepts)
3. How does data or control flow through the system at a high level? (map)
4. What does each component do in detail? (mechanics)
5. How do the components combine in a real scenario? (synthesis / worked example)

If motivation comes after mechanics, or if concepts are scattered inline rather than collected upfront, that is a structural problem worth raising explicitly.

**Step and section granularity.** A single step that covers five distinct sub-topics is really five steps. A reader cannot build a mental model around a 200-line step. If you see a step covering: (a) why the thing exists, (b) two different paths through the mechanism, (c) sample output and (d) the lifecycle of the output object — split it. Each step should teach one idea.

**Worked example placement.** The example should confirm what the reader just learned, not introduce new material. If the example section is teaching concepts rather than confirming them, either the example is misplaced or the body is missing content that should precede it. An example that introduces the rule-mapper for the first time belongs after the rule-mapper is explained in prose, not before.

**Diagram placement.** A high-level architectural diagram belongs early, as a map that orients the reader before the detail sections begin. Diagrams placed at the end serve as summary, not orientation. If the document's diagrams appear after the prose they summarize, consider whether moving at least one diagram earlier would give readers a useful reference point. For guidance on what a diagram should show at a given placement point — which nodes and labels are appropriate — see Phase 2.

## Phase 2: Diagrams, tables and examples

Before scanning for prose gaps, assess every non-prose artifact in the document. These are the places where writers most often assume the reader shares their mental model, and where a misfire wastes the most cognitive effort.

**Diagrams** should orient, not overwhelm. Ask: does this diagram serve as a map that helps a new reader navigate what follows, or does it compress so much information that it requires understanding the system to make sense of it? A useful diagram shows only what the reader has been introduced to at the point it appears. Any node, arrow or label that hasn't been explained yet is noise. If a diagram shows five services but the text has only explained two, a new reader is left guessing at three of them. Check also that the labels in the diagram match the terminology in the surrounding text exactly — divergence between diagram names and prose names forces the reader to reconcile two vocabularies.

**Tables** answer a question. Before evaluating a table, ask: what question is this table answering? If you can't identify the question, the table lacks purpose and should either be removed or restructured around a clearer question. A good table header makes the question obvious. Check also for density: a table with more than four or five columns forces the reader to track too many dimensions at once. If a table is too wide, split it by question rather than trying to compress it. A table with two rows is usually just a sentence.

**Examples** do one of two things: they either introduce a concept concretely before it is explained in the abstract, or they confirm that the reader understood an abstraction correctly. The first kind belongs before the explanation; the second kind belongs after. The most common mistake is placing a confirmatory example before the concept has been explained, which forces the reader to extract the concept from the example rather than checking their understanding against it. Check also for example density: a code block or JSON object with twenty fields when only three are relevant to the point being illustrated is too dense. Either trim the example to the relevant fields, or annotate which fields matter and why the others are present.

The general test for any artifact: can a reader with no prior context look at this diagram, table or example, understand what it is showing and why, and have their mental model of the system grow or be confirmed as a result? If the answer is no — if the artifact requires the reader to already know the thing it's trying to teach — it needs to be simplified, annotated or moved.

**Exception: reference and trace documents.** Some documents are explicitly framed as a "complete trace grounded in source code" or a pipeline reference. In these documents, dense diagram labels are intentional — the internal service names, track names and component identifiers are the information the document exists to provide. Do not simplify those labels. Instead, treat the diagram's unlabeled terms as a gap list for Phase 3: each unexplained label is a narrative gap to fill via inline definition in the prose, not a diagram content problem to fix. Raise the structural question (should a Key Concepts section precede the diagram?) as a structural issue per Phase 1, then proceed with inline gap-filling regardless of the structural decision.

## Phase 3: Narrative gaps

Narrative gaps are places where the author knew something implicitly and the text glosses over it. New readers get stuck here. They manifest as:

- **Vague equivalences:** "GCP, Azure and M365 each have equivalent provider-specific fields" — what are those fields? Name them.
- **Dropped agent:** "entities are extracted" — by what, from where, when?
- **Implicit prerequisites:** using an acronym before defining it, or referencing a component before introducing it.
- **Missing motivation:** "the projection system runs before rule evaluation" — a reader wants to know why before they care how.
- **Undefined architecture terms:** "the mapper sends a MappedLog to the assigner" — what is the assigner?

For each gap, use this format: "At [location], a reader would ask [question]. Fill with: [answer]." Ask what question a new reader would ask at that point that the text doesn't answer, then provide the answer.

**In reference and trace documents**, the gap list is often long (10+ unexplained internal service names, acronyms and framework names). Work through all of them. A parenthetical inline definition is usually the right fix — light enough not to interrupt the technical flow, but sufficient to unblock a reader who doesn't already know the term. Don't batch them into a new Key Concepts section unless the structural assessment has already flagged that as the right approach.

## Phase 4: Style corrections

Before writing or rewriting any prose, invoke the `justins-voice` skill and follow it. `justins-voice` is the authoritative style guide for this work — it covers em dashes, passive voice, Oxford commas, counting preambles, numbered vs bullet lists, bold usage and sentence structure. Apply it to every sentence you write, not just to the original document.

After writing or rewriting a section, run a `justins-voice` self-check by grepping for the four most common violations before moving on. New prose is as subject to the style rules as old prose, and these violations appear frequently in rewrites:

```bash
grep -n " — "   # em dashes in prose — replace with comma, period or parentheses
grep -n ";"     # semicolons joining clauses — split into two sentences or use "and"
grep -n ": "    # narrative colons — restructure or remove (colons are fine in headings/labels)
grep -rn ", and \|, but \|, or "  # comma before coordinating conjunction — drop the comma
```

Run these on the file after every batch of edits. The goal is zero hits in narrative prose (non-headings, non-code-blocks, non-tables).

Invoke the `humanizer` skill on completed prose sections to remove AI writing patterns after the `justins-voice` pass.

## Phase 5: Implement in the right order

For **structural changes** (reordering sections, splitting steps, adding a missing concepts section, moving the worked example): present findings first and ask for confirmation. These changes touch many lines and may have intentional reasons.

For **narrative gap-filling and style corrections**: implement directly. These are unambiguously improvements. Batch-report them after: "I expanded [location] to explain [concept] because a new reader would ask [question]."

When filling a gap, match the voice and technical register of the surrounding text. Preserve every technical detail — the goal is accessibility, not simplification. Defining a term inline ("the projection system, Datadog's field normalization layer, runs on every matching event") is often lighter and more readable than creating a separate definition section.

**Scope constraint.** Fill gaps using information that is already present or implied in the document. Do not add new sections, tables, diagrams or content types that the original document doesn't include unless a structural issue genuinely requires it. A document that lacks a motivation section needs one added; a document that lacks a failure-modes table doesn't need one invented. The test is whether the original author would recognize the improved document as their own, only clearer.

## Output format

Present your assessment in this order:

1. **Structural issues** — highest impact, requires confirmation before implementing. Phrase each as: "Section X should come before Section Y because a reader encountering Y hasn't yet learned [concept], which X establishes."
2. **Artifact issues** (diagrams, tables, examples) — content and density issues implement directly; placement issues require confirmation. These findings come from Phase 2.
3. **Narrative gaps** — implement directly after listing them. Phrase each as: "At [location], a reader would ask [question]. Fill with: [answer]."
4. **Style corrections** — batch implement and report as a summary.

If there are no structural or artifact issues, say so and proceed directly to implementing the other categories.

## Caution: Factual accuracy when filling narrative gaps

Phase 3 asks you to fill gaps using "information that is already present or implied in the document." This assumes the document is factually correct. When the document describes the behavior of a system whose source code can be read, that assumption needs testing before you fill gaps.

Specifically: if a worked example or stage description attributes a behavior to a specific trigger (e.g., "when event X arrives, Y happens"), check whether that attribution is plausible before repeating it in a gap fill. A gap fill that adds detail to a wrong claim embeds the error more deeply into the document. When in doubt, state what the document implies ("the pane is finalized on the last event's arrival") and flag it for code verification rather than expanding it with invented detail. For Datadog internal documents, combine this skill with `dd-research` so that narrative gaps are filled from code, not from inference.

# Superpowers Integration Reference

Specific skills map to specific points in the research, writing, and verification workflow. Use them at the exact moments described below — don't substitute your own judgment for the structured approach each skill provides.

These skills take precedence over the default loop mechanics where they apply. The research execution order (discover → read → write → verify) is unchanged; these skills enhance specific steps within that order, they don't restructure it.

---

## Session Start (Before Any Research)

**`superpowers:brainstorming`** — invoke at the start of any research session before opening any files. Use it to lock down scope (current production state vs. planned architecture?), depth (high-level vs. deep code paths?), output format (document vs. inline answer?), and focus (which subsystem matters most?). The "Handling Ambiguity" section of SKILL.md covers the same ground but brainstorming structures it more rigorously. If the request is clearly scoped, the session is short. If it's ambiguous, brainstorming surfaces the questions before you read any files.

---

## During Phase 1 (Discovery — Code First)

Phase 1 is codebase-first. Start by mapping the actual code — entry points, directory structures, proto definitions, BUILD files. Do not consult Confluence to understand the system before reading the code. Docs are secondary sources; reading them before code risks anchoring your understanding to what the docs claim rather than what the code does. That bias is hard to undo once it's set.

**`superpowers:dispatching-parallel-agents`** — invoke after initial terrain mapping, before Phase 2 reading, whenever multiple repos or services need to be explored simultaneously. Use it to structure the parallel discovery work. Subagents find the files; the main session reads them.

**`atlassian:search-company-knowledge`** — invoke during Phase 1 only as a **navigation aid**, not a source of understanding. Acceptable use: finding which Confluence space a team owns, locating a design doc that names the relevant service or EVP track, identifying which repo owns a behavior. Use the results to populate the file list (e.g., a design doc mentions `EntityRiskOutput.java` → add it to Phase 2 reads). Do not use Confluence findings to make claims in the draft. The cross-check against Confluence docs happens after writing (see the Confluence cross-check section in SKILL.md), not before reading.

---

## Between Phase 1 and Phase 2 (Completeness Gate)

**`superpowers:writing-plans`** — invoke after Phase 1 discovery is complete, before starting Phase 2 reads. Use it to write down the full file list and reading order. This doubles as the Phase 2 completeness gate check: if you can't write a complete plan, discovery isn't done.

---

## After Phase 3 (Writing — Before Entering the Verification Loop)

**`justins-voice`** — invoke after the draft is written, before the verification loop begins, when the output is a document intended for distribution (not an inline answer). Apply it to the full prose draft to ensure tone and style match Justin's voice. Do not apply to source table entries, code citations, or technical identifiers — only to narrative prose sections.

**`rewrite:rewrite`** — invoke after `justins-voice` (or alone for inline answers) to edit the draft for clarity, concision, and precision. This is the prose quality gate before verification. Do not run verification passes on prose that hasn't been through this step — style corrections during verification pass inflate the iteration count.

**`humanizer`** — invoke after `rewrite:rewrite` to remove AI writing patterns (rule-of-three, em dash overuse, vague attributions, inflated language) from the draft. This is the final prose pass before the verification loop starts. Verification should be checking code accuracy, not AI writing patterns.

**`mermaid:mermaid-diagrams`** — invoke when the research includes a diagram. Don't hand-write Mermaid syntax; use this skill. It handles the diagram type selection, syntax generation, and PNG export. Invoke it with the pipeline or architecture description, not a pre-written diagram.

---

## During the Verification Loop

**`superpowers:systematic-debugging`** — invoke when a verification pass finds something unexpected: a line that doesn't match its citation, a claim that seems wrong but you're not sure, or a discrepancy between what the code says and what the draft claims. Use it before classifying the finding as minor or substantive. This is the investigation step, not the correction step.

**`dual-agents-review:dual-review`** — invoke when the clean counter reaches 3. This is the adversarial final gate. Pass the absolute document path only. The skill runs independent parallel reviews and surfaces what Claude missed. **Pre-flight check:** run `git -C "$(dirname DOC_PATH)" rev-parse --is-inside-work-tree 2>/dev/null` before invoking. If the document is not in a git repository (exit non-zero), do not invoke this skill — it requires git context. Instead, use the `pr-review-toolkit` fallback described in `references/verify-existing.md` Step 5.

**`superpowers:receiving-code-review`** — invoke after `dual-agents-review:dual-review` returns findings. Before accepting or rejecting any finding, run this skill. It guards against performative agreement and reflexive dismissal. Each finding gets evaluated by direct read before a decision is made.

**`superpowers:verification-before-completion`** — invoke immediately before exiting the verification loop and publishing the document. Do not claim the loop has passed without running this skill. It checks that every source table entry is "direct read" or "unable to verify: [specific reason]" and that the verification certificate accurately describes what was done.

---

## Parallel Verification (Multiple Independent Claims)

**`superpowers:dispatching-parallel-agents`** — invoke during the verification loop when multiple independent source table entries need spot-checking simultaneously. If you're running Claude passes that need to verify several entries in parallel, use this skill to dispatch those reads concurrently rather than sequentially.

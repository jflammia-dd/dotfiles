# Self-Improvement Retrospective

Run this after every research session completes — after the output is published and the verification loop has exited cleanly. The skill improves with every use.

**What to collect.** For each correction made during the verification loop, record:
1. What the draft said
2. What the code showed
3. The root cause — not "I missed it," but the specific pattern that led to the error

**Patterns to watch for** (these should trigger an update to `references/failure-modes.md` if seen):
- A file read stopped before reaching the relevant method (partial read → wrong claim)
- A claim described only one code path when multiple existed in parallel
- A feature flag's scope was overstated or understated
- A "directory structure only" entry survived into the clean-pass counter
- A class or method name came from prior knowledge or a subagent, not a direct read
- A vague description ("equivalent provider-specific fields") masked a verifiable claim

**Cross-model patterns** — track these separately across research sessions; they reveal systematic biases rather than one-off mistakes:

- *Codex finds X that Claude missed, Claude confirms it:* Claude has a blind spot for X. Add it to `references/failure-modes.md` with a concrete example.
- *Codex flags X, Claude cannot reproduce after re-reading:* Either Claude's re-read is not deep enough, OR Codex is over-aggressive on this class of claim. Count the occurrences. If Codex is right more than 50% of the time when re-read more deeply, update Claude's verification practice. If Claude consistently cannot reproduce after genuine effort, note that this class of Codex finding is unreliable.
- *Codex's Check 5 spot-checks consistently find line-range mismatches:* Claude is citing line ranges loosely. Add a specific note to the "Citing a specific line number without verifying it" failure mode.
- *Codex consistently finds uncited claims that Claude then confirms:* Claude is writing claims without inline citations. Strengthen the "Every claim needs a source" guidance in Phase 3 (Write).

**How to update the skill:**

1. Check `references/failure-modes.md`. If the root cause matches an existing mode, add a concrete example. If it's a new pattern, add a new bullet with a specific description.

2. Check the "What Good Research Looks Like" section below. If a correction from this session illustrates a principle better than the current examples, replace or augment the example.

3. Add any new Datadog-specific traps to "The Exists ≠ Active Trap" in SKILL.md if relevant (e.g., a new config file type that controls deployment, a new pattern for activation).

4. Use the Edit tool to update the relevant files directly. Write the retrospective while the session is still fresh — corrections have context that fades quickly.

Do not add vague principles like "read more carefully." Every update must be a specific, actionable pattern with enough detail that a future session would recognize it and behave differently. "Stopped reading EntityRiskHandler at line 160 because all cited claims were covered, missing the OCSF parallel emission path at lines 174–184" is useful. "Read files more thoroughly" is not.

---

# What Good Research Looks Like

The SIEM Risk Insights pipeline research is the reference model. Key properties:

- Claims were supported by specific file paths and line numbers
- When a claim was challenged (entity chain resolution), the code was re-read and the answer was corrected with evidence
- Secondary sources (design docs) were flagged as such
- The scope was confirmed before diving in (current production state only, no UEBA)
- The wrong assumption about `raw_signal_score` driving the UI was caught by reading the Caniche DDSQL and corrected, not glossed over
- Repo topology was explained proactively (dd-source owns the API; logs-backend owns the stream processing)

The verification pass that corrected the same research is also a reference model for what the verification pass is supposed to catch. The initial draft described `cloud_siem.risk_scores_signals` as an active production Caniche view because the `.ddsql` file existed in the directory. The verification pass checked `views.tf` and found the view was never registered — the file was dead code. That single check changed the entire Step 3 and Step 4 descriptions and the diagrams. Without the verification pass, a plausible-sounding but wrong architecture description would have shipped as documentation.

The SIEM Streaming Detection Rules post-publication verification is a reference model for what the adversarial gate (`dual-agents-review:dual-review`) adds beyond Claude's blind passes. Three blind Claude passes found only style and labeling issues (timeline code block, diagram node name). The adversarial reviewers — two independent agents reading the document cold — found four structural issues that all three Claude passes missed:

1. `NETFLOW`/`SECRUNTIME` track inventory was incomplete and contradictory across Key Concepts and Stage 1.
2. `GenericPane` and `NewValuePane` both claimed to handle new-value detection in the same numbered list.
3. Mermaid diagram arrows implied the mapper and reducer wrote to blob storage; prose said they fetched.
4. `Percolator<ParsedRuleQuery>` (Key Concepts) and `RulesPercolator` (Stage 2) named the same object differently.

All four are cross-section consistency issues. Claude's blind passes read each section against the code — they don't naturally cross-reference between non-adjacent sections. Adversarial reviewers read the whole document as a reader, not section by section, and catch these. This is the structural reason the dual-review gate matters: it catches a class of error that linear, section-by-section verification misses by design.

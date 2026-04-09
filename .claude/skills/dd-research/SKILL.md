---
name: dd:research
description: >
  Use this skill when asking how any Datadog internal system works, to find which service
  or repo owns a behavior, to trace a data flow, or to get documentation about internal
  systems. This skill reads actual source code — without it, answers about Datadog
  internals are guesses, not facts. Trigger on questions like: "how does risk scoring
  work?", "which service handles X?", "is this in logs-backend or dd-source?", "trace
  how a log becomes a signal", "create a note explaining how X works", "where is X
  implemented?", "what's the pipeline for X?", "is this feature actually in production?".
  Also trigger when these Datadog-specific systems are mentioned: rule-reducer,
  entity-risk-score-api, REDAPL, Caniche, EVP, SIEM signals, Risk Insights, Cloud SIEM,
  CSM, findings, detection rules, Temporal Husky, siem-entity-crawler, signal pipeline,
  or any internal service under investigation. When uncertain whether an answer requires
  reading Datadog source code — it does. Use this skill rather than guessing.
  Do NOT trigger for: deploy requests, writing unit tests, fixing code bugs, CI failures,
  PR reviews, or running services locally.
---

# Datadog Codebase Research

Your job is to produce accurate, citable answers about how Datadog systems work, grounded
in source code. Think of this as writing a research paper: every claim needs a source,
intuitions are hypotheses until verified, and the code is the primary witness.

---

## Design Philosophy — Front-Load the Work

**The goal is to minimize verification loop iterations.** The ideal session runs one clean
Claude pass and one Codex pass, both finding nothing. That outcome is only possible if the
research phases are thorough enough that the draft is correct when first written.

The verification loop is an audit layer — a final check for slippage, not a mechanism for
doing research. Every iteration of the loop that catches a substantive error is evidence
that the research phase was not complete. The correct response is to invest more in Phase 1
and Phase 2, not to run more verification passes.

**The quality metric is loop iteration count.** Fewer iterations means better research.
More iterations means the work was front-loaded in the wrong place. If you find yourself
on pass 10 still correcting claims, the research phase was the problem.

**The investment order:**

1. Phase 1 (Discover) — the most leveraged phase. Finding the right files before reading
   anything saves more time than any amount of verification. Incomplete discovery means
   you write claims you can't back, which means the loop runs.

2. Phase 2 (Read) — the most time-consuming phase, and intentionally so. Every file on
   the list must be read to its end before writing starts. Time spent reading in Phase 2
   is always cheaper than time spent re-reading in the verification loop after a wrong
   claim is found.

3. Phase 3 (Write) — only after the Phase 2 completeness gate is satisfied. If you start
   writing before reading is complete, you will write claims you can't cite, which the
   loop will catch and which should have been avoided by not writing them.

4. Verification loop — should find nothing, or at most minor citation issues. If it finds
   substantive errors consistently, add time to Phases 1 and 2, not here.

This is not a judgment about effort — it's a judgment about where effort is placed. A
session that spends 80% of its time in Phases 1 and 2 and 20% in verification is a better
session than one that splits evenly. Front-loading is the measure of quality.

---

## Source Hierarchy

Always make clear which type of source backs each claim:

**Primary (code is truth):** Source files in any Datadog repo. A behavior exists if the
code says it does. Cite with `repo/path/to/file.go:line`.

**Secondary (context, not proof):** Confluence pages, Google Docs, design docs, RFCs.
Useful for understanding *intent*, *history*, and *what was planned* — but treat them
with explicit skepticism. Docs drift. Features get cut or changed after the doc was
written. When using a secondary source, say so: "According to the design doc [link], the
intent was X — the code confirms / does not confirm this."

Never present a claim from a secondary source as settled fact. Use it to form hypotheses,
then verify against code.

Secondary sources also play a specific role in the verification pass: searching
Confluence for docs that describe the system you just researched is a required step.
Divergence between Confluence and code is a signal to investigate, not ignore. See
"Verification Pass" for the full procedure.

---

## Superpowers Integration

Specific skills map to specific phases of this workflow — session start, discovery, writing, and verification. Read `references/superpowers.md` for the full phase-by-phase guide, including which skill to invoke at each moment and why the order matters.

---

## Repo Discovery

Justin may not know which repo contains the code he's asking about, and may point you
to the wrong one. This is expected — repo discovery is a core part of the skill, not
a problem to work around.

**Step 1 — Check local repos first:**
```
~/dd/
```
List what's available. For each candidate repo, check whether it plausibly owns the
behavior being researched before diving in. See `references/repo-map.md` for a guide
to what each repo owns.

**Step 2 — Discover unlisted repos via `gh`:**
If the local set doesn't seem complete, search the DataDog org:
```bash
gh repo list DataDog --limit 100 --json name,description
```
Use the descriptions to identify candidates. For a repo not cloned locally, you can
read files directly:
```bash
gh api repos/DataDog/REPO/contents/PATH
gh api "repos/DataDog/REPO/git/trees/HEAD?recursive=1" | jq '.tree[].path'
```

**Step 3 — Correct misdirection with evidence:**
If Justin names a repo that turns out to be wrong, say so directly and show your work:
"I looked in `logs-backend` as you suggested, but the entity risk scoring logic actually
lives in `dd-source` — specifically `entity-risk-score-api`. Here's how I found it: [...]"

Never silently search a different repo. State what you searched, what you found (or
didn't find), and where you ended up.

---

## Handling Ambiguity

Ask clarifying questions only when the request is genuinely ambiguous — when the answer
would materially change the research direction. If the request is specific enough to
produce a deterministic answer, start immediately.

**Before you start, resolve:**
- Scope: current production state, or include planned/target architecture?
- Depth: high-level (services and arrows), medium (services + key data flows), or deep
  (code paths, schemas, specific implementations)?
- Output format: saved document, inline answer, diagram only?
- Focus: if the topic has multiple sub-systems, which matters most?

**If you uncover ambiguity mid-research, stop and ask.** Do not assume. Do not pick
the more likely interpretation and proceed. Surface the specific question: "I found two
different paths this could go — [A] or [B]. Which one are you asking about?"

---

## Research Execution

> **Before starting:** Read `references/failure-modes.md` — it catalogs error patterns from past sessions. Read it before opening any files.

The workflow is: **discover → read → write**, in that order. Do not write claims and
then try to verify them. Read the code first, then write only what you've confirmed.
This collapses what would otherwise be multiple iterative sessions into one.

**The verification loop is an audit layer, not a research mechanism.** A single
thorough pass through Phases 1 and 2 should be sufficient to produce a correct draft.
If the verification loop is catching substantive errors — wrong claims, missing code
paths, wrong line numbers, uncited facts — that is a failure of the research phase,
not a reason to run more verification passes. The goal is a research phase so complete
that verification finds nothing.

**Phase 1 — Discover (before writing anything)**

1. **Map the terrain.** List directories and file names across all relevant repos.
   Understand the structure before committing to reading specific files. Use subagents
   to explore multiple repos simultaneously — this is the right use of subagents.

2. **Follow the data, not the names.** Services named "entity-something" don't always
   own entity logic. Read entry points (`main.go`, `main.java`, `README.md`, proto
   definitions) to confirm ownership before exploring deeply.

3. **Build a complete file list.** Before reading any file in depth, identify every
   file you'll need to cite. Think through the full pipeline: entry points, data schemas,
   configuration files, SQL queries, deployment manifests. Write this list down. Do not
   start writing the draft until you have a complete picture of what needs to be read.

4. **Trace calls across service boundaries.** Follow EVP track names, gRPC service names
   and topic names to find producers and consumers. A behavior often spans 3–4 repos.
   Add every file you find to the list.

5. **Find the boundaries.** The file list is complete when you can describe what would
   need to change in the codebase if the behavior you're researching changed — without
   looking anything up. That means you've read far enough to understand both how the
   system works and where each piece of logic lives. If you're unsure whether a file is
   in scope, it probably is. Add it and read it.

**Phase 2 — Read (directly, in parallel, before writing)**

6. **Read every file on the list directly, in the main session.** Use the Read tool.
   Read all identified files in parallel where possible. A subagent that reads a file
   produces `agent-verified` evidence; the Read tool in this session produces `verified`
   evidence. The goal is `verified`. Do not write the draft until every file on the list
   has been read.

7. **Read every file to its end.** Always run `wc -l` when a file enters the source
   table. Never stop reading because the lines read so far cover the claims you've
   drafted — the remaining lines may contain parallel code paths, overrides, or
   conditions that change the meaning of what you've already read. If a file is long,
   read it in blocks. Mark each block read. The remaining-unread tail is always in scope
   until you've confirmed it contains nothing relevant.

8. **Complete the "exists ≠ active" check on every artifact during this phase.** For
   every file, class, view, query, or schema you plan to cite, find the thing that
   activates it — the `views.tf`, the `main.go` wire-up, the `BUILD.bazel` dependency,
   the feature flag — and read that too before writing. This check belongs in Phase 2,
   not the verification loop.

9. **Note what you can't find.** If a file or behavior doesn't exist where expected,
   say so explicitly. Do not invent a plausible explanation.

**Phase 2 completeness gate — do not start writing until all of these are true:**

- Every file on the discovery list has been read to its end (or confirmed irrelevant
  past a specific line).
- Every artifact that will be cited has an activation source read alongside it.
- Every call chain has been traced to the call site (not stopped at an interface boundary).
- Every config default that will be cited has been found in its constructor function,
  not inferred from context.
- You can describe the full pipeline from input to output, including which code runs
  on which service, without consulting any file you haven't read.

If any of these is false, keep reading. Do not move to Phase 3.

**Phase 3 — Write (from what you've already verified)**

10. **Write the draft from your direct reads.** Every claim in the draft should trace
    back to a specific file and line you read in Phase 2. If you find yourself writing
    a claim you can't back with a Phase 2 read, stop — either read the relevant file
    now or mark the claim as needing verification before including it.

---

## Verifying an Existing Document

When the task is to verify a document written in a previous session, the workflow differs from new research. Prior-session "direct read" entries carry no current-session verification weight. Read `references/verify-existing.md` for the full 5-step workflow.

---

## Verification Loop

After the draft is written, run the verification loop as a final audit — not as the
primary verification mechanism. A well-run session reaches this point with a draft that
is already correct. The loop catches the occasional slip: a claim introduced during
writing that wasn't in the Phase 2 reads, a file that was on the list but not actually
read, or a detail that needs a specific line number.

**A high iteration count is a diagnostic signal, not a badge of thoroughness.** It means
Phase 2 was incomplete. The right response is not to keep looping — it is to note the
root cause, persist it as a failure mode, and invest more in the research phases next
time. The verification loop has a 50-iteration hard limit precisely because unconstrained
looping is a symptom of insufficient front-loading, not a solution to it.

If the loop consistently finds nothing after 1–2 passes, the research phases are working.
If it consistently finds substantive issues past pass 3, fix the research phase.

Do not exit the loop and do not produce output until every source table entry says
"direct read" or carries a specific "unable to verify" reason. If a file is accessible
in a local repo or via `gh`, "unable to verify" is not an acceptable label for it.

The same requirement applies to every item in the Verification Gaps section. Each gap
represents an open claim. If the underlying file or data is accessible — local repo,
`gh api`, or `gh search code` — it must be read before the loop exits. A gap listed
as "not yet read" without attempting the 6 approaches is an unverified claim; it keeps
the clean counter at 0. The Verification Gaps section may only contain items for which
all 6 approaches were genuinely exhausted. "I didn't have time" and "the file is long"
are not exhaustion reasons. If the file exists and is readable, read it.

The loop does not end at the end of a session. If the session ends with outstanding
agent-verified items and the files are accessible, the research is not done. Restart
and close the gaps before treating the output as final.

**For each unverified claim, work through these approaches in order:**

1. **Direct read.** Find the file, read the relevant section, cite the line.

2. **Grep local repos.** If you don't know the file, search across all local repos for
   the class name, method name, constant or field name. Multiple search terms if the
   first doesn't hit. Cast wide — the code may be in `dd-go`, `logs-backend`, or any
   other repo, not just the one you started in.

3. **GitHub search across the DataDog org.** If local repos don't have it, run:
   ```bash
   gh search code "TERM" --owner DataDog --limit 20
   ```
   This is not optional. A string that doesn't appear in local repos may appear in
   `dd-go`, `logs-backend`, `driveline`, `experimental`, or other repos that aren't
   cloned locally. Run multiple searches with different terms (the constant name, the
   string value, the struct name, the config key). When `gh search code` finds a match,
   read the file directly via:
   ```bash
   gh api "repos/DataDog/REPO/contents/PATH" --jq '.content' | base64 -d
   ```
   This is a direct read from source. It closes the gap just as definitively as reading
   a local file.

4. **Subagent.** If the search space is very large or requires exploring a directory
   tree across multiple non-local repos, dispatch a research subagent.

5. **Confluence.** If the claim is architectural (intent, design decision, why something
   works a certain way), search Confluence before giving up. A design doc may name the
   exact class or config that proves the claim.

6. **Adjacent evidence.** If you can't find the exact thing, find something adjacent that
   makes the claim very likely — a test that exercises it, a comment that references it,
   a changelog entry. Document the indirect nature of the evidence.

**Every file cited in the source table must be directly read by the main session.**
This is not negotiable and it is not optional. Use subagents to find the right files;
use the Read tool in the main session to read them.

**The following are all open items that keep the loop running:**
- Any source table entry that says anything other than "direct read" or "unable to verify: [reason]"
- Entries like "directory structure only", "registration confirmed; content unread",
  "agent-verified", or any partial-read notation (e.g., "lines 1–80")
- Any file referenced in the prose whose relevant sections haven't been read
- Any claim in the prose that traces to a class, method or constant you haven't read

The clean-pass counter does not start until every source table entry shows "direct read"
or "unable to verify: [reason]." A pass with any open item is not a clean pass regardless
of whether prose corrections were made.

**When you reach an entry like "directory structure only":** that means the claim backed
by it has no code evidence. Either read the relevant code and update the entry to "direct
read," or explicitly mark it "unable to verify: [reason]." Never leave the loop with
ambiguous source table entries that are neither direct reads nor acknowledged gaps.

**Mark "unable to verify" only when all six approaches fail.** The reason must be
specific, not generic. Acceptable reasons:

- *"The behavior depends on a runtime feature flag value not visible in source code."*
- *"Searched locally and via `gh search code` with terms [X, Y, Z]; no results in any DataDog repo."*
- *"The claim is about production infra state (e.g., which datacenter is primary), not code."*
- *"The file exists but the relevant logic is generated at build time from [template], not readable directly."*

Not acceptable:
- *"Could not find it"* or *"Not verified this session."* — those mean keep looking.
- *"The code is not in a locally-cloned repo."* — that means run `gh search code` next,
  not stop. Not being local is not a reason. Every DataDog repo is readable via `gh api`.
  If the file is in `dd-go`, `logs-backend`, `driveline`, or any other org repo, read it.
  "Not cloned locally" only becomes an acceptable qualifier if `gh search code` also
  returns no results for every relevant search term.

**For claims about runtime values (track names, default configs, timeouts, flag defaults):**
these are almost always visible in code. Before marking "unable to verify," follow this
chain:

1. Find the constructor function (`NewXClient`, `NewXConfig`, `defaultXConfig`) and read it.
   Default values are set there.
2. Find every `With*` option function. Check which ones the caller passes at the call site.
   Options not passed mean the default applies.
3. If the call site uses only `WithGRPC()` and `WithSource()` but not `WithTrack()`, the
   track is the default, which is in the config constructor.

A claim like "we don't know which EVP track the client uses" is never acceptable if the
client library is in a local repo. The default is in the config file. Read it.

**"Unable to verify" is not a shortcut for "I didn't look hard enough."** If the code is
in `dd-source`, `logs-backend`, `dogweb`, `web-ui` or any other locally-cloned repo, the
information is accessible. Exhausting all approaches means following the call chain from
the call site through the config constructor, not stopping at the interface boundary.

**Confluence cross-check (mandatory — loop cannot exit without it):**

The Confluence cross-check is not optional and not skippable. No document may be
published and the loop may not exit cleanly until this check is complete. "Not performed
this session" is an open gap identical in weight to an unread source file — it keeps
the clean counter at 0.

After the draft exists — after you've formed your understanding from code — invoke
`atlassian:search-company-knowledge` to find architecture or design docs for the system.
Search by service name and restrict to the relevant team's space key (found in the
repo's `README` or `CODEOWNERS`). If you already used it during Phase 1 for navigation,
use those results here rather than searching again.

This order matters. Reading Confluence before code lets the docs frame your interpretation
before you've seen the evidence. The cross-check is adversarial: compare what Confluence
claims against what you found in the code, not the other way around.

For each doc you find, do three things:

1. **Read the page body** for architecture and design claims.

2. **Read the comments.** A Confluence page's body is often the starting point of a
   design conversation, not the final word. The real signal lives in the comments:
   reviewers flagging stale sections, authors clarifying intent, corrections that never
   made it back into the body, and decisions that changed after the page was written.
   For every page found, fetch both comment types using the Atlassian MCP tools:

   ```
   mcp__plugin_atlassian_atlassian__getConfluencePageInlineComments(pageId)
   mcp__plugin_atlassian_atlassian__getConfluencePageFooterComments(pageId)
   ```

   For any comment that has replies, fetch the thread:
   ```
   mcp__plugin_atlassian_atlassian__getConfluenceCommentChildren(commentId)
   ```

   Pay close attention to comments that say things like "this is outdated since X",
   "we changed this in the refactor", "see PR #N for the actual implementation", or
   "this section was superseded by". These are corrections to the body text and carry
   higher signal than the page itself.

3. **Check for divergence.** Does what you read — body *and* comments — match what
   the code shows? If they disagree, investigate before publishing. The code is the
   tie-breaker, but a comment pointing at a newer approach or a recently merged PR may
   be pointing at something you missed.

**Note the relationship explicitly in the output** using one of three states:
- *Confirmed:* "The design doc [link] describes X, and the code confirms it."
- *Diverged:* "The design doc [link] describes X, but the code shows Y. The code
  is authoritative here; the doc appears to be outdated."
- *Not found:* "No Confluence documentation found for this component."

Never silently discard a Confluence doc or comment thread that disagrees with your
code findings. The divergence itself is worth surfacing — it often means the doc is
stale or a correction never propagated back to the body.

**When the loop catches a discrepancy,** classify it first (minor or substantive — see
Main Loop). Minor discrepancies: correct inline and note what changed and why. Substantive
discrepancies: persist the failure mode to this skill file, then restart research. Do not
silently update anything in either case — the correction is part of the output.

---

## The "Exists ≠ Active" Trap

This is the most common source of errors in Datadog codebase research. A file being
present in a directory does not mean it is deployed, registered, scheduled or called.

**Examples of how this manifests:**

- A `.ddsql` file exists in the Caniche query directory → you assume it's a live view.
  But `views.tf` is the source of truth for which views are registered. Check it.
  A `.ddsql` file without a `views.tf` entry is dead code or an unused template.

- A Java class named `XyzHandler` exists in the rule-reducer → you assume it's in the
  production call path. Check that it's actually instantiated and wired into the
  service's startup or request handling.

- A SQL file exists in an API's `sql/` directory → you assume it's the active query.
  Check the Go/Java code that loads it. There may be multiple SQL files and the one
  that runs depends on a feature flag or request parameter.

- A proto definition exists → you assume the service uses it. Find where it's imported
  and called, not just where it's defined.

**The rule:** For any artifact you cite (file, class, view, query, schema), find the
thing that *activates* it — the `views.tf`, the `main.go` wire-up, the `BUILD.bazel`
dependency, the feature flag — and read that too. If activation evidence doesn't exist,
say so explicitly. Do not present the artifact as production behavior.

---

## Diagrams

Include a Mermaid diagram when:
- The topic has a clear sequential or hierarchical flow (pipelines, data flows)
- The user asks for one
- The topic involves multiple services and a diagram would be faster to read than prose

Use `<br/>` for line breaks inside Mermaid node labels (not `\n`).

---

## Confidence Labeling

Every research output must tell the reader how much to trust what they're reading.
Justin shouldn't have to ask — the confidence level should be embedded in the document
itself so he can calibrate while reading, not after.

**The valid final labels:**

`verified` — You read the file directly in this session using the Read tool. You can
cite the exact path and line. The reader can check it themselves. This is the target
final state for every file cited in the source table — `unable to verify: [reason]` is
the only alternative when all six approaches are genuinely exhausted.

`agent-verified` — A research subagent read the file. This is an **intermediate state**,
not a final one. When a claim is agent-verified, the verification loop is not done —
it is still open. Use the subagent's citation to find the file, then read it yourself.
An output should never be published with `agent-verified` items remaining if the files
are accessible in the local repos or via `gh`.

`unable to verify: [reason]` — The verification loop exhausted all six approaches and
could not produce a direct read. The reason must be specific. This label should be rare
and should never be used to avoid the work of reading an accessible file.

**Both "unverified" and "agent-verified" are transitional states.** Neither may appear
in the final output unless the file is genuinely inaccessible. Before publishing, every
source table entry must say "direct read" or carry a specific "unable to verify" reason.

**Where labels appear in the output:**

1. **Inline, on the claim itself.** Any claim that is `agent-verified` or
   `unable to verify` gets a parenthetical at the end of the sentence or paragraph.
   Examples:
   - "...resolves the role ARN back to the calling identity. *(agent-verified: EntityEnricherService.java:115)*"
   - "...a feature flag controls which providers use the OCSF path. *(unable to verify: the flag check is evaluated at runtime against an experiment config, not visible in source)*"

   Don't label every sentence. Label claims where the confidence level matters — where
   a wrong answer would mislead someone making a real decision.

2. **A Verification Gaps section** at the end of every document listing every
   `agent-verified` and `unable to verify` claim with its citation or reason. This
   section is not optional. If everything was directly verified, write "No gaps — all
   claims verified by direct read this session."

3. **The Source Locations table** gets a "How verified" column. Entries are one of:
   `direct read`, `agent-verified (file:line)`, or `unable to verify: [reason]`.

**What this is not:**

Don't label every verified claim — that buries the signal. The goal is to surface what
still carries risk, not to turn the output into a citation exercise. When a claim is
directly verified, the source table handles the citation and the prose needs no marker.

---

## Output

Format the output for where it's going. Apply whatever formatting conventions the
destination requires (e.g., a note-taking tool may need specific frontmatter or
link syntax; a wiki platform may have its own export process). When the destination
is unclear:

- **Saved document:** Standard Markdown. Mermaid in fenced code blocks.
- **Inline answer:** Prose with inline code citations (`file.go:line`).
- **No format specified:** Ask, or default to an inline answer with a note offering to
  create a formal document.

Every output — regardless of format — must include inline `*(unverified)*` or
`*(agent-verified: file:line)*` markers on any claim below `verified` tier that would
mislead someone if wrong.

**Document appendix (saved documents only):** All document-status material goes in an
appendix at the end of the document, after a horizontal rule (`---`), with a heading
that makes clear it is not part of the body — for example `## Document Status` or
`## Appendix: Verification`. Never embed source tables or verification certificates
inside the body text. The appendix must contain:

- **Source Locations** table with a "How verified" column (`direct read`, `agent-verified`, or `unverified`)
- **Confluence cross-check** section listing each page found with its relationship status (Confirmed / Diverged / Not found) and a summary of any relevant comment thread findings. If no Confluence docs were found, write "No Confluence documentation found for this component."
- **Verification Gaps** section. This section may ONLY contain items for which all 6 verification approaches were genuinely exhausted — runtime state, build-generated code, production infra values, or things confirmed absent from every accessible repo. It may NOT contain files that are accessible but simply unread. If a file is in a local repo or reachable via `gh api`, it must be read before it can appear here. If everything was directly verified, write "No gaps — all claims verified by direct read this session."
- **Verification certificate** (one line, must reflect all three mandatory steps):
  - Completed loop: `Verified: N passes + adversarial review + Confluence cross-check (N pages, [Confirmed/Diverged/Not found]). Self-improvement: complete. All claims direct-read or unable-to-verify with reason.`
  - Incomplete: `Verification: incomplete — [what was skipped and why].`

**Inline answers:** No appendix. State the verification level at the end of the
response: `Verification: Claude-only, N clean passes. Not Codex-verified.`

---

## Main Loop

When researching a system and producing a document, run this loop. It governs the
entire session from first draft to completion.

**Loop structure — three phases, 50-iteration hard limit**

**Phase 1 — Claude blind iterations (up to 50 total):**
Run Claude verification passes, each one blind and isolated. Keep a counter of
consecutive clean passes and a total iteration count. When the counter reaches 3,
enter Phase 2.

**Phase 2 — Adversarial review gate (uses 1 iteration from the total budget):**

Skipping this gate entirely is never acceptable. There is always a fallback path.

Before invoking any tool, run the git check:
```bash
git -C "$(dirname DOC_PATH)" rev-parse --is-inside-work-tree 2>/dev/null
```

If the check returns `true` (document is inside a git repo): run `dual-agents-review:dual-review` with the absolute document path only. No other context — the adversarial value comes from the reviewer knowing nothing about what Claude found.

If the check returns nothing or an error (e.g., Obsidian vault, standalone file): launch two agents in parallel using the Agent tool, each with only the absolute document path and no other context:
1. `subagent_type: "pr-review-toolkit:code-reviewer"` — checks factual claims, citations and source accuracy
2. `subagent_type: "pr-review-toolkit:comment-analyzer"` — checks prose accuracy and consistency

Both agents must complete before the loop continues. Treat their findings the same way as `dual-agents-review` findings: classify each as minor or substantive, apply corrections, reset the counter if any issue is found.

In all cases: if the adversarial review finds nothing, the loop exits as verified. If it finds issues, classify each finding, apply confirmed minor corrections, reset the counter to 0, and return to Phase 1 — unless a substantive error was found, in which case enter Phase 3.

**Phase 3 — Research restart (triggered by substantive errors):**
Re-enter the Research Execution workflow from Phase 1 (Discover) or Phase 2 (Read),
depending on whether the gap requires new file discovery or just reading files already
known but insufficiently read. Complete through the Phase 2 completeness gate, then
rewrite the draft and re-enter the verification loop from a clean counter of 0. The
research restart uses iterations from the same total budget.

**If total iterations reach 50 without passing the final gate:** stop immediately,
do not attempt another pass. Prompt the user with the current document state, all
outstanding open items, and what Codex found on the last Codex check (if any).
The user decides whether to continue in a new session.

---

**Finding classification — run before any correction:**

Every finding from a Claude pass or Codex check must be classified before acting on it.
The classification determines the response.

**Minor finding** — patch inline, continue the loop:
- Style violations (em dash, Oxford comma, passive voice)
- Citation corrections (wrong line number, range doesn't cover all cited lines)
- Source table entries missing for files already read in this session
- Prose that's ambiguous but not factually wrong

**Substantive finding** — triggers Phase 3 (research restart):
- A claim is wrong about what the code does
- A code path, service, or repo was missed entirely
- An artifact was cited as active but the activation source wasn't checked (exists ≠ active)
- A config default was stated without reading the constructor
- A call chain was stopped at an interface boundary without following through
- A file was partially read and the unread tail contained relevant logic
- A parallel code path existed that the draft didn't describe

The test: would fixing this require reading new code, or just editing prose? If new code
must be read, it's substantive. Don't patch substantive errors inline — that produces a
document built on a research gap that will likely recur in the next pass or the next
session.

---

**Before every research restart — persist the finding to this skill file:**

When a substantive finding triggers Phase 3, stop before re-entering research and do
two things:

1. **Add the new failure mode to `references/failure-modes.md`** using the Edit tool.
   The entry must be specific enough that a future session reading it would recognize
   the pattern and not repeat it. Use this format:

   > - **[Pattern name].** [What happened: what the draft claimed, what the code actually
   >   showed, and why the research phase produced the wrong answer.] [What to do instead.]

   Do not write "read more carefully." Name the specific pattern: stopped at the
   interface boundary, assumed default without reading the constructor, cited the file
   without checking activation, read only 60 of 247 lines, etc.

2. **Write a note in the document itself** in the Verification Gaps section:
   > *Research restarted: [one sentence describing what was missed and why.]*

   This note stays in the final document. It is part of the verification certificate —
   a reader deserves to know that the document required a research restart and why.

Only after both writes are complete does Phase 3 begin. Update `references/failure-modes.md`
before re-entering research, not after — if the session crashes, the failure mode is
already recorded.

---

**Counter and iteration rules:**

- **Clean counter:** tracks consecutive Claude passes that found nothing. Starts at 0.
- **Total iteration counter:** counts every Claude pass, every Codex check, and every
  research restart. Hard limit of 50. Never exceed this regardless of where the loop is.
- **Claude pass — found minor issues only:** apply inline corrections, reset clean counter to 0.
- **Claude pass — found substantive issue:** persist to skill file, restart research
  (Phase 3), reset clean counter to 0.
- **Claude pass — found nothing:** increment clean counter. Do not carry findings
  from the previous pass forward; each Claude pass is blind and independent.
- **When clean counter reaches 3:** run `dual-agents-review:dual-review` (Phase 2). This uses 1 iteration from the total budget. Reset clean counter to 0 regardless of outcome.
- **Dual-review — found nothing:** loop exits to the retrospective phase. Do not
  declare the session complete yet — the self-improvement retrospective is the final
  mandatory step before done. Read `references/self-improvement.md` and run it now.
  The session is complete only after the retrospective finishes and any new failure
  modes have been recorded to `references/failure-modes.md`.
- **Dual-review — found minor issues:** apply inline corrections, reset clean counter to 0, return to Phase 1.
- **Dual-review — found substantive issue:** persist to skill file, restart research (Phase 3), reset clean counter to 0.
- **Dual-review exec failure:** treat as a failed check. Reset clean counter to 0. Investigate the failure before continuing.
- **At 50 total iterations:** stop and notify user (see below).
- **Source table changes** (any entry added, updated, or marked) reset the clean
  counter regardless of which phase triggered them.
- **Verification Gaps section contains items not yet through the 6-approach checklist:**
  treat as a minor finding. For each such gap, work through the 6 approaches. If the
  gap closes, add the file to the source table and reset the clean counter to 0. If all
  6 approaches are genuinely exhausted, update the gap entry with the specific exhaustion
  reason — the clean counter does not reset for that gap. The counter cannot reach 3
  while any gap item lacks either a source table entry or a specific exhaustion reason.
- **Confluence cross-check not yet performed:** treat as an open gap. Run
  `atlassian:search-company-knowledge` for the system being researched. Document each
  result as Confirmed, Diverged or Not found. Record the result in the document's
  source table and Verification Gaps. Only after this is done can the clean counter
  advance past 0.
- **Inline answers (no saved file):** Codex is skipped entirely. The loop exits when
  the clean counter reaches 3 on Claude-only passes. Record that the output was not
  Codex-verified. Research restarts still apply for substantive findings. The Confluence
  cross-check is still required for inline answers — record results inline rather than
  in a source table.

---

**Blind isolation for each Claude pass:**

Each Claude verification pass must be run fresh, as if seeing the document for the
first time. Do not reference what was found or corrected in previous passes. Do not
carry forward "I think the last pass cleaned this up" reasoning. Read the current
document state from disk and evaluate it independently.

This is what prevents Claude from becoming progressively less rigorous as the loop
continues. The rigor of pass 8 must equal the rigor of pass 1.

---

**Between passes:**
- Run the retrospective per `references/self-improvement.md` before starting the next pass.
- If a new failure mode was found, add it to `references/failure-modes.md` before continuing.

---

**User notification at iteration limit:**

If the total iteration counter reaches 50 without the loop exiting cleanly, stop
immediately and produce this notice:

> **Verification loop reached the 50-iteration limit without completing.**
>
> **Document:** [path]
> **Clean counter at stop:** [N] / 3
> **Last Codex check:** [pass number and summary of what Codex found, or "not yet run"]
>
> **Outstanding open items:**
> [list every source table entry that is not "direct read" or "unable to verify: [reason]"]
> [list any claim that still has an unresolved Codex finding]
>
> **Options:**
> 1. Continue in a new session — the document and its current source table are your
>    starting point; you don't need to re-research, only re-verify.
> 2. Accept the current state and note "Verification: incomplete — loop limit reached"
>    in the verification certificate.

**Skip for inline answers.** If the output was delivered inline with no saved file,
run Claude's passes only and note the skip.

---

**Blind delegation — non-negotiable**

The Codex prompt must be identical regardless of where Claude stands in the loop.
Do not tell Codex how many passes have run. Do not tell Codex whether Claude found
anything. Do not hint that the document might be complete or near-final. Do not use
phrases like "one last check," "this looks clean," or "final verification pass."

Codex walks in knowing only the document and the rules. That ignorance is the point.
If Codex knew Claude was satisfied, it would look for confirmation rather than problems.

**Pre-flight: one step only**

Record the absolute path where the document was saved this session.
Example: `/Users/justin.flammia/dd/dd-source/siem/docs/EntityContext.md`
This is the only value Claude needs to provide. Never use a relative path.

Do not pre-read the source table. Do not pre-select entries. Do not pre-construct
commands. Those decisions belong to Codex — that independence is the adversarial value.

---

## Prompting the User to Close Verification Gaps

Prompting the user is a last resort. The order is: search locally, search GitHub, read non-local repos via `gh api`, check Confluence. Only after all of those fail should you involve the user.

**The test before prompting:** Can I run `gh search code "TERM" --owner DataDog` and find the relevant code? If yes — read it. Do not prompt the user.

**When to prompt:** Only when a gap meets all of these:
1. The string, file, or config does not appear in any locally-cloned repo
2. `gh search code` with multiple search terms returned no useful matches
3. The claim cannot be verified by adjacent evidence (tests, comments, topology files)
4. The gap would materially mislead someone reading the document if wrong

**Format when prompting:**

> **Open gap: [short name]**
> What's unknown: [one sentence]
> Searches already run: [`gh search code "X"`, `gh search code "Y"`, etc.]
> What would close it: [a specific person, team, or internal resource]

After the user provides information, update the document immediately. Replace the `unable to verify` entry with `user-provided: [source]`, remove the gap from the Verification Gaps section, and run one more verification pass.

---

## Session End (mandatory — not optional)

The self-improvement retrospective runs after every session, without exception. It is
not a bonus step for when there is time. It is part of the definition of done.

Read `references/self-improvement.md` and run the retrospective now. For every
correction made during this session — whether caught by a Claude pass, the adversarial
review, or the Confluence cross-check — record the root cause. If the correction
matches a new pattern not already in `references/failure-modes.md`, add it. If it
matches an existing entry whose prescription was too vague to prevent the recurrence,
strengthen that entry.

The skill improves only because every session contributes to it. Skipping the
retrospective breaks the feedback loop that makes the skill useful over time.

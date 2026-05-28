---
name: confluence-comment-review
description: >
  Use this skill when the user wants to review and respond to inline comments on a Confluence page
  they authored, work through reviewer feedback systematically, track comment status in Obsidian, or
  run a review loop on a doc that is currently under review. The skill is idempotent — safe to run
  repeatedly on the same document without repeating work. Triggers on: "work through my Confluence
  comments", "respond to reviewer feedback", "check what's new on my doc", "run the comment review",
  "what comments came in", "new feedback on my doc", "address comments on my Confluence page", or
  when the user shares a Confluence URL and asks about reviewer comments. Also triggers when continuing
  a previous review session — always diff against what's already been addressed before doing anything new.
---

# Confluence Comment Review

This skill manages the full loop for reviewing and responding to inline comments on a Confluence doc
under review: fetching comments, diffing against what's already been addressed, drafting responses for
approval, posting approved responses, and keeping an Obsidian tracking note in sync. The process is
designed to be run repeatedly as new reviewers and new comments arrive.

---

## Phase 1: Setup (first run only)

If no Obsidian tracking note exists yet, create one at `docs/[Doc Title] - Review Feedback.md` using
this template:

```markdown
# [Doc Title] - Review Feedback

Tracking questions, concerns and feedback on the [[Doc Title]](CONFLUENCE_URL).

**Last reviewed:** YYYY-MM-DD

---

## How to Re-Run This Loop

1. Fetch all open inline comments and compare IDs against the flat ID list in "Responded" below. Any ID not in the list is new.
2. For each existing thread, fetch replies and compare reply IDs against what's recorded. Any ID not recorded is new.
3. Address new items one at a time: draft → get approval → post → update note.
4. When a Confluence comment is marked resolved, move its entry to "Resolved."
5. Update "Last reviewed" at the top.

Reviewer attribution is not returned by the Confluence MCP. Add names manually when identified.

---

## Action Items

### Doc Edits
### Research
### Research / Outreach
### Implementation

---

## Open — Needs Response

_(none yet)_

---

## Responded — Pending Resolution

Known comment IDs (for diff): _(none yet)_

---

## Slack Questions

---

## Resolved

_(none yet)_
```

---

## Phase 2: Fetch and Diff (every run)

Run these in parallel:
- `getConfluencePageInlineComments` (resolutionStatus: open) — gets all open inline comments
- `getConfluencePageFooterComments` — gets any footer comments

**Diff against the tracking note:**
1. Compare every returned comment ID against the flat ID list in the "Responded — Pending Resolution" section header. IDs not in that list are new.
2. For every comment ID that IS in the list, fetch its replies via `getConfluenceCommentChildren`. Compare returned reply IDs against those recorded in the note. Reply IDs not recorded are new.

New top-level comments → add to "Open — Needs Response."
New replies on existing threads → add as sub-entries under the existing "Responded" entry. These may change how you respond.

**Resolving reviewer attribution:**

The `getConfluencePageInlineComments` MCP does not return author information. To identify who left each comment, use CQL search with all comment IDs in a single query:

```
searchConfluenceUsingCql(
  cql: "id in (ID1, ID2, ID3, ...)",
  expand: "history.createdBy"
)
```

This returns each comment with an `author.displayName` field. Run this once after fetching comments to resolve all authors in one call. Then:
1. Update the tracking note to replace `**Reviewer:** unknown` with `**Reviewer:** [[Full Name]]` using Obsidian wiki-links
2. If the person doesn't have a profile in the vault yet, suggest creating one via `/add-person`

---

## Phase 3: Triage New Items

**Always surface every new item to the user.** Never silently log a reply as "no response needed" without presenting it first. Even a one-word acknowledgment ("ok", "thanks", "👍") is a new item the user should see. The user decides what is worth their attention. Your job is to surface everything new and let them make that call.

Before drafting anything, categorize each new item:

- **Quick answer.** The answer is clear from context and no external lookup is needed.
- **Needs research.** A code link, external doc or data lookup is required. Do the research before drafting.
- **Needs author input.** The comment raises a design question or trade-off only the doc author can resolve (e.g. "would it be cleaner to use X instead of Y?"). Summarize the trade-off for the user, present the options, get their decision, then draft the response. Do not draft a response before the author has weighed in.
- **Acknowledgment only.** The reviewer is confirming understanding, reacting or making an observation with no explicit question or ask (e.g. "ok that makes more sense", "👍", "🔥", "this introduces some interesting UX decisions"). Surface it to the user and explicitly ask whether to reply before drafting anything. Do not assume a reply is warranted and do not draft speculatively. Any reply to a pure observation risks implying commitment or forward motion the author may not want.
- **Defer.** The item is out of scope for this doc or belongs to a later phase. Say so directly.
- **Blocking.** The item requires external input (a PR link, a reviewer reply) before action is possible.

If a comment contains a link to code, follow the link and read the code before forming an opinion. Comments that look like they might change the doc's correctness claims (e.g. "I believe this can already be done") deserve verification, not just acknowledgment.

Flag blocking items with ⚠️ BLOCKING in both the action item list and the note entry. Do not attempt the associated doc edit until unblocked.

**Research obligation before escalating.** Never categorize an item as "needs clarification" or ask the user for information until you have exhausted available tools. Do this research as part of triage, before presenting anything:

- **Unknown term or system** (e.g., "Who is Iris?"). Search local vault docs with `Grep` before asking. The vault often has extensive notes on internal systems, pipelines and services.
- **Ambiguous anchor** (a single character, short phrase or period). Fetch the Confluence page with `getConfluencePage` and search for the text in context. If still ambiguous, use the comment's timestamp position relative to other comments from the same reading session to infer which section of the doc the reviewer was in. Comments from a single reviewer reading top-to-bottom are ordered by document position.
- **Diagram or API reference** (e.g., "I don't see X on the diagram"). Read the local source files (`.mmd`, `.yml`, etc.) to confirm whether the element exists before assuming it's missing.

The threshold for asking the user is genuine inability to determine the answer after using these tools, not uncertainty alone.

---

## Phase 4: Work Through Comments One at a Time

**Never present multiple comments at once.** One comment per turn, always. Wait for explicit approval or a decision before moving to the next.

Process items in this order: quick answers first, then research items, then deferrals, then blocking.

For each item, present it using this mandatory format before asking for approval:

```
**Comment [N] of [total]**
**Reviewer:** [name]
**Anchored text:** "[exact text the comment is attached to]"
**Direct link:** [full Confluence comment URL with focusedCommentId]
**Comment:**
> [full quoted comment text]

[Any existing thread replies, quoted in full]

**Draft response:**
[the proposed reply]

Approve to post or let me know if you want to adjust.
```

Everything in that block is mandatory. Do not omit the direct link, the anchored text or the full comment quote. The user must have everything they need to evaluate the response without opening Confluence.

After presenting, wait. Do not move to the next comment until the user explicitly approves, rejects or defers.

Steps for each item:

1. Present using the format above
2. Wait for explicit approval. Never post without it.
3. Post via `createConfluenceInlineComment` with `parentCommentId` set to the original comment's ID
4. Update the Obsidian note (Phase 5)
5. If the response generated a doc edit, research task or implementation requirement, add it to the relevant Action Items subsection
6. Then and only then, present the next comment

Continue until all items in the Open section have been addressed.

---

## Phase 5: Obsidian Note Sync

After each response is posted:

1. Remove the entry from "Open — Needs Response"
2. Add it to "Responded — Pending Resolution" using this format:

```markdown
### [Short descriptive title]
**Reviewer:** [name, or "unknown" — check Confluence if important]
**On:** "[exact anchored text from the comment]"
[comment](COMMENT_URL) | [our reply](REPLY_URL)

> [quoted comment text]

**Response posted YYYY-MM-DD:** [one-sentence summary of what was said]
```

3. Add **every ID that appeared in this thread** to the **Known IDs** line at the top of the "Responded" section: the top-level comment ID, every reviewer reply ID and every reply ID you posted. The format is a space-separated list of backtick-quoted IDs on a single line. This includes emoji reactions, one-word replies and any thread activity that needs no response. If an ID is not in the list, the next session will flag it as new and waste time re-triaging it. On the next session `getConfluenceCommentChildren` returns all children of each known comment. Any child ID not already in Known IDs is genuinely new and needs attention.
4. If a new reply arrived on an existing thread, append it as a sub-entry:

```markdown
**Reply (REPLY_ID), new YYYY-MM-DD:** [summary of what they said]
[our reply](REPLY_URL): [one-sentence summary]
```

5. Update "Last reviewed" at the top of the note

For blocking items, append ⚠️ BLOCKING to the section title and note what's blocking it.

---

## Drafting Rules

These rules come directly from observed preferences. The reasoning behind each one matters — follow the spirit, not just the letter.

### Pre-draft checklist (mandatory before presenting any response)

Run this scan on every draft before showing it to the user. Do not skip it because the draft "feels right."

1. **Em dashes.** Scan for U+2014. None are acceptable. Restructure into two sentences or use parentheses. (justins-voice owns the rewrite patterns.)
2. **Oxford commas.** Scan every list of three or more items. Remove any comma before the final "and" or "or". (justins-voice owns this rule.)
3. **Comma splices.** Scan for independent clauses joined by only a comma with no conjunction. "The pipeline runs, it finds nothing" is a comma splice. Split into two sentences or add a conjunction. High-risk pattern: consequence or follow-on sentences ("X happens, Y follows").
4. **Filler transitions.** Scan for "That said," "Additionally," "Furthermore," "Moreover" and similar openers. Delete them and restructure so the sentence connects naturally without a transitional crutch. (justins-voice owns this rule.)
5. **Unnecessary content.** Read the draft and ask: did the reviewer ask for this? If a sentence adds context, a caveat or a follow-up thought that the reviewer didn't request and that doesn't directly answer their question, delete it. "If the point is made, stop" means stop at the point, not after one more sentence. Also scan for mid-draft affirmations that add no information: "Both alternatives are worth considering," "This is a valid approach," "All of these are reasonable." If the sentence doesn't say anything specific, cut it.

   **Draft to the ask, not the underlying concern.** When the author gives direction like "just X" or "simply point to Y," the response should be exactly that and nothing more. The instinct to engage with the reviewer's deeper concern (e.g. "does the data model solve the right problem?") produces sentences the author didn't approve. If the author wanted that framing, they would have said so. When in doubt, do less and wait for feedback.
6. **Sycophantic or acceptance opener.** If the first word or phrase acknowledges the reviewer positively ("Good," "Thanks for," "That's") or accepts their suggestion as a preamble ("Taking this.", "Taking your advice.", "Agreed.", "Happy to."), delete it and start with the answer or action. When accepting a suggestion, lead with what you're doing: "I'll update X to use Y" not "Taking this. I'll update X to use Y." The action is the response. See justins-voice (Slack/Confluence section) for the engagement-vs-sycophancy distinction and when opening with the shared concern is appropriate.
7. **"we'll" vs "I'll".** Scan for "we'll" in doc-update commitments. Replace with "I'll."
8. **Phasing language.** Scan for "Phase 1," "Phase 2" and similar references. If the doc under review does not define these phases, replace with "this design," "this proposal" or an equivalent scope marker. Phase references that mean nothing without an external roadmap confuse readers and weaken the response.
9. **Dismissive openers.** Scan for openers that close the conversation rather than engage it. "The [X] design covers this," "That's already handled by," and similar framings signal that the reviewer's concern is a distraction. Rewrite to lead with what the design does, not with the fact that the concern is resolved.

If any of these fail, fix before presenting. Presenting a draft with a known violation and hoping the user won't notice is not acceptable.

### Voice and tone

Invoke `justins-voice` before drafting any response. It is the authoritative source for all style decisions: punctuation, active voice, sentence structure, em dashes, Oxford commas, sycophancy vs. genuine engagement and collegial tone. If it cannot be invoked, read it directly at `~/.claude/skills/justins-voice/SKILL.md`.

The following rules apply specifically to Confluence inline comment replies and are not in justins-voice:

**Never restate what the reviewer already knows.** If someone points out a fact, they know the fact. Don't echo it back as confirmation. Go straight to what it means and what you'll do next.

**Use "I'll" not "we'll"** when committing to a doc update. The doc belongs to the author. Own the edits.

**If the point is made, stop.** Don't add closing sentences that summarize what you just said, promise to keep the reviewer updated, or restate the reasoning if it wasn't asked for. One extra sentence is often one too many.

### Content rules

**Out of scope — name where it lives.** "That's out of scope for this document" is incomplete. Say where it is in scope: "covered in the RFC," "that belongs in the implementation plan," "future work for Phase 2."

**Deferring — give a brief reason.** "Deferred to a later phase" is fine if the reason is obvious. If it isn't, one sentence of explanation earns trust.

**Research before drafting.** If a comment references a code file, follow the link, read the code, and form an actual opinion before writing anything. Comments that look like they might invalidate a doc claim deserve verification. This extends to any question resolvable with tools: unknown internal system names, ambiguous anchor context, diagram discrepancies and "does X exist?" questions. See the Phase 3 research obligation for the specific tools to use.

**Design rationale questions require doc research, not inference.** When a reviewer asks "why did you choose X?" or "why does the design do Y?", do not answer from general architecture knowledge or reasoning. Fetch the relevant section of the doc being reviewed and find the stated rationale. Guessing at design intent based on how Datadog systems typically work is how wrong answers get posted. If the doc doesn't state the reason, say so and ask the author rather than inventing one.

**Blocking — ask specifically.** "Can you share the PR link?" is better than "We need more information." Be precise about what's needed.

**Don't promise unpublished things.** If the RFC isn't published yet, don't say "I'll link to it." Say "The RFC is in draft and not yet published to Confluence."

**Frame optimization as post-launch.** "This is worth tuning once we have production telemetry" is better than "We'll figure this out later."

**Avoid phasing language that has no context in the doc.** "Phase 1" means nothing to a reader who hasn't seen the roadmap. Use "this proposal" or "this design" to scope a claim to the document itself. Only use phase references if the doc explicitly defines them.

### Response categories

Each category has a generalized pattern followed by a concrete example from a real review session.

---

**Scope deferral** — the question is valid but belongs in a different document.

Pattern: `[Topic] is out of scope for this document, which focuses on [scope]. The full design will be covered in [RFC/plan/next phase].`

Example (data model doc, question about how the ER service performs federation resolution):
> The federation resolution mechanics are out of scope for this document, which focuses on the data model and Caniche join pattern. The full design will be covered in the Entity Resolution RFC, which is currently in draft.

---

**Factual answer with source** — the answer is knowable; provide it with supporting data or a reference.

Pattern: `[Direct answer]. [Source] [shows/confirms/documents] [supporting data]. [What still needs validation, if anything].`

Example (question about expected row count and run time for a new Caniche view):
> Row count will be lower than the current view since it groups by anchored entity rather than inferred entity ID. Jason's brief has a [sample distribution from org2](URL) showing that ~86% of users have 3 child identities with a long tail up to 71. We'll need to validate actual run time against the three-way join during design partner rollout.

---

**Acknowledgement + doc edit** — the reviewer added useful context the doc is missing; thank them and commit to a specific update.

Pattern: `Thanks for the context. I'll update [specific element] to reflect [what will change].`

Example (reviewer noted a field has a secondary purpose not documented in the schema comment):
> Thanks for the context. I'll update the schema comment for `entity_sub_type` to reflect that it also carries the data the Investigator needs to open an entity pivot (`entityID` and `entityType`), not just the human-readable subtype string.

---

**Blocking — ask for specific input** — a doc edit is needed but requires information the author doesn't have.

Pattern: `[Acknowledge the in-flight state]. Can you share [specific thing] so I can [specific edit] accurately?`

Example (reviewer flagged that view names are being renamed and GROUP BY is being removed, but didn't include the PR):
> Looks like this is an in-flight change. Can you share the PR link so I can update the view name references and remove the `GROUP BY entityType` from the query accurately?

---

**Action commitment with list** — committing to add a substantive new section; enumerate what it will cover so the reviewer knows what to expect.

Pattern: `I'll add [section/diagram/note] to the doc. The [items/alternatives/options] are: [numbered list]. I'll add [the section] with the reasoning behind each decision.`

Example (reviewer asked what alternatives were considered):
> I'll add a formal alternatives section to the doc. The main options considered were:
> 1. Writing resolution records directly into `redaplinfra` rather than a new track
> 2. Doing the join at query time with no dedicated resolution track
> 3. Embedding resolution logic into the existing `entityrisk-worker`
> 4. Using `AS_OF`-style temporal queries instead of explicit bounds
>
> I'll add a proper alternatives section with the reasoning behind each decision.

---

**Simple deferral / action acknowledgement** — a one-liner when the response is purely an action, no explanation needed.

Pattern: `[Action being taken].`

Example (reviewer said "worth discussing with the Caniche team"):
> Setting up a discussion with the Caniche team to work through this.

---

**Enthusiastic acknowledgement** — when a reviewer finds something genuinely significant that changes the doc's claims. Show real engagement without being performative.

Pattern: `[What's still left to confirm]. [What this means for the doc once confirmed].`

Example (reviewer found that temporal columns were already registered in the BeagleSQL schema, contradicting the doc):
> Really helpful find. What's left to confirm is whether the ON-clause range condition on those columns executes correctly in DataFusion, which is part of the Caniche team discussion I'm setting up. Once that's validated, the live-state vs temporal trade-off section needs a rewrite since the temporal join would be achievable at launch rather than deferred.

---

## Phase 6: Self-Improvement (mandatory, every session)

This phase is non-negotiable. Run it at the end of every session in which this skill was used, even a short one. The skill must improve over time by capturing what it learned from this specific interaction.

### What to look for

Review the full conversation for:

1. **Corrections** — any time the user said "no not that," "don't say X," "change this," "remove that sentence," or rewrote a draft. Each correction encodes a preference.
2. **Rewrites** — when the user edited a response before approving, compare the before and after. The delta is a rule.
3. **Rejections** — drafts the user rejected outright. What was wrong with them?
4. **Patterns that worked** — responses the user approved without pushback, especially if they were non-obvious choices. These validate the approach.
5. **New content** — response examples, framing approaches, or categories that emerged in this session and aren't in the skill yet.
6. **Voice drift** — any place where a response violated the drafting rules (sycophantic opener, em dash, "we'll" instead of "I'll", unnecessary closing sentence). Note it so the rule is reinforced.

### What to update

Make targeted edits to this SKILL.md file:

- **New rule** — if a correction reveals a pattern not covered by existing rules, add it to the Drafting Rules section with the reasoning
- **New response example** — if a response worked particularly well and represents a type not already covered, add it to the Response Categories section with the pattern and a concrete example
- **Refinement** — if existing rules need sharpening based on what you observed, edit them in place
- **Deprecation** — if a rule turned out to be wrong or too rigid based on what the user actually wanted, remove or soften it

**For repeated violations:** If a rule was violated that already exists in the skill, do not just restate it. Instead, answer: why did the rule fail? Was it not visible enough? Was there a drafting pattern that made the violation feel natural? Was the rule too vague to catch the specific case? Then add a structural fix — a mandatory checklist step, a more specific version of the rule, or a concrete example of the violation and its fix. Restating a rule that was already violated achieves nothing.

### How to update

Read the current SKILL.md, identify the specific section to change, and make a targeted edit. Do not rewrite the whole file. Do not add a "session learnings" section or timestamp entries — integrate learnings directly into the existing rule and example sections so the skill reads as a single coherent document, not a changelog.

After updating, briefly tell the user what changed and why. One sentence per change is enough. If nothing changed (every response was approved as-is with no corrections), say so explicitly.

---

## Working Through Action Items

Use `confluence-write.py` for all text edits. It fetches the current page, makes a targeted text replacement and resubmits. Inline comment anchors and page formatting are preserved exactly because only the matched text nodes change.

Script location: `~/.claude/plugins/marketplaces/datadog-claude-plugins/confluence-write/scripts/confluence-write.py`

**Workflow for text edits:**

1. Identify the exact old text (the string to find on the page) and the new text (the replacement). Get explicit user approval before applying.
2. Run a `--dry-run` first to verify the match and the result look correct.
3. Apply: `uv run python3 confluence-write.py PAGE_ID "old text" "new text"`
4. Mark the action item done in the Obsidian tracking note.

**Critical: plain-text-only match targets.** `confluence-write.py` searches text nodes inside `_INLINE_CONTAINERS` (paragraph, heading, table cell, list item, etc.). It cannot match text that spans across inline code marks. A search string like "`RESOLVED`. If the anchor" looks like one string in rendered markdown but is stored as two separate ADF nodes: a code-marked text node ("RESOLVED") and a plain text node (". If the anchor"). The script only matches within a single contiguous run of text sharing the same marks.

Always choose match targets that are entirely plain text (no backtick code spans). If the section you need to edit starts with or contains inline code marks, split the edit into multiple smaller replacements, each targeting a plain-text-only segment between code spans. Verify with `--dry-run` before applying.

**Code blocks cannot be edited with this script.** `codeBlock` nodes are not in `_INLINE_CONTAINERS`. The script will never find text inside a code block, even on a single-line match. Use a direct ADF patch for code block edits:
1. Fetch the ADF: `curl ... "https://datadoghq.atlassian.net/wiki/api/v2/pages/PAGE_ID?body-format=atlas_doc_format"`
2. Locate the target `codeBlock` node by index (enumerate `adf['content']`) and check its text content
3. Verify no annotation marks are on the block (`"marks"` with `"type": "annotation"`)
4. Replace the text node content: `block['content'] = [{"type": "text", "text": NEW_CODE}]`
5. PUT the updated ADF back with version+1

**Inline mark limitations.** The script inherits marks (bold, code, annotation) from the first character of the matched selection. If new text needs a code mark on a specific word, the replacement will land as plain text. Fix this with a direct ADF patch: fetch the page ADF via the v2 API, locate the text node, split it into three nodes (before / target word with `{"type": "code"}` mark / after), then PUT the updated ADF back. This handles any sub-span formatting the script cannot express. Do not tell the user to apply formatting manually.

**Annotation preservation.** When the old text overlaps with an inline comment anchor, the script preserves the annotation mark on surviving characters and warns only if the anchor is deleted entirely (dangling comment risk). Do not replace text that is itself the complete annotation anchor unless you intend to dangle the comment. Before any direct ADF patch, check for annotation marks on the target nodes by scanning for `"type": "annotation"` in the marks array.

**Bulk text replacement via ADF (global renames).** When doing a page-wide rename with a Python ADF patch rather than `confluence-write.py`, run an annotation check before applying any replacement:

```python
annotated = [
    node for node in all_text_nodes
    if target in node.get('text', '')
    and any(m['type'] == 'annotation' for m in node.get('marks', []))
]
```

If any annotated nodes are found, do NOT skip them silently. Replacing the text changes the displayed anchor but preserves the annotation mark ID, so the comment stays linked. This is safe because Confluence uses the mark ID for linkage, not the stored `inlineOriginalSelection` text. Proceed with the replacement across all nodes including annotated ones. (The earlier guidance to restore annotated nodes was wrong; it is not necessary.)

**Diagram action items.** Re-render from the local `.mmd` sources: `npx @mermaid-js/mermaid-cli -i <file>.mmd -o <file>.png --theme neutral --width 1600 --scale 2`. Display the rendered image for review, then upload and embed it using the two-step process below.

Step 1. Upload or update the attachment (v1 API, via curl with keychain credentials):
```bash
TOKEN=$(security find-generic-password -s "confluence-api-token" -w)
EMAIL=$(git config user.email)
AUTH=$(echo -n "$EMAIL:$TOKEN" | base64)

# New attachment:
curl -s -X POST "https://datadoghq.atlassian.net/wiki/rest/api/content/PAGE_ID/child/attachment" \
  -H "Authorization: Basic $AUTH" -H "X-Atlassian-Token: no-check" \
  -F "file=@/path/to/image.png;type=image/png" -F "minorEdit=true"

# Update existing attachment (get ATT_ID from the list endpoint first):
curl -s -X POST "https://datadoghq.atlassian.net/wiki/rest/api/content/PAGE_ID/child/attachment/ATT_ID/data" \
  -H "Authorization: Basic $AUTH" -H "X-Atlassian-Token: no-check" \
  -F "file=@/path/to/image.png;type=image/png" -F "minorEdit=true"
```

The response includes `extensions.fileId`, a UUID used as the `id` field in the ADF `media` node.

Step 2. Embed in the page body using `confluence-write.py --insert-image-after`:
```bash
uv run python3 confluence-write.py PAGE_ID "anchor text in the preceding block" \
  --insert-image-after FILE_ID_UUID \
  --collection contentId-PAGE_ID \
  --alt filename.png
```

This inserts a `mediaSingle` node immediately after the block containing the anchor text. Use `--dry-run` first to verify the insertion point.

If the inserted image renders too large (Confluence defaults to full natural width), fix the display width:
```bash
uv run python3 confluence-write.py PAGE_ID \
  --update-image-width filename.png \
  --display-width 760 \
  --media-width ACTUAL_PX_W \
  --media-height ACTUAL_PX_H
```

Target display width is 760px (matches the Confluence content column). Get actual dimensions from the PNG before running.

**Global renames.** For renames that span the whole page, direct the user to use Confluence's built-in Find & Replace in the page editor. It is a native operation that preserves comment anchors.

Work through one action item at a time. Show the before/after, wait for approval, apply, then move to the next.

---

## Key Constraints

- **Never post without approval.** Show every draft and wait for explicit "yes" before calling `createConfluenceInlineComment`.
- **Always diff first.** Before doing any work, compare comment IDs and reply IDs against the tracking note. Skip anything already addressed.
- **Fetch thread replies before drafting.** Existing replies in a thread change what needs to be said. A reviewer may have already answered their own question, or someone else may have validated the claim.
- **Reviewer attribution is unavailable from the MCP.** The inline comment API does not return author IDs. Note as "unknown" and fill in manually when identified.
- **Footer comment replies use `parentCommentId` only.** When replying to a footer comment, pass only `parentCommentId` to `createConfluenceFooterComment`. Passing both `pageId` and `parentCommentId` returns a 400 error. Inline comment replies use `createConfluenceInlineComment` with `parentCommentId`.
- **Blocking items stay blocked.** Don't make up a doc edit for an item that needs external input. Flag it and move on.
- **Always run Phase 6.** Self-improvement is not optional. If the session ends without Phase 6 running, run it before the conversation closes.

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

Before drafting anything, categorize each new item:

- **Quick answer** — the answer is clear from context and no external lookup is needed
- **Needs research** — a code link, external doc, or data lookup is required; do the research first
- **Defer** — the item is out of scope for this doc or belongs to a later phase; say so directly
- **Blocking** — the item requires external input (a PR link, a reviewer reply) before action is possible

If a comment contains a link to code, follow the link and read the code before forming an opinion. Comments that look like they might change the doc's correctness claims (e.g. "I believe this can already be done") deserve verification, not just acknowledgment.

Flag blocking items with ⚠️ BLOCKING in both the action item list and the note entry. Do not attempt the associated doc edit until unblocked.

---

## Phase 4: Work Through Comments One at a Time

Process items in this order: quick answers first, then research items, then deferrals, then blocking.

For each item:

1. Show the user the comment, its anchored text and any existing thread replies
2. Draft a response (see drafting rules below)
3. Show the draft and ask for approval — **never post without explicit approval**
4. After approval, post via `createConfluenceInlineComment` with `parentCommentId` set to the original comment's ID
5. Update the Obsidian note (Phase 5)
6. If the response generated a doc edit, research task or implementation requirement, add it to the relevant Action Items subsection

Continue until all items in "Open — Needs Response" have been addressed.

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

3. Add the comment ID to the **Known IDs** line at the top of the "Responded" section. The format is a space-separated list of backtick-quoted IDs on a single line. Just append — no prose description needed.
4. If a new reply arrived on an existing thread, append it as a sub-entry:

```markdown
**Reply (REPLY_ID) — new YYYY-MM-DD:** [summary of what they said]
[our reply](REPLY_URL): [one-sentence summary]
```

5. Update "Last reviewed" at the top of the note

For blocking items, append ⚠️ BLOCKING to the section title and note what's blocking it.

---

## Drafting Rules

These rules come directly from observed preferences. The reasoning behind each one matters — follow the spirit, not just the letter.

### Pre-draft checklist (mandatory before presenting any response)

Run this scan on every draft before showing it to the user. Do not skip it because the draft "feels right."

1. **Em dashes** — search the draft character by character for `—`. If found, rewrite the clause as two sentences or use parentheses. There are no acceptable em dashes in these responses.
2. **Unnecessary content** — read the draft and ask: did the reviewer ask for this? If a sentence adds context, a caveat or a follow-up thought that the reviewer didn't request and that doesn't directly answer their question, delete it. "If the point is made, stop" means stop at the point — not after one more sentence.
3. **Sycophantic opener** — if the first word or phrase acknowledges the reviewer positively ("Good," "Thanks for," "That's"), delete it and start with the answer.
4. **"we'll" vs "I'll"** — scan for "we'll" in doc-update commitments. Replace with "I'll."

If any of these fail, fix before presenting. Presenting a draft with a known violation and hoping the user won't notice is not acceptable.

### Voice and tone

Invoke `justins-voice` before drafting any response. If it cannot be invoked, read the skill file directly at `~/.claude/skills/justins-voice/SKILL.md` for the complete style rules.

The baseline tone is casual and direct. These are inline comments on a technical doc, not formal correspondence.

The following rules are specific to Confluence comment replies and are not covered by justins-voice:

**No sycophantic openers.** "Good callout," "Great question," "That's really helpful" and "Interesting point" are performative and add nothing. Start with the answer.

**Never restate what the reviewer already knows.** If someone points out a fact, they know the fact. Don't echo it back as confirmation. Go straight to what it means and what you'll do next.

**Use "I'll" not "we'll"** when committing to a doc update. The doc belongs to the author. Own the edits.

**If the point is made, stop.** Don't add closing sentences that summarize what you just said, promise to keep the reviewer updated, or restate the reasoning if it wasn't asked for. One extra sentence is often one too many.

### Content rules

**Out of scope — name where it lives.** "That's out of scope for this document" is incomplete. Say where it is in scope: "covered in the RFC," "that belongs in the implementation plan," "future work for Phase 2."

**Deferring — give a brief reason.** "Deferred to a later phase" is fine if the reason is obvious. If it isn't, one sentence of explanation earns trust.

**Research before drafting.** If a comment references a code file, follow the link, read the code, and form an actual opinion before writing anything. Comments that look like they might invalidate a doc claim deserve verification.

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

When the user is ready to execute doc edits from the Action Items list, do NOT use the `updateConfluencePage` API. The API requires submitting the full page body, which risks:

1. **Dangling comments.** Inline comments are anchored to specific text. Renaming or removing anchored text causes the comment to lose its anchor. The comment persists but shows as dangling.
2. **Format degradation.** The ADF/storage XML round-trip can subtly alter panels, code blocks and structured macros.

**The correct workflow for doc edits:**

1. For each action item, draft the exact text change — the precise wording to add, the specific string to rename, or the new section content.
2. Tell the user exactly where in the Confluence page to apply it (section name, heading, specific sentence).
3. Copy the text to the macOS clipboard using `pbcopy` so the user can paste it directly. Do this every time without being asked — for prose additions use plain text via `pbcopy`, for code block content use plain text via `pbcopy`. Only use the HTML clipboard method (hexdump + osascript) for rich text that needs formatting preserved outside of code blocks.
4. For diagram action items, generate the diagram using `npx @mermaid-js/mermaid-cli`. Write the Mermaid source to `/tmp/diagram-name.mmd`, render to PNG at `attachments/diagram-name.png` with `--theme neutral --width 1600 --scale 2`, then display the rendered image for review. Save the Mermaid source code in the Obsidian tracking note alongside the action item so it can be regenerated. Tell the user to upload the PNG manually to Confluence via the page editor's image upload. The user inserts the image where the diagram belongs in the doc.
4. For global renames (e.g. `siem_entity_resolution` → `siem_er`), direct the user to use Confluence's built-in Find & Replace in the page editor — it's a native operation that preserves comment anchors.
5. Once the user confirms the edit is applied, mark the action item done in the Obsidian tracking note.

Work through one action item at a time. Present the draft text, specify the location, wait for confirmation, then move to the next.

---

## Key Constraints

- **Never post without approval.** Show every draft and wait for explicit "yes" before calling `createConfluenceInlineComment`.
- **Always diff first.** Before doing any work, compare comment IDs and reply IDs against the tracking note. Skip anything already addressed.
- **Fetch thread replies before drafting.** Existing replies in a thread change what needs to be said. A reviewer may have already answered their own question, or someone else may have validated the claim.
- **Reviewer attribution is unavailable from the MCP.** The inline comment API does not return author IDs. Note as "unknown" and fill in manually when identified.
- **Footer comment replies use `parentCommentId` only.** When replying to a footer comment, pass only `parentCommentId` to `createConfluenceFooterComment`. Passing both `pageId` and `parentCommentId` returns a 400 error. Inline comment replies use `createConfluenceInlineComment` with `parentCommentId`.
- **Blocking items stay blocked.** Don't make up a doc edit for an item that needs external input. Flag it and move on.
- **Always run Phase 6.** Self-improvement is not optional. If the session ends without Phase 6 running, run it before the conversation closes.

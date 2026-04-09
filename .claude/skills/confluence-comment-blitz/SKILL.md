---
name: confluence-comment-blitz
description: >
  Use when the user wants to process all open inline comments on a Confluence page in a single batch
  workflow, review and approve everything at once before any changes are posted, or handle a high
  comment volume efficiently. Triggers on "confluence-comment-blitz", "blitz my comments", "process
  all comments at once", "batch process my Confluence feedback", or when the user wants a consolidated
  review-then-execute workflow rather than comment-by-comment iteration.
---

# Confluence Comment Blitz

Batch-oriented comment processing. Fetches all open inline comments, generates response pairs (doc edit + reply) for every comment, presents a single consolidated review for approval, then executes everything in one pass.

The key difference from `confluence-comment-review` is the workflow model: blitz collects and plans everything before asking for approval, rather than working comment by comment. Use this when there are many comments and you want to review the full picture at once.

---

## Phase 1: Fetch and Group

Run these in parallel:
- `getConfluencePageInlineComments` (resolutionStatus: open) to fetch all open inline comments
- `getConfluencePage` with `expand: body.storage` to get the current page body for ADF patching and section detection

After fetching, run a single CQL batch to resolve author names:

```
searchConfluenceUsingCql(
  cql: "id in (ID1, ID2, ID3, ...)",
  expand: "history.createdBy"
)
```

For each comment that has replies, fetch thread context via `getConfluenceCommentChildren` so the full conversation is visible before drafting.

**Grouping by section:** To find which section each comment belongs to, locate the comment's `inlineMarkerRef` text in the page body. Walk backward through the storage XML to find the nearest heading (`h1` through `h4`). That heading is the comment's section. If no heading precedes the text, group it under "Preamble."

---

## Phase 2: Generate Response Pairs

For each comment, produce:

1. **Doc edit** (if needed): the exact text change to make. If no doc edit is needed (the comment is a question, a scope deferral or a pure acknowledgement), mark as `no-edit`.
2. **Reply draft**: the reply to post on the comment thread.

**Before drafting any reply:** Invoke `justins-voice`. Apply the pre-draft checklist below to every draft before including it in the consolidated review. Do not skip it.

**Pre-draft checklist (mandatory):**
1. Em dashes: scan the draft for the em dash character (U+2014). If found, restructure the sentence. Do not substitute another punctuation mark.
2. Double-hyphen `--`: same rule.
3. Sycophantic opener: if the first word or phrase praises the reviewer, delete it and start with the answer.
4. `we'll` in doc-update commitments: replace with `I'll`.
5. Unnecessary closing sentence: if the last sentence summarizes what was just said, delete it.

**Addressing the commenter:** Use their first name from the CQL author lookup. Address them directly in second person ("you", "your"). Never refer to a commenter in third person.

**Response tone:** Casual and direct. These are inline comments on a technical doc, not formal correspondence. Follow the drafting rules and response categories in `confluence-comment-review`.

---

## Phase 3: Consolidated Review

Present the full plan to the user before taking any action. Format as a single document organized by section:

```
## Section: [Section Heading]

### Comment 1 — [Author First Name] on "[anchored text excerpt]"
> [quoted comment text]

Doc edit: [exact proposed text change, or "none"]
  Before: "[original text]"
  After:  "[replacement text]"

Reply draft:
  [full reply text]

---

### Comment 2 — ...
```

Show every comment. Include diff-style before/after for every doc edit. If a comment is deferred or out of scope, show the reply and mark doc edit as "none."

At the end of the consolidated review, ask for a single approval:

> Review all planned edits and replies above. Reply "approve" to execute, or tell me which items to revise.

Do not execute anything until explicit approval is given.

**If the user revises specific items:** Update only those items, re-present the affected sections, and ask for confirmation on the revised items before proceeding.

---

## Phase 4: Execute

Execute in two passes after approval:

**Pass 1 — Doc edits (all edits before any replies):**

For each comment that has a doc edit:
1. Fetch the current page body via `getConfluencePage` (re-fetch to get the latest version number).
2. Apply the edit as a surgical string replacement within the storage body. Only change the specific text identified in the diff. Do not alter surrounding content, macros, headings or comment anchor tags.
3. PUT the page back via `updateConfluencePage` with `version.number` incremented by 1.
4. Re-fetch the page and confirm the edit is present before moving to the next edit.

**Important:** Never replace the full page body speculatively. If the target text appears in multiple locations, identify the correct instance using surrounding context before applying the replacement.

**Pass 2 — Replies (all replies after all edits):**

Post each reply via `createConfluenceInlineComment` with `parentCommentId` set to the original comment's ID. Wait 2 seconds between each API call to avoid 500 errors.

```python
# Execution order
for edit in doc_edits:
    apply_surgical_edit(edit)
    verify_edit()

for reply in replies:
    create_inline_comment(reply)
    sleep(2)
```

---

## Phase 5: Status Report

After execution, report:

```
## Blitz Complete

Doc edits applied: N
  - [Section] — [one-line description of change]
  - ...

Replies posted: N
  - [Author] on "[anchor excerpt]" — posted
  - ...

Failures (retry manually):
  - [any that failed with error detail]
```

If any edit or reply failed, provide the exact content so the user can retry manually.

---

## Key Constraints

- **Never post without approval.** The consolidated review in Phase 3 is the only approval gate. Wait for it.
- **Address commenters by first name, directly.** Never third person.
- **Invoke `justins-voice` before drafting.** Apply the pre-draft checklist to every reply.
- **Doc edits before replies, always.** Replies confirm that changes were made. Don't post a reply promising an edit before the edit is applied.
- **Surgical ADF patching only.** Never replace the full page body. Only change the specific text identified in the diff preview.
- **2-second delay between reply API calls.** The Confluence API returns 500 errors under rapid sequential calls.
- **Re-fetch before each edit.** The version number must be current. Two edits in a row on a stale version will conflict.
- **No replies to already-resolved comments.** Check `resolutionStatus` before including a comment in the plan.

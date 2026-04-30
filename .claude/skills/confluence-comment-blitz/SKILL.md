---
name: confluence-comment-blitz
description: >
  Use when the user wants to process open inline comments on a Confluence page one at a time,
  with per-comment approval before executing each edit and reply. Triggers on
  "confluence-comment-blitz", "blitz my comments", "process my Confluence feedback" or when
  the user wants the comment-by-comment review format with doc edit diffs and reply drafts.
---

# Confluence Comment Blitz

Comment-by-comment processing. Fetches all open inline comments upfront, then presents each one
individually with a doc edit diff and reply draft. The user approves or revises each comment
before execution moves to the next.

---

## Phase 1: Fetch and Group

Run these in parallel:
- `getConfluencePageInlineComments` (resolutionStatus: open) to fetch all open inline comments
- `getConfluencePage` to get the current page body for section detection

After fetching, run a single CQL batch to resolve author names:

```
searchConfluenceUsingCql(
  cql: "id in (ID1, ID2, ID3, ...)",
  expand: "history.createdBy"
)
```

For each comment that has replies, fetch thread context via `getConfluenceCommentChildren` so the
full conversation is visible before drafting.

**Grouping by section:** To find which section each comment belongs to, locate the comment's
`inlineMarkerRef` text in the page body. Walk backward through the storage XML to find the nearest
heading (`h1` through `h4`). That heading is the comment's section. If no heading precedes the
text, group it under "Preamble."

---

## Phase 2: Per-Comment Loop

Work through comments in page order (section by section). For each comment:

### 2a. Generate the response pair

Produce:
1. **Doc edit** (if needed): the exact text change to make. If no doc edit is needed (the comment
   is a question, a scope deferral or a pure acknowledgement), mark as `no-edit`.
2. **Reply draft**: the reply to post on the comment thread.

**Before drafting any reply:** Invoke `justins-voice`. Apply the pre-draft checklist below to every
draft. Do not skip it.

**Before drafting, do three checks:**

1. **Verify factual claims.** If the comment makes an assertion about system behavior (e.g., "TH is
   eventually consistent", "REDAPL handles schemaless data"), verify it before agreeing or
   disagreeing. Use `dd-research`, read code directly or search Confluence. Don't agree with a
   claim just because it sounds plausible.

2. **Check the vault.** When the reply involves scale numbers, decisions made in prior conversations
   or vendor confirmations, search the Obsidian vault first. Meeting notes, Zoom summaries and
   Slack threads may contain verified context that belongs in the reply. Never cite a specific
   number from a derivation or AI summary. Use qualitative framing if the figure can't be verified
   from a primary source.

3. **Re-read the current doc state.** Before proposing a new doc addition, check whether the
   comment is already answered by existing content in another section. Pointing to a relevant
   section is always better than duplicating the answer. Use `getConfluencePage` with markdown
   format to read the current body if needed.

**Pre-draft checklist (mandatory):**
1. Em dashes: scan the draft for the em dash character (U+2014). If found, restructure the
   sentence. Do not substitute another punctuation mark.
2. Double-hyphen `--`: same rule.
3. Sycophantic opener: if the first word or phrase praises the reviewer, delete it and start with
   the answer.
4. `we'll` in doc-update commitments: replace with `I'll`.
5. Unnecessary closing sentence: if the last sentence summarizes what was just said, delete it.

**Addressing the commenter:** Use their first name from the CQL author lookup. Address them
directly in second person ("you", "your"). Never refer to a commenter in third person.

**Response tone:** Casual and direct. These are inline comments on a technical doc, not formal
correspondence. Follow the drafting rules and response categories in `confluence-comment-review`.

### 2b. Present the comment

Format each comment presentation as:

```
### Comment N of M: [Author First Name] on "[anchored text excerpt]"
[Section: Section Heading]

> [quoted comment text]

Doc edit: [exact proposed change or "none"]
  Before: "[original text]"
  After:  "[replacement text]"

Reply draft:
  [full reply text]
```

Then ask:

> Approve, or tell me what to revise.

Do not execute until the user approves this specific comment.

### 2c. Execute the approved comment

After approval:

1. **Doc edit first (if any):**
   - Re-fetch the current page body via `getConfluencePage` to get the latest version number.
   - Apply the edit as a surgical string replacement. Only change the specific text in the diff.
     Do not alter surrounding content, macros, headings or comment anchor tags.
   - PUT the page back via `updateConfluencePage` with `version.number` incremented by 1.
   - Re-fetch and confirm the edit is present before proceeding.

2. **Reply after edit:**
   - Post the reply via `createConfluenceInlineComment` with `parentCommentId` set to the
     original comment's ID.
   - Wait 2 seconds after posting before moving to the next comment.

Report what was done in one line, then immediately present the next comment.

### 2d. Repeat

Continue until all comments are processed. After the final comment, report totals:

```
## Done

Processed: N comments
Doc edits applied: N
Replies posted: N

Failures (retry manually):
  - [any that failed with error detail]
```

---

## Key Constraints

- **Never post without per-comment approval.** Each comment must be explicitly approved before
  its edit and reply are executed.
- **Doc edits before replies, always.** Replies confirm that changes were made. Don't post a
  reply promising an edit before the edit is applied.
- **Address commenters by first name, directly.** Never third person.
- **Invoke `justins-voice` before drafting.** Apply the pre-draft checklist to every reply.
- **Surgical edits only.** Never replace the full page body. Only change the specific text in
  the diff.
- **Re-fetch before each edit.** The version number must be current.
- **2-second delay after each reply post.** The Confluence API returns 500 errors under rapid
  sequential calls.
- **No replies to already-resolved comments.** Check `resolutionStatus` before including a
  comment in the plan.

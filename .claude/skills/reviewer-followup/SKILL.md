---
name: reviewer-followup
description: Use when Justin wants to check whether a Confluence page he reviewed (NOT authored) has actually been updated in response to his inline comments, and whether the doc is ready for his approval. This is the reverse of confluence-comment-review, which handles Justin responding to comments on his own pages. This skill handles checking whether an author responded to comments Justin left on someone else's page. Trigger on: "did [author] address my comments", "check if my feedback was incorporated", "can I approve this now", "check the status of my review comments on [page]", "has [author] updated the doc", "ready to approve this RFC", "check if Shariq addressed my comments", "were my comments resolved", or any request to evaluate a doc for approval based on prior review comments. Always trigger before Justin marks a Confluence page as approved.
---

# Reviewer Comment Followup

This skill checks whether a doc author has actually addressed Justin's review comments, both by responding in the thread and by updating the document. The goal is a clear approval decision.

## Step 1: Fetch everything in parallel

Given a Confluence page URL, extract the `pageId` from the path and fetch in a single parallel batch:
- Page content (markdown format) via `getConfluencePage`
- Open inline comments via `getConfluencePageInlineComments` (resolutionStatus: open)
- Resolved inline comments via `getConfluencePageInlineComments` (resolutionStatus: resolved)

Use `cloudId: datadoghq.atlassian.net` for all calls. Fetching open and resolved separately matters because resolved comments are often the most informative: they show what was already acknowledged and fixed.

## Step 2: Filter to Justin's comments

Justin's Atlassian author ID: `712020:12e11061-cd2b-4940-acd0-af1b111dd526`

From the combined comment list (open + resolved), keep only comments where `authorId` matches. These are the only comments to track.

## Step 3: Fetch reply threads in parallel

For each of Justin's comments, call `getConfluenceCommentChildren` to get the full reply thread. Do all of these in parallel.

The reply thread reveals what the author acknowledged. Common patterns:
- "Will fix" / "Will update" / "Updated": commitment or claim; requires doc verification
- "Will make a note": weak acknowledgment; verify whether anything changed
- "Will remove": specific claim; verify removal in doc
- Substantive reply explaining a design choice: the author may be choosing a different approach than suggested; verify the doc reflects that approach

## Step 4: Verify each comment against the doc

This is the critical step. **Do not use comment resolution status as a signal.** A resolved comment does not mean the doc was fixed. An open comment does not mean it wasn't. What matters is whether the document content actually reflects the correction.

For each of Justin's comments:

1. Read `inlineOriginalSelection` to locate the relevant doc section
2. Find that area in the fetched page content
3. Check whether the doc now says what the comment requested

**Matching claims to doc state:**
- "Will remove [X]" → verify X is gone
- "Updated" → verify the substance changed in the relevant section
- "Will update if we move over" → deferral, not a fix; note as non-blocking pending
- Substantive reply committing to a different approach → verify the doc reflects that approach (not necessarily what Justin originally suggested — the author's chosen path is what matters)

**Diagram verification:** When a reply says "Updated diagram" and the section contains an Excalidraw or similar embedded diagram link, use Playwright to open it and verify:
1. Navigate to the Excalidraw URL
2. Click "Replace my content" if prompted with a load dialog
3. Press Shift+1 to fit the diagram to the viewport
4. Take a screenshot
5. Check whether the old incorrect components are gone and the correct ones are present

Look at the actual node labels in the diagram. "Updated diagram" in a reply is a claim — the diagram may or may not actually reflect the correction.

## Step 5: Produce the report

Classify each comment into one of four states:

**Verified in doc** — the document actually reflects the correction. Clear for approval.

**Author replied, doc not updated** — the author acknowledged or committed to a change, but the document hasn't been updated to match. Blocking.

**Deferred / Non-blocking** — the author said it's intentional, out of scope, or will change during implementation. Acceptable to leave open if the reasoning is sound.

**No reply** — the author hasn't responded. Blocking.

Use this structure:

```
## Approval Status: [Ready to approve / Blocking items remain]

### Verified in doc
- Issue name: what was fixed and how you confirmed it

### Author replied, doc not updated
- Issue name: Author said "[brief quote]" but [specific thing that still needs updating in the doc]

### Deferred / Non-blocking
- Issue name: why this is acceptable to leave open

### No reply
- Issue name: original concern summary
```

Include a confidence level (High / Medium / Low) and a brief note on what you checked for each verification.

## Step 6: If blocking items remain, offer to draft a Slack message

When there are items in "Author replied, doc not updated" or "No reply", offer to draft a Slack message to the author.

When drafting:
1. Invoke the `justins-voice` skill first for voice and style
2. State what needs to change in the doc (not just what the original comment said — if the author chose a different approach, frame it around that)
3. Include deep links to each relevant comment:
   `https://datadoghq.atlassian.net/wiki/spaces/[space]/pages/[pageId]/[title]?focusedCommentId=[commentId]`
4. For items where the author's reply commits to a sound approach, acknowledge that the reply is correct and just ask for the doc to match it — this frames the ask constructively
5. Close with what resolving the items together would unlock (approval)

Use the `clipboard-slack` skill to format and copy to clipboard.

## Scope discipline

The goal of this workflow is approval, not continued review. Don't surface new issues that weren't in the original comments. The only question is: did the prior comments get addressed in the doc?

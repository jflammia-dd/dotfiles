# Verifying an Existing Document

When the task is to verify a document written in a previous session (not created this session), the workflow differs. The Source Locations table may say "direct read" for every entry, but those reads are stale — they happened in a different session and carry no current-session verification weight. Every entry is effectively unread until you read it in this session.

**Do not start the verification loop until you have re-read the sources.**

**Step 1 — Read the document.** Read the full document. Extract the Source Locations table. Note every cited file, line range, and claim.

**Step 2 — Triage the re-reads.** You don't have to re-read every file to start. Prioritize:

- Files backing claims that are specific enough to be wrong (line numbers, constant values, state machine logic, field names)
- Files backing claims that would most mislead a reader if wrong
- Files whose claims weren't verified in this session by the conversation so far

Use `superpowers:dispatching-parallel-agents` to re-read multiple files simultaneously.

**Step 3 — Re-read the prioritized files.** Use the Read tool directly. As you read each file, update the source table entry from "direct read [prior session]" to "direct read [this session]" or flag it as needing correction. Do not run the verification loop until you have direct-session reads for every high-risk entry.

**Step 4 — Run the verification loop.** Enter the loop as normal. Apply the same finding classification (minor vs. substantive), the same research restart rules for substantive findings, and the same Codex/dual-review gate. The loop runs until every source table entry shows "direct read [this session]" or "unable to verify: [reason]."

**Step 5 — Adversarial review.** The goal is two independent cold reads of the document with no knowledge of what the main session found. The specific tool depends on context.

**If the document is in a git repository:** Run `dual-agents-review:dual-review`. Pass the absolute document path only. This is the preferred path.

**If the document is NOT in a git repository** (e.g., an Obsidian vault, a standalone file outside any repo): Run `dual-agents-review:dual-review` will fail immediately. Do not attempt it. Instead, launch two `pr-review-toolkit` agents in parallel — one `code-reviewer` and one `comment-analyzer` — each receiving only the absolute document path. The agents must not receive any hints about prior corrections. Use prompts along these lines:

For `code-reviewer`:
> "Review the document at [ABSOLUTE_PATH] for factual accuracy, internal consistency, style violations and uncited claims. Check: (1) are all component names, class names and track names used consistently throughout? (2) does the Mermaid diagram match the prose? (3) are source table entries backed by specific files rather than directories? (4) are there factual claims with no source table entry? (5) are there em dashes, Oxford commas, passive voice or comma-before-coordinating-conjunction violations? Return a numbered list of findings; if none, say 'Clean.'"

For `comment-analyzer`:
> "Review the document at [ABSOLUTE_PATH] for documentation accuracy and potential misleading claims. Check: (1) are any two sections internally contradictory? (2) does the worked example match the mechanism described in the body? (3) does the verification gaps section understate any unread claims? (4) are list items checked against each other for contradictions (not just against code)? (5) do diagram arrow directions match the prose verbs (fetch/read vs. publish/write)? Return a numbered list of findings; if none, say 'Clean.'"

Check for git context before deciding which path to take:
```bash
git -C "$(dirname ABSOLUTE_PATH)" rev-parse --is-inside-work-tree 2>/dev/null
```
If this returns `true`, use `dual-agents-review:dual-review`. If it exits non-zero, use the parallel `pr-review-toolkit` approach.

**After corrections, update the verification certificate.** The format should reflect that this was a post-publication verification pass:

> `Verified: post-publication pass YYYY-MM-DD. N substantive corrections applied. All claims direct-read (this session) or unable-to-verify with reason.`

If you find no issues: `Verified: post-publication pass YYYY-MM-DD. No corrections. All claims confirmed by direct read this session.`

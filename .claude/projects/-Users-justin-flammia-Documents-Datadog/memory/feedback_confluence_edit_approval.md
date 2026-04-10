---
name: Confluence edit approval
description: Show verbatim before/after and get explicit approval before applying any Confluence page edit
type: feedback
originSessionId: 102724a9-42fc-4ed1-ba26-716886af197c
---
Before applying any edit to a Confluence page (via confluence-write.py, a Python ADF script or any other method), show the exact before/after text and get explicit approval. Do not apply after a dry-run without pausing for review.

**Why:** Confluence pages are shared documents. An applied edit is visible immediately to all readers and reviewers. Getting the before/after wrong (wrong section, wrong scope, wrong text) requires another edit to fix and may confuse in-progress review threads.

**How to apply:** Run dry-run mode first. Show the output to the user with a clear "Approve?" prompt. Only apply after an explicit yes. This applies to every edit, even small ones.

For structural edits (deleting sections, reorganizing content), show the full resulting section text, not just the diff, so the user can see how it reads in context.

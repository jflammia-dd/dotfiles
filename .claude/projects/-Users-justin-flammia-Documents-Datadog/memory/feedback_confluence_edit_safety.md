---
name: feedback_confluence_edit_safety
description: Confluence edit safety rule requiring a live page fetch before any edit, surgical changes only, no Obsidian regeneration
metadata: 
  node_type: memory
  type: feedback
  originSessionId: fdfa1da7-e87f-454c-8d43-688f1128761d
---

Before making any edit to a Confluence page, always fetch the current live version in ADF or storage format first. Make surgical edits to that fetched content. Never replace the full page body with a regeneration from the Obsidian source.

**Why:** Obsidian and Confluence diverge. Inline comments, reviewer annotations, formatting adjustments and other changes made directly in Confluence are invisible in the Obsidian source. Regenerating from Obsidian silently discards all of that. This has happened twice and caused data loss that required manual recovery.

**How to apply:**

1. Before any Confluence page edit, call `GET /wiki/api/v2/pages/{id}?body-format=atlas_doc_format` (or `?body-format=storage` for HTML edits) and hold the result.
2. Make the minimum targeted change to the fetched ADF or HTML. Replace or insert specific nodes. Do not replace the entire `content` array unless reconstructing from scratch is genuinely necessary and explicitly approved.
3. The fetched version is the safety net. If a PUT goes wrong, the fetched content is still in memory and can be used to restore.
4. If Obsidian is the only available source (page was never published), re-convert from Obsidian and publish fresh. This is acceptable only for new pages, never for existing ones.
5. Confirm body node count after PUT is roughly equal to or greater than the count before. A dramatic reduction (e.g. from 40 nodes to 0-1) is a signal that something went wrong before the PUT is made.

Related: [[feedback_confluence_edit_approval]]

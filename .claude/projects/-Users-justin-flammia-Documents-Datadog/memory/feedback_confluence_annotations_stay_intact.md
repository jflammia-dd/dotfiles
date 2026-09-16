---
name: feedback-confluence-annotations-stay-intact
description: Confluence inline-comment annotation marks must always survive an edit; verify with an ADF parser, never a regex.
metadata:
  type: feedback
---

Inline-comment annotation marks must always survive a Confluence edit. Justin stated this as a standing rule on 2026-09-16.

Verify mark presence by walking the parsed ADF for `marks[].type == "annotation"` and collecting `attrs.id`. Never grep the serialized JSON. A regex like `"annotationType":"inlineComment"` fails on key spacing and key order, which reported 0 marks on a page that actually had 7.

**Why:** a mark that silently disappears makes a reviewer's comment invisible in the UI while the API still reports `resolutionStatus: open`, so there is no signal that anything broke. The API cannot tell you a comment lost its anchor.

**How to apply:**
1. Before editing, walk the ADF and record every annotation ref.
2. Prepend or insert by fetching the existing ADF, mutating the `content` array and PUTting the same tree back. Assert the untouched nodes are byte-identical before the PUT. That preserves marks, unlike regenerating a page body from markdown.
3. After editing, walk again and compare refs and per-ref instance counts against the pre-edit record.
4. If open comments report zero marks, suspect the check before the page. `--add-annotation` on a mark that already exists is a no-op, but each run burns a page version.

See [[reference-confluence-surgical-prepend]] and [[feedback_confluence_edit_safety]].

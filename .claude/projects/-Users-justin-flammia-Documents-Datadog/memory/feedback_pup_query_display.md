---
name: Always print and copy PUP queries
description: When sharing PUP/Trino queries, always print them to screen AND copy to clipboard
type: feedback
originSessionId: 166167d7-001e-4049-a359-1acb9941bc4d
---
Always print the query as a code block in the conversation AND copy it to the clipboard via pbcopy. The user multitasks and their clipboard may be overwritten, so the screen display is the reliable reference.

**Why:** User explicitly requested this after several queries were clipboard-only.

**How to apply:** Every time a PUP/SQL query is shared, do both: render as a markdown code block in the response, and run pbcopy.

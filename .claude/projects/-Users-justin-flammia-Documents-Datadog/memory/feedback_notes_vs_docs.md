---
name: Notes vs docs placement
description: Working trackers and session notes belong in notes/, not docs/
type: feedback
---

When the user asks to "open a note" or create a working tracker for a session, put it in `notes/` with the `YYYY-MM-DD - [Description].md` naming convention. The `docs/` directory is for reference guides, runbooks, research notes and ticket workpads. Session status trackers and meeting-style working docs are notes.

**Why:** User corrected this explicitly when a status tracker was placed in docs/.

**How to apply:** Any time the user says "open a note", "create a note", or asks for a working tracker tied to a date, default to `notes/YYYY-MM-DD - Description.md`. Only use `docs/` for durable reference material.

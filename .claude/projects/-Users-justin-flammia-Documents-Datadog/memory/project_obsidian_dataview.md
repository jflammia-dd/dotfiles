---
name: Obsidian Dataview Plugin Dependency
description: All people notes and the Person template depend on the Dataview community plugin for dynamic tenure display
type: project
---

Every person note and the Person template (`templates/Person.md`) contain a `dataviewjs` block that renders a dynamic callout at the top of the note.

**What it does:** For active people, shows a blue info callout with tenure calculated from `start_date` to today (e.g., "1 year, 3 months and 22 days"). For inactive people (`status: inactive`), shows a red danger callout saying they're no longer at Datadog.

**Why:** Dataview's inline JS (`$=`) and `dataviewjs` blocks compute values at render time without modifying the file, keeping tenure always current.

**How to apply:** If the callout shows an evaluation error, check that the Dataview community plugin is installed and enabled, and that "Enable JavaScript Queries" is turned on in Dataview settings. The `dataviewjs` block uses template literals (backticks) for multi-line strings — regular double-quoted strings with literal newlines are invalid JS and will cause a SyntaxError.

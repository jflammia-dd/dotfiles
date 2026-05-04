---
name: log.md wiki-link convention
description: When writing to docs/log.md, use Obsidian wiki-links for all references to other vault documents
type: feedback
originSessionId: 0768b74c-3e44-45cb-8c41-9074f210a17a
---
Use `[[Page Title]]` wiki-link syntax (not bare file paths) when referencing vault documents in `docs/log.md`.

**Why:** Obsidian resolves wiki-links to clickable page links in the graph and editor; bare paths like `docs/Entity Context - Status.md` are dead text.

**How to apply:** Strip the folder prefix and `.md` extension: `docs/Entity Context - Status.md` → `[[Entity Context - Status]]`, `people/Loïc Fontolliet.md` → `[[Loïc Fontolliet]]`. Use `[[Title|display]]` for display aliases where helpful.

---
name: Mermaid newlines in Obsidian
description: Mermaid diagrams in Obsidian require <br/> for newlines, not \n
type: feedback
---

Use `<br/>` for line breaks inside Mermaid node labels in Obsidian. The `\n` escape does not render correctly.

**Why:** Obsidian's Mermaid renderer requires HTML line break syntax inside node labels.

**How to apply:** Any time writing Mermaid diagrams for the Obsidian vault, replace all `\n` in node labels with `<br/>`.

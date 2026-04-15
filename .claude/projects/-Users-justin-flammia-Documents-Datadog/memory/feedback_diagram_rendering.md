---
name: Diagram rendering workflow
description: How to edit and re-render Mermaid diagrams in the Datadog Obsidian vault
type: feedback
originSessionId: adcc26da-aba6-43f1-a53f-5e533cf5a199
---
Mermaid diagram sources live at `attachments/*.mmd`. After editing the source, render the PNG with:

```bash
mmdc -i attachments/diagram-name.mmd -o attachments/diagram-name.png
```

**Why:** The user manually renders when I miss it, but expects me to handle the full edit+render cycle going forward.

**How to apply:** Any time a slide or doc references a diagram that needs updating, edit the `.mmd` source and run `mmdc` to regenerate the PNG in the same step. Don't stop at editing the source.

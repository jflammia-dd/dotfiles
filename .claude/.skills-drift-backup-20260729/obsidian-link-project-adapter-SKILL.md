---
name: obsidian-link
description: This skill should be used when an obsidian:// URI appears in the conversation, or when injected context reports "Obsidian link unresolved". Resolves the URI to a vault file path and opens it. Triggers on "obsidian://open", "obsidian://vault/", "obsidian:///", a pasted Obsidian link, or a request to open a note from a link.
---

# Resolving Obsidian Links

Claude-native skill entrypoint. Canonical shared skill content lives in `agents/skills/obsidian-link/SKILL.md`.

Read that file and follow it exactly. Resolution itself runs in the `obsidian-link-resolve.py` `UserPromptSubmit` hook, wired in `~/.claude/settings.json`.

@../../../agents/skills/obsidian-link/SKILL.md

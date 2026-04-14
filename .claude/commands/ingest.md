---
description: Ingest a source into the Obsidian vault wiki. Pass a URL, or run the command and paste content.
argument-hint: "[URL or source description]"
---

# Ingest Source into Wiki

The user invoked: `/ingest $ARGUMENTS`

Use the obsidian skill's ingest workflow.

If `$ARGUMENTS` contains a URL: fetch it first, then proceed with the ingest workflow.
If `$ARGUMENTS` is empty or a description: ask the user to paste the source content, then proceed.

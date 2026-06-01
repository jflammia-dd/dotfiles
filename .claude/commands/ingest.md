---
description: Ingest a source into the Obsidian vault wiki. Pass a URL, or run the command and paste content.
argument-hint: "[URL or source description]"
---

# Ingest Source into Wiki

The user invoked: `/ingest $ARGUMENTS`

## Routing

If `$ARGUMENTS` contains a `hub.zoom.us/doc/` URL: invoke the `ingest-zoom-meeting` skill. That skill's Step 0 Option A covers how to fetch the doc via Playwright and continue with the full ingest workflow.

If `$ARGUMENTS` contains any other URL: fetch it first using WebFetch or the appropriate MCP tool, then proceed with the obsidian skill's ingest workflow.

If `$ARGUMENTS` is empty or a description: ask the user to paste the source content, then proceed with the obsidian skill's ingest workflow.

---
name: Move Zoom files to attachments on ingest
description: When ingesting a Zoom summary from a file path, move it to the Obsidian attachments folder before referencing it
type: feedback
originSessionId: d523b44c-d75a-4f0e-ad7a-44536e367a4e
---
When the user provides a Zoom meeting notes file for ingestion, move it to `attachments/` in the Obsidian vault immediately. Don't leave it in ~/Downloads or wherever it came from.

**Why:** Files in ~/Downloads are transient and will be cleaned up. The attachments folder is the vault's permanent storage.

**How to apply:** After reading the file for ingestion, run `mv "<source path>" "/Users/justin.flammia/Documents/Datadog/attachments/<filename>"` before filing notes. Update any log entries to reference the new path (`attachments/<filename>`).

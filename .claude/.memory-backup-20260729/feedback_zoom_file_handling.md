---
name: zoom-file-handling-on-ingest
description: Do NOT move Zoom source files to attachments when notes are filed to the vault from them
metadata: 
  node_type: memory
  type: feedback
  originSessionId: a91eda59-08d2-4a88-9355-2dbc0dd04702
---

When a Zoom meeting file (transcript or AI summary export) is provided as input for ingestion and notes are successfully filed to the vault, do NOT move or copy the source file to `attachments/`. The filed vault notes are the artifact. The source file is ephemeral input and can stay wherever it is or be discarded.

**Why:** Moving it to attachments was flagged as unnecessary overhead. The vault notes capture what matters. Saving the raw source alongside them creates redundancy without value.

**How to apply:** After filing notes from a file path, skip the `mv` step entirely. Do not reference the source file path in log entries.

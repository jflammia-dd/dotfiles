---
name: feedback_retriever_cli_queries
description: Always use retriever-cli to run and test Trino/DDSQL queries; generate PUP URLs for sharing
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 9e3008a4-f66c-4a3d-ba95-efe6ebacc74e
---

Use `retriever-cli` for all Trino and DDSQL query work in sessions. When running or testing queries, execute them with retriever-cli rather than describing them abstractly.

**Why:** Direct execution gives real results and catches query errors immediately. Describing queries abstractly is less useful than running them.

**How to apply:** When a query needs to be shared or distributed (in a ticket, Slack or doc), generate a PUP URL with `retriever-cli link --execution-engine <engine> --query "..."` so the recipient can open it directly in the browser without copying SQL manually.

---
name: feedback_deep_dive_reproduction_block
description: Always include a reproduction query block in deep-dive and research docs
metadata: 
  node_type: memory
  type: feedback
  originSessionId: d0961064-4b8d-463b-a727-2d62c03ab0d5
---

Every deep-dive or research doc (the kind that uses code reads plus production data to answer a question) must include a reproduction block: the exact queries or commands used to pull the data (retriever-cli invocations, SQL, the schema/table/datacenter, auth flags).

**Why:** Two reasons Justin gave. First, it lets anyone reproduce the deep-dive data later if the question resurfaces or the data changes. Second, it provides substantive proof and credibility for the work, the reader can see the evidence is real and re-run it.

**How to apply:** Keep the reproduction block in the published Confluence version, not just the vault note. It is legitimate engineering content for an engineering audience, not local-process language. Scrub only AI-tooling and personal-workflow references (agent-read, Codex-verified, "this session"); keep the real queries, schemas and access notes. See [[GitHub Actor Resolution in UEBA]] for the pattern and [[reference_retriever_cli_cloud_siem]] for the query mechanics.

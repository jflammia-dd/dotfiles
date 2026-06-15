---
name: feedback_ers_no_outbound_api
description: ERS first-order principle that all data must exist within Datadog; no outbound API calls to external systems
metadata: 
  node_type: memory
  type: feedback
  originSessionId: fdfa1da7-e87f-454c-8d43-688f1128761d
---

ERS must never make outbound API calls to external systems (AWS, PAM tools, IdPs or any other third-party service). Every resolution path must read from data already ingested into Datadog's infrastructure (EVP tracks, logs pipeline, siementity, etc.).

**Why:** This is a stated first-order architectural principle for the project, confirmed by Justin 2026-06-15.

**How to apply:** When designing or reviewing any ERS strategy or resolution path:
- If data is in an EVP track, a Datadog logs dataset, or siementity → valid
- If data requires an API call to AWS Identity Store, a PAM tool API, an IdP API, or any external service → not valid; the strategy is blocked pending an ingestion pipeline that brings that data into Datadog
- Missing datasets are expected and acceptable; they mean more ingestion work is needed before that resolution branch can be implemented
- Document the ingestion gap explicitly rather than designing around an assumed external call

---
name: reference-ddsql-unknown-provider-precedent
description: existing DDSQL CASE mapping precedent for representing a missing/unknown enum-like value
metadata: 
  node_type: memory
  type: reference
  originSessionId: 7828ebc5-5cd9-4841-a308-95dbcd285183
  modified: 2026-08-05T22:08:08.251Z
---

`cloud_siem_risk_insights_risk_scores_signals.ddsql` already has a CASE mapping convention for representing a missing or unclassifiable value in an enum-like field. This was the precedent found and followed when choosing `unknown` as the fallback for an empty `provider` tag in `siem-entity-resolution-api`'s `entityResolutionTags` (SEC-34424).

How to apply: when introducing a fallback value for a missing/unknown categorical field elsewhere in Cloud SIEM code, check this file's CASE mapping first rather than inventing a new convention.

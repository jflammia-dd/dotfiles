---
name: reference_retriever_cli_cloud_siem
description: "How to query Cloud SIEM risk-scoring and entity views with retriever-cli (schema qualifier, auth, datacenter)"
metadata: 
  node_type: memory
  type: reference
  originSessionId: d0961064-4b8d-463b-a727-2d62c03ab0d5
---

To query Cloud SIEM serving views (risk scores, signal entities, IdP identities) with `retriever-cli`:

- The risk-scoring views live in the `cloud_siem` schema and MUST be qualified: `cloud_siem.risk_insights_risk_scores`, `cloud_siem.risk_insights_risk_scores_signals`. An unqualified name fails with "relation does not exist" even though it appears in `information_schema.tables` (the catalog lists global view names; only the qualified form resolves).
- Column names are case-sensitive and must be double-quoted, e.g. `"entityProviders"`, `"entityTypes"`, `"resolvedEntityName"`, `"signalsDetected"`. Nested columns use dotted quoted names like `"entity_metadata.id"`.
- `--customer-auth=skip` reads as the employee without the customer OBO JWT. The prod datacenter blocks the OBO path for employees ("use support-admin or ISA"); skip mode works for reads.
- Datacenter: staging environment org 2 is `--datacenter us1.staging.dog --org-id 2`. Prod is `us1.prod.dog` (default).
- The IdP identity table (what ERS matches against) is `resources.siem_entity_identity` (columns: email, accounts, principal_id, external_id, provider, display_name, department, ...). The raw entity track is `events.siem_entity` (fields under `fields.*`).
- `risk_insights_risk_scores` carries both the inferred entity (`entityID`, `entityName`, `entityTypes`, `entityProviders`) and the resolved entity (`resolvedEntityID`, `resolvedEntityName`), so a resolved actor shows `resolvedEntityName` != `entityName`.
- UEBA Risk Insights views are NOT materialized in dogfood (org 197728) or prod org 2; query the staging environment org 2.

Example query is captured in [[GitHub Actor Resolution in UEBA]].

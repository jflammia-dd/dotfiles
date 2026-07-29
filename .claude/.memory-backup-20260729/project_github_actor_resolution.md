---
name: project_github_actor_resolution
description: Empirical finding on which GitHub actors resolve in UEBA/ERS and why
metadata: 
  node_type: memory
  type: project
  originSessionId: d0961064-4b8d-463b-a727-2d62c03ab0d5
---

GitHub actors reach ERS as inferred entities built from the log's OCSF observables. There are two GitHub feeds with different identity, confirmed by code and prod data (staging env org 2, 90d):

1. `github` source = commit/PR metadata, carries a corporate email (git author/committer email) -> `Email Address` entity -> resolves on the email key (~96%, 452/472).
2. `github-telemetry` source = audit log, carries only the GitHub login -> `User Name` entity -> does NOT resolve (1/579). The login appears nowhere in ingested IdP data (`resources.siem_entity_identity` accounts are email-shaped only).

The audit/login slice is the larger share of GitHub actor signal volume (~64%) and the unresolvable one. Many top login actors are GitHub App bots (non-human, belong on the classify path).

Verdicts:
- A within-trust join (audit login -> commit email) is too flimsy: the two feeds share no key, and commit emails are self-set (personal/noreply/co-author trailers).
- Resolving GitHub logins needs the GitHub-to-IdP linkage (GitHub external identities/SCIM, or IdP per-app provisioning usernames like Okta app-assignment `userName`). Verified the Entra `app_role_assignments` field cannot supply it: unpopulated in our data and structurally records app+role, not the username. The `siem-entity-crawler` fetches only core user profiles (Okta `/api/v1/users`; Entra core columns), never app assignments. Real ingestion gap, not a discarded field.
- DETERMINISM RISK: the linkage exists only where the customer configured GitHub SAML SSO + a usable NameID mapping + SCIM provisioning (or we ingest GitHub external identities). All admin opt-ins, none default. So GitHub login coverage is non-deterministic per-customer and must be raised as a coverage risk. Post-Q3.
- Q3: GitHub email-bearing activity resolves with no new work; login slice is out of Q3. GitHub needs no within-trust resolver.

Full analysis: [[GitHub Actor Resolution in UEBA]]. Query pattern: [[reference_retriever_cli_cloud_siem]]. Related: [[project_ers_three_track_structure]], [[project_ueba_q3_integration_framing]].

---
name: project_ueba_q3_integration_framing
description: "UEBA Q3 plan, prioritization and ownership for the seven new data sources, plus the principles used to defend scope"
metadata: 
  node_type: memory
  type: project
  originSessionId: 49aeed08-56c3-41f5-8bab-8c8f17430d6a
---

UEBA Q3 (2026) takes on seven sources across three thrusts: deepen CSP coverage (AWS CloudTrail, GCP, Azure, GitHub resolution), expand identity entity context (Workday, SpyCloud), begin non-human actor resolution (CrowdStrike devices + actor classification). Two canonical docs, kept in sync:
- [[UEBA Q3 Integration Briefs]] (`docs/`): the plan and value framing.
- [[UEBA Q3 Deliverables and Ownership]] (`docs/`): tactical companion, organized by team, text-only dependency tags, prioritization.
Backed by the fact-find [[UEBA Q3 Data Sources - Workday, CrowdStrike, SpyCloud]].

Frame: one entity graph, three operations. Resolve (opaque observation to known entity), enrich (context onto a known entity), relate (connect entities, the deferred convergence layer = canonical merge). Four invariants: bridge on a key, resolve at ingestion + join at read (`entity_resolution` edges), best-effort so partial counts, point-in-time via Temporal Husky.

Principles (defend scope with these):
- End-to-end over depth. Every thrust ships a thin, working, customer-visible last mile in Q3 before any goes deep. When squeezed, cut depth, not the last mile.
- Apply our own judgment to unlock value for decisions within our control; don't wait on an external signal for something already clearly valuable.
- Boundary: each goal is a quarter-buildable increment; nothing waits on the long-horizon shared capabilities (canonical entity ID is a non-blocking value-add, not a foundation).

Ownership: G+C (Quentin) builds crawlers (Workday, CrowdStrike) + the extensions producer contract. SDE (Daniel) builds the SpyCloud feed (+ REDAPL email reference-table type). I+R (Corey) owns resolution AND every customer-facing surface and drives their design (asset inventory API/UI, resolved-actor view, SpyCloud surfacing, Workday side-panel render).

Prioritization:
- IdP/CSP resolution rooted in the design-partner delivery order in [[ERS - Resolution Matrix]] (Datadog internal first, then 1Password). Build order: `AWSFederationStrategy` → `PrincipalIdExactStrategy` (principal_id) → `AccountsContainsStrategy` → GitHub/Entra identity ingestion (Entity Context, not ERS).
- The matrix is scoped to IdPs/CSPs on purpose; Workday/CrowdStrike/SpyCloud are deliberately excluded, so absence is NOT a downgrade. They're committed end-to-end on their own merits; demand provenance unconfirmed (open item, not a gate); no forced order among them.
- Non-human: partial resolution (classify + attribute) is HIGH priority for the entity volume it covers (tens of thousands of service accounts per org). Full resolution (owner-link) is out of Q3, needs non-human identity datasets such as PAM and credential-broker feeds we have no insight into.

Resolution model: corporate email is the primary human key. Federated cloud actors resolve full-path: within-trust role-chain walk → cross-trust bridge on email/username/principal_id to ANY already-ingested IdP (non-zero where the human also lives in an ingested IdP; Azure can be zero on GUID-only or `onmicrosoft.com` events). ERS commits the capability + a best-effort terminal state (INDETERMINATE / `dataset_not_ingested`), not a flat outcome. Returns one-or-more candidate IdP entries (canonical merge deferred). Builds on actor_class HUMAN/NON_HUMAN/UNKNOWN ([[ADR-0002]]).

Per-source Q3 scope: CrowdStrike = G+C schema+ingest + I+R asset inventory API/UI/design. Workday = G+C crawl + I+R read-only side-panel render on provisional `siem_entity_identity` (HRIS product brief gates only the deep lifecycle phase). SpyCloud = SDE feed + I+R consumption design + thin surfacing gated only by legal/procurement (weighted scoring deferred). Out of Q3: full non-human (PAM/broker), canonical merge, SpyCloud detection enrichment + weighted scoring, Workday lifecycle risk, deeper Azure (waits on Entra ingestion, Azure Integrations team).

Related: [[project_er_proposal]], [[project_ers_three_track_structure]], [[feedback_ers_best_effort]], [[ueba-doc-intent]].

---
name: project_ers_prod_redesign_domain_model
description: "ERS clean-slate read-path redesign; canonical doc, locked decisions and where the open questions live"
metadata: 
  node_type: memory
  type: project
  originSessionId: f50e4857-7659-451d-9679-88efcedcdd38
---

Active design artifact for the ERS clean-slate read-path rebuild: [[ERS Production Redesign - Domain Model and Lifecycle]] (`docs/`). Supersedes the PoC as code; the PoC is grain-of-salt, do not lean on its constants.

Decisions locked in the doc (2026-07-06 session):
- `actor_class` (HUMAN/NON_HUMAN/UNKNOWN) is a resolved output on `Resolution`, not a request-time fork. `EntityType` selects the strategy; the walk sets the class.
- Input retention and resolution lifecycle are decoupled (design principle 5). Source-signal retention bounds only how far back a fresh resolution can be triggered; a written record lives by the resolution track's own retention and serves any consumer by actor as-of-T.
- Ledger semantics: Temporal Husky (bitemporal layer over Husky) is the point-in-time ledger. Re-resolution appends a superseding version at valid-time T, it does NOT overwrite in place. The resolution track is an append-only materialized projection over the input ledgers, rebuildable from them, read by consumers as-of-T (CQRS-shaped read model).
- Original design stands. Temporal-Husky-as-ledger was correct all along. The "lazy / derived view" framing is a mental model, not a new architecture; a materialized resolution track still requires the settling loop and the deferred late-identity trigger to stay fresh.
- Dropped as too specific: a trigger-ID output facet (submit signal IDs, get resolution back). Actor+T query is the native facet.

Input track: risk signals come from the `entityrisk` EVP track (Temporal Husky scope `entityrisk`, `SIGNAL_GENERATED` events). Exact `entityrisk` retention was not pinned this session.

Open questions are captured in the doc's "Open questions and deferred decisions" section (10 items) plus two build-time items under "Open implementation dependencies". Highest-value unresolved item: sealed `AMBIGUOUS`/`PARTIAL` have no revival path (late-identity revives only `UNRESOLVED`, backfill handles mapping changes). Others: resolution-track retention + an Expired state are unset; `UNRESOLVED` eligibility horizon unpinned; INDETERMINATE-vs-UNRESOLVED rule for empty searches; identity continuity across the key on recreate/rename; late-sync `valid_from` backdating policy; settling-loop selection inconsistency. See [[project_risk_insights_caniche_vs_siementity]] and [[ERS - Delivery Plan]].

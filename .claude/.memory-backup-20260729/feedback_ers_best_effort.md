---
name: feedback_ers_best_effort
description: ERS second first-order principle covering best-effort resolution, the INDETERMINATE state and stop reason vocabulary
metadata: 
  node_type: memory
  type: feedback
  originSessionId: fdfa1da7-e87f-454c-8d43-688f1128761d
---

ERS is a best-effort system. It resolves as far as available data allows and stops cleanly with structured evidence. It never fails silently.

**Why:** Confirmed as a first-order architectural principle 2026-06-15. Complements the no-outbound-API principle ([[feedback_ers_no_outbound_api]]).

**How to apply:**

Resolution state model (ADR-0003 as reconciled by [[ADR-0004]], 2026-07-10, Justin's framing):
- Axis is whether ERS reached the cross-trust lookup. `INDETERMINATE` = could not attempt it (within-trust could not produce the value, OR no supported strategy for the entity type, OR anchor track fault). `UNRESOLVED` = attempted it and matched nothing.
- `INDETERMINATE` is terminal and does NOT convert to `UNRESOLVED` at settle. A settled incomplete record stays `INDETERMINATE` and keeps its partial.
- No supported strategy → `INDETERMINATE` with `stop_reason = no_supported_strategy`. This REVERSES ADR-0003's old unsupported_gap → UNRESOLVED; the stop reason keeps unbuilt strategies trackable.
- Both states still ship the furthest point reached (progressive resolution).

INDETERMINATE record carries three optional fields (defined in Q-state, populated by P-series tasks):
- `intermediate_actor`: structured ActorIdentifier for the furthest stable actor ERS reached
- `stop_reason`: one of `dataset_not_ingested` (no pipeline exists), `dataset_not_configured` (pipeline exists, org has not connected it), `data_not_found` (data exists in principle, not available for this lookup)
- `stopped_at_route`: the actor route ERS had classified the intermediate actor as (e.g. `credential_broker_session`, `aws_identity_center_user`)

actor_class REMOVED: [[ADR-0004]] (2026-07-10) supersedes ADR-0002 and withdraws the actor_class field entirely. ERS no longer classifies human vs non-human. Progressive resolution replaces it: resolve as far as the evidence allows and record the furthest identity reached. A workload terminus is the furthest point, not a NON_HUMAN class. `RESOLVED` reverts to its ADR-0001 meaning, reaching the anchored person. Classification is deferrable to a later request-driven pass. The best-effort and `INDETERMINATE` model above (ADR-0003) stands, decoupled from actor_class. Supersede compare keys on resolution_state, resolved reference and the furthest identity reached. Note: the domain-model doc's INDETERMINATE semantics still diverge from ADR-0003 and need a reconciliation pass.

Outcome-to-state mapping (post-[[ADR-0004]], final):
- UNRESOLVED = had everything needed, ran the cross-trust lookup, matched nothing. This is the ONLY UNRESOLVED case.
- INDETERMINATE = every other stop short of a completed lookup: within-trust incomplete, `dataset_not_ingested` / `dataset_not_configured` / `data_not_found`, `no_supported_strategy`, `structurally_unresolvable`, anchor fault, guardrail exit (hop cap / cycle / no-op), runtime `error`. Each carries the furthest point + stop reason.
- Runtime `error` is INDETERMINATE AND retried: it leaves a best-effort record and gets another attempt.

Sequencing rule: INDETERMINATE ships as a complete state in Q-state with all three fields defined in proto/schema as optional. P1/P2/P3 populate the fields for their respective stop conditions progressively.

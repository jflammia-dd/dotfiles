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

Resolution state model (ADR-0003):
- `INDETERMINATE` is a first-class terminal state: ERS reached a useful intermediate actor but the chain is incomplete due to a data availability constraint
- `UNRESOLVED` is narrowed: ERS made no useful progress, or a guardrail condition (hop cap, cycle, no-op) fired, or a runtime error occurred
- `unsupported_gap` always maps to `UNRESOLVED`, never `INDETERMINATE`. It is an ERS implementation gap, not a data availability constraint, and must never be used to defer work indefinitely

INDETERMINATE record carries three optional fields (defined in Q-state, populated by P-series tasks):
- `intermediate_actor`: structured ActorIdentifier for the furthest stable actor ERS reached
- `stop_reason`: one of `dataset_not_ingested` (no pipeline exists), `dataset_not_configured` (pipeline exists, org has not connected it), `data_not_found` (data exists in principle, not available for this lookup)
- `stopped_at_route`: the actor route ERS had classified the intermediate actor as (e.g. `credential_broker_session`, `aws_identity_center_user`)

actor_class rename: `INDETERMINATE` renamed to `UNKNOWN` in actor_class field (HUMAN / NON_HUMAN / UNKNOWN). INDETERMINATE is reserved for the resolution state.

Outcome-to-state mapping:
- `dataset_not_ingested` / `dataset_not_configured` / `data_not_found` → INDETERMINATE
- `unsupported_gap` / `structurally_unresolvable` / `error` / guardrail exits → UNRESOLVED

Sequencing rule: INDETERMINATE ships as a complete state in Q-state with all three fields defined in proto/schema as optional. P1/P2/P3 populate the fields for their respective stop conditions progressively.

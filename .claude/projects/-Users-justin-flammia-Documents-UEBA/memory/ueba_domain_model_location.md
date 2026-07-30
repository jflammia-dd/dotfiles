---
name: ueba-domain-model-location
description: "Where the UEBA domain model files live and how they're structured"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 63acdae5-3ac8-4a7d-9d8f-c8453f7ef876
  modified: 2026-07-30T16:26:51.114Z
---

The UEBA domain model (built 2026-07-30 via `domain-modeling`/`grill-with-docs`) lives at `/Users/justin.flammia/Documents/UEBA/`:

- `CONTEXT-MAP.md`: four bounded contexts (Entity Context, Entity Resolution, Entity Risks, User Inventory), their relationships and the device-asset scope note
- `entity-context/CONTEXT.md`, `entity-resolution/CONTEXT.md`, `entity-risks/CONTEXT.md`, `user-inventory/CONTEXT.md`: per-context glossaries
- `entity-resolution/docs/adr/0001-write-directly-to-siementity.md`: the one ADR so far, covering the REDAPL/Iris rejection and the 2026-06-15 wholesale architecture rewrite

Behavior AI and Signal are documented as adjacent/external, not modeled in depth.

Keep updating these files in place as the model evolves. See [[ueba_source_authority]] for where to go to verify or refresh claims.

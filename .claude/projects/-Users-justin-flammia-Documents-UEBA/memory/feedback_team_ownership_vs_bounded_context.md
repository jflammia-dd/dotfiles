---
name: feedback-team-ownership-vs-bounded-context
description: "Draw bounded-context boundaries from the domain model, not from current team ownership"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 63acdae5-3ac8-4a7d-9d8f-c8453f7ef876
  modified: 2026-07-30T16:27:38.661Z
---

When justifying why something should be its own bounded context (e.g. User Inventory vs Entity Context), don't lean on which team currently owns it. Justin corrected this directly when I used "Growth and Content owns the data, Entities team owns the UI" as the reason for a context split: "we need to make sure that we correct the team names and ownership boundaries. However, this might be something that operates on a different layer of conception?"

**Why:** team ownership is an organizational fact that shifts independently of the domain model (Cloud SIEM's Investigation & Response team had already split into "Entities & Investigation" and "Risk Assessment" mid-project). Baking current org structure into the justification for a context boundary means the reasoning goes stale even when the boundary itself is still correct.

**How to apply:** when a context split is proposed, find the domain-level justification first (different concerns, different data ownership, different consistency requirements) and use that as the stated reason. Team ownership can be noted as supporting evidence or tracked separately in project memory but shouldn't be the stated "why" in `CONTEXT-MAP.md` or similar durable docs.

See [[ueba_domain_model_location]] for the CONTEXT-MAP.md this shaped.

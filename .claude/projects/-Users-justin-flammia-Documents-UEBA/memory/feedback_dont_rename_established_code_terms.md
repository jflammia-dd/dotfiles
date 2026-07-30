---
name: feedback-dont-rename-established-code-terms
description: "Don't propose renaming a well-understood code identifier just to resolve a glossary/naming collision"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 63acdae5-3ac8-4a7d-9d8f-c8453f7ef876
  modified: 2026-07-30T16:27:24.085Z
---

When two concepts share a name across bounded contexts (e.g. `EntityType` meaning different things in `siem-entity-api` vs the resolution worker), don't propose a new name for the code-level identifier to disambiguate. Justin pushed back on this directly: "EntityType is a self-describing, well-understood term among the software team. There is real cost to changing this name."

**Why:** renaming an established, team-familiar code identifier has real migration cost and erodes team fluency, even if it would make the glossary cleaner in isolation.

**How to apply:** when a same-named term collides across contexts, first check whether the contexts are already modeled as separate bounded contexts. If so, document the term twice, once per context, with a cross-reference note ("same name as X's Y but a different axis"), rather than inventing a new term to force uniqueness. Only propose an actual rename when the user asks for one or when the collision is within a single context/team's own vocabulary (not across context boundaries).

See [[ueba_domain_model_location]] for where this played out (Entity Resolution vs Entity Context's `Entity Type`).

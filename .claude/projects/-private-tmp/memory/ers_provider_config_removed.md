---
name: ERS provider config removal (YAGNI)
description: Removed InferredEntitySources config entirely; entity type routing sufficient for dispatch
type: feedback
originSessionId: 325e3c5e-3f06-4761-800e-162a7981d5f1
---
**Decision:** Removed `InferredEntitySources` config file and provider gate from `AnchorLookupStrategy.CanResolve`.

**Why:** The provider gate served two purposes: (1) skip known-bad providers like GitHub, (2) feed the planner's org eligibility check. Analysis showed both were unnecessary overhead.

- Attempting resolution on any provider with detectable email format produces only UNRESOLVED if no anchor exists — no false positives, no incorrect resolutions. The 22 GitHub actors in the staging run would have been attempted, found nothing, and returned UNRESOLVED. That's the correct outcome; the provider gate just saved 22 EVP queries per tick at the cost of configuration maintenance.
- Org eligibility check can be simplified: include `AnchorLookupStrategy` for all orgs unconditionally if any IdP is configured. The planner no longer needs to enumerate which providers are "known."

**What stayed:** Entity type routing lives in code as `EntityTypeResolutionPaths` (map email-bearing types to resolution paths). This is declarative policy about what ERS can handle, not a provider registry. New entity types require code changes anyway (new resolution implementation), so config adds no value.

**What this means for future work:**
- Adding a new signal provider (e.g., Workday) requires zero ERS changes: entities flow through, get attempted, return UNRESOLVED if no anchors exist. No registration step.
- Adding a new entity type (e.g., device identity) requires adding a resolution path and methods — a code change, justified.
- The provider/IdP distinction was architectural friction that this decision removed.

**How to apply:** If someone asks why there's no provider registry, the answer is we tried it, measured the value (prevention of ~20 extra queries/tick), and removed it because configuration overhead outweighed the benefit. YAGNI.

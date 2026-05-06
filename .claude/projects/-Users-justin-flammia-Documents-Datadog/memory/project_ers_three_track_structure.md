---
name: ERS three-track project structure
description: The UEBA/ERS work has three parallel tracks with distinct owners and dependencies
type: project
originSessionId: c81bf2b9-a173-4be3-a1cb-bea71ce61e1c
---
The entity resolution work is three related tracks building toward the same outcome.

1. **Entity Context** (Engineering, Justin): crawls identity data from customer IdPs (Okta, Google Workspace, Entra ID) and surfaces it in the Entity Context sideplane UI. Going to design partners now. GitHub is NOT yet an ingested IdP; adding it is an open item blocking ERS capability 5.

2. **ERS (Entity Resolution Service)** (Engineering, Justin): maps security signal actors to verified identities in siementity. PoC complete internally. Depends on Entity Context ingestion for each provider before resolution for that provider can ship.

3. **Risk Insights Entity Rollup** (Engineering, Shariq Syed): consumes ERS output via a Caniche view to surface entity-level risk aggregation in Risk Insights. Interim approach uses a direct table join while ERS matures. Requires siementity exposure to Caniche/Beagle, which Shariq owns.

**Why:** These are distinct milestones for the same IdP. A customer can have Entity Context ingestion live before ERS resolution is live, and resolution live before Risk Insights aggregation is available. Documents in this space must track all three dimensions.

**How to apply:** When working on any ERS, Entity Context or Risk Insights planning document, frame it against all three tracks. The delivery plan covers the ERS dimension; the project overview covers all three.

Key canonical docs: [[Entity Context and ERS - Project Overview]], [[ERS - Delivery Plan]], [[ERS - Resolution Matrix]]

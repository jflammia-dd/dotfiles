---
name: Entity Resolution Design Proposal
description: Location, status and key decisions from the ER RFC built in March 2026 session
type: project
---

The file `docs/Entity Resolution - Design Proposal.md` in the Obsidian vault is an early draft of the Data Model Proposal Confluence page, not a standalone RFC. There will not be a single ER RFC. The full design will emerge from a constellation of smaller focused documents over time.

**Status (as of 2026-04-03):** The Data Model Proposal is published on Confluence (page 6460145982) and is in active review. The Obsidian file is superseded by the published page.

**What it covers:** Entity Resolution (ER) — connecting inferred entities from Cloud SIEM signals back to anchored identities in Temporal Husky. Does NOT cover Entity Relationships, Entity Context, Entity Actions or Role Chaining (EntityEnricherService is untouched).

**Key architectural decisions:**
- Scheduled execution (5-minute interval), not real-time
- Storage: new `siem_entity_resolution` EventStore track in Temporal Husky
- Input: inferred entities from EventStore `entityrisk` scope (existing Risk Insights pipeline output)
- Input: anchored entities from `redaplinfra` track (siem-entity-crawler output)
- Query model: records keyed by inferred entity ID (forward lookup O(1)); Caniche three-way join for Risk Insights reverse lookup
- Resolution states: ACTIVE, AMBIGUOUS (excluded from roll-up score), FLAGGED (future), OVERRIDDEN (future)
- Phase 1 tracer bullet: Google Workspace (IdP) → AWS (CSP) via AssumeRoleWithSAML

**Phase structure:**
- Phase 1: GW → AWS tracer bullet, dogfood inflection at milestone 1.7
- Phase 2: Entra ID + Okta + GCP + Azure, design partner ready at milestone 2.6
- Phase 3: Confidence scoring, SCIM externalId, EntityEnricherService migration, GA
- Future: User Entity notifications, AI agent resolution

**Product dependency:** Phase 1+2 together deliver the User Entity Roll-up in Risk Insights brief (Jason Hunsberger, Google Doc: https://docs.google.com/document/d/1oimUS57kyhY3LBHxxI2BYl1NYSs4cf-36MeMCwtYZSY/edit?usp=sharing). M1 success metric (30% coverage) requires Phase 2 completion.

**System diagram:** FigJam board at https://www.figma.com/board/xIyPmg0KUEgnqm2rHcbri4/. Local .jam file at `/Users/justin.flammia/Downloads/Entity Resolution – System Diagram (Phase 2 Complete).jam`.

**Key outstanding items before publishing:**
- Assign owners to open questions 1, 7, 8 (product inputs needed)
- Start EP team coordination for `siem_entity_resolution` track (milestone 1.1, doesn't need RFC sign-off)
- Update UEBA Engineering Landscape Confluence page to link back to this RFC once published

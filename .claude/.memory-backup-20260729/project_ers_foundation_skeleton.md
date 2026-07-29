---
name: project-ers-foundation-skeleton
description: The skeleton-first plan for the ERS foundation epic, freeze the seams and file locations before the provider lanes start so code does not diverge or move
metadata:
  node_type: memory
  type: project
  originSessionId: 3d46bbd5-10c0-4989-9bf0-6166976d4540
---

Decided 2026-07-10 via a grilling session. The provider swimlanes (AWS, Azure, GCP) must not start until a stubbed skeleton freezes the seams and file locations, so parallel development does not diverge and code does not move as the foundation matures.

The skeleton is frozen seams plus stubbed bodies plus the physical repo locations. Concretely:
- The proto contracts, `ResolutionRequest` and `Resolution`, frozen shape (the existing proto tickets).
- The `EntityType` enum with all four values and the mapping-table shape.
- The strategy interface and the dispatch registry.
- The source package and the worker EVP-client and anchor-read signatures.
- The `worker` and `api` package trees (the existing service-scaffold tickets), so provider code has a named place to land.
- One stubbed email exemplar showing the pattern. Email is a reference, not a matured path. A stub is enough.

Guardrails, not spoon-feeding. YAGNI applies. Provide the reference structure and one stubbed exemplar, not self-registration machinery and not pre-wired per-provider stubs. A one-line registry append per provider is fine, not divergence.

Backlog shape (agreed, apply pending). The service scaffolds and the protos already are the skeleton's start. A single stubbed-code quick-follow ticket lands the strategy seam, the enum and mapping shape, the source and anchor signatures, the reference file locations and the stubbed email exemplar. The provider swimlanes block on that stub ticket rather than on scattered foundation implementation tickets. The real implementations, email included, the as-of-T anchor, the EVP client, the RecordWriter, the resolver behavior and the three provider strategies, proceed in parallel behind the frozen seams. See [[ERS - Jira Ticket Drafts]] and [[reference_ers_epic_process]].

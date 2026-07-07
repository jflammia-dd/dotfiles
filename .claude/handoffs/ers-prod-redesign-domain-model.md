---
name: ers-prod-redesign-domain-model
created: 2026-07-06T20:05:42Z
summary: Grilled the ERS clean-slate domain-model/lifecycle doc; locked several decisions, corrected ledger semantics, captured 10 open questions
project: /Users/justin.flammia/Documents/Datadog
---

# ERS Production Redesign - Domain Model and Lifecycle

The whole session worked one artifact: `docs/ERS Production Redesign - Domain Model and Lifecycle.md`. It's the clean-slate design for the ERS read path, superseding the PoC as code. The PoC is grain-of-salt, do not lean on its constants.

## Decisions locked this session (now in the doc)

1. `actor_class` (HUMAN/NON_HUMAN/UNKNOWN) is a resolved output on `Resolution`, not a request-time fork. `EntityType` picks the strategy, the walk sets the class. Non-human terminates at the role/workload, human continues to the person anchor.
2. Input retention and resolution lifecycle are decoupled (design principle 5). Source-signal retention bounds only how far back a fresh resolution can be triggered. A written record lives by the resolution track's own retention and serves any consumer by actor as-of-T.
3. Ledger semantics corrected. Temporal Husky (bitemporal layer over Husky) is the point-in-time ledger. Re-resolution appends a superseding version at valid-time T, it does not overwrite in place. The resolution track is an append-only materialized projection over the input ledgers, rebuildable from them, read by consumers as-of-T. This is the CQRS-shaped read model.
4. Original design stands. Temporal-Husky-as-ledger was correct. The "lazy / derived view" idea explored mid-session is a mental model, not a new architecture. A materialized resolution track still needs the settling loop and the deferred late-identity trigger to stay fresh. The scale reason: pure recompute-on-read is N as-of-T anchor reads per Caniche refresh, so the materialized track is required.
5. Dropped as too specific: a trigger-ID output facet (submit signal IDs, get resolution back). Actor+T is the native query facet.

## Open, not decided (captured in the doc's "Open questions and deferred decisions" section)

Highest value: sealed `AMBIGUOUS`/`PARTIAL` have no revival path (late-identity revives only `UNRESOLVED`, backfill handles mapping changes). The other nine: resolution-track retention + an Expired lifecycle state are unset; `UNRESOLVED` eligibility horizon unpinned; the INDETERMINATE-vs-UNRESOLVED rule for an empty search; identity continuity across the key on recreate/rename; late-sync `valid_from` backdating policy; settling-loop selection inconsistency (all provisional vs retryable-status only); consumer semantics for provisional reads; as-of-now read; selective materialization.

Two build-time items were added under "Open implementation dependencies": `entityrisk` track retention (exact value unconfirmed) and concurrent-write ordering between the window pipeline and the settling loop.

## Facts confirmed

Risk signals are read from the `entityrisk` EVP track (Temporal Husky scope `entityrisk`, `SIGNAL_GENERATED` events), verified in `dd-source` at `domains/cloud-security-platform/apps/apis/siem-entity-resolution-api/internal/entity/entity.go:120` and `internal/entityreader/source.go`. The `entityrisk` scope retention was not locatable in cloned repos this session.

## Suggested next step

Pick one of the two unpinned numbers (resolution-track retention, eligibility horizon) or the sealed-status finality question, since those three make "how long do we check for updates" answerable. The doc's Open Questions section is the re-entry point.

## Suggested skills next session

`dd-research` if pinning the `entityrisk` retention or any Temporal Husky scope config. `justins-voice` before editing the doc prose (impersonal third-person spec voice). Memory: `project_ers_prod_redesign_domain_model`.

---
name: ers-state-model
created: 2026-05-27T02:30:00Z
summary: ERS resolution state model redesign, PUP query fixes and Confluence publishing
project: /Users/justin.flammia/Documents/Datadog
---

# Handoff: ERS Session 2026-05-27

## Context

Working in the `siem-entity-resolution-api` service at
`dd-source/domains/cloud-security-platform/apps/apis/siem-entity-resolution-api/`.
All active PoC work is on branch `justin.flammia/SEC-30573-entity-resolution-poc`.
The PoC epic is [SEC-30573](https://datadoghq.atlassian.net/browse/SEC-30573).
The staging test drive is `suzuki-x-90` at `rapid-td-suzuki-x-90.us1.staging.dog:443`.

---

## What happened this session

### 1. PUP query validation and fixes

`docs/ERS - Querying by Run ID.md` in the vault was audited and corrected:

- `@valid_from` and `@resolved_at` in the resolution records query were declared as `varchar` but
  are stored as `structpb.NewNumberValue` (float64). Fixed to `double`.
- Run status query was missing 9 fields present in the actual record
  (`triggered_at`, `started_at`, `completed_at`, `writes_*`, `error_message`). Added all of them.
- `GetResolutionStatus` O(n) description was imprecise. It only looks back 7 days
  (`runRecordLookback` in `run_writer.go:29`). Fixed.
- All timestamp/date fields in all three PUP queries were converted from raw epoch values to
  `from_unixtime(... / 1000)`. `started_at` and `completed_at` use `IF(... > 0, ..., NULL)`
  guards because they are zero until the run reaches those states.
- All three queries were validated live in PUP against org 2 staging and pass cleanly.

### 2. Resolution state model redesign

A full design discussion produced a new state model for `resolution_state` and a new
`resolution_sub_state` field. Key decisions:

- Old `PARTIAL` (anchor found, IdP fields incomplete) is removed. IdP completeness is
  orthogonal to resolution. Finding one anchor = `RESOLVED`.
- `completeness_score` and `missing_evidence` removed (YAGNI).
- New `PARTIAL` means within-trust ran and produced an intermediate identity; cross-trust found
  nothing. This is more informative than `UNRESOLVED`.
- `UNRESOLVED` now means no new information was discovered at all.
- Sub-states provide pipeline-stage diagnostics without polluting the primary state.
- Resolution chain (`resolution_chain`) will be persisted to `siementity` alongside the state;
  currently it is logged via `resolve_chain_step` events only (design gap vs. system design spec).

Full model:

| `resolution_state` | `resolution_sub_state` | Meaning |
|---|---|---|
| `RESOLVED` | (none) | One anchor found |
| `AMBIGUOUS` | (none) | Multiple anchors found |
| `PARTIAL` | `WITHIN_TRUST_COMPLETE` | WT complete, cross-trust found nothing |
| `PARTIAL` | `WITHIN_TRUST_INCOMPLETE` | WT stalled before reaching cross-trust |
| `UNRESOLVED` | `NO_WITHIN_TRUST` | No WT applicable; cross-trust found nothing |
| `UNRESOLVED` | `WITHIN_TRUST_FAILED` | WT applicable but zero progress on first pass |

`FLAGGED` and `OVERRIDDEN` remain reserved and unchanged.

### 3. ADR written

`docs/ADR-0001 - ERS Resolution State Model.md` in the vault captures the full decision,
considered options and consequences. Do not rewrite it; reference it.

### 4. Jira tickets created

- [SEC-32004](https://datadoghq.atlassian.net/browse/SEC-32004): Redesign ERS resolution state
  model. Covers the enum, sub-states, pipeline routing, proto, tests and removal of
  `completeness_score` / `missing_evidence`.
- [SEC-32005](https://datadoghq.atlassian.net/browse/SEC-32005): Persist resolution chain to
  siementity. Covers `buildCustomFields` serialization, round-trip via `LoadPriorResolutions`,
  PUP query update and tests. Depends on SEC-32004.

### 5. Confluence published

New page: [ERS: Resolution State Model](https://datadoghq.atlassian.net/wiki/spaces/CSiem/pages/6771409239)
under the [Entity Resolution](https://datadoghq.atlassian.net/wiki/spaces/CSiem/pages/6531219996)
parent. Follows the series doc convention (author table with @mention, rich date node, Review
Status table matching the SAML doc, series navigation links).

Parent index updated to add item 10 with a green NEW pill (version 11).

[Entity Resolution Service: System Design](https://datadoghq.atlassian.net/wiki/spaces/CSiem/pages/6525748475)
updated to version 102: a note appended to the State Transitions section pointing to the new doc.

---

## What is not done yet

The two Jira tickets (SEC-32004, SEC-32005) are unimplemented. The code still uses the old flat
state enum. The implementation touches:

- `internal/entity/entity.go`: `ResolutionState` enum, new `ResolutionSubState` type,
  `ResolutionRecord` and `ResolutionResult` structs
- `internal/pipeline/pipeline.go`: outcome routing logic
- `internal/recordwriter/evp_writer.go`: `buildCustomFields` (sub-state field + chain serialization)
- `internal/recordwriter/prior_state.go`: `LoadPriorResolutions` chain deserialization
- Proto definitions and `GetResolutionStatus` handler
- All affected tests
- `docs/ERS - Querying by Run ID.md`: add `@resolution_chain` column once SEC-32005 is implemented

---

## File locations

| Artifact | Location |
|---|---|
| PUP query reference | `docs/ERS - Querying by Run ID.md` (vault) |
| ADR | `docs/ADR-0001 - ERS Resolution State Model.md` (vault) |
| Core domain types | `internal/entity/entity.go` |
| EVP writer | `internal/recordwriter/evp_writer.go` |
| Run record writer | `internal/recordwriter/run_writer.go` |
| Writer (logs + write logic) | `internal/recordwriter/writer.go` |
| Prior state loader | `internal/recordwriter/prior_state.go` |

---

## Suggested skills

- `superpowers:test-driven-development`: invoke before writing any implementation code for
  SEC-32004 or SEC-32005
- `dd-research`: use before modifying pipeline routing or proto definitions to verify current
  call chains and confirm no other consumers of `ResolutionState` were missed
- `justins-voice`: invoke before writing any human-facing prose (Confluence comments, Jira
  updates, Slack messages)
- `confluence-write`: for surgical edits to existing Confluence pages
- `dd:pr:address-feedback`: for addressing review comments once the implementation PRs are up

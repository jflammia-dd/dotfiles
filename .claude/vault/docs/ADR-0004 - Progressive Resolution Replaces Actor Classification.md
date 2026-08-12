# ADR-0004: Progressive Resolution Replaces Actor Classification

> [!info] Not yet published to Confluence
> This note needs to be published to the CSiem space. The existing ADR-0002 and ADR-0003 pages should be updated to reflect the supersede and amendment.

## Status

Proposed

Date: 2026-07-10

Supersedes: [[ADR-0002 - Human and Non-Human Actor Classification]]
Amends: [[ADR-0003 - Best-Effort Resolution and INDETERMINATE Terminal State]]
Extends: [[ADR-0001 - ERS Resolution State Model]]

## Context

[[ADR-0002 - Human and Non-Human Actor Classification]] proposed `actor_class` (`HUMAN`/`NON_HUMAN`/`UNKNOWN`) as an orthogonal field alongside `resolution_state`. It broadened `RESOLVED` from "reached the anchored person" to "reached a definitive identity" so a confidently identified machine could terminate in a success state without an IdP anchor. The resolution worker never implemented it.

The broadening overloaded `RESOLVED`. A consumer reading `RESOLVED` could no longer assume an IdP anchor was found. It had to read a second field (`actor_class`) to know whether the result was a person or a machine. It then recombined two axes to understand the outcome.

The problem ADR-0002 identified was real: a machine should not share `UNRESOLVED` with a human ERS failed to identify. The solution created more complexity than the problem warranted.

## Decision

### 1. Remove `actor_class`

ERS does not persist a human-versus-workload classification. The `actor_class` and `actor_class_reason` fields proposed in [[ADR-0002 - Human and Non-Human Actor Classification]] are withdrawn. A record carries `resolution_state`, the resolved reference, the furthest identity reached, and the audit trail. Nothing on the record labels the actor a person or a machine.

### 2. `RESOLVED` reverts to the [[ADR-0001 - ERS Resolution State Model]] meaning

`RESOLVED` means ERS reached the anchored person. The broadening to "reached a definitive identity" is withdrawn. A workload terminus (service principal, managed identity) is not `RESOLVED`. ERS attempts the cross-trust lookup on the role or service account, finds no person, and terminates `UNRESOLVED` carrying the workload identity as the furthest point reached.

### 3. Progressive resolution is the organizing principle

ERS resolves each actor as far as the available data allows and records the furthest identity it reached. This affirms the best-effort principle in [[ADR-0003 - Best-Effort Resolution and INDETERMINATE Terminal State]]. A resolution that cannot reach the person still carries the intermediate actor it did reach. A consumer gets the role, session, or service account instead of a bare non-answer.

### 4. Supersede compare keys on the furthest identity

The single writer appends a superseding version only when the resolution outcome moves. With `actor_class` gone, the comparison is `resolution_state`, the resolved reference, and the furthest identity the walk reached. The furthest identity is stable across attempts and moves only when the walk actually gets further.

A deeper walk supersedes a shallower one even when the state and the resolved reference have not changed. This is what makes progressive progress persist.

### 5. [[ADR-0003 - Best-Effort Resolution and INDETERMINATE Terminal State]] amendment: `INDETERMINATE` and `UNRESOLVED` align to whether ERS reached the cross-trust lookup

ADR-0003 split `INDETERMINATE` and `UNRESOLVED` on whether ERS reached a useful intermediate actor. The split is now whether ERS reached the cross-trust lookup at all.

`UNRESOLVED` is the single narrow outcome: ERS had everything it needed, ran the cross-trust lookup, and matched nothing. Every other stop short of a completed lookup is `INDETERMINATE`, carrying the furthest point ERS reached plus a stop reason. The causes are:

1. A within-trust step could not produce the value to query.
2. The actor's shape cannot be traced to anything queryable.
3. The entity type has no supported strategy.
4. The anchor track faulted.
5. A guardrail fired: hop cap, cycle, or no-op next actor.
6. A runtime error interrupted the attempt.

The `no_supported_strategy` case takes `stop_reason = no_supported_strategy` and maps to `INDETERMINATE`. This reverses ADR-0003's mapping of an implementation gap to `UNRESOLVED`. The stop reason keeps an unbuilt strategy visible rather than hiding it as a data gap.

A runtime error is `INDETERMINATE` and also retried. A failure both leaves a best-effort record and gets another attempt. `INDETERMINATE` is terminal at settle. It does not convert to `UNRESOLVED`, since a resolution that never reached the lookup cannot become one that ran and matched nothing.

ADR-0003's `intermediate_actor`, `stop_reason`, and `stopped_at_route` fields and the rest of its stop-reason vocabulary stand. The axis changes, along with the mappings for `no_supported_strategy`, guardrail exits, and runtime errors.

### 6. ADR-0003 amendment: `actor_class` rename is moot

With `actor_class` removed entirely, the rename from `INDETERMINATE` to `UNKNOWN` is moot. The `actor_class` value set no longer exists.

## What changes from previous documents

| Document | What it said | What this ADR changes |
|---|---|---|
| [[ADR-0001 - ERS Resolution State Model]] | `RESOLVED` means "exactly one anchor found" | Unchanged. The broadening is reverted. |
| [[ADR-0002 - Human and Non-Human Actor Classification]] | `actor_class` field (`HUMAN`/`NON_HUMAN`/`UNKNOWN`) on every record | Withdrawn entirely. No `actor_class` or `actor_class_reason` on the proto or schema. |
| [[ADR-0002 - Human and Non-Human Actor Classification]] | `RESOLVED` broadened to "reached a definitive identity" | Reverted to ADR-0001's meaning, reached the anchored person. |
| [[ADR-0002 - Human and Non-Human Actor Classification]] | `NON_HUMAN` + `RESOLVED` = machine identified, no anchor needed | A machine terminus is `UNRESOLVED` carrying the workload identity as the furthest point reached. |
| [[ADR-0003 - Best-Effort Resolution and INDETERMINATE Terminal State]] | `actor_class = INDETERMINATE` renamed to `UNKNOWN` | Moot. `actor_class` no longer exists. |
| [[ADR-0003 - Best-Effort Resolution and INDETERMINATE Terminal State]] | `INDETERMINATE` vs `UNRESOLVED` split on whether ERS reached a useful intermediate actor | Split now hinges on whether ERS reached the cross-trust lookup at all. |
| [[ADR-0003 - Best-Effort Resolution and INDETERMINATE Terminal State]] | `unsupported_gap` maps to `UNRESOLVED` | Reversed. `no_supported_strategy` maps to `INDETERMINATE` with `stop_reason = no_supported_strategy`. |

## Consequences

**Positive:**

- One axis carries the resolution outcome. `RESOLVED` again means an anchored person, so a consumer reads a single field without recombining two.
- Every record is simpler. No `actor_class` or `actor_class_reason` on the proto or the `siementity` schema.
- Partial progress is the first-class output. A workload or an incomplete chain surfaces the furthest identity reached rather than a classification, which is what an investigator acts on.
- Classification stays open. A later request-driven pass can add a human-versus-workload label without reworking the resolution contract.

**Negative:**

- A consumer that wanted a definitive machine-versus-human signal on every record does not get it from ERS today. It reads the furthest identity and the route instead. A later classification pass can add the label.
- A confidently identified machine is not a `RESOLVED` success. It is an incomplete chain carrying the workload identity, which a consumer reads from the intermediate actor rather than the state alone.

**Neutral:**

- [[ADR-0002 - Human and Non-Human Actor Classification]] is not implemented, so no migration is required to withdraw it.
- [[ADR-0001 - ERS Resolution State Model]]'s primary state taxonomy is unchanged. [[ADR-0003 - Best-Effort Resolution and INDETERMINATE Terminal State]]'s best-effort principle and structured evidence stand. Its `INDETERMINATE` axis is repointed and the `no_supported_strategy` case now maps to `INDETERMINATE`, both recorded here.

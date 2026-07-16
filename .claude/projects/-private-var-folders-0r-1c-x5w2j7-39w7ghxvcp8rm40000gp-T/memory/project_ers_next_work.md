---
name: ers-active-work
description: Entity resolution service (ERS) next work item and related tickets
metadata: 
  node_type: memory
  type: project
  originSessionId: d005f7fe-8bbb-4acb-b041-533ab0eadf3c
---

## Active Work

SEC-34237 (Core resolver) is the selected next work item, marked In Progress as of last session end.

**Why:** ERS is the primary current initiative; resolver is critical path in the epic.

**How to apply:** When starting next session, check SEC-34237 status and continue from last checkpoint.

## Related Tickets Context

- SEC-34229: ERS worker Snap scaffold (merged PR #20972)
- SEC-34231: Proto trigger_info fix (merged)
- SEC-34233: Strategy interface, domain types, validating constructor (merged post-review)
- SEC-34232: siem_entity_resolution_api proto (PR #21104, needs rebase with extended AnchorChangedResponse)
- SEC-34241/34250: Dependent work requiring matched/dedup/enqueue counts and failure tracking

## Design Notes

AnchorChangedResponse requires: epochs, matched count, dedup count, enqueue count, failures per SEC-34241/34250 (flagged in PR #21104 review).

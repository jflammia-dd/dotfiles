---
name: project_ers_q2_commitment
description: "ERS Q2 delivery commitment for federation and role chain resolution (June 30, 2026)"
metadata: 
  node_type: memory
  type: project
  originSessionId: 52f74ec4-b766-42f8-bb6f-1af65554dce4
---

Both ERS roadmap items committed to Q2 delivery (June 30, 2026), confirmed with Corey Finley via Google Sheets comments on 2026-06-08.

**Why:** Corey questioned the roadmap statuses. Federation resolution was correctly "In development." Role chain resolution was stale ("Scoping") and was updated to "In development" since that IS the CloudTrail AssumeRole tracing work actively in progress.

Delivery definition:
- Both federation resolution and role chain resolution deployed to production behind a feature flag for org 2
- PoC state: resolution pipeline works end-to-end but may have rough edges
- Remaining blocker: Dash freeze lifts June 11, after which SEC-32319 and SEC-32597 can merge

**How to apply:** When discussing ERS timeline with stakeholders, the committed date is June 30 in PoC/feature-flag state. Do not quote GA or full production rollout for Q2.

Roadmap doc: [Cloud SIEM - Roadmap - 2026](https://docs.google.com/spreadsheets/d/1uBCafGiXjcEm9cmEzVuEFscftEb_q_BJaExEakWoCAg), sheet "[Q2 26] Investigation and Response - Project List", rows 15-16.

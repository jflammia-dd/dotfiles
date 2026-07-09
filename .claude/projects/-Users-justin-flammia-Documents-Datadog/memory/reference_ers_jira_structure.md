---
name: reference-ers-jira-structure
description: "How ERS/UEBA work maps in Jira, the OKR/Initiative/Epic hierarchy and which epics hold ERS build vs consumer work"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 3d46bbd5-10c0-4989-9bf0-6166976d4540
---

ERS Q3 Jira hierarchy (Datadog Atlassian cloudId `66c05bee-f5ff-4718-b6fc-81351e5ef659`): Goal/Objective (issue type `Goal`, level 3, `SECPRODK9`) → Initiative/Key Result (issue type `Initiative`, level 2, `SECPRODK9`) → Epic (`SEC`, level 1) → Story/Task/Bug (level 0) → Sub-task (rare).

Objective `SECPRODK9-1292` = UEBA (User Entity Behavior AI), owner Jason Hunsberger. Dashboard `5uz-bvt-5e4`, which queries the epics within an initiative. Three KRs (Initiatives):
- KR1 `SECPRODK9-1301`: IdP directory import + Entity Risks experience. Product/UI/consumer epics.
- KR2 `SECPRODK9-1302`: attribution rate on human-actor signals. The ERS BUILD lives here.
- KR3 `SECPRODK9-1303`: Behavior AI detection (TPR/FPR).

ERS build epics under KR2: `SEC-33707` (AWS role-chained), `SEC-33708` (GCP SA impersonation), `SEC-33709` (Azure object-ID GUID), `SEC-33713` (point-in-time), plus a NEW epic "Resolve Email Address Actors to the Human" (foundation + email + settling + anchor watcher + operator + ops) that replaces the PoC epic. `SEC-30573` (ERS: PoC Implementation) is being CLOSED: mark Done, Won't-Do open children, recreate fresh. Corey approved mark-done + new epic under the same initiative; do NOT rename or delete existing epics. Do NOT use `SEC-30573` or its children as a Jira style reference; those were Justin's own.

`SEC-33721` (Risk Insights Roll-Up to Use ERS Resolved Users) is under KR1, the downstream CONSUMER of ERS output, not the build.

Team Jira conventions (Corey/SIEM, full note [[Cloud SIEM - Jira Conventions and Patterns]]): epics immutable + outcome-oriented (tied to OKR reporting); Story/Task by Jira definitions; no sub-tasks; relationships in NATIVE fields only, never description text (parent for aggregation, `is blocked by` links for the dependency DAG); sequencing via sprints + priority (team adopting is-blocked-by for these epics); components mirror the parent epic; labels sparse/gating-only; OKR labels on the epic not children; no sizing at creation.

Finalized plan→Jira mapping + logical ticket list with DAG: [[ERS - Jira Structure and Backlog Mapping]]. Engineering plan: [[Entity Resolution Service - Engineering Plan and Backlog]]. See also [[project_ers_three_track_structure]].

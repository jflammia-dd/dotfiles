---
name: reference-cloud-siem-jira-conventions
description: "K9 Cloud SIEM team's Jira conventions, how to structure epics/tickets so planning maps to native fields and OKR reporting"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 3d46bbd5-10c0-4989-9bf0-6166976d4540
---

K9 Cloud SIEM Jira conventions (how Corey and the SIEM org run the boards). Full note: [[Cloud SIEM - Jira Conventions and Patterns]].

Hierarchy (two projects): Goal/Objective (`Goal` type, level 3) → Initiative/Key Result (`Initiative` type, level 2), both in `SECPRODK9` → Epic (level 1) → Story/Task/Bug (level 0) → Sub-task (rare), in `SEC`. OKR dashboards query the epics within an initiative and roll children up by parent link.

Epics are effectively immutable (tied to reporting). Do not rename or delete an existing epic; edit description and add tickets only. To retire one, mark it Done and create a new epic under the same initiative, never replace in place. Epics are outcome-oriented (a measurable KR-moving capability), not delivery phases. Uneven epics are fine; scale is carried by ticket count, not by re-carving epic boundaries.

Issue types by the Jira definitions: Story = user-facing capability, Task = enabling work (infra, refactor, ops, docs, spikes), Bug = defect. Flat list under the epic, no sub-tasks.

Relationships in NATIVE fields only, never in description text: parent link for aggregation (Story/Task→epic→initiative), `is blocked by` issue links for the dependency DAG (link only genuine prerequisites, keep sparse). Sequencing runs on sprints + the priority field; the team historically does not use blocks-links, so adopting them is a deliberate add that only helps if honored in sprint planning.

Ticket fields: components on every ticket mirroring the epic (`Cloud SIEM - Risk Assessment`, `Cloud SIEM - Investigation & Response`; SEC requires a component at creation); labels sparse and gating-only (`needs-product`, `needs-design`); OKR/quarter labels on the epic not children; priority on every ticket; no story points at creation (set in refinement).

Applied to ERS: [[reference_ers_jira_structure]].

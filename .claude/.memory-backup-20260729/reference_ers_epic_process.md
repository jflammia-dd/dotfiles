---
name: reference-ers-epic-process
description: The repeatable ERS process for fact-checking a drafted epic and shaping its tickets, apply to each new provider or foundation cohort before touching Jira
metadata:
  node_type: memory
  type: reference
  originSessionId: 3d46bbd5-10c0-4989-9bf0-6166976d4540
---

Process doc: [[ERS - Epic Fact-Check and Ticket-Shaping Process]] (in `docs/`). Apply once per ERS epic before creating anything in Jira. Built on Azure (SEC-33709), refined on AWS (SEC-33707).

Three phases: fact-check (deeplinked research against primary sources, never PoC code or PoC Jira tickets) → report (findings as an appendix on the drafts, stop for Justin's review) → apply (rework/fold/create, renumber in dependency order, sync the DAG, trim the appendix to durable findings and keep it handle-free).

Ticket-shaping rules that matter most, learned across Azure and AWS:
- Native fields carry structure. No parent, dependency or ordering in description prose.
- Right-size both ways. Fold a sub-step or a ticket that only extends another (chain extension into the walk, two adjacent spikes into one). Do not collapse distinct mechanisms into one giant ticket.
- Number in dependency order. Prerequisites carry lower numbers. Spikes first, story last. Handles are throwaway, renumber freely.
- Standalone readability. No Obsidian or local-doc refs, no prod metrics or customer data, GitHub links for code.
- Acceptance names the domain-model status (`RESOLVED` / `UNRESOLVED` / `INDETERMINATE`) and states the partial it still delivers (progressive resolution, some resolution beats none).
- Cross-team: a real dependency is a ticket on the owner's epic linked `is blocked by`; reuse of existing functionality is a research-and-collaboration spike, not build work on their board.
- Align to the domain model and ADRs. Escalate a design gap to an ADR, do not bake an ad-hoc choice into a ticket.
- Defer eventual-but-not-now work to an out-of-scope note with its owner named, never a ticket.

Next cohorts: GCP (SEC-33708), the foundation/email epic, the IdP anchor side. See [[reference_ers_jira_structure]], [[ERS - Jira Ticket Drafts]], [[ERS - Jira Structure and Backlog Mapping]].

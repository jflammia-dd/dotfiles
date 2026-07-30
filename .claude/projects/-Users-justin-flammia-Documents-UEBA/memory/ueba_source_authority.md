---
name: ueba-source-authority
description: "Where to find and how to weigh UEBA/Entity Resolution source material (Confluence, Jira, code, product briefs)"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 63acdae5-3ac8-4a7d-9d8f-c8453f7ef876
  modified: 2026-07-30T16:27:13.886Z
---

Code lives under `/Users/justin.flammia/dd/dd-source/domains/cloud-security-platform/apps/apis/`: `siem-entity-api`, `siem-entity-resolution-api`, `siem-entity-resolution-worker`, `siem-entity-resolution-scheduler`.

Confluence docs are nested under `https://datadoghq.atlassian.net/wiki/spaces/CSiem/pages/6459031643/UEBA`, though some relevant docs live outside that tree (found one in a personal space during the 2026-07-30 research pass).

Jira: `SECPRODK9-1292` is the current Q3 2026 OKR/Goal tree (active roadmap). `SEC-25564` ("Entity Context") is a separate, long-running delivery epic (since 2025-11) that's the engineering backbone the OKR tree builds on. Recurse to leaf tickets on both; they are not one tree.

**Most authoritative single document found so far**: the "Entity Resolution Service: Product Brief & Roadmap" Google Doc (id `1XRHinTYlSQV9wREQYweMjjGu1dEalBu092pyghUfw80`, PM Jason Hunsberger, dated 2026-06-23, one week after the architecture rewrite). It has a formal glossary and approval-tracking table and is newer than the April "System Design" Confluence doc, which describes the pre-rewrite architecture.

**Why this matters**: on 2026-06-15, the first-generation ERS architecture (ActorEntity/ActorPlanner/actorroute classifier, Caniche schema) was scrapped wholesale (SEC-32908 through SEC-32933, ~15 stories marked Won't Do) after research showed the REDAPL/Iris write path was wrong for ERS. Anything dated before 2026-06-15 describing ERS internals should be treated as historical unless corroborated by current code or the June 23 brief. Newer isn't automatically right though: public Datadog docs (e.g. `docs.datadoghq.com/security/cloud_siem/triage_and_investigate/entities_and_risk_scoring`) still use pre-rebrand terminology as of 2026-07-30 (the "Entity Risks" rename was only approved 2026-07-24), so public docs can lag internal decisions by weeks.

GA target: 2026-09-28. Preview at Black Hat: 2026-08-01.

See [[ueba_domain_model_location]] for where findings from this material were written down.

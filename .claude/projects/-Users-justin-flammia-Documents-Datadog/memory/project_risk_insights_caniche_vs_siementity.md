---
name: project_risk_insights_caniche_vs_siementity
description: "Whether siementity/ERS records can replace the Risk Insights Caniche metadata join, and how the two roll-up view sets relate"
metadata: 
  node_type: memory
  type: project
  originSessionId: 0af46bb4-ebda-4b60-abbc-141dcc06cb4b
---

Feasibility study filed at `docs/Risk Insights Roll-up - Replacing the Caniche Metadata Join with siementity ERS Records.md` (2026-06-15, code-verified + dual-review).

Key findings, non-obvious and likely to recur:

- CORRECTED 2026-06-15: `risk_insights_*` is the LIVE set the entity-risk-score-api queries (GetViewNames in `risk-scores/store_utils.go:25-36`, unconditional, since 2026-03-26). The `*_v3` set is the prior generation, still registered in Caniche but referenced only in old test recordings, effectively legacy. Earlier "two co-equal parallel sets" framing was wrong. The materialized-view feature-flag limitation still matters for FUTURE gated rollout (a view can't check a flag, so per-org rollout needs a parallel `risk_insights_v2_*` family selected in GetViewNames), not as a current v3-vs-risk_insights split.
- Only `risk_insights_risk_scores` reads `siem_entity` (siementity), via the `siem_identity` CTE filtering `type='siem_entity_identity'`. The `*_v3` set has no siementity integration. All code grounded in `origin/main` (PoC branch merged + deleted): entity.go consts at 76/88/115/120, tracks.go:49, siemEntityTable 881-925, types.go:15. CrowdStrike is a 4th IdP integration type.
- "The Caniche join" = `risk_insights_metadata`, a UNION of 12 cloud-inventory orgstore tables. Its load-bearing job is mapping cloud `resource_id` to `entity_id`, which is the only bridge attributing compliance findings (INNER JOIN, no fallback) and CSM `resource_security_attributes` to entities.
- siementity carries ONLY identity records: `siem_entity_identity` (crawler IdP anchors with `fields.accounts`) and ERS `entity_resolution` edges. No cloud resource entities, and its `resource_id` is `Base64(SHA-256(key))`, a different namespace from the cloud-inventory key. So ERS records CANNOT replace the metadata join.
- The roll-up's resolution CTE (`siem_identity`) reads the crawler's `siem_entity_identity` records, NOT ERS `entity_resolution` records. Wiring ERS resolution in is additive (~1-2 wk: extend `siemEntityTable()` schema in xps-api, add a terminal-view CTE, temporal join on the Husky span, key reconciliation), gated upstream by ERS reaching prod for org 2.
- Gotcha verified during review: ERS does NOT write a `valid_until` custom field. Validity upper bound is the Temporal Husky `end_timestamp` (tombstones only); only `valid_from` is a custom field.

Refined scope (2026-06-15): Justin does NOT want to replace the metadata/decoration join. He wants to replace the resolution/roll-up grouping (the `siem_identity` email-match CTE) with ERS `entity_resolution` records, keeping cloud-inventory metadata, findings and security attributes as-is. Grilled design decided: collapse on RESOLVED+PARTIAL (AMBIGUOUS/UNRESOLVED fall back to inferred entityID); per-signal resolution at signal time (join moves into `risk_scores_signals`, terminal view aggregates by per-signal-resolved anchor, risk splits across anchors on mid-window changes); requires ERS change to backdate `valid_from` from run-time `now` (`writer.go:147`) to earliest contributing signal time; resolved-entity name from a second siementity lookup on the anchor; apply to `risk_insights_*` + add ERS columns (inferred_entity_id, anchored_entity_id, resolution_state) to `siemEntityTable()`.

Today's email-match handles a multiply-claimed entity by silently picking MIN(external_id), no ambiguity flag (`risk_insights_risk_scores.ddsql:43-60`). ERS join key is clean: ERS `InferredEntityID = Custom.EntityMetadata.EntityID` (`entityreader/source.go:252`) = the roll-up's entityID. ERS resolves actor-role only (`source.go:238`).

Runtime (2026-06-15, retriever-cli `--customer-auth=skip`): PROD org 2 siementity = 21,445 records, ALL `siem_entity_identity`, all carry `fields.accounts`, ZERO `entity_resolution` (ERS had only dry-run on prod; full write run kicked off 2026-06-15). STAGING org 2 = 10,478 `entity_resolution`, 54 `entity_resolution_run`, 5 `entity_resolution_result` (type not in current code, possibly transitional); resolution_state 10,456 UNRESOLVED vs 27 RESOLVED (sparse PoC anchors, not representative). Pending: re-query prod org 2 after the full run for RESOLVED coverage vs email-match coverage to validate the "replace entirely" decision.

Related: [[project_ers_three_track_structure]], [[project_er_proposal]].

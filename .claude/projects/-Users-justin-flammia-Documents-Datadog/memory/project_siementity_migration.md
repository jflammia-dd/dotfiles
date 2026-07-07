---
name: project_siementity_migration
description: "siementity track migration final state (complete), full history and practical impact on ERS reads and writes"
metadata: 
  node_type: memory
  type: project
  originSessionId: 2ba082ea-9628-449b-8b97-ea358fd51f74
---

Current production state (as of 2026-05-07): MIGRATION COMPLETE. Both sides are done. The REDAPL double-write to `siementity` is deployed. Antara's [dd-source#432500](https://github.com/DataDog/dd-source/pull/432500) flipped the `secmon-public-api` entity context handler to default to `siementity`. Full use of the `siementity` track is enabled. The `siem-redaplinfra-killswitch` FF exists as an emergency fallback only. ERS PoC session confirmed working against `siementity` only.

History: the full track timeline is `siementity` → `redaplinfra` → `siementity`. Originally SIEM wrote directly to `siementity` using custom dedup in `siem-entity-api`. PR [#346014](https://github.com/DataDog/dd-source/pull/346014) switched writes to flow through REDAPL's Iris dedup pipeline, landing on `redaplinfra`. `siementity` stopped receiving data Jan 30, 2026 but the track was never deleted. The migration returns to `siementity`, the same physical track, now powered by the REDAPL pipeline (Iris dedup, Temporal Husky versioning) rather than the old custom direct-write.

Decision (2026-04-24): migrate entity data back to `siementity`. Reason: `redaplinfra` has only 3-day Temporal Husky retention (subject to other producers' scope settings); `siementity` has its own dedicated 90-day retention scope. `siementity` is the correct spelling (all lowercase, one word).

The REDAPL pipeline and Iris dedup are unchanged; the only difference is `resource-processor-temporal-husky` writes SIEM data to `siementity` instead of `redaplinfra`. Practical impact on ERS: (1) reads in `EmailExactStrategy` and entity context handlers point at `siementity`; (2) ERS's RecordWriter (Phase 3) writes to REDAPL via `RedaplAsyncIntakeClient.SendBatch()` the same way `siem-entity-crawler` does. REDAPL routes that output to `siementity`.

`siementity-worker` exists at `dd-source/domains/evp-workers/apps/siementity-worker`. Takes `TemporalResource` protobuf, writes to Temporal Husky scope `"siementity"`. Cloud SIEM owns this worker. Temporal versioning formula `(payload.version << 48) + timestampMilli` is implemented in `siementity-worker/src/worker.ts:128`. The "Temporal Husky Versioning Gap" executive summary (March 2026) was retracted; the root cause analysis was wrong. See [[feedback_no_TH_abbreviation]].

---
name: reference-temporal-husky-retriever-cli
description: retriever-cli with -e trino is the agent path to Temporal Husky; AS_OF takes Unix SECONDS, not milliseconds.
metadata:
  type: reference
---

Two working agent paths run the same `eventplatform.system.track` Trino table function. No wrapper needed.
Verified 2026-09-01 against `siementity`, org 2, identical counts from both.

- `mcp__odp__query_tool` with `type: "TrinoSQL"`. Prefer this for prod. No shell approval, and
  `min_timestamp`/`max_timestamp` can be omitted entirely, which sidesteps the CLI window trap.
  Pinned to `us1.prod.dog` with no datacenter parameter.
- `retriever-cli -e trino -d <dc>`. The only path to staging.

Gotchas that cost real time:

- `AS_OF` is **Unix seconds**, not milliseconds. Milliseconds return zero rows silently. Negative values mean
  seconds in the past relative to now (`AS_OF => -604800`). `MIN_TIMESTAMP`/`MAX_TIMESTAMP` are also seconds.
- `AS_OF` is typed `bigint` in the Trino signature, so an ISO 8601 string is rejected. BeagleSQL's
  `table@{AS_OF='2d ago'}` form does accept strings.
- CLI only: default `--start` is 15 minutes ago. Too narrow a window panics with
  `triggerFindFragmentsForTime: failed to fetch fragments` instead of returning empty.
- `IS_LIVE`, `AS_OF` and `MIN_TIMESTAMP`/`MAX_TIMESTAMP` are mutually exclusive.

Full recipe lives in `docs/EVP Storage and Query Patterns.md`. Canonical upstream page:
[Temporal Husky: How to query Temporal Husky](https://datadoghq.atlassian.net/wiki/spaces/EP/pages/5500240121/Temporal+Husky+How+to+query+Temporal+Husky).
Related: [[reference_retriever_cli_cloud_siem]], [[feedback_retriever_cli_queries]], [[reference_evp_explorer_events_ui]].

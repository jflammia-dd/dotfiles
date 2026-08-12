# ADR-0004 Withdraws actor_class

ADR-0004 ("Progressive Resolution Replaces Actor Classification") supersedes ADR-0002 and withdraws `actor_class` (`HUMAN`/`NON_HUMAN`/`UNKNOWN`) entirely. The resolution worker only uses `status` (RESOLVED, AMBIGUOUS, INDETERMINATE, UNRESOLVED). `RESOLVED` reverts to its ADR-0001 meaning: reached the anchored person. A workload terminus is `UNRESOLVED` carrying the workload identity as the furthest point reached.

Any RFC, design doc, or code referencing `actor_class` is designing against an abandoned path. ADR-0002's broadening of `RESOLVED` to "reached a definitive identity" is also withdrawn.

Published to Confluence: https://datadoghq.atlassian.net/wiki/spaces/CSiem/pages/7075169395
Jira: SEC-34228

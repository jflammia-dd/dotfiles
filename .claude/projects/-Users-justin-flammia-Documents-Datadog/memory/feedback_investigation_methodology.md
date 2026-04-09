---
name: Investigation methodology - verify data sources before comparing results
description: When comparing query results from different systems/tracks/engines and finding discrepancies, verify both sources are live and receiving the same data before attributing the difference to application logic. Learned from the Temporal Husky versioning gap investigation (March 2026).
type: feedback
---

When investigating a discrepancy between two data sources, verify that both sources are actually live and receiving the same data before building theories about why the results differ.

**Why:** In the Temporal Husky versioning investigation (March 2026), BeagleSQL queries against the `siementity` track returned 1 version per entity, while Trino queries and the UI against `redaplinfra` showed multiple revisions. The difference was attributed to a version=0 overwrite bug, which led to an executive summary sent to the REDAPL team with incorrect conclusions. The actual cause: `siementity` had stopped receiving data on Jan 30 (33 days before the test). The investigation had the right information in its own notes ("Removed EVP path," "unused for reads") but interpreted it as an architectural note rather than a data freshness issue.

**How to apply:**
- When two data sources show different results, the first hypothesis should be "are they looking at the same data?" not "why does the application treat the data differently?"
- Check for data freshness: when was the last write to each source? Are producers still active?
- Be skeptical of data flow diagrams that show fan-out to multiple destinations. Verify each branch is actually active, especially after migrations.
- If the convenient testing tool (e.g., BeagleSQL) only accesses one data source and the production system reads from another, test against the production source even if it requires a less convenient tool (e.g., Trino).
- Stated-as-fact architectural assumptions ("both tracks receive the same data") are the most dangerous kind of false premise because they're never questioned. Always verify empirically before building on them.

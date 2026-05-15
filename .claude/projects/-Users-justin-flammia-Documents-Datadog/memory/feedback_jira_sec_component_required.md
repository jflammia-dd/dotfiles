---
name: jira-sec-component-required
description: Every issue created in the Jira SEC project requires a components field; for Cloud SIEM tickets the id is 10488
metadata: 
  node_type: memory
  type: feedback
  originSessionId: ea0492c0-e69e-42cf-a798-97f2498649d1
---

Every issue created in the Jira SEC project (`projectKey: SEC` on `datadoghq.atlassian.net`) requires a `components` field at creation time. Omitting it returns HTTP 400 with message `"A component is required to create an issue. Please provide a component."`.

For Cloud SIEM tickets, pass `additional_fields: {"components": [{"id": "10488"}]}` to `mcp__plugin_atlassian_atlassian__createJiraIssue`. To find component ids for other K9 sub-teams, fetch any existing ticket from that team via `getJiraIssue` with `fields: ["components"]` and inspect `components[].id`.

**Why:** The SEC project has a workflow rule that enforces component selection. The Atlassian tool schema does not advertise the field as required, so a fresh `createJiraIssue` call against SEC will fail on the first attempt without this hint. Wastes a round-trip.

**How to apply:** Whenever calling `createJiraIssue` against the SEC project, set the components field via `additional_fields`. For batch creates of related tickets, reuse the same component id across the whole batch.

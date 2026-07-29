---
name: siem-entity-api is not a golden path
description: Do not treat siem-entity-api as an authoritative reference for ERS implementation
type: feedback
originSessionId: 7da81963-1801-4858-a15d-eb928abdeb37
---
`siem-entity-api` is an example that can be referenced but is not a golden path. It may be incomplete or reflect older patterns.

**Why:** The service predates some current conventions and may not reflect best practices for new services.

**How to apply:** Use general software engineering practices and official Datadog documentation (Confluence, Rapid docs, Language Foundations space) as the primary source of truth. Reference `siem-entity-api` for orientation only, and verify anything borrowed against official guidance before using it.

---
name: ers-poc-staging-test-drive
description: Current Rapid test drive name and endpoint for the ERS PoC staging environment
metadata: 
  node_type: memory
  type: project
  originSessionId: 8b39854a-a55d-43de-a980-73227a502649
---

No active staging test drive as of 2026-06-01. `suzuki-x-90` was torn down on that date.

Service: `siem-entity-resolution-api`, namespace: `rapid-cloud-security-platform`.

To spin up a new TD:
```bash
rapid td create -s siem-entity-resolution-api
```

**Why:** `suzuki-x-90` was the active TD from 2026-05-20 until teardown on 2026-06-01. Prior TD `peugeot-db9-gt` was retired when the service was renamed from `entity-resolution` to `siem-entity-resolution-api`.

**How to apply:** When staging validation is needed again, create a new TD and update this memory with the new name and endpoint.

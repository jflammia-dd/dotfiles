---
name: ers-poc-staging-test-drive
description: Current Rapid test drive name and endpoint for the ERS PoC staging environment
metadata: 
  node_type: memory
  type: project
  originSessionId: 8b39854a-a55d-43de-a980-73227a502649
---

The active staging test drive for the ERS PoC is `suzuki-x-90`. Service: `siem-entity-resolution-api`, namespace: `rapid-cloud-security-platform`.

Endpoint: `rapid-td-suzuki-x-90.us1.staging.dog:443`

Health check:
```bash
grpcurl rapid-td-suzuki-x-90.us1.staging.dog:443 grpc.health.v1.Health/Check
```

Log filter (staging Datadog org `dd.datad0g.com`): `service:rapid-td-suzuki-x-90`

Update the TD after pushing a commit:
```bash
rapid td update -t -n suzuki-x-90
```

**Why:** `peugeot-db9-gt` was the prior TD, created when the service was named `entity-resolution`. The service was renamed to `siem-entity-resolution-api` and the TD was rotated to `suzuki-x-90` on 2026-05-20. Turbo updates on `peugeot-db9-gt` would fail because Rapid looks for `entity-resolution/rapid.json` which no longer exists.

**How to apply:** Use `suzuki-x-90` as the TD name in all staging validation steps, grpcurl commands and log searches.

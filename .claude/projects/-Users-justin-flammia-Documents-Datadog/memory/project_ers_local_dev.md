---
name: ERS local development workflow
description: How to run and verify the entity-resolution service locally
type: project
originSessionId: 7da81963-1801-4858-a15d-eb928abdeb37
---
Run the service locally from the dd-source root. Do not run through Claude Code; rapid run uses bzl which hits the python3 shim.

```bash
DD_ENV=dev rapid run -s entity-resolution
```

Verify it's healthy in a second terminal:

```bash
grpcurl -plaintext localhost:8080 grpc.health.v1.Health/Check
# Expected: { "status": "SERVING" }
```

**Why:** `DD_ENV=dev` disables auth checks. The statsd warning (`write: connection refused` on port 8125) is expected in all Rapid services without a local Datadog Agent. It is not a code bug and does not affect functionality.

**How to apply:** Use this workflow to verify each ticket before closing it out. The grpcurl health check is the minimum bar. Once handlers are wired up (SEC-30575+), also send a test request via `grpcurl` or `curl` against the Resolution Request API.

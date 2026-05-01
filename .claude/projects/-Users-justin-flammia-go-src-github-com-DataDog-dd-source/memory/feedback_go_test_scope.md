---
name: Always scope go test to the service directory
description: Never run go test ./... from the monorepo root
type: feedback
originSessionId: a78207aa-e334-41ca-9a4a-40f2208e4d25
---
Always run `go test` from the service directory or with a scoped path. Never run `go test ./...` from the dd-source root, as it spawns tests across hundreds of packages and runs for 30+ minutes.

**Why:** dd-source is a monorepo with ~250 domains. Unscoped `./...` hits every package and wastes significant time and CPU.

**How to apply:** cd into the service directory first, or scope the path explicitly:

```bash
cd domains/cloud-security-platform/apps/apis/entity-resolution && go test ./...
# or
go test ./domains/cloud-security-platform/apps/apis/entity-resolution/...
```

# dd-source Development

## Repository
- Location: `$DATADOG_ROOT/dd-source` → `/Users/justin.flammia/dd/dd-source`
- Polyglot monorepo using Bazel (`bzl` wrapper)
- Go version pinned in `rules/go/version.bzl` (currently 1.25.6)
- System Go (Homebrew): 1.26.0 — OK since Bazel uses its own toolchain

## Team Domain
- Path: `domains/cloud-security-platform/`
- Contains: apps/apis/ (42+ services), agentless, asm-vm, ciem, iac, k9-sca, libs, shared, security-graph, triage
- No repo-wide `.golangci.yml` — individual domains may have their own

## Build & Test Commands
```bash
# Build a service
bzl build //domains/cloud-security-platform/apps/apis/<service>:<service>

# Run all tests for a service
bzl test //domains/cloud-security-platform/apps/apis/<service>/...:all

# Update BUILD files after changing Go imports
bzl run //:gazelle -- update domains/cloud-security-platform/apps/apis/<service>

# Regenerate protobuf snapshots
bzl run //:snapshot -- //domains/cloud-security-platform/apps/apis/<service>/entitiespb/...
```

## Git Config for Large Repo Performance
```bash
git config feature.manyFiles true
git config core.fsmonitor true
```

## Key Environment Variables
- `DATADOG_ROOT=$HOME/dd`
- `GOPRIVATE=github.com/DataDog`

## Tools
- `bzl` — Bazel wrapper (v1.23.0 / Bazel 9.0.0)
- `golangci-lint` — `/opt/homebrew/bin/golangci-lint` (v2.10.1)
- `grpcurl` — `/opt/homebrew/bin/grpcurl` (v1.9.3)
- `rapid` — Rapid CLI for service management

## Atlassian Cloud ID
- `66c05bee-f5ff-4718-b6fc-81351e5ef659` (for Jira/Confluence MCP calls)

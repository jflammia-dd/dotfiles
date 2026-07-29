# GoLand Setup for dd-source

## Version
- GoLand 2025.3.3 (Build #GO-253.31033.129)
- Licensed via Datadog

## Key Settings
- **Memory**: 8192 MB (`-Xmx8192m`)
- **Bazel binary**: `bzl` (not `bazel`)
- **Query Sync**: Must be OFF
- **Index entire GOPATH**: Must be OFF (per-project setting, verify on each new project)
- **Go Modules**: Enable integration + vendoring + download dependencies
- **Actions on Save**: Reformat code + Optimize imports (replaces old File Watcher approach)
- **Go Linter plugin**: golangci-lint at `/opt/homebrew/bin/golangci-lint` (v2.10.1)
  - Old v1 binary at `~/go/bin/` was removed
  - Old File Watcher for golangci-lint was removed (plugin handles it natively)

## Bazel Plugin
- Must use **"Bazel for IntelliJ (legacy)"** plugin — NOT the newer "JetBrains Bazel Plugin"
- Current version: 2026.02.05-api-version-253

## Cloud SIEM .bazelproject
- Best file: `domains/cloud-security-platform/etc/ijwb/cloud_siem/cloud_siem.bazelproject`
- Excludes ~100+ unrelated domains for fast indexing
- Includes pre-built run configs: deps, fmt, gazelle, protogen
- Also available: broader CSP file at `domains/cloud-security-platform/etc/ijwb/.bazelproject`

## Installed Plugins
- Rainbow Brackets, Indent Rainbow, GitToolBox, GitLink, Go Linter, Bazel (legacy)

## Config File Locations
- Global settings: `~/Library/Application Support/JetBrains/GoLand2025.3/options/`
- VM options: `~/Library/Application Support/JetBrains/GoLand2025.3/goland.vmoptions`
- Code styles: `~/Library/Application Support/JetBrains/GoLand2025.3/codestyles/`
- Project-level: `dd-source/.ijwb/`

## Formatting
- Go files use real tabs (enforced by gofmt), tab size 4 — this is correct default
- gofmt runs on save via Actions on Save > Reformat code

## Confluence References
- Bazel IDE Configuration: https://datadoghq.atlassian.net/wiki/spaces/FF/pages/3006464880
- Setup an IDE with dd-source: https://datadoghq.atlassian.net/wiki/spaces/OPE/pages/3565486554
- GoLand Setup (Core-Index): https://datadoghq.atlassian.net/wiki/spaces/C/pages/2120646746

# siem-entity-api

## Overview
gRPC Rapid service that transforms raw identity provider entities (Okta, Google Workspace, Azure/Entra ID) into standardized SIEM entity format using declarative YAML-based JQ mappings.

## Location
`/Users/justin.flammia/dd/dd-source/domains/cloud-security-platform/apps/apis/siem-entity-api`

## Key Files
- `main.go` — gRPC server entry point
- `rapid.json` — Rapid metadata (team: cloud-siem, protocol: grpc)
- `entitiespb/entities.proto` — gRPC service definition (TransformEntity, TransformEntityBatch)
- `entity_model/models.go` — UserIdentityEntityV1 struct, AccountStatusInfo
- `entity_model/types.go` — Enums: IntegrationType, EntityType, UserType, AccountStatus
- `internal/entities/mapper_registry.go` — Transformation orchestrator
- `internal/entities/mappers.go` — YAML mapper parsing + JQ execution
- `internal/entities/mappers/` — YAML transformation definitions per provider
- `internal/handler/handler.go` — TransformEntity & TransformEntityBatch RPCs
- `internal/handler/metrics.go` — Datadog metrics (siem.entity_api.requests, .duration, .errors)

## Architecture
- YAML mappers embedded at compile time (no file I/O at runtime)
- Batch: max 1000 entities, 50 concurrent workers, 5s per-entity timeout
- Validation: go-playground/validator with custom enum validators
- Observability: dd-trace spans + statsd metrics

## grpcurl Setup
- Alias `grpc-siem` in `~/.zshrc`
- Proto imports: service entitiespb dir + `/opt/homebrew/include` (google/protobuf) + `~/.local/share/proto-include` (google/rpc/status.proto)
- No gRPC reflection enabled — must use proto file flags

## Current Work (SEC-28505)
- Migrated `account_status_v2` → `account_status` (structured object with status + description)
- Removed old flat string `account_status` field
- Added missing `provider: ENTRA_ID` to Azure mapper
- Draft PR: https://github.com/DataDog/dd-source/pull/367447
- Pending: FE sync with Alexandre Florez, redapl schema update, staging testing

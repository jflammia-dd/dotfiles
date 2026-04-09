---
description: Migrate a CDM field in the siem-entity-api entity model. Updates the Go struct, all three YAML provider mappers, and the mapper registry tests in one coordinated pass.
argument-hint: "<old_field> <new_field> [new_go_type]"
---

# SIEM Entity CDM Migration

Perform a CDM field migration in `siem-entity-api`. This touches exactly four locations: the Go struct, the three YAML mapper files (Okta, Google Workspace, Azure), and the mapper registry test.

The user invoked: `/siem-entity-migration $ARGUMENTS`

Parse the arguments:
- `old_field` — current field name in `UserIdentityEntityV1` (snake_case, matches JSON tag)
- `new_field` — new field name (snake_case)
- `new_go_type` — optional; new Go type if the type is also changing (e.g. `*AccountStatusInfo`). If omitted, keep the existing type.

**Service root**: `~/dd/dd-source/domains/cloud-security-platform/apps/apis/siem-entity-api`

## Steps

### 1. Read current state

Before making any changes, read these files to understand the current field definition:
- `entity_model/models.go` — find the field with JSON tag matching `old_field`
- `entity_model/types.go` — check if any types need to be added or updated
- `internal/entities/mappers/user_identity_okta_v1.yaml` — find the `target: old_field` mapping
- `internal/entities/mappers/user_identity_google_workspace_v1.yaml` — same
- `internal/entities/mappers/user_identity_azure_v1.yaml` — same
- `internal/entities/mapper_registry_test.go` — find assertions referencing `old_field`

### 2. Plan the changes

Show the user a summary of what will change before editing:
- The struct field rename (and type change if provided)
- Each mapper YAML `target:` line that will be updated
- Any `expr:` changes needed if the field shape is changing
- Test assertion updates

Ask for confirmation before proceeding.

### 3. Apply changes

After confirmation, update all four locations:

**`entity_model/models.go`**: Rename the field and update its JSON tag. If `new_go_type` was provided, update the type too. Keep the inline comment describing the field.

**Each mapper YAML**: Update the `target:` value from `old_field` to `new_field`. If the shape changed (e.g. flat string → nested struct), update the `expr:` to produce the correct output shape. For nested fields, use dot notation (e.g. `target: account_status.status`).

**`internal/entities/mapper_registry_test.go`**: Update any test data maps and assertions that reference the old field name or its expected value type.

If `new_go_type` was provided and it's a new type (not already in `types.go`), add it there too.

### 4. Verify

Run the tests to confirm the migration is correct:

```sh
cd ~/dd/dd-source && bzl test //domains/cloud-security-platform/apps/apis/siem-entity-api/internal/entities:go_default_test
```

Report the test results. If tests fail, diagnose and fix before declaring completion.

### 5. Summary

After tests pass, output a brief summary of all files changed and what changed in each.

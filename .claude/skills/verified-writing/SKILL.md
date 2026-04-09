---
name: verified-writing
description: "Research-first technical writing with verified references. Applies to both net-new drafting and revision of existing documents. Use whenever writing or editing any section of a technical document (RFC, design doc, data model, architecture doc or system explanation) that references code, schemas, configs, component behavior or design decisions. The skill reads authoritative sources before writing a single claim and treats existing unverified claims in sections being revised with equal skepticism. It never invents or silently preserves field names, types, component names, or design rationale. Triggers on: 'write the [X] section', 'update this doc', 'revise this section', 'add a paragraph about [Y]', 'edit this RFC', 'update the data model section', 'review this doc for accuracy', 'draft the [Y] design', 'document the schema for Z', 'describe how [system] works', or any writing or editing task where specific technical facts need to be accurate."
---

# Verified Writing

The guiding principle: **verified claims get written, unverified claims get a placeholder**. Never invent field names, types, component names, behaviors, or design rationale. Omission is always better than hallucination.

When sources conflict or are missing, surface it to the user rather than guessing.

---

## Phase 1: Claim Inventory

Before reading or writing anything, identify every technical claim that needs verification.

For each claim, name:
1. What specific artifact it depends on (e.g., "the field names and types in the Go struct for EntityResolutionRecord", "why composite versioning was chosen over timestamp ordering in the RFC")
2. What type of source would be authoritative (source code, config, design doc)
3. Whether the claim requires combining multiple sources (e.g., code shows two implementations, design doc explains which one was adopted)

Present this list to the user before proceeding. If the scope is unclear, ask. Don't guess at what the document needs to cover.

### Net-new writing

Inventory claims for all content being added.

### Revision of an existing document

Do not assume existing claims are accurate. When revising a section, inventory:

1. **New claims** being added (same as net-new)
2. **Modified claims** being changed (verify the new version)
3. **Existing claims in the same section** being touched: scan for technical assertions (field names, types, component names, behavioral descriptions, design rationale) and add them to the inventory

The rule: when you leave a section, it should be clean. You're not required to audit the entire document, but the sections you modify should have no unverified claims remaining in them.

### Full document accuracy review

If asked to review a document for accuracy (not just edit a section), inventory all technical claims throughout the document and verify them. Flag anything that can't be verified and present it to the user before proposing any changes.

---

## Phase 2: Source Resolution

For each claim, locate and read the authoritative source. Work through this priority order:

**1. Source code (highest authority)**
Proto/struct definitions, schema migration files, Go/Java/Python source, tests. Ground truth for field names, exact types, interfaces and behavior. For data models: always read the actual struct or proto, never infer field types from context.

**2. Configuration (authoritative for runtime facts)**
deploy.yaml, Helm values, feature flag configs. Ground truth for how the system is actually deployed and what's enabled.

**3. Design documents (authoritative for decisions and rationale)**
Confluence RFCs, Google Docs design specs. Ground truth for why one approach was chosen over another, what tradeoffs were considered, what constraints shaped the design. Required when writing about design decisions. Code alone doesn't explain why.

**4. Other documentation (context only, never sole authority)**
Runbooks, meeting notes, Slack threads. Use only to find pointers to authoritative sources, or to understand context. Never cite as the primary basis for a technical claim.

### When a source can't be located

Do not guess. Do not write the claim. Do two things:

1. Ask the user: "I couldn't locate [X]. Do you have a file path or Confluence URL?"
2. Insert a placeholder in the draft: `[TODO: verify - couldn't locate source for X]`

### When sources conflict

Do not pick one silently. Surface the conflict:

> "The Go struct uses `float64` but the proto definition uses `double`. Which is the canonical definition for this document?"

Do not write the claim until the user resolves it.

### When multiple sources are needed

This is common. Code may show two implementation paths that both exist; the design doc explains which one is active and why. Read both before writing. Make the synthesis explicit in Phase 3.

---

## Phase 3: Synthesis

Before writing, produce a brief factual summary of what was learned across all sources. This is the foundation the prose will rest on.

Format it as a bulleted list of verified facts, with the source noted for each. Example:

```
Verified facts:
- Field `entity_id` is type string (source: siem_entity.proto line 14)
- Field `version` is type int64, not int32 (source: entity_model.go line 88)
- Composite versioning was chosen over timestamp-only to handle concurrent writes (source: Entity Model RFC, "Versioning Strategy" section)
- The crawler writes to redaplinfra, not siementity (source: PR #346014, verified by user)
```

If the synthesis reveals gaps (claims the document needs but couldn't be verified), list them explicitly before writing. The user decides whether to provide the missing source, accept a placeholder, or remove the claim from scope.

---

## Phase 4: Write

Write the document using only facts from Phase 3. Apply these rules without exception:

- Every field name must come from a struct, proto, or migration file that was read
- Every type (float64, int64, string, bool, etc.) must come from the source definition; never infer or assume
- Every component name must use the exact name from the codebase
- Every design decision must trace to a design document or explicit user confirmation
- Every behavioral claim must trace to source code or tests

If a claim can't be grounded in a verified source, either omit it entirely or insert `[TODO: verify: <what's missing>]`. Do not write a placeholder that sounds like a real fact.

---

## Phase 5: Flag Gaps

After the draft, list every placeholder and unresolved question. These are blockers before the document can be published.

```
## Verification Gaps

- [TODO: verify field types] - couldn't locate the EntityRisk proto; suggest checking
  domains/security/siem/entity in dd-source
- [TODO: confirm design decision] - couldn't determine whether V2 or V3 resolution
  was adopted; needs confirmation from the RFC or team
- [Conflict: float vs decimal] - source A uses float64, source B uses decimal(18,6);
  user needs to identify the canonical definition
```

---

## After the Draft

Once the draft is complete and gaps are resolved:

1. Apply `justins-voice` for voice and style
2. Apply `edit-doc` for adversarial style enforcement (em dashes, Oxford commas, passive voice, etc.)

These are downstream steps. Do not apply them before the factual content is verified.

---

## Source Priority Reference

| Claim type | Primary source | What to look for |
|---|---|---|
| Field names | Proto definition or Go struct | Exact field name, casing |
| Field types | Proto definition or Go struct | Exact type (float64 not float, int64 not int) |
| Component behavior | Source code | Method implementations, not comments |
| Expected behavior | Tests | What the tests assert |
| Runtime config | deploy.yaml / Helm values | Actual deployed values |
| Design decisions | RFC / design doc | Decision section, rationale |
| Why X over Y | Design doc | Tradeoffs / alternatives considered |
| API contracts | Proto / OpenAPI spec | Exact signatures |
| Data flow | Source code + design doc | Both needed: code for what exists, doc for what's intentional |

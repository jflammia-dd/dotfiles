---
name: ERS Phase 1 implementation complete (SEC-31163)
description: Architecture pivot to entity-type-first dispatch with orthogonal format/path axes. Staging findings validated provider string casing bug. AnchorLookupStrategy replaces two-strategy split.
type: project
originSessionId: 39ed4a3a-33bf-48d0-a8ea-3d520a1ac545
---
## What shipped

**AnchorLookupStrategy** — replaces BareEmailStrategy + OCSFCompositeStrategy. Single config-driven strategy runs two phases: (1) format detection/normalization (OCSF composite checked first, bare email fallback), (2) anchor lookup via queryAnchorsByEmail. Both formats rejoin at phase 2 with identical resolution code.

**InferredEntitySources config** — YAML-loaded per-startup (`config/inferred_entity_sources.yaml`), maps signal source → anchor IdP. Adding new source requires one YAML entry, zero strategy code changes.

**EntityTypeResolutionPaths** — orthogonal to sources. Maps entity type (Email Address, IAM User) → resolution path (email only, username stubbed). Entity types are fixed/slow-moving; sources grow with IdP onboarding.

**Staging validation** — discovered provider string casing bug (legacy extraction writes `"Okta"` uppercase; entity context content packs use lowercase). Fixed at parse time (`EntityRiskSource.parseEntityRiskEvent`) so normalization happens once at entry.

## Architectural pivot (non-obvious)

Original design: per-provider strategy registrations with separate entity type handling.

Actual design: **entity-type-first dispatch with orthogonal axes**. The reduction came from recognizing that:
- Entity types are the dispatch axis (determines what to do after normalization)
- Formats are how identities are encoded (legacy bare email vs OCSF composite)
- Sources are operational onboarding points (when Entity Context adds an IdP)

These three concerns are genuinely independent. Entity type → resolution path is a code change (involves implementing new lookup logic). Source → anchor IdP is a YAML change (operational, per-IdP onboarding). Format detection is runtime (both formats produce same canonical value).

## Staging findings

**Provider casing:** Azure/M365 entities from org 2 all had `provider = "azure"` or `provider = "microsoft-365"` (lowercase). Legacy Okta extraction in test data showed `provider = "Okta"` (uppercase). Without the normalization fix, Okta entities would silently skip as `unknown_provider:Okta`. Confirmed by injected Okta signals: before fix = `unknown_provider:Okta` skip, after fix = RESOLVED or UNRESOLVED per anchor match.

**Entity type casing:** OCSF extraction produces `"Email Address"` (quoted in entity_metadata), stored bare as string in `EntityTypeResolutionPaths` key. Match is literal string equality, no case handling needed.

**AWS volume:** Org 2 dominated by AWS ARNs (~1700 entities) with entity_type="User Name" and provider="AWS". These correctly skip as unknown_provider because AWS needs within-trust (CloudTrail federation) before cross-trust, not implemented yet. Phase 2 work.

## Performance wins

1. **detect() returns extracted value** — was calling strings.SplitN three times per entity (CanResolve → detect, Resolve → detect, Resolve → ExtractValue). Now one pass, value returned, used directly.

2. **strings.Cut instead of SplitN** — IDFormat.Matches and ExtractValue both called SplitN, allocating `[]string` on every entity. strings.Cut does the same split without allocation (substrings backed by original).

3. **slices.Sort instead of sort.Strings** — modern generic API, no interface dispatch.

## Naming decisions

**AnchorLookupStrategy** (not ProviderStrategy, not EmailResolutionStrategy): The strategy's core job is anchor lookup. It handles multiple formats (OCSF composite, bare email) and multiple entity types (Email Address, IAM User) but all resolve the same way: extract identity, look up anchor. Name describes the mechanism, not the provider or format. Contrasts cleanly with AWSFederationStrategy (within-trust, traces ARN).

**InferredEntitySources** (not ProviderConfig): "Provider" is too broad (doesn't distinguish IdP vs CSP). "Source" is precise: these are systems that produce inferred entity identities appearing in entityrisk.

## Config pattern

YAML-based (`config/inferred_entity_sources.yaml` embedded at startup via `//go:embed`). Loaded once at init, panics if malformed. Changes don't require code recompile — ops change YAML and redeploy. Inline comments document each entry without risk of comment rot.

## Next work (project context)

1. **SEC-30832** — write entity_resolution_result schema YAML. This blocks SEC-30880 (record writer implementation).
2. **Signal audit** — run TestProviderStrategyResolutionCoverage against all 9 design partners (not just org 2) to understand email vs non-email entity type distribution before GA definition conversation with Product.
3. **Unblocked open questions** — OCSF adoption timing for CloudTrail (AWS federation), GitHub identity ingestion (SCIM pending), service account resolution (non-human identities).

## Development logging (newly added)

Verbose per-entity output with clear visual separation (`═════` for entity boundaries, `─────` for phase boundaries). Shows:
- Raw inferred entity fields (type, provider, ID)
- Config printout at startup (registered sources, routable types)
- Each gate's evaluation and skip reason
- Normalization format+value
- Final resolution result with anchor and completeness

Allows mental model building per-entity without log aggregation queries.

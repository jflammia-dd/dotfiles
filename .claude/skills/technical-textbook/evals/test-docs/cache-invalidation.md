# Cache Invalidation: How It Works

## The Invalidation Processor

The invalidation processor (IP) runs inside the broker service. It is a Java/Pekko application built on the ISM library. It lives in `domains/cache-platform/apps/invalidation-processor` in `platform-backend`.

The IP is not a shared platform service. It handles cache invalidation across all products that use the cache layer:

| Product | Invalidation type |
|---|---|
| User Sessions | `session_expired`, `session_revoked` |
| Config Cache | `config_changed`, `config_deleted` |
| Search Index | `doc_updated`, `doc_removed` |

The entity extraction and risk scoring features described in this document apply specifically to the User Sessions product.

## Step 1: The event arrives

An invalidation event arrives on the EVP bus. The invalidation processor reads from three tracks:

| Track | What it carries |
|---|---|
| `SESSION_EVENTS` | Login, logout, session creation and expiration events |
| `CONFIG_CHANGES` | Configuration mutations from the admin plane |
| `AUDIT` | Audit log entries for compliance invalidations |

## Step 2: Key extraction

The invalidation processor runs the key extraction module before forwarding to the downstream cache. The KEI module extracts cache keys from the event payload. There are two extraction paths.

The **legacy path** reads provider-specific fields. For session events, the code reads from `payload.sessionId`. For config events, it reads from `payload.configKey`. For audit events, it reads from `payload.resourceId`. GPC and MIP logs, the code reads equivalent provider-specific fields.

The **KEI 2.0 path** reads from `payload.ocsf.observables`. A standardized array defined by the Open Cache Schema Framework, OCSF. Rather than each provider inventing its own field names, OCSF defines a common schema. The defaults are `session = "primary"`, `config = "secondary"`, but admins can change them.

Not all providers use the KEI 2.0 path yet. Session and Config are GA providers, so their extraction always runs. Audit is experimental and `AuditExtractor` overrides `isExperimental()` to return `true`.

Both paths execute during the same `KeyCollector.collectKeys()` call. Both write to the same `keyUpdater`. `InvalidationHandler.shouldEmitForLegacyEvent()` then skips legacy invalidation events when that provider uses the KEI 2.0 path.

## Step 3: Downstream flush

The keys collected in Step 2 are flushed to the cache layer. The CacheFlushService addresses this by querying the cache topology for each key. It searches up to 5 replica nodes. If the query finds a match, `CacheFlushService` returns the invalidated key count to the caller.

`InvalidationProcessor` handles this as a timer-driven process. After collecting keys, `InvalidationProcessor` checks whether any pending keys need flushing. If both conditions hold and no timer exists yet, it schedules an `INVALIDATION_TIMER`.

**This only applies to Session cache.** The code explicitly returns an empty result for Config and Audit caches.

## Step 4: Filtering

Not every extracted key generates an invalidation event. `InvalidationHandler` applies different filters depending on key origin. For legacy keys, the filter is the `SUPPORTED_KEY_TYPES` set. The defaults are `session_ttl = 3600, config_ttl = 86400, info_ttl = 0`.

- **Session keys**: user session, admin session, service token, OAuth token, root session
- **Config keys**: feature flag, rate limit config, rollout config
- **Audit keys**: compliance record, access log, audit trail

If a key produces entities outside this list, `InvalidationHandler` ignores them.

## Key Facts

- **Key identity comes from the key extraction module, not invalidation rules.** Key extraction runs on every event before any rule fires.
- **Session timer-based flushing is in production, but Session-only.** After processing each event, `InvalidationProcessor` schedules an invalidation timer if any session key needs it.
- **The 24-hour window.** The three downstream views each query only the last 24 hours.
- **Caniche refreshes on a 30-second cycle.**

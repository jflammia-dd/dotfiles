# Datadog Repo Map

Quick reference for what each repo owns. Use this to route research to the right place
before searching. When in doubt, check multiple candidates.

## Locally Cloned (`/Users/justin.flammia/dd/`)

| Repo | What it owns |
|---|---|
| `dd-source` | Polyglot monorepo for most Datadog services. Owns RAPID HTTP APIs, Go services, TypeScript EVP workers, Caniche view definitions (under `domains/xpq/`), frontend-adjacent backends. Most user-facing API services live here. |
| `logs-backend` | Event Platform backends and stream processing. Owns Kafka Streams reducers (Java), the rule-reducer (signal generation), SIEM detection engine, EVP track processing, compliance reducers. If something processes log events at scale, it's probably here. |
| `dd-go` | Go monorepo for shared Go libraries and some standalone Go services. Caniche materialized view infrastructure, shared clients. |
| `dogweb` | Web frontend and legacy Python backend. Squire query endpoints, dashboards, monitors, some legacy API handlers. |
| `web-ui` | Modern React/TypeScript frontend. |
| `infrastructure-resources` | Infrastructure-as-code, Kubernetes manifests, Helm charts for production services. |
| `k8s-resources` | Cluster-wide configuration for non-Datadog services (Redis, Memcached, etc.). |
| `terraform-config` | Terraform for cloud infrastructure. |
| `consul-config` | Service discovery and configuration via Consul. |
| `datacenter-config` | Datacenter-level configuration. |
| `datastores` | Datastore configuration and schemas. |
| `cloud-inventory` | Cloud inventory data and schemas. |
| `devtools` | Internal developer tooling. |
| `images` | Container images. |
| `architecture` | Architecture decision records and diagrams. |

## Key Domain Patterns in `dd-source`

Within `dd-source`, code is organized under `domains/`:

| Domain path | What it owns |
|---|---|
| `domains/cloud-security-platform/` | Cloud SIEM, CSM, entity risk scoring, detection rules API, triage, Risk Insights API (`entity-risk-score-api`), entity crawler |
| `domains/xpq/` | DDSQL / UserSQL / Caniche materialized views. All Caniche view definitions under `apps/caniche-terraform/config/cloud/queries/` |
| `domains/evp-workers/` | TypeScript workers that process EVP tracks (e.g., `entityrisk-worker`) |
| `domains/aaa/` | Authentication, Authorization, Accounts |
| `domains/api_platform/` | RAPID framework, API gateway infrastructure |
| `domains/alerting/` | Monitors, alerts, notification rules |
| `domains/metrics/` | Metrics pipeline |

## Key Domain Patterns in `logs-backend`

| Domain path | What it owns |
|---|---|
| `domains/cloud-security-platform/apps/rule-reducer/` | Core SIEM signal generation (Java, Kafka Streams) |
| `domains/cloud-security-platform/apps/siem-queries-reducer/` | SIEM query processing |
| `domains/cloud-security-platform/apps/user-resolution-reducer/` | User/entity resolution in signal context |
| `domains/cloud-security-platform/apps/behavior-detection-reducer/` | Behavioral anomaly detection |
| `domains/cloud-security-platform/libs/core-reducer/` | Shared signal processing logic, Signal proto, serializers |
| `domains/cloud-security-platform/libs/projections/` | Log projection system (entity extraction from logs) |
| `domains/event-platform/` | EVP track definitions, topology, shared constants |

## Finding Repos Not Cloned Locally

```bash
# List all DataDog repos with descriptions
gh repo list DataDog --limit 100 --json name,description | jq '.[] | "\(.name): \(.description)"'

# Search for repos related to a topic
gh repo list DataDog --limit 100 --json name,description | jq '.[] | select(.name | contains("KEYWORD"))'

# Read a file from a non-local repo
gh api repos/DataDog/REPO/contents/PATH | jq -r '.content' | base64 -d

# List top-level structure of a non-local repo
gh api "repos/DataDog/REPO/git/trees/HEAD?recursive=0" | jq '.tree[].path'
```

## Common Research Routing

| Question type | Start here |
|---|---|
| "How does signal X get generated?" | `logs-backend/domains/cloud-security-platform/apps/rule-reducer/` |
| "How does Risk Insights work?" | `dd-source/domains/cloud-security-platform/apps/apis/entity-risk-score-api/` |
| "How does a Caniche view work?" | `dd-source/domains/xpq/apps/caniche-terraform/config/cloud/queries/` |
| "How does entity context/crawling work?" | `dd-source/domains/cloud-security-platform/apps/apis/siem-entity-crawler/` and `siem-entity-api/` |
| "How does a RAPID service work?" | `dd-source/domains/api_platform/rapid/` |
| "How does EVP track X get processed?" | `dd-source/domains/evp-workers/` |
| "What does detection rule X do?" | `logs-backend` rule-reducer + `dd-source` secmon-public-api |
| "How does DDSQL/Trino query work?" | `dd-source/domains/xpq/` and `dd-go/caniche/` |

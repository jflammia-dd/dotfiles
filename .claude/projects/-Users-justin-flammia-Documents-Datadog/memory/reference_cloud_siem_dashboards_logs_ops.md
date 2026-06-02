---
name: reference-cloud-siem-dashboards-logs-ops
description: "Where Cloud SIEM dashboards and monitors live as code, and how they deploy"
metadata: 
  node_type: memory
  type: reference
  originSessionId: c346e76e-a722-41bf-8703-53959444fbc4
---

Cloud SIEM operational dashboards and monitors are managed as code in `logs-ops`, NOT `terraform-config`. Home: `logs-ops/domains/cloud-security-platform/config/monitoring/cloud-siem`. Holds ~28 dashboard `.tf` files (mostly typed `datadog_dashboard`, a few `datadog_dashboard_json`), ~120 monitors, plus `logs/`, `metrics/`, `detection-rules/`. There is already a `dashboards/siem_entity_dashboard.tf` for `siem-entity-crawler` + `siem-entity-api`.

`terraform-config/k9-app` is the Cloud SIEM dir but holds only synthetics, no dashboards. Searching there alone falsely suggests click-ops. Always check `logs-ops` for any logs/security-platform team.

Deploy: Bazel `monitoring_module` macro (`logs-ops/rules/monitoring/monitoring.bzl`) fans out `plan`/`apply` jobs across `ENVS` (`rules/monitoring/constants.bzl`) = gov, prod, staging, all sites. NOT the `terraform-config` GitLab scheduled-apply flow. `env/` subdirs only hold per-site overrides; the base dashboard definition is shared across all envs.

Team convention: typed `datadog_dashboard` HCL with `locals` for service names and filters, opposite the org-wide "JSON for complex" default. Live `[K9][SIEM]` dashboards carry a "Provisioned by terraform, modify here or your changes will be discarded" footer.

Full guide: [[Dashboards as Code at Datadog]] (docs/). Related: [[Dashboards as Code at Datadog]] covers the org-wide route via [[terraform-config]] too.

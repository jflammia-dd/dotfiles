---
name: project_siem_era_prod_deploy_cmd
description: Exact command and expected timing for manual us1-only prod deployment of siem-entity-resolution-api
metadata: 
  node_type: memory
  type: project
  originSessionId: 6902e1c3-4751-4c0f-9ab6-a74b1192c1c9
---

Command for a manual us1-only prod deployment of `siem-entity-resolution-api`:

```
rapid release --env prod --branch main --datacenters us1.prod.dog --unsafe -s siem-entity-resolution-api
```

**Why:** Conductor is deactivated for this service (SEC-32487). All prod deploys are manual. The `--unsafe` flag skips the hardcoded 45-minute per-DC monitor gate. Without it the DDCI job times out after ~2h waiting for gates that never auto-pass.

**Expected timing:**
- Build phase (DDCI/delta_workflow_gen-release): ~15-20 min
- us1 pod rollout: ~20-25 min (~1 pod/min, ~21 pods in us1 based on June 2026 observations)
- Total: ~35-45 min

**How to apply:** Use this command whenever deploying to us1 only. For full multi-DC rollout, omit `--datacenters`. Always run in a clean terminal (not via Claude Code). The wrapper script blocks prod deploys by injecting `RAPID_INVOKER=claude_code`.

Documented in: `docs/siem-entity-resolution-api Prod Deployment Latency.md`

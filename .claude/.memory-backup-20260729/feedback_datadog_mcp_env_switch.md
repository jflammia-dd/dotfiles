---
name: feedback-datadog-mcp-env-switch
description: Ask Justin to re-authenticate the Datadog MCP when a query needs a different org/environment; do not give up
metadata: 
  node_type: memory
  type: feedback
  originSessionId: c346e76e-a722-41bf-8703-53959444fbc4
---

When a Datadog MCP query needs a different org or environment than the one currently authenticated, ask Justin to re-authenticate the Datadog MCP for that environment. A common trigger is a cross-org 404 like "Not found in this org" that names a different target org. The MCP defaults to staging, so prod resources surface this way. He will re-auth so the work can continue.

**Why:** The Datadog MCP is bound to one org at a time (it defaults to staging per [[reference_cloud_siem_dashboards_logs_ops]] context). A cross-org resource returns 404 with the target org named in `cross_org`. That is a re-auth step, not a hard wall.

**How to apply:** Do not conclude "I can't see into that org" and stop. Ask Justin to switch or re-auth the Datadog MCP to the needed environment, wait for confirmation, then re-run the query. Treat the cross-org 404 as a prompt to ask, not a reason to give up.

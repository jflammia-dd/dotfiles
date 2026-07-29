---
name: feedback_rapid_prod_deployment
description: "How to run ERS (and other Rapid service) production deployments. Wrapper script blocks prod; must run rapid binary directly."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 16d2788a-bcc3-418b-80e8-63a7261fc1a6
---

For production deployments, never use the Claude plugin wrapper script (`~/.claude/plugins/cache/.../rapid.sh`). The wrapper injects `RAPID_INVOKER=claude_code` which causes `rapid` to block production releases with "AI agents are not allowed to release with --env=prod".

**Why:** The rapid CLI explicitly blocks AI-agent-originated production deployments. The wrapper script sets `RAPID_INVOKER=claude_code` even when a human runs it, so the CLI still sees it as an AI invocation.

**How to apply:** For prod deployments, give the user this exact command to run themselves in a clean terminal (where `RAPID_INVOKER` is unset):

```bash
cd /Users/justin.flammia/dd/dd-source
rapid release --env prod --branch main --service siem-entity-resolution-api --wait
```

Staging deployments work fine through the wrapper. Only production is blocked.

Alternative: Mosaic UI at https://mosaic.us1.ddbuild.io/deployments/new?type=dynamic (Bundle: `*/helm/bundle`, Target: `prod`). This is the Rapid-recommended path for manual prod deploys.

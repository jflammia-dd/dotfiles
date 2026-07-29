---
name: feedback_ddci_mcp_auth
description: Authenticate DDCI MCP at the start of any CI debugging session before querying logs or job status
metadata: 
  node_type: memory
  type: feedback
  originSessionId: a4af6c84-be83-436f-a2f9-72b997621bd9
---

When a session involves investigating DDCI failures or CI job logs, authenticate the DDCI MCP server before attempting any queries. Without authentication the tools are unavailable and fallback approaches (Datadog MCP log searches, get_ddci_logs.sh) hit the wrong environment or return empty results.

**Why:** In a session investigating a failed DDCI run, Datadog MCP log queries hit ddstaging.datadoghq.com instead of prod and returned nothing. The get_ddci_logs.sh script produced incomplete output. Only after loading and authenticating mcp__ddci-mcp-prod did the proper investigation tools become available. This wasted significant time on dead-end approaches.

**How to apply:** At the start of any session that will involve CI debugging, call `mcp__ddci-mcp-prod__authenticate` immediately. Complete the OAuth flow in the browser. The DDCI MCP tools (getCIStatus, getJobErrorSummary, getJobLogs) are far more reliable than the fallback approaches and should always be the first choice.

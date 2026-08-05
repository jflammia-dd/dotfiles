---
name: project_sec_32487_poc_scoped
description: "SEC-32487's manual-CD gate on siem-entity-resolution-api was scoped to the PoC phase and is not a constraint on the productionized service"
metadata: 
  node_type: memory
  type: project
  originSessionId: 2b388718-e96f-4ff7-ae34-a81bfebbecff
  modified: 2026-08-05T15:59:22.385Z
---

SEC-32487 ("Disable automatic CD for siem-entity-resolution-api pending ERS GA") disabled automatic Conductor deploys to staging and prod because PoC-era resolution runs had no protection from pod termination mid-deploy. Justin confirmed (2026-08-05) that ticket was scoped to the PoC phase. Now that the productionized service is being built, that manual-CD status is stale and should not be treated as a current blocker on either the API or the worker.

**Why:** [[project_ers_branching]] already established the PoC graduated to production and all work moved off the PoC branch onto `main`. SEC-32487's exit criteria (ERS GA) was written for the PoC-era deployment model, not the productionized one.

**How to apply:** Don't cite SEC-32487 as a reason to keep deploys manual going forward. The underlying technical question it raised, whether graceful shutdown covers a full resolution run so continuous deploys don't interrupt in-flight work, is still worth confirming on its own merits. Treat that as an open technical question for the productionized service rather than an inherited PoC-era policy.

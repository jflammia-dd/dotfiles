---
name: feedback_aws_within_trust_not_shipped
description: "AWS within-trust resolution (CloudTrail assume-role walk) is in-flight Q3 work, not shipped"
metadata: 
  node_type: memory
  type: project
  originSessionId: d0961064-4b8d-463b-a727-2d62c03ab0d5
---

AWS within-trust resolution (the CloudTrail assume-role walk, `CloudTrailAssumeRoleStrategy` / "AWS Federation Strategy") is in-flight and is a Q3 goal. It has NOT shipped or gone GA. Do not describe it as "already ships," "done" or "Q3 deepens it."

**Why:** The code exists in the ERS repo (the strategy is registered in the planner, `enableLegacyAWSCloudTrail = true`), but code-merged is not the same as GA/live product capability. Justin owns this scope and corrected the claim twice.

**How to apply:** Frame all resolution beyond email matching as Q3 work. The four-provider resolution split: (1) email matching via `EmailExactStrategy` works out of the box today across AWS/GCP/Azure/GitHub (the early GA win); (2) AWS within-trust walk is the Q3 build for assumed-role session actors; (3) Azure GUID actors need Entra anchor ingestion + a net-new principal-ID cross-trust strategy; (4) GitHub login is the customer-config-dependent long tail. See [[project_github_actor_resolution]] and the docs `UEBA Q3 Integration Briefs.md` / `UEBA Q3 Deliverables and Ownership.md`.

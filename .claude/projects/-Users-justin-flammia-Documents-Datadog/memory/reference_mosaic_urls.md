---
name: reference_mosaic_urls
description: Mosaic URL patterns for Rapid service deployment tracking
metadata: 
  node_type: memory
  type: reference
  originSessionId: a9a13146-949c-4724-8968-3d06c815c0e8
---

Mosaic deployment tracking URLs for Rapid services:

- **All deployments for a service:** `https://mosaic.us1.ddbuild.io/services/details?name=<service-name>&service_tab=allDeployments`
  - Example: https://mosaic.us1.ddbuild.io/services/details?name=siem-entity-resolution-api&service_tab=allDeployments
- **DDCI change request:** `https://mosaic.us1.ddbuild.io/change-request/<request-id>` (shows delta_workflow_gen job, not the Conductor rollout per DC)

The `allDeployments` tab is the right place to track a rolling prod deployment progress. The change-request URL only tracks the CI pipeline (bundle generation), not the downstream Conductor apply.

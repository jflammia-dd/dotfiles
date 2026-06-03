---
name: feedback_rapid_json_deployment_gap
description: "rapid.json-only changes don't trigger Conductor redeployment; must use rapid release to force it"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: a9a13146-949c-4724-8968-3d06c815c0e8
---

`rapid.json` sits in `exports_files()` in a Rapid service's `BUILD.bazel` but is NOT a dependency of the Docker image build target. Conductor only schedules redeployment when the CI pipeline produces a new image artifact. A `rapid.json`-only change produces no new image so Conductor never picks it up and never regenerates the CNAB.

**Why:** Bazel's impact analysis traces changed files through dependency edges. Since `rapid.json` has no downstream build targets depending on it, the change is invisible to the pipeline.

**How to apply:** Any time a `rapid.json` change lands on main without a code change in the same PR (e.g., adding `runtime.isp: true`, changing gating config, updating slack channels), the change will not deploy automatically. Run `rapid release -s <service> --env <env> --branch main` to force `delta_workflow_gen` to run and regenerate the CNAB. For prod, the user must run this themselves (the Rapid CLI blocks AI agents from prod releases).

Discovered during SEC-32318 while investigating why `isp: true` in [PR #456739](https://github.com/DataDog/dd-source/pull/456739) never deployed the Fabric routing domain to prod.

We ship changes to the entity resolution pipeline on a rolling basis. The team runs a full integration test before each deployment. Failures in staging block the release until the team resolves the issue. Feature flags control the rollout of each change, allowing the team to limit exposure and roll back quickly if problems appear after release.

---
Edit summary: Added a sentence explaining that feature flags govern rollout, enabling limited exposure and fast rollback. Also fixed one passive-voice instance ("the issue is resolved" became "the team resolves the issue").
Style gate: passed in 2 pass(es)
Violations caught and fixed: 1 (passive voice: 1)
Ambiguous (not fixed): none

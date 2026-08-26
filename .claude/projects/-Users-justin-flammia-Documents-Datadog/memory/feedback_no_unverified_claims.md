---
name: feedback_no_unverified_claims
description: "Never say \"verified\", \"confirmed\" or \"checked\" unless the specific check was actually run against the specific source; label inference separately from citation."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: dc71663b-b0ab-4e3d-b061-5ccac8194903
  modified: 2026-08-26T17:58:52.679Z
---

Never use verification language ("verified", "confirmed", "checked", "re-verified") in a response unless the exact check was actually performed in that turn against the specific source being cited. If a claim is inference rather than something a source states directly, label it as inference inline, not folded into a cited paragraph.

**Why:** In the third-party OCI PoC runbook, a claim that local Minikube use is exempt from Datadog's registry-allowlist and image-signing policies was presented next to a real "References:" citation, as though it were sourced. It was actually my own inference. Earlier in the same session I told Justin both reference-link fixes were "confirmed" and the file was "re-verified" for other broken links, without having actually re-searched for the specific claim he later asked about. He caught this and called it untrustworthy, not just inaccurate.

**How to apply:**
1. Before writing "verified" or "confirmed" in any response, state what was checked and against what source in the same sentence. If you can't name the specific check, don't use the word.
2. In any document with a "References:" or citation line, every sentence in that paragraph must trace to something in those references. A claim that doesn't (an inference, an extrapolation, a "because X, therefore Y" not stated by the source) gets pulled into its own labeled line: "Inference, not documented policy: ..."
3. When the user says "keep researching," "check that," or "verify this" a second time, treat it as a request to redo the check now, not a request to summarize what you previously believed you had already done.
4. This applies most directly to runbooks, research answers and any artifact where the user's stated goal is avoiding hallucination or ambiguity (see [[project_er_proposal]] context and the `dd-research` skill's verification-loop discipline). The rule also holds for any conversational claim of having checked something, not just written artifacts.

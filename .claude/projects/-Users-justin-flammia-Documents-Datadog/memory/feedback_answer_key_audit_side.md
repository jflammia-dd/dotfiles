---
name: feedback_answer_key_audit_side
description: A corpus with a known answer keeps its answer key on the audit side, never importable by the step being gated.
metadata:
  type: feedback
---

When a step is gated on deriving an answer that is already written down somewhere, the
answer must live where the grader reads it and the step cannot. In the CloudTrail Actor
Ontology PoC this meant deleting `corpora.load_answer_key()` and moving the harmful-actor
name into `progress/expectations.json`, which `audit` reads and no step imports.

**Why:** A low-capability no-touch agent handed the puzzle and the answer sheet in the same
module will read the answer sheet, record it, pass the gate and demonstrate nothing. The
gate becomes un-failable, which is the same defect as a threshold set below the floor. It
is not a question of whether the agent is trustworthy. A one-line import is the path of
least resistance and it will be taken.

**How to apply:** Ground truth for a gated measurement goes in the audit-side file. Provide
no loader for it in the library the step imports, since the absence of the helper is most
of the enforcement. Say in the step spec that reading the key records nothing and that the
grader scores against ground truth held separately, so a copied answer passes the gate and
fails the audit. Related: [[project_ers_foundation_skeleton]].

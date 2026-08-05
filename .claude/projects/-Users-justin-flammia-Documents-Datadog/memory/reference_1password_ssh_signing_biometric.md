---
name: reference_1password_ssh_signing_biometric
description: "git commit signing uses 1Password SSH agent, which requires Touch ID approval and times out if Justin isn't at the keyboard"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 2b388718-e96f-4ff7-ae34-a81bfebbecff
  modified: 2026-08-05T21:59:14.631Z
---

Git commits are signed via SSH (`gpg.format: ssh`), backed by the 1Password SSH agent. Every `git commit` prompts a biometric (Touch ID) approval in 1Password. If Justin isn't physically at the keyboard when the prompt fires, it times out and the commit fails with errors like:

```
Couldn't sign message (signer): communication with agent failed?
```
or
```
Couldn't sign message (signer): agent refused operation?
```

**Why:** Confirmed directly by Justin on 2026-08-05 after this happened repeatedly during a long session. Not an AppGate issue, not a network issue, a biometric approval that requires physical presence.

**How to apply:** When a `git commit` fails with a signing/agent error, don't diagnose it as a network or AppGate problem (see [[feedback_ground_connectivity_diagnosis_empirically]]). Nothing is lost, the staged changes and commit message survive. Just report the failure plainly and ask Justin to authenticate, then retry the exact same commit once he confirms he's back.

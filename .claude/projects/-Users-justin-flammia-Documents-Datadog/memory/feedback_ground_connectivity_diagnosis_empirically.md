---
name: feedback_ground_connectivity_diagnosis_empirically
description: "Don't attribute connectivity failures to a named cause (AppGate, VPN, etc.) based on a high-level tool's self-reported error string; verify empirically first"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 2b388718-e96f-4ff7-ae34-a81bfebbecff
  modified: 2026-08-05T20:26:50.335Z
---

When a command fails with a network-flavored error (`not connected to appgate`, `Network is unreachable`, a git fetch timeout, etc.), don't repeat the tool's own diagnosis as fact. Check the actual network state directly before naming a cause: `ifconfig` for the relevant tunnel/interface, `netstat -rn` for the active default route, and a raw `nc -zv` connectivity test to both an internal host and a general internet host. Compare what a real connection failure looks like (`Network is unreachable`, no route) against a real timeout (packet loss, silence, interface otherwise healthy) before concluding what's actually broken.

**Why:** On 2026-08-05, Justin was on a moving train and then a cellular hotspot in a moving car. A `rapid terraform plan` retry loop kept failing with `not connected to appgate`, and Claude repeatedly reported "AppGate is disconnected" in status updates, parroting the CLI's own error string. Justin corrected this twice: once to point out AppGate couldn't be down because the session itself was alive, and once to say stop attributing failures to AppGate by name at all. Empirical checking both times showed the real cause was transient packet loss on an unstable cellular uplink rather than an AppGate session or config problem. `utun4` (the AppGate tunnel) stayed up throughout, with valid routes; individual probe/fetch calls just timed out unpredictably depending on that moment's signal quality.

**How to apply:** Any time a connectivity failure needs describing to the user, especially in a status update during a retry loop, ground the description in what was actually checked (interface state, route table, raw TCP result), not in whichever subsystem's name happened to appear in the failing tool's error message. If the direct checks weren't done, say the failure is unexplained rather than naming a cause. Applies broadly to any flaky-connection diagnosis, not just AppGate.

---
name: project-corporate-ai-gateway-model-defaults
description: "Claude Code runs through Datadog's corporate AI gateway; default model is Sonnet 5 at 256k context, with cost-efficiency pressure"
metadata: 
  node_type: memory
  type: project
  originSessionId: 275b2f36-d649-4e77-b53e-2a5e8453ae84
  modified: 2026-07-29T12:26:21.046Z
---

Justin's Claude Code sessions run through Datadog's corporate AI gateway. The gateway
sets the default model to **Sonnet 5 with a 256k context window** (not the 1M variant).
Sonnet 5 1M and Opus 5 are both selectable manually. The org actively encourages
"doing more with less" and tracking cost, so the default is the operating assumption.

**Why:** managed settings pin the default on every session restart, so a fresh session
gets Sonnet 5 / 256k regardless of what `/model` was set to previously. Any configuration
that only works comfortably at 1M is effectively broken for day-to-day use.

**How to apply:**
- Treat 256k as the real context budget when sizing always-on instruction text
  (global CLAUDE.md, AGENTS.md, CONTEXT.md, MEMORY.md index all load before the first turn).
- Prefer on-demand loading (skill bodies, imports) over always-on prose.
- Don't rely on Opus-only mechanisms. Notably, mid-conversation system messages
  (`{"role": "system"}` in `messages[]`) are supported on Opus 5 and Opus 4.8 but **not**
  Sonnet 5. Verify before recommending.
- Cost framing is per-turn, not per-session: standing instructions sit in the cached
  prefix (~0.1x on reads), so anything that mutates the front of the prefix mid-session
  forces a re-pay. Placement is a cost decision.

Related: [[reference-claude-startup-hooks]]

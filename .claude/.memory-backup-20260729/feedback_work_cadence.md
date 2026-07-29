---
name: ERS PoC work cadence
description: How Justin and Claude work through implementation tickets together
type: feedback
originSessionId: 7da81963-1801-4858-a15d-eb928abdeb37
---
When working through implementation tickets, follow this cadence exactly:

1. Justin says to start the next ticket.
2. Update the Jira ticket status and local Obsidian tracking docs (ERS - Status.md, ERS PoC - Implementation Plan.md) before touching any code.
3. Report back the EXACT steps planned before doing any work. Wait for acknowledgment.
4. Do work in manageable, reviewable chunks with good git hygiene. Always use `git-dd` instead of vanilla `git` for all git operations in dd-source.
5. Never work around blocked tools or commands. Stop, research the proper solution and ask the user if still blocked. Workarounds create technical debt and break assumptions other contributors depend on.
5. NEVER push to remote without explicit approval from Justin in that session. Approval in a prior session does not carry forward.
6. NEVER attribute Claude to git commit messages or PR descriptions.

**Why:** Justin wants to review and control every push. He also does not want to force his agentic workflow on other contributors.

**How to apply:** Workflow preferences (this cadence, agentic tooling choices, personal git habits) go in Obsidian memory only. Repo documentation (AGENTS.md, README.md) is written for any contributor and must not reference Justin's personal workflow or AI tooling preferences.

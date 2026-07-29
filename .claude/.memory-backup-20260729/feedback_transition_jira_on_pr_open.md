---
name: feedback-transition-jira-on-pr-open
description: "Always transition a Jira ticket to In Review when its PR is opened, without being asked"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: f31c3f69-db8b-4364-a517-45073a1c549c
---

When a draft PR is opened for a Jira ticket, transition that ticket to "In Review" immediately as part of the same action, don't wait to be asked.

Why: Justin explicitly asked for this as a standing rule after having to ask separately following SEC-34235's PR creation. It mirrors what already happened naturally for SEC-34237 (transitioned to In Review right after that PR opened), so the pattern should be automatic, not a manual follow-up.

How to apply: after `gh pr create` succeeds for a ticket, look up its Jira transitions and move it to whichever transition is literally named "In Review" (id may vary per project; on SEC project it has been transition id 51 → status id 11640). If multiple "In Review"-ish transitions exist (e.g. emoji variants), match the plain "In Review" one used elsewhere in the same epic for consistency. Applies to any ticket with an associated PR being opened, not just ERS/SEC-342xx tickets.

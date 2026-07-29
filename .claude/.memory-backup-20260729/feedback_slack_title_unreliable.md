---
name: Slack title field is unreliable
description: Never use Slack profile title for the role frontmatter field in person profiles
type: feedback
---

Do not use the Slack "title" field to populate the `role` frontmatter in person profiles. Slack titles are user-editable and some people use them for satire or jokes.

**Why:** Slack titles are not an authoritative source; they're self-set and often inaccurate or humorous.

**How to apply:** When enriching person profiles via Slack, only pull email, slack deep-link, and timezone/location. For `role`, use the `whoisthis` tool (Workday data) or ask the user directly.

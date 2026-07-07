---
name: No profile needed for manager references
description: Don't create vault profiles for people who only appear as a manager field in someone else's profile
type: feedback
originSessionId: 1c23090d-f3ac-49ec-afd9-a92499a4579b
---
Don't create a `people/` profile for someone who only appears as a `manager:` reference in another person's profile. A wiki-link to an uncreated page is fine in that context.

**Why:** Manager fields are often senior leaders or skip-level managers Justin doesn't interact with directly. Creating a full profile for every referenced manager adds noise without value.

**How to apply:** When adding a manager field to a profile, just use `[[Name]]` syntax. Only create a full profile if Justin has a direct relationship with that person. This overrides the "Creating a new person with enrichment" combined-step rule even when a lookup (Rimeto, whoisthis, Slack) surfaces enough info to fully enrich them: having the data available doesn't change the rule, it's about relationship, not data completeness. Repeated in 2026-07-07 session (created and enriched a manager-only reference from a Rimeto profile lookup before catching the mistake).

---
name: Detecting and marking inactive people
description: How to identify departed Datadog employees and update their person profiles accordingly
type: feedback
---

Person profiles have a `status:` frontmatter field with two allowed values: `active` or `inactive`.

**Why:** People leave Datadog. Profiles should reflect this so Justin knows who is still reachable and the vault doesn't become misleading over time.

**How to apply:**

1. **When enriching or updating any person profile**, run whoisthis first. If it returns `null`, the person has likely departed. Try one or two email variations before concluding they're gone.

2. **When whoisthis returns null for an existing active person**, proactively flag this to Justin and offer to mark them inactive. Don't silently ignore it.

3. **Marking someone inactive:**
   - Set `status: inactive` in frontmatter
   - Add `inactive` to the `tags:` field (YAML list format):
     ```yaml
     tags:
       - inactive
     ```
   - Do not attempt a Slack lookup for inactive people

4. **Never update a person note marked `status: inactive`.** Do not enrich, backfill, or modify their profile for any reason. Their record is frozen.

4. **New profiles** default to `status: active` (baked into the Person template).

5. **Currently inactive people** (as of 2026-03-17): Bruno Goncalves, Nimisha Saxena, JB Aviat, Quentin Blin, Roxane Brenier, Zhong Ren — all return null from whoisthis.

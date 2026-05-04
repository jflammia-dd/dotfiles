---
name: obsidian
description: >
  Use when working with the Datadog Obsidian vault at /Users/justin.flammia/Documents/Datadog.
  Triggers on: "ingest this", "process this source", "file this to the wiki", "add a person",
  "create a meeting note", "vault health", "lint the vault", "create a presentation",
  "update office tracking", "enrich this profile" or any request to create, edit or organize
  notes in the vault. Also use when the user shares a URL, doc or Slack thread and asks to
  summarize or file it.
---

# Obsidian Vault Workflows

Vault location: `/Users/justin.flammia/Documents/Datadog`

The vault is maintained as an LLMWiki: a persistent, compounding knowledge base where sources
are ingested, synthesized and filed into structured pages. Claude writes and maintains all wiki
pages. The user curates sources, directs analysis and asks questions.

## Ingest a Source

When the user shares a source (Confluence page, design doc, Slack thread, article, PDF):

1. Read the source. If it's a URL, fetch it. If it's pasted text, work with what's provided.
2. Discuss key takeaways with the user: what's important, what to emphasize, what to skip.
3. Create or update a `docs/` page with the synthesis:
   - Summary of the source's key claims
   - Implications or open questions
   - Links to related `items/` or `people/` pages using `[[Name]]` wiki-link syntax
4. Create or update `items/` pages for any concepts, systems or projects that appear without a page.
5. Update `people/` profiles if specific individuals are discussed.
6. Append to `docs/log.md`:
   ```
   ## [YYYY-MM-DD] ingest | <source title>
   Source: <URL or filename>
   Pages updated: [[Page Title]], [[Another Page]]
   ```

The user decides depth and emphasis at step 2. Filing something useful is better than filing nothing.

## File a Good Answer

When a conversation produces substantive analysis (an investigation result, a comparison, a design
decision, a how-something-works explanation):

1. Ask: "Should I file this to the wiki?"
2. If yes, determine the right destination:
   - `docs/` for synthesis, reference material or investigation results
   - `items/` for a concept or system explanation
3. Create or update the page with the analysis from the conversation.
4. Append to `docs/log.md`:
   ```
   ## [YYYY-MM-DD] query | <topic>
   Filed to: [[Page Title]]
   ```

## Vault Health Lint

Audit the vault for:

1. **Orphan pages**: pages in `docs/` or `items/` with no inbound `[[wiki-links]]`. Use Grep
   to find pages that aren't referenced from anywhere.
2. **Missing stubs**: concepts or systems referenced in `notes/` and `docs/` using `[[Name]]`
   syntax that don't have a corresponding `items/` page.
3. **Expandable stubs**: `items/` pages that are just a title and one line, where existing
   vault content could flesh them out.
4. **Stale people profiles**: `people/` pages missing enrichment fields (slack, role, team, location).
5. **Log coverage** — check `docs/log.md` for recent activity; flag if nothing has been ingested recently.

Report findings grouped by category. Offer to fix them.

## Create a Marp Presentation

1. Determine the topic and agree on an outline (or generate one from existing wiki content).
2. Create a file in `docs/` named `YYYY-MM-DD - <Title>.md` with this frontmatter:
   ```yaml
   ---
   marp: true
   theme: default
   paginate: true
   ---
   ```
3. Write slides separated by `---`. Typical structure: title slide, agenda, content slides
   (one main idea each), summary or next steps.
4. Draw content from existing `docs/` and `items/` pages where relevant.
5. Remind the user: open the file in editing mode (not Reading mode), then run
   "Marp Slides: Slide Preview" from the command palette.

## Looking Up Contact Data

People notes at `people/[First Last].md` are the primary source for contact and identity data. Read the frontmatter before searching externally:

- `email`: email, invites and whoisthis lookups
- `slack_id`: bare Slack user ID for @-mentions in Slack drafts via `/slackfmt` (format: `<@UXXX>`)
- `slack`: deep-link `slack://user?...` to open a DM in the Slack desktop app
- `atlassian_id`: @-mentions in Confluence and Jira comments
- `manager`: wiki-link to their manager's profile
- `doc_link`: link to the recurring 1-on-1 doc
- `how_to_work_with_me`: link to their personal working style doc
- `role`, `team`, `org`: job title, team and department
- `location`, `start_date`: city/remote and Datadog start date

If a field is blank, the profile needs enrichment. Run the workflow below.

## Person Enrichment

When enriching a new person profile in `people/`:

**Step 1 — whoisthis** (team, org, role, Slack ID):
```bash
cd /Users/justin.flammia/dd/dd-source && bzl run //domains/language_tools/apps/whoisthis:whoisthis -- email <email>
```
Populate: `team` (googleIdentity.team), `org` (workdayIdentity.department), `role`
(workdayIdentity.title), `email`, `location` (workdayIdentity.location). Extract
`slackIdentity.id` for step 2.

If whoisthis returns null: try common email variations (hyphens dropped from hyphenated last
names, non-obvious first name spellings). If still null, the person has likely departed —
set `status: inactive` and `tags: [inactive]`. Flag this to the user. Never enrich a profile
already marked `status: inactive`.

**Step 2 — Slack profile** (using ID from step 1):
```
slack_read_user_profile(user_id: "<slackIdentity.id>")
```
Populate:
- `slack` as `"[Display Name](slack://user?team=T024FSN2Y&id=SLACK_USER_ID)"` (deep-link)
- `slack_id` as the bare ID string, e.g. `U05QPSQGLL9` (used for @-mentioning in Slack drafts)

Do NOT use the Slack `title` field for `role`. It's user-editable and unreliable.

**Step 3 — Start date via Playwright:**
Navigate to `https://app.slack.com/client/E023QM6JUS0/D0A9XPWB6AF/rimeto_profile/<SLACK_USER_ID>`,
wait 3 seconds, extract the "Start Date" field. Set as `start_date: YYYY-MM-DD`.

## Office Attendance Tracking

Office tracking lives in `docs/office tracking/YYYY - In-Office Tracking.md`. Use the `/office`,
`/wfh` and `/pto` slash commands — they handle entry creation and compliance recalculation
automatically. Weeks are full Mon-Fri units owned by the month containing the Monday. Only record
WFH for notable deviations (bad weather, transit issues, illness); routine WFH is not recorded.

---
name: ingest-zoom-meeting
description: Use when ingesting Zoom AI-generated meeting notes (summaries, next steps, transcripts) into the Obsidian vault. Zoom AI systematically mistranscribes internal codenames, abbreviations and people's names.
---

# Ingest Zoom AI Meeting Notes

Zoom AI notes have predictable transcription errors. Always verify and correct before filing.

## Step 0: Fetch the Summary from Gmail (preferred)

If the user has not pasted the notes, search Gmail first. Zoom sends summaries shortly after each meeting.

```
search_messages(query: "from:zoom summary after:YYYY/MM/DD", max_results: 10)
```

Subject pattern: `Meeting assets for [Name] / [Name] - [Meeting Title] are ready!`

Fetch the matching message with `get_message(message_id)`. The full summary (quick recap, next steps and detailed sections) is in the HTML body. Strip HTML tags mentally; the text content is clean and complete.

If multiple summaries are returned, confirm which meeting the user wants before fetching. If none are found, ask the user to paste the content.

## Step 1: Pre-Filing Verification (never skip)

Before writing anything to the vault:

1. **List every person mentioned** and their role in the meeting
2. **Flag uncertain names.** Zoom AI commonly:
   - Assigns the same person multiple different names across the summary
   - Mishears names (e.g. "Shark" = Shariq, "Andra" = Antara, "Andre" = Antara)
   - Uses a recognizable but wrong name for someone (e.g. "Sarah" = Antara)
3. **Flag internal codenames** Zoom AI doesn't know:
   - Internal system names (e.g. "Red Apple" = REDAPL, "Iris" = deduplication service in REDAPL)
   - Project codenames and abbreviations the AI spells out phonetically
4. **Ask the user to confirm all flagged items before proceeding.** Do not guess.

## Step 2: Meeting Type

| Type | Where to file |
|---|---|
| 1:1 with one person | New `## YYYY-MM-DD` section in `people/[Person].md` |
| Group meeting / standup | New file `notes/YYYY-MM-DD - [Description].md` with attendees frontmatter |

## Step 3: File the Notes

For 1:1s, insert a new date section above the previous most-recent entry:

```markdown
## YYYY-MM-DD

[One-line summary. No Oxford commas. No em dashes.]

- **[Topic]**: key point
  - detail with [[wiki-links]] to people and systems
  - use `[[Full Name|Short Name]]` for display aliases

### Follow-up
- [ ] Action item description #todo
```

Use `[[wiki-link]]` syntax for every person, system or concept. Link to `items/` pages for systems, `people/` pages for individuals.

## Step 4: New People

For any person not yet in the vault, run the full enrichment workflow before filing:

1. **whoisthis**: populates team, org, role and Slack ID. Use the `dd:whoisthis` skill.
2. **Slack profile**: call `slack_read_user_profile(user_id)` for the deep-link and bare `slack_id`.
3. **Atlassian ID**: call `lookupJiraAccountId` with `searchString: firstname.lastname`.
4. **Start date and manager**: use Playwright to navigate to the Slack profile URL below, wait 3s, then extract the full panel text via `document.querySelector('.p-flexpane').innerText`.
   ```
   https://app.slack.com/client/E023QM6JUS0/D0A9XPWB6AF/rimeto_profile/<SLACK_USER_ID>
   ```
   Start date appears under "About me". Manager appears under "People > Manager".

Add a `## Context` section to the new profile linking back to where they first appeared.

## Step 5: Correct Zoom AI Errors

After the user confirms corrections, use `replace_all: true` to fix every occurrence in the filed content. Never leave uncorrected Zoom AI artifacts in the vault.

## Step 6: Update log.md

```
## [YYYY-MM-DD] ingest | 1:1 with [Person] (YYYY-MM-DD)
Source: Zoom AI email (Gmail message ID: [id]) or pasted
Pages updated: people/[Person].md, people/[New Person].md, items/[Concept].md
```

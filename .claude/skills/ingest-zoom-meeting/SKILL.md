---
name: ingest-zoom-meeting
description: Use when ingesting Zoom AI-generated meeting notes (hub.zoom.us/doc/ links or Gmail email summaries) into the Obsidian vault. Zoom AI systematically mistranscribes internal codenames, abbreviations and people's names.
---

# Ingest Zoom AI Meeting Notes

Zoom AI notes have predictable transcription errors. Always verify and correct before filing.

## Known Corrections

Apply these automatically without asking for confirmation. When new corrections are confirmed during an ingestion, add them to this table immediately.

### Codenames and systems

| Zoom AI writes | Correct | Notes |
|---|---|---|
| "Red Apple" | REDAPL | The entity ingestion pipeline |
| "Red Apple Infra" | `redaplinfra` | REDAPL's track in Temporal Husky |
| "Iris" / "iris system" | IRIS | Deduplication service inside REDAPL |
| "SIM entity" / "SIM entity track" | `siementity` | Temporal Husky track owned by Cloud SIEM |
| "Cloud SIM" | Cloud SIEM | Zoom AI consistently mishears "SIEM" as "SIM" |
| "UABA" | UEBA | User Entity and Behavior Analytics |
| "NED [X]" / "NAD [X]" | "Entity [X]" | e.g. "NAD Resolution" = "Entity Resolution" |
| "Enter ID" | Entra ID | Microsoft Entra ID identity provider |
| "Temporaliski" | Temporal Husky | Phonetic mishear of "Temporal Husky" |
| "Cold Strike" | CrowdStrike | Phonetic mishear of "CrowdStrike" |
| "Canine Simueba" | `#k9-siem-ueba` | The UEBA Slack channel |
| "Scooby-Doo" / "k9 Scooby-Doo" | `#k9-scooby-doo` | Cloud SIEM general Slack channel |
| "bluff" (in summary/comms context) | BLUF | Bottom Line Up Front acronym |
| "EBB track" / "EBB" | EVP track | Phonetic mishear of "EVP" (Entity Versioning Pipeline) |
| "Kanish" | [[Caniche]] | Zoom AI mishears the internal tool name "Caniche" |
| "N80" / "N80 resolution" | "entity" / "entity resolution" | Phonetic mishear of "entity" |

### People

| Zoom AI writes | Correct person | Notes |
|---|---|---|
| "Anthura" | [[Antara Hebbar]] | Common mishear of "Antara" |
| "Luis" / "Louis" | [[Loïc Fontolliet]] | Zoom AI mishears the French name "Loïc" as a more familiar name |
| "Andra" / "Andre" | [[Antara Hebbar]] | Common mishear of "Antara" |
| "Morten" | [[Martin Guyard]] | Common mishear of "Martin" |
| "Shark" / "Sharik" | [[Shariq Syed]] | Common mishear of "Shariq" |
| "Quinton" | [[Quentin Fabre]] | Phonetic mishear of the French name "Quentin" |
| "Roxanne" | [[Roxane Brenier]] | Mishear of the French name "Roxane" |

## Step 0: Fetch the Summary

Three ways to get the content, in priority order:

### Option A: Zoom Hub link (hub.zoom.us/doc/...)

When the user provides a `hub.zoom.us/doc/...` URL, fetch it via Playwright:

```
browser_navigate(url: "https://hub.zoom.us/doc/<id>...")
browser_wait_for(time: 3)
browser_snapshot()
```

If the page redirects to `zoom.us/signin`, the browser session is not logged in. Tell the user to log into Zoom in the browser, then retry navigation.

Once loaded, the page title shows the doc name and the snapshot contains the full structured content. Zoom Hub AI summaries use these sections: **Key Outcomes**, **Decisions Made**, **Pending Confirmation**, **Engineering Context for [Name]** and **Action Items**. Extract all text from those sections. The `browser_snapshot()` YAML includes all visible text. Read it carefully since the content is nested under heading and paragraph nodes.

Note: Zoom Hub docs don't always show the meeting date. Ask the user for the date and time if it's not visible in the snapshot.

### Option B: Gmail (for email-format summaries)

Zoom sends summaries by email shortly after each meeting.

```
search_messages(query: "from:zoom summary after:YYYY/MM/DD", max_results: 10)
```

Subject pattern: `Meeting assets for [Name] / [Name] - [Meeting Title] are ready!`

Fetch the matching message with `get_message(message_id)`. The full summary (quick recap, next steps and detailed sections) is in the HTML body. Strip HTML tags mentally; the text content is clean and complete.

If multiple summaries are returned, confirm which meeting the user wants before fetching.

### Option C: Pasted content

If neither option above works, ask the user to paste the content directly.

## Step 1: Pre-Filing Verification (never skip)

Before writing anything to the vault:

1. **Apply known corrections silently.** Scan the summary for every entry in the Known Corrections table above and note what will be substituted. No need to ask the user about these.
2. **List every remaining person mentioned** and their role in the meeting.
3. **Flag uncertain names.** Zoom AI commonly:
   - Assigns the same person multiple different names across the summary
   - Mishears names in ways not yet in the Known Corrections table
   - Uses a recognizable but wrong name for someone (e.g. "Sarah" = Antara)
4. **Flag unrecognized internal codenames** not already in the Known Corrections table:
   - Internal system names spelled out phonetically
   - Project codenames and abbreviations the AI doesn't know
5. **Ask the user to confirm only the flagged items before proceeding.** Do not guess.

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

If the user confirmed any new name or codename corrections during this ingestion, add them to the Known Corrections table now so future ingestions benefit from them. Attribute each new entry clearly (codename vs. person and a short note on the pattern).

## Step 6: Update log.md

```
## [YYYY-MM-DD] ingest | 1:1 with [Person] (YYYY-MM-DD)
Source: Zoom AI email (Gmail message ID: [id]) or pasted
Pages updated: [[Person]], [[New Person]], [[Concept]]
```

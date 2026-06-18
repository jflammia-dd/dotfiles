---
name: ingest-zoom-meeting
description: Use when ingesting Zoom AI meeting summaries into the Obsidian vault. Zoom AI systematically mistranscribes internal codenames, abbreviations and people's names.
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
| "ORC2" | org 2 | Datadog internal staging organization (dd.datad0g.com), used as a test environment |
| "Cloud Strike" / "CloudStrike" | CrowdStrike | Variant of "Cold Strike" with different mishear pattern |
| "SimLeads" | `#k9-siem-leads` | The Cloud SIEM leads Slack channel |
| "INR" | I&R | Investigation & Response, Corey Finley's team |

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
| "Bhutan" | [[Quentin Fabre]] | Phonetic mishear of "Quentin" (or his team name); confirmed 2026-06-16 |

## Step 0: Fetch the Summary

Four ways to get the content, in priority order:

### Option A: Exported file (preferred)

Zoom Hub can export the AI summary via **⋯ → Export → Markdown (.md)**. When the user provides a local file path (e.g. via `@/path/to/file.md` in Claude Code), read it directly. Markdown is the cleanest format; `.docx` and `.pdf` exports are also valid but harder to parse.

Do NOT move or copy the file to `attachments/` afterward. The filed vault notes are the artifact; the source file is ephemeral input.

**Distinguishing summary exports from raw transcripts:** Zoom Hub also offers **Download transcript**, which produces a VTT or plain-text file of the verbatim conversation. If the file looks like timestamped speaker turns with no Key Outcomes/Action Items structure, it is a raw transcript and out of scope for this skill. Tell the user to use the transcript ingestion skill instead.

### Option B: Zoom Hub link (hub.zoom.us/doc/...)

When the user provides a `hub.zoom.us/doc/...` URL, fetch it via Playwright:

```
browser_navigate(url: "https://hub.zoom.us/doc/<id>...")
browser_wait_for(time: 3)
browser_snapshot()
```

If the page redirects to `zoom.us/signin`, the browser session is not logged in. Tell the user to log into Zoom in the browser, then retry navigation.

Once loaded, the page title shows the doc name and the snapshot contains the full structured content. Zoom Hub AI summaries use these sections: **Key Outcomes**, **Decisions Made**, **Pending Confirmation**, **Engineering Context for [Name]** and **Action Items**. Extract all text from those sections. The `browser_snapshot()` YAML includes all visible text. Read it carefully since the content is nested under heading and paragraph nodes.

Note: Zoom Hub docs don't always show the meeting date. Ask the user for the date and time if it's not visible in the snapshot.

### Option C: Gmail (for email-format summaries)

Zoom sends summaries by email shortly after each meeting.

```
search_messages(query: "from:zoom summary after:YYYY/MM/DD", max_results: 10)
```

Subject pattern: `Meeting assets for [Name] / [Name] - [Meeting Title] are ready!`

Fetch the matching message with `get_message(message_id)`. The full summary (quick recap, next steps and detailed sections) is in the HTML body. Strip HTML tags mentally; the text content is clean and complete.

If multiple summaries are returned, confirm which meeting the user wants before fetching.

### Option D: Pasted content

If none of the above apply, ask the user to paste the content directly.

## Step 1: Pre-Filing Verification (never skip)

Before writing anything to the vault:

1. **Apply known corrections silently.** Scan the summary for every entry in the Known Corrections table above and note what will be substituted. No need to ask the user about these.
2. **Check the vault for every person mentioned.** Run `obsidian files folder=people` and check whether a profile exists before flagging anyone. A person with an existing profile is known and requires no confirmation. Only flag people whose profiles are absent.
3. **Flag uncertain names.** After applying known corrections, cross-reference every remaining name against the vault's people directory. Any name-shaped token that does not match a vault profile and is not already in the corrections table should be flagged as a candidate mishear. Zoom AI commonly:
   - Assigns the same person multiple different names across the summary
   - Mishears names in ways not yet in the Known Corrections table
   - Uses a recognizable but wrong name for someone (e.g. "Sarah" = Antara)
4. **Flag unrecognized internal codenames** not already in the Known Corrections table:
   - Internal system names spelled out phonetically
   - Project codenames and abbreviations the AI doesn't know
5. **If nothing is flagged, proceed directly to filing.** If there are flagged items, ask the user to confirm them one at a time before proceeding. Do not guess. When the user confirms a new name or codename correction, add it to the Known Corrections table immediately before filing.

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

For any person not yet in the vault, create a stub profile immediately so wiki-links resolve, then run enrichment after filing.

**Create the stub:**
```
obsidian create path="people/First Last.md" template=Person
```

**File the notes first** (Step 3), then run the full enrichment workflow:

1. **whoisthis**: populates team, org, role and Slack ID. Use the `dd:whoisthis` skill.
2. **Slack profile**: call `slack_read_user_profile(user_id)` for the deep-link and bare `slack_id`.
3. **Atlassian ID**: call `lookupJiraAccountId` with `searchString: firstname.lastname`.
4. **Start date and manager**: use Playwright to navigate to the Slack profile URL below, wait 3s, then extract the full panel text via `document.querySelector('.p-flexpane').innerText`.
   ```
   https://app.slack.com/client/E023QM6JUS0/D0A9XPWB6AF/rimeto_profile/<SLACK_USER_ID>
   ```
   Start date appears under "About me". Manager appears under "People > Manager".

Add a `## Context` section to the new profile linking back to where they first appeared.

## Step 5: Confirm Filing

After writing to the vault, report:
- The file path and section where the notes landed
- A one-sentence summary of the meeting
- The number of action items captured
- Any new people stubs created and whether enrichment is pending

Do not dump the full filed content into the conversation.

## Step 6: Update log.md

```
## [YYYY-MM-DD] ingest | 1:1 with [Person] (YYYY-MM-DD)
Source: Zoom AI email (Gmail message ID: [id]) or pasted
Pages updated: [[Person]], [[New Person]], [[Concept]]
```

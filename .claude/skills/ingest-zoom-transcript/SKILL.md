---
name: ingest-zoom-transcript
description: Use when ingesting a raw Zoom transcript (timestamped speaker turns, no AI summary structure) into the Obsidian vault. Companion to ingest-zoom-meeting, which explicitly refuses this input shape.
---

# Ingest Raw Zoom Transcripts

A raw transcript is verbatim, timestamped speaker turns (VTT-style or plain text), with no Key Outcomes/Decisions Made/Action Items structure. `ingest-zoom-meeting` handles Zoom AI summaries and explicitly stops on this shape. This skill picks up where it stops: same filing conventions and output format, different input handling because there is no AI summary to lean on, the whole thing has to be read and synthesized by hand.

## Step 0: Get the Transcript

Local file path only (`@/path/to/file.txt` or similar). Zoom's "Download transcript" export produces VTT or plain text; either is fine.

## Step 0.5: Confirm This Is In Scope

Read the file. If it has Key Outcomes/Decisions Made/Action Items sections, it's a Zoom AI summary, not a raw transcript. Stop and use `ingest-zoom-meeting` instead. If it's timestamped speaker turns with no such structure, proceed.

## Step 1: Identify Speakers

Transcripts label turns by whatever Zoom captured as the speaker name, which is not always a person:

- **Conference room mics**: a shared-room label (e.g. `NYC 29.14 Virginia Virginia`) can appear as the "speaker" for everyone physically in that room, not a single individual. Do not assume the label is a person's name. If the label looks room-shaped (floor/room number, a location word) or if dialogue content is inconsistent with one person, flag it and ask the user who was actually speaking before filing anything.
- **Known name corrections**: apply the same substitutions as `agents/skills/ingest-zoom-meeting/SKILL.md`'s Known Corrections table (people and codenames both). Zoom's live-transcript mishears are the same engine as its AI summaries, so the same table applies.
- **Vault cross-reference**: run `obsidian files folder=people` and check every speaker label against it. Flag any name-shaped label with no vault match and not already in the corrections table; don't guess.

## Step 2: Meeting Type

Same as `ingest-zoom-meeting`:

| Type | Where to file |
|---|---|
| 1:1 with one person | New `## YYYY-MM-DD` section in `people/[Person].md` |
| Group meeting / standup | New file `notes/YYYY-MM-DD - [Description].md` with attendees frontmatter |

## Step 3: Synthesize, Don't Transcribe

There is no AI summary to extract from, so read the full transcript and write the summary yourself. Skip filler, false starts and small talk. Pull out: what was actually decided, what's still open, who owns what and any concrete facts (numbers, names, tools, deadlines) that came up. A transcript this raw usually runs long, thin it down hard, the note should read like a synthesized summary, not a cleaned-up script.

## Step 4: File the Notes

Identical format and rules to `ingest-zoom-meeting` Step 3 (topic bullets, `[[wiki-links]]`, `### Follow-up` with `#todo` items, 1:1 insertion order, group-meeting attendees frontmatter). Reuse that skill's format section rather than duplicating it here.

## Step 5: New People

Same as `ingest-zoom-meeting` Step 4: create a stub immediately so links resolve, file the notes, then run the whoisthis + Slack + Atlassian ID + start-date/manager enrichment workflow. The Slack profile panel (`https://app.slack.com/client/E023QM6JUS0/D0A9XPWB6AF/rimeto_profile/<SLACK_USER_ID>`) requires an active logged-in Slack session in the Playwright-controlled browser; if the panel doesn't load, ask the user to log in there and retry rather than skipping the fields.

## Step 6: Confirm Filing

Same as `ingest-zoom-meeting` Step 5: report the file path and section, a one-sentence summary, the action-item count and any new people stubs plus enrichment status. Don't dump the full filed content into the conversation.

## Step 7: Update log.md

```
## [YYYY-MM-DD] ingest | 1:1 with [Person] (YYYY-MM-DD)
Source: raw Zoom transcript (local file)
Pages updated: [[Person]], [[New Person]], [[Concept]]
```

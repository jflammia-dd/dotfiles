---
name: ueba-sync-recap
description: Posts a Slack recap of the weekly UEBA Sync (Wednesday 11am ET) for people who missed it, and persists the same entry to the UEBA Confluence page's Project Updates section. Invoke when Justin says "recap the UEBA sync", "post the UEBA sync summary", "summarize this week's UEBA sync" or anything about sharing this week's UEBA sync notes to Slack. Pulls the live Google Doc notes and the Zoom AI summary, groups status by O4 KR (fixed weekly structure), tags blocked-item owners with real Slack mentions, links every epic with descriptive anchor text and delivers via slackfmt.
---

# UEBA Sync Recap

Turns this week's UEBA Sync (recurring Wednesday 11am ET, `UEBA Sync` on the calendar) into a Slack-native status recap for people who weren't there and a matching dated entry on the `UEBA` Confluence page. Leads with KR status, not meeting chronology, using a fixed KR1/KR2/KR3 structure every week so leadership can track the same three lines over time and report them up.

UEBA is Q3 OKR **O4** in the Cloud SIEM OKR doc. O4 has three KRs:
- **KR1**: orgs import their user directory from an IdP and adopt Entity Risks (includes Workday side panel, CrowdStrike Asset Inventory, full-text search in User Inventory)
- **KR2**: orgs achieve a >30% attribution rate on human-actor signals (the ERS work: Email, AWS, GCP, Azure, Point-in-Time, and anything feeding actor resolution)
- **KR3**: orgs have a true positive Behavior AI signal, TPR ≥90% / FPR <0.001%

The doc's exact KR bullet text is the ground truth for what belongs where (e.g. "find users fast with full-text search" under KR1 is what resolved FTS's mapping), not a hardcoded epic list.

## Reference: constants

These are stable across weeks. Use them directly rather than rediscovering them each run.

| What | Value |
|---|---|
| OKR doc ID | `1HxaRKaiLKgZZVjqev7tic7RgIQ8MphZPnh2kQZDN94Q` ("Cloud SIEM OKRs - 2026Q3") |
| Confluence page ID | `6459031643` (title `UEBA`, CSiem space) |
| Confluence Project Updates deep link (use in the Slack closing line) | `https://datadoghq.atlassian.net/wiki/spaces/CSiem/pages/6459031643/UEBA#Project-Updates` |
| Comment marker 1 (must survive every edit) | `d225675b-f484-4f55-8b15-9bacda5c0de2` (anchors "entity activity" in the intro paragraph) |
| Comment marker 2 (must survive every edit) | `a53dcc9d-c077-4c32-8014-3fded8bf3760` (anchors "anchored entities" in the workstreams list) |
| Context panel detection string (idempotency check) | `Cloud SIEM Q3 OKR O4's three key results` |
| Project Updates `<h2>` anchor | `<h2 local-id="ff7e94e0f3d4">Project Updates</h2>` |
| Slack channel | `#k9-siem-ueba` (`C0B0QRZLCKX`) |

## Reference: known epics

Descriptive anchor text for each epic, sourced from its Jira `summary` field. Use this table first. Only call `get_issue` for a key not listed here or if you suspect a summary has changed (epic titles rarely change once created), then add the new row to this table for next time.

| Key | Jira summary | Descriptive anchor text (use verbatim in both Slack and Confluence) |
|---|---|---|
| SEC-34444 | Cloud SIEM UEBA - Workday - Q3 2026 | Workday side panel |
| SEC-34228 | ERS - Resolve Email Address Actors to the Human | Email actor resolution |
| SEC-33707 | ERS - Resolve AWS Role-Chained Actors to the Human | AWS role-chain resolution |
| SEC-33708 | ERS - Resolve GCP Service-Account Impersonation | GCP service-account impersonation resolution |
| SEC-33709 | ERS - Resolve Azure Actors Logged as Object-ID GUID | Azure object-ID resolution |
| SEC-33713 | ERS - Point-in-Time Resolution for User Entity Pill in Signals | Point-in-time resolution |

Assets (CrowdStrike Asset Inventory) and FTS (full-text search in User Inventory) have no epic key yet as of 2026-07-15. Leave them as plain text until one exists. Check this each week. A topic gaining a key is real news (worth a bullet noting it), not just a formatting change.

## Step 1: Invoke justins-voice

Every sentence in the draft is governed by it. This recap is a broadcast Slack announcement in justins-voice terms: "Hi all," opener, progressive build, a single bolded severity word (`*blocked*`) where it applies, numbered/lettered structure only if genuinely needed, close with a named ask.

## Step 2: Find this week's meeting

Compute the most recent Wednesday:

```bash
python3 -c "
from datetime import date, timedelta
today = date.today()
days_back = (today.weekday() - 2) % 7
print((today - timedelta(days=days_back)).isoformat())
"
```

Find the event and its attached notes doc:

```
mcp__datadog-google-calendar__list_events(query: "UEBA Sync", time_min: "<date>T00:00:00-04:00", time_max: "<date>T23:59:59-04:00")
mcp__datadog-google-calendar__get_event(event_id: <id from above>)
```

`get_event` returns an `attachments` array with the Google Doc's `fileId`. That doc is a running log with one section per week (newest section first). This week's notes doc URL feeds the Confluence context panel in Step 9, so hold onto it.

## Step 3: Pull the Zoom AI summary (secondary source only)

```
mcp__datadog-gmail__search_messages(query: "from:zoom summary subject:\"UEBA Sync\" after:<date>")
mcp__datadog-gmail__get_message(message_id: <id>)
```

**Known limitation: Zoom's speaker attribution in this meeting is by conference room, not by person** ("NYC", "Paris"). Never use the Zoom summary to decide who owns what. Use it only for:
- catching detail the doc's terse bullets compressed away (e.g. a specific nuance on what someone is doing this week)
- sanity-checking that the doc's top section is actually this week's (its "Quick recap" and "Next steps" should match the doc's newest section topic-for-topic)

If the doc's top section doesn't match the Zoom recap, stop and ask before drafting. The doc is manually maintained; a mismatch means a section got skipped or reordered.

## Step 4: Read the notes doc without losing ownership data

**Do not use `get_doc_as_markdown`.** This doc uses Google Docs person chips to record who owns each item, and the markdown export silently drops every chip, leaving blank owners. Use the raw document instead:

```
mcp__datadog-google-workspace__read_document(document_id: <fileId>, content_only: true)
```

This response is large enough that it may be saved to a file instead of returned inline. Either way, run the bundled extractor over the JSON (inline result: save it to a temp file first) to get person-chip ownership correlated with its surrounding bullet text, in document order:

```bash
python3 /Users/justin.flammia/Documents/Datadog/agents/skills/ueba-sync-recap/scripts/extract_doc_owners.py <path-to-doc-json>
```

This prints `PERSON <name> <email>` and `TEXT <content>` lines in document order. Read the first section (topmost `Attendees:` block through the next one) as this week's notes. A `PERSON` line immediately after a topic label (`"Email - "`, `"AWS - "`) is that topic's owner; a `PERSON` line inside a sub-bullet (e.g. after `"waiting product brief from "`) is who a blocked item is waiting on, not the owner.

## Step 5: Resolve each named owner to a Slack ID

For every person who owns an item this week (not just blocked ones), read `people/[First Last].md` and check `slack_id` per the lookup table in `agents/skills/obsidian/references/vault-conventions.md`.

**If a person note is missing, or exists but has no `slack_id`:** stop and say so before drafting anything. Run the enrichment workflow (whoisthis + Slack profile lookup, per `agents/skills/ingest-zoom-meeting/SKILL.md` Step 4) to fill the gap, then continue. Do not invent a mention format or skip the tag silently. This keeps the Slack ID living in one place (the person note) rather than a second copy inside this skill.

## Step 6: Pull the O4 KR structure and match topics to KRs

Fetch the OKR doc for the fixed KR headers (safe to use markdown export here, there's no person-chip data to lose):

```
mcp__datadog-google-workspace__get_doc_as_markdown(document_id: "1HxaRKaiLKgZZVjqev7tic7RgIQ8MphZPnh2kQZDN94Q")
```

Extract O4's KR1/KR2/KR3 bullet text. These three KRs are this week's fixed section headers, in this order, every week, regardless of what has an update.

For each topic surfaced in Step 4, match it to a KR by content against the doc's bullet text, not by a hardcoded epic-to-KR table (KR text and epic ownership both shift between quarters; hardcoding breaks silently).

For each topic with a Jira key, check the known-epics reference table above first. Only fetch a fresh copy if the key is missing from that table:

```
mcp__datadog-atlassian__get_issue(issue_key: "SEC-XXXXX")
```

This can exceed the inline token limit and get saved to a file. Extract just what's needed:

```bash
python3 -c "
import json
d = json.load(open('<path>'))
f = d['fields']
parent = f.get('parent') or {}
print(d['key'], '|', f['summary'], '|', f['status']['name'], '| parent:', parent.get('key'), (parent.get('fields') or {}).get('summary'))
"
```

Add any new key, summary and a short descriptive anchor (2-6 words) to the reference table in this file so next week's run skips the fetch.

**If a topic doesn't clearly match any O4 KR bullet, stop and ask** which KR it belongs to, or whether it's genuinely unmapped. Do not force-fit it to avoid asking; a wrong KR attribution in a leadership-facing report is worse than a pause. If a topic turns out to belong to a different OKR entirely (e.g. crawler work matching an O1 bullet instead of anything in O4), drop it from this recap and flag it to Justin for separate follow-up. Don't include an out-of-scope OKR item just because someone raised it in the sync.

## Step 7: Draft the Slack recap

Structure:

```
Hi all, this week's UEBA Sync recap for anyone who couldn't make the meeting.

*O4, KR1: <KR1 summary>*
- [<descriptive epic title>](<jira link>): <status this week, 1-2 sentences, names the owner>
- <topic with no epic key>: <status this week, 1-2 sentences, names the owner>
*O4, KR2: <KR2 summary>*
- [<descriptive epic title>](<jira link>): <status this week, 1-2 sentences, names the owner>
- ...
*O4, KR3: <KR3 summary>*
- <topic, or "No update this week.">
Full history and links: [UEBA Project Updates page](https://datadoghq.atlassian.net/wiki/spaces/CSiem/pages/6459031643/UEBA#Project-Updates)
```

Rules:
- All three KR sections appear every week, even with no news, so leadership can see a KR go quiet rather than have it silently disappear. Use "No update this week." rather than omitting the section.
- One blank line after the opening sentence, before the first KR header. No blank lines between KR sections after that. The whole KR block reads as one contiguous unit.
- One bullet per topic. Name the owner in prose; only wrap it in a real `<@slack_id>` mention if that person is the one something is blocked on, or the item is itself blocked and they're the owner. Routine on-track updates name the person without a notifying tag, so a weekly recap doesn't ping everyone every week.
- Blocked items always get `*blocked*` (bold, lowercase, matches justins-voice's single-severity-word convention) and a real mention for whoever it's waiting on.
- Close with a named ask only if there's a real one this week (a decision needed, a review requested), placed before the closing Confluence link. Otherwise skip the ask rather than manufacture one.
- **Any topic with a Jira key gets a link with descriptive anchor text from the reference table above, never the raw key as the link text.**
- The closing line is always the last line of the message, no blank line before it, and always the Project Updates deep link (constants table above), not the tiny page link.
- **Write every link, Confluence and Jira alike, as standard markdown `[text](url)`.** `slackfmt` (Step 11) expects GitHub-flavored markdown as input and converts it to a real Slack hyperlink. Slack's own `<url|text>` syntax is what a live message looks like once posted, not what you feed into the formatter.

## Step 8: Draft the Confluence entry

Same content as the Slack KR bullets, same descriptive anchor text from the reference table, formatted as Confluence storage XML. Save this to a file (referenced as `<entry_html_file>` in Step 9); it becomes the `entry_html_file` input to `build_confluence_body.py`.

```xml
<h3><time datetime="YYYY-MM-DD" /></h3>
<p><strong>O4, KR1: <KR1 summary></strong></p>
<ul><li><p><a href="https://datadoghq.atlassian.net/browse/SEC-XXXXX">Descriptive anchor text</a> (SEC-XXXXX): status...</p></li></ul>
<p><strong>O4, KR2: <KR2 summary></strong></p>
<ul><li><p>...</p></li></ul>
<p><strong>O4, KR3: <KR3 summary></strong></p>
<ul><li><p>...</p></li></ul>
```

Rules:
- Link format is `<a href="...">Descriptive anchor text</a> (SEC-XXXXX)`, anchor text first, key in parens after, so the reader gets both a scannable label and the raw key for cross-reference. Never `<a href="...">SEC-XXXXX</a>` (the bug this skill shipped on 2026-07-15, fixed the same day).
- Escape literal `>` as `&gt;` in prose (e.g. KR2's ">30%").
- Topics without a Jira key stay as plain text, matching Step 7's Slack rule.

On the very first run ever (context panel not yet on the page), also save the panel content to a separate file for `build_confluence_body.py`'s `--panel-html-file`:

```xml
<ac:structured-macro ac:name="info" ac:schema-version="1"><ac:rich-text-body><p>This section is updated weekly after the UEBA Sync (Wednesdays, 11am ET), a cross-team sync covering entity ingestion, resolution and Behavior AI status. Updates are grouped against Cloud SIEM Q3 OKR O4's three key results, defined in the <a href="https://docs.google.com/document/d/1HxaRKaiLKgZZVjqev7tic7RgIQ8MphZPnh2kQZDN94Q/edit">Cloud SIEM OKRs - 2026Q3</a> doc. Full meeting notes live in the <a href="[THIS WEEK'S NOTES DOC URL FROM STEP 2]">UEBA Sync notes</a> doc.</p></ac:rich-text-body></ac:structured-macro>
```

After the first run, the panel is permanent and `--panel-html-file` is never needed again.

## Step 9: Show both drafts, get approval

Present the Slack recap and the Confluence entry together, as readable prose, not raw XML. Wait for explicit approval. Do not proceed past this step without it.

## Step 10: Pre-flight link checks

Run these before touching Confluence or Slack. Both catch real bugs this skill has shipped before.

**10a. No bare-key Confluence anchors.** Confirm the Confluence entry file has no `<a href="...SEC-\d+">SEC-\d+</a>` pattern (anchor text identical to the key):

```bash
grep -oE '<a href="https://datadoghq\.atlassian\.net/browse/(SEC-[0-9]+)">\1</a>' <entry_html_file>
```

Any output here is a bug. `build_confluence_body.py` (Step 11) also enforces this and will refuse to run but check it here too so you catch it before drafting is "done."

**10b. Every Jira key in the Slack draft is linked, and no Slack-native link syntax leaked in.**

```bash
# every SEC-XXXXX mentioned anywhere in the draft
grep -oE 'SEC-[0-9]+' <slack_draft_file> | sort -u > /tmp/ueba_keys_all.txt
# every SEC-XXXXX that's actually inside a markdown link
grep -oE '\]\(https://datadoghq\.atlassian\.net/browse/SEC-[0-9]+\)' <slack_draft_file> \
  | grep -oE 'SEC-[0-9]+' | sort -u > /tmp/ueba_keys_linked.txt
comm -23 /tmp/ueba_keys_all.txt /tmp/ueba_keys_linked.txt
# any output = an unlinked key, fix before continuing

# Slack's own <url|text> syntax should never appear in a file destined for slackfmt
grep -nE '<https?://[^|>]*\|' <slack_draft_file>
# any output = wrong link syntax, rewrite as markdown [text](url)
```

## Step 11: Persist to Confluence

The `UEBA` page (`6459031643`) has a "Project Updates" section that this skill maintains, one dated entry per week, newest first. It absorbed the retired `ueba-weekly-update` skill's old per-workstream table entirely: rows dated 2026-05-08 and earlier are that skill's format and stay as history, untouched.

**11a. Fetch the current page body and version:**

```
mcp__datadog-atlassian__get_page(page_id: "6459031643")
```

Always fetch fresh immediately before editing. Never reuse a body from earlier in the conversation, even from the same session, since the version number must match exactly.

**11b. Save the fetched body to a file**, then build the new body with the helper script instead of hand-editing strings:

```bash
python3 /Users/justin.flammia/Documents/Datadog/agents/skills/ueba-sync-recap/scripts/build_confluence_body.py \
  <current_body_file> <entry_html_file> \
  --date YYYY-MM-DD \
  --out <new_body_file>
  # add --panel-html-file <panel_html_file> only on the first-ever run
```

The script refuses to run (nonzero exit, no file written) if: an entry for that date already exists, any anchor text in the entry is just the bare Jira key or either inline comment marker would be lost. Read its error and fix the input file rather than overriding it.

**11c. Read `<new_body_file>` in full immediately before the next step.** This is the exact content that goes into `update_page`'s `body` argument. Never type or paste a placeholder, a summary or a partial value there. On 2026-07-15 this skill's body argument was accidentally sent as the literal string `<PLACEHOLDER>`, which briefly overwrote the live page. The fix: the value passed to `body` must always be the freshly-read output of Step 11b's script, copied verbatim, never hand-typed.

**11d. Call update_page:**

```
mcp__datadog-atlassian__update_page(
  page_id: "6459031643",
  title: "UEBA",
  version_number: <fetched_version + 1>,
  body: <exact content of new_body_file>
)
```

## Step 12: Deliver to Slack

Never post via the Slack MCP. Use the `clipboard-slack` workflow (`agents/workflows/clipboard-slack.md`) in clipboard mode. Pipe the approved markdown to `slackfmt` on its own, with nothing chained after it:

```bash
cat <path to approved draft> | npx @slackfmt/cli@latest
```

`slackfmt` copies to the clipboard itself and prints "Copied to clipboard!" to stdout. Never pipe its output into `pbcopy`; that overwrites the clipboard with the literal confirmation string instead of the formatted message.

## Step 13: Log it

Append to `docs/log.md`:

```
## [YYYY-MM-DD] update | UEBA Sync recap posted to Slack and Confluence
Source: [[UEBA Sync Notes]] (week of <meeting date>), Zoom AI summary
Pages updated: [[UEBA]]
```

---
name: ueba-weekly-update
description: Adds a weekly Friday Project Updates entry to the UEBA Confluence page. Invoke whenever Justin says "add weekly update", "Friday UEBA update", "update the UEBA page", "add a project update", or anything about adding or writing the weekly UEBA status entry. Pulls from Obsidian notes, Jira epics and Slack, drafts the entry covering all active workstreams, shows it for review, then applies the update and logs it in the vault.
---

# UEBA Weekly Update

Adds a weekly Friday entry to the Project Updates table on the UEBA Confluence page.

- **Page:** https://datadoghq.atlassian.net/wiki/spaces/CSiem/pages/6459031643/UEBA
- **Page ID:** `6459031643`
- **Page title:** always `UEBA` (never changes)

The table is near the top of the page (after the intro metadata block), with the most recent entry first.

## Step 1: Invoke justins-voice

Invoke the `justins-voice` skill before drafting any prose. Every word in the entry is governed by it: no Oxford commas, no em dashes, active voice, backtick formatting for technical identifiers, short factual bullets that lead with the insight rather than the setup.

## Step 2: Determine the entry date

The entry date is the most recent Friday. Compute it:

```bash
python3 -c "
from datetime import date, timedelta
today = date.today()
days_back = (today.weekday() - 4) % 7
print((today - timedelta(days=days_back)).isoformat())
"
```

## Step 3: Gather context (run in parallel)

Pull from all three sources before drafting.

### Obsidian vault (past 7 days)

List files in `/Users/justin.flammia/Documents/Datadog/notes/` whose names start with a date in the past 7 days. Read the ones that mention ERS, Entity Resolution, Entity Ingestion, Entity Context, `siementity`, REDAPL, Temporal Husky, design partners or PoC work. Daily notes and meeting notes are both relevant.

### Jira epics

Fetch recent comments from active epics using `mcp__datadog-atlassian__get_issue`. Currently active epics:

| Workstream | Epic |
|---|---|
| Entity Resolution PoC | `SEC-30573` |

Focus on comments from the past 7 days. Older comments are context, not news.

### Slack

Only read specific threads you already have a pointer to from Obsidian notes or Jira comments. Do not search Slack broadly.

## Step 4: Identify what to cover

Derive active workstreams from the Obsidian notes read in Step 3. A workstream is active for this entry if it appears in any note from the past 7 days. The notes are the ground truth; do not rely on a hardcoded list.

The four UEBA workstreams to scan for:

| Workstream | Signals to look for in notes |
|---|---|
| Entity Resolution (ERS) | "entity resolution", "ERS", "SEC-30573", "PoC", resolution strategy names, `siem_er` |
| Entity Ingestion | "entity ingestion", "entity context", "siementity", "redaplinfra", "design partner", crawlers, IdP |
| Entity Extraction | "entity extraction", "OCSF", log normalization, field extraction |
| Entity Context | "entity context" as a downstream consumer (composing entity state for detection/scoring/investigation) |

Note: "entity context" is overloaded. When it refers to the ingestion/crawler work, that is Entity Ingestion. When it refers to the downstream consumer workstream that composes entity state for detection and scoring surfaces, that is Entity Context. Context in the notes will disambiguate.

After scanning, list the workstreams that appeared. Those are the sections to include. A workstream that was active in recent weeks but had no notes this week can be acknowledged with a single "no updates this week" omission (just leave the section out entirely).

General initiative notes (a new Slack channel, a cross-cutting announcement) go at the end of the entry as standalone paragraphs, not under any workstream header.

## Step 5 — Draft the entry

### Row format (Confluence storage XML)

```xml
<tr>
<td><p><time datetime="YYYY-MM-DD" /> </p></td>
<td>[content cell]</td>
</tr>
```

### Content cell structure

Each active workstream with news this week:

```xml
<p><strong>Workstream Name</strong></p>
<ul>
<li><p>bullet one</p></li>
<li><p>bullet two</p></li>
</ul>
```

General notes at the end (not under a workstream):

```xml
<p><a href="https://dd.enterprise.slack.com/archives/CHANNEL_ID">#channel-name</a> description of general note</p>
```

### Writing rules

These come from justins-voice. Treat them as non-negotiable:

- No Oxford commas. "X, Y and Z" not "X, Y, and Z."
- No em dashes. Restructure the sentence.
- Active voice. Name the subject that performed the action.
- Backtick formatting for technical identifiers: track names (`siementity`, `redaplinfra`), branch names, service names, feature flag names.
- Link to relevant Confluence docs and Slack channels. Never leave a bare URL as plain text.
- Lead with the most significant workstream.
- Bullets state what happened and what it means. They do not preview what comes next or describe in-progress work without a concrete milestone.

### Full example (reference, not a template to fill in)

```xml
<tr>
<td><p><time datetime="2026-05-08" /> </p></td>
<td>
<p><strong>Entity Resolution (ERS)</strong></p>
<ul>
<li><p>Phase 2 implementation started: direct write to Temporal Husky via EVP intake client; query-before-write pattern implemented in <code>justin.flammia/SEC-30573-entity-resolution-poc</code></p></li>
</ul>
<p><strong>Entity Ingestion</strong></p>
<ul>
<li><p>E2E testing complete on <code>siementity</code> track; design partner org (PWC) verified end-to-end</p></li>
<li><p>Okta content pack complete; Entra ID date confirmed by Antara</p></li>
</ul>
</td>
</tr>
```

## Step 6: Show the draft for review

Present the entry to Justin as readable prose (not raw XML). One workstream section at a time is easier to review than a wall of XML. Wait for explicit approval before proceeding. Do not apply the update without it.

## Step 7: Apply the update

The `confluence-write` skill is the default for Confluence edits because it makes surgical text-level changes that preserve inline comment markers and version history. Use it for any corrections to existing text (fixing a typo, updating a bullet, changing a date). See the `confluence-write` skill for usage.

Adding a new table row is a structural operation (`<tr>` insertion) that `confluence-write.py` cannot do via text replacement. For this specific case, use a targeted single-substitution body update: one string in the body changes, everything else is preserved verbatim.

**7a. Fetch the current page body and version:**

```
mcp__datadog-atlassian__get_page(page_id: "6459031643")
```

**7b. Locate the insertion point.** The Project Updates table header row ends with this unique string:

```
<p local-id="9251cf047bba" /></th></tr>
```

**7c. Construct the new body** with exactly one string substitution on the fetched body:

- Find: `<p local-id="9251cf047bba" /></th></tr>`
- Replace with: `<p local-id="9251cf047bba" /></th></tr>[NEW ROW XML]`

No other part of the body changes.

**7d. Verify comment markers are intact.** Before calling update_page, confirm the body string still contains both inline comment marker refs:
- `d225675b-f484-4f55-8b15-9bacda5c0de2` (anchors "entity activity" in the intro paragraph)
- `a53dcc9d-c077-4c32-8014-3fded8bf3760` (anchors "anchored entities" in the workstreams list)

If either is absent, stop and re-fetch the body before proceeding.

**7e. Call update_page:**

```
mcp__datadog-atlassian__update_page(
  page_id: "6459031643",
  title: "UEBA",
  version_number: <fetched_version + 1>,
  body: <updated body>
)
```

**7f. Correct existing content using confluence-write.** If Justin asks to fix wording, change a date or update a bullet in an existing row after the fact, use `confluence-write.py` for that edit rather than a full-body update:

```bash
~/.claude/plugins/cache/datadog-claude-plugins/confluence-write/[version]/scripts/confluence-write.py \
  6459031643 "old text" "new text"
```

Use `--dry-run` to preview before applying. Use `--occurrence N` if the text appears in multiple rows.

## Step 8: Log in Obsidian

Append to `/Users/justin.flammia/Documents/Datadog/docs/log.md` using `mcp__obsidian__str_replace` or `mcp__obsidian__insert`:

```
## [YYYY-MM-DD] update | UEBA weekly project update
Pages updated: [[UEBA]]
```

Use today's date (not the Friday date) for the log entry.

---

## Reference: Jira epics by workstream

Pull recent comments from any epic that corresponds to a workstream detected as active in Step 4.

| Workstream | Epic | Status |
|---|---|---|
| Entity Resolution (ERS) | [SEC-30573](https://datadoghq.atlassian.net/browse/SEC-30573) | Active (PoC) |
| Entity Ingestion | (no dedicated epic; track via Obsidian notes and `siementity` milestone notes) | Active |
| Entity Context | (no epic yet) | Not started |
| Entity Extraction | (no epic yet) | Not started |

Update this table when epics are created or workstream status changes. The "Status" column is a hint for Step 4, not a substitute for reading the notes.

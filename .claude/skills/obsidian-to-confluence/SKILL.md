---
name: obsidian-to-confluence
description: Use when publishing an Obsidian vault document to Confluence, exporting a markdown note to Confluence, or converting an Obsidian .md file into a Confluence page. Triggers on phrases like "publish to Confluence", "export to Confluence", "create a Confluence page from", "push this doc to Confluence", or any request to take an Obsidian note and make it available in Confluence. Also triggers when someone says a document is "locked" and should be moved to Confluence, or when they want teammates without Obsidian access to read a document.
---

# Obsidian to Confluence Publisher

This skill publishes an Obsidian markdown document to Confluence as a properly formatted page using the **Confluence v2 REST API** and **Atlassian Document Format (ADF)**, which is the native JSON format used by Confluence Cloud. It uses a bundled Python converter rather than the markdown import endpoint, which does not reliably preserve formatting.

Scripts bundled at `${CLAUDE_PLUGIN_ROOT}/scripts/`:
- `md_to_adf.py` - Obsidian markdown to ADF JSON converter
- `review_table_adf.py` - Review status table builder/extractor (ADF format)

## Prerequisites

- Atlassian API token stored in macOS Keychain under service name `confluence-api-token`
- Git configured with Datadog email (`git config user.email`)
- Python 3 available

## Conversion coverage

The converter handles the following Obsidian markdown elements:

| Element | Conversion |
|---|---|
| YAML frontmatter | Stripped |
| `# Headings` (H1-H6) | ADF `heading` nodes |
| Paragraphs | ADF `paragraph` nodes |
| `**bold**` | `strong` mark |
| `*italic*` / `_italic_` | `em` mark |
| `~~strikethrough~~` | `strike` mark |
| `` `inline code` `` | `code` mark |
| `==highlight==` | `strong` mark (bold; ADF has no highlight) |
| ` ```lang ... ``` ` code blocks | ADF `codeBlock` with language |
| `[text](url)` links | ADF `link` mark |
| `[[WikiLink]]` | Plain text (page name), unless it matches a key in `mention_map`, in which case it becomes an ADF mention (Confluence user tag) |
| `[[WikiLink\|Display]]` | Plain text (display text), or mention if the page name matches `mention_map` |
| Plain `First Last` in prose | ADF mention when the full name matches a `people/` profile in `people_roster`; skipped inside code, inline code and links |
| `[[#Heading]]` anchor links | ADF `link` mark pointing to `#heading-slug` |
| `- item` / `* item` bullet lists | ADF `bulletList` with `listItem` |
| `1. item` ordered lists | ADF `orderedList` with `listItem` |
| Nested lists (indented) | Nested ADF list nodes |
| `- [ ]` / `- [x]` task checkboxes | Plain bullet list items (no checkbox) |
| `\| col \| col \|` tables | ADF `table`, `tableRow`, `tableHeader`, `tableCell` |
| `---` horizontal rules | ADF `rule` node |
| `> regular blockquote` | ADF `blockquote` node |
| `> [!NOTE]` callouts | ADF `panel` (info type) |
| `> [!WARNING]` callouts | ADF `panel` (warning type) |
| `> [!TIP]` / `> [!SUCCESS]` | ADF `panel` (tip type) |
| `> [!DANGER]` / `> [!ERROR]` | ADF `panel` (error type) |
| `> [!QUESTION]` / `> [!EXAMPLE]` | ADF `panel` (note type) |
| `![[image.png]]` embedded images | ADF `mediaSingle` + `media` (after upload) |
| `![alt](path)` standard images | ADF `mediaSingle` + `media` (after upload) |
| Bare Figma URL on its own line | ADF `embedCard` (Confluence renders an interactive iframe of the FigJam board, Figma file, etc.) |
| `:date:YYYY-MM-DD:` inline | ADF `date` node (Confluence renders a styled date pill) |
| Bare `YYYY-MM-DD` as the sole content of a table cell | ADF `date` node (auto-detection so metadata tables get rich date rendering without explicit markup) |
| `:status:LABEL:` inline | ADF `status` node, green (the standard pill used for `NEW` badges on index pages) |
| `:status:LABEL:COLOR:` inline | ADF `status` node with explicit color. Valid colors: `neutral`, `purple`, `blue`, `red`, `yellow`, `green` |
| `%%comment%%` inline | Stripped from body; posted as Confluence inline comments |
| `%%\nblock comment\n%%` | Stripped from body; posted as Confluence inline comments |

## Step 1: Prepare the document

Review the Obsidian file before converting:

**Requires manual handling:**
- `[[WikiLink]]` references to other Obsidian notes. These are stripped to plain text by the converter. Reword the surrounding sentence before publishing if the link context matters.
- Dataview queries (` ```dataview ``` ` blocks) - these are code blocks that won't execute; remove or replace with static text.
- Any content that only makes sense in Obsidian (backlinks, graph view references).

**Handled automatically:**
- Everything in the coverage table above.

## Step 1a: Resolve person mentions

Scan the document for `[[Person Name]]` wikilinks that match files in `people/`. Resolution uses three tiers, tried in order. **Always output the resolution report** regardless of outcome.

```python
import re, os

VAULT_DIR = "/Users/justin.flammia/Documents/Datadog"
wikilink_pattern = re.compile(r'\[\[([^\]|#][^\]|]*)(?:\|[^\]]*)?\]\]')

mention_map = {}       # name -> {account_id, display_name}
dynamic_resolved = []  # names resolved via live API call (not stored in vault)
failed = []            # names where resolution failed entirely

for m in wikilink_pattern.finditer(content):
    person_name = m.group(1).strip()
    person_file = os.path.join(VAULT_DIR, "people", f"{person_name}.md")
    if not os.path.exists(person_file):
        continue  # not a person wikilink; leave as plain text silently

    fm = read_frontmatter(person_file)  # parse YAML frontmatter into dict

    # Tier 1: stored atlassian_id in frontmatter (deterministic, no API call)
    atlassian_id = fm.get("atlassian_id")
    if atlassian_id:
        mention_map[person_name] = {
            "account_id": atlassian_id,
            "display_name": (fm.get("aliases") or [person_name])[0],
        }
        continue

    # Tier 2: dynamic lookup via email
    email = fm.get("email")
    if email:
        # Use MCP: mcp__plugin_atlassian_atlassian__lookupJiraAccountId(
        #   cloudId="datadoghq.atlassian.net", searchString=email)
        # Extract: result["data"]["users"]["users"][0]["accountId"] if total > 0
        account_id = lookup_atlassian_id_via_mcp(email)  # returns accountId string or None
        if account_id:
            mention_map[person_name] = {
                "account_id": account_id,
                "display_name": (fm.get("aliases") or [person_name])[0],
            }
            dynamic_resolved.append(person_name)
            continue

    # Tier 3: failed
    failed.append(person_name)
```

After building the map, **always print the resolution report**:

```
Person mention resolution:
  ✓ stored (3):  Shariq Syed, Martin Guyard, Jason Hunsberger
  ~ dynamic (1): Alessandro Siragusa (consider adding atlassian_id to their profile)
  ✗ failed (2):  Zhong Ren, Some Name (will appear as plain text in the published document)
```

If everything resolved from stored IDs, still print the report:
```
Person mention resolution:
  ✓ stored (3):  Shariq Syed, Martin Guyard, Jason Hunsberger
```

For dynamic resolutions, suggest storing the ID permanently:
- "Alessandro Siragusa resolved dynamically. To avoid the API call on future publishes, run `/add-person` to add `atlassian_id` to their profile."

For failures, the wikilink becomes plain text. The document still publishes; the failed names just won't be clickable Confluence mentions. No human gate is needed unless you want to verify.

### Full-name text mentions

`mention_map` tags only `[[wikilink]]` references. To also tag people who appear as plain "First Last" text in prose, build a `people_roster` from every `people/` profile that has an `atlassian_id` and pass it to the converter. The converter replaces exact whole-name matches with mention nodes, leaving code blocks, inline code and link text alone.

```python
people_roster = {}  # "First Last" -> {"account_id", "display_name"}
for fname in os.listdir(os.path.join(VAULT_DIR, "people")):
    if not fname.endswith(".md"):
        continue
    name = fname[:-3]
    fm = read_frontmatter(os.path.join(VAULT_DIR, "people", fname))
    aid = fm.get("atlassian_id")
    if aid:
        people_roster[name] = {"account_id": aid, "display_name": name}
```

Only profiles with a stored `atlassian_id` are included, so plain-text matches resolve with no API call. Names without an ID stay plain text. Every occurrence of a matched name is tagged.

Pass both to the converter in Step 6: `convert(content, image_map=image_map, mention_map=mention_map, people_roster=people_roster)`.

## Step 1b: Review Status table

Ask the user: "Would you like a Review Status table at the top of the Confluence page? Reviewers can sign off by adding their name, status and date directly in Confluence."

If yes, proceed with the review table. The `review_table_adf.py` script handles both building a fresh table and preserving an existing one on republish.

On first publish, generate the table using `build_review_table_adf(date_str)`.

On republish, always fetch the current page ADF first and call `extract_review_table_adf()` to recover whatever reviewers have filled in. Never regenerate a fresh table for a page that already has one.

```python
import sys, json
sys.path.insert(0, '${CLAUDE_PLUGIN_ROOT}/scripts')
from review_table_adf import build_review_table_adf, extract_review_table_adf

# On first publish:
review_nodes = build_review_table_adf('2026-04-09')  # returns a list of ADF nodes

# On republish: recover existing reviewer sign-offs from the current page body
current_adf = json.loads(current_page_body_value)   # body.value is a JSON string
review_nodes, _ = extract_review_table_adf(current_adf)
if not review_nodes:
    review_nodes = build_review_table_adf('2026-04-09')
```

The review section is separated from the document body by a `rule` node. `extract_review_table_adf` finds the first `rule` node (the sentinel) and returns everything before it.

`build_review_table_adf` already renders the metadata table natively: the Author cell is a Confluence user mention and the Published cell is a date pill (date node). Use its output as-is. Do not overwrite either cell with plain text when assembling the page, doing so is what strips the native rendering.

## Step 1c: Ask about the AI disclaimer

Ask: "Would you like the standard AI disclaimer added at the top of this page?" Default to no; only add it if Justin confirms.

If yes, insert this as the first line of the document body, immediately after the H1 heading (before any Review Status table):

```
🤖 *AI Disclaimer: This document was drafted with Claude based on [source material]. I have reviewed it for accuracy before publishing.*
```

Fill in `[source material]` from the document's actual origin (for example, "PoC code and notes kept locally", "meeting transcripts and Slack threads"). Keep the rest of the wording fixed. See `agents/policies/published-artifacts.md` for why this is exempt from the local-process-language ban on saying "Claude" in published content: it is a deliberate, opt-in disclosure, not a workflow-mechanics leak.

## Step 2: Scan for images

Run a dry pass to discover which images need uploading:

```python
import sys, json, subprocess
sys.path.insert(0, '${CLAUDE_PLUGIN_ROOT}/scripts')
from md_to_adf import convert

with open('path/to/document.md') as f:
    content = f.read()

# Pass 1: no image_map - discovers required images
result = convert(content)
print("Images needed:", result["images"])
# e.g. ["ers-system-context.png", "ers-component-detail.png"]
```

Images live in the vault's `attachments/` directory: `/Users/justin.flammia/Documents/Datadog/attachments/<filename>`.

## Step 3: Get credentials and target page info

```bash
EMAIL=$(git config user.email)
API_TOKEN=$(security find-generic-password -s "confluence-api-token" -w 2>/dev/null)
```

The target parent page ID is the number in the URL:
`https://datadoghq.atlassian.net/wiki/spaces/SPACE/pages/PAGE_ID/Title`

Get the `spaceId` (numeric) from the parent page - required for the v2 API:

```bash
curl -s -u "$EMAIL:$API_TOKEN" \
  "https://datadoghq.atlassian.net/wiki/api/v2/pages/PARENT_PAGE_ID" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print('spaceId:', d['spaceId'])"
```

## Step 4: Create the page (new pages only)

For new pages, create a skeleton first to get the page ID before uploading images. The `body.value` in the v2 API must be a **JSON string** (double-encoded), not a raw object.

```python
import json, subprocess, urllib.request, base64

EMAIL = subprocess.run(['git','config','user.email'], capture_output=True, text=True).stdout.strip()
TOKEN = subprocess.run(['security','find-generic-password','-s','confluence-api-token','-w'],
                       capture_output=True, text=True).stdout.strip()
CREDS = base64.b64encode(f'{EMAIL}:{TOKEN}'.encode()).decode()
BASE_URL = "https://datadoghq.atlassian.net"

def api(method, path, payload=None):
    req = urllib.request.Request(
        BASE_URL + path,
        data=json.dumps(payload).encode() if payload else None,
        headers={'Authorization': f'Basic {CREDS}', 'Content-Type': 'application/json'},
        method=method,
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

# Create skeleton page (body can be minimal - we update it after images are uploaded)
skeleton_adf = {"type": "doc", "version": 1, "content": [
    {"type": "paragraph", "content": [{"type": "text", "text": "Publishing..."}]}
]}

page = api('POST', '/wiki/api/v2/pages', {
    "spaceId": "SPACE_ID",         # numeric space ID
    "parentId": "PARENT_PAGE_ID",  # numeric parent page ID
    "title": "Your Page Title",
    "status": "current",
    "body": {
        "representation": "atlas_doc_format",
        "value": json.dumps(skeleton_adf),
    }
})
PAGE_ID = page["id"]
print(f"Created page: {BASE_URL}/wiki/pages/{PAGE_ID}")
```

## Step 5: Upload images

Use the v1 attachment API (the v2 API has no attachment upload endpoint). Upload each image found in Step 2.

```python
import mimetypes, urllib.request

VAULT_ATTACHMENTS = "/Users/justin.flammia/Documents/Datadog/attachments"
image_map = {}  # filename -> {"file_id": str, "collection": str}

for filename in result["images"]:
    path = f"{VAULT_ATTACHMENTS}/{filename}"
    mime = mimetypes.guess_type(path)[0] or "application/octet-stream"

    # Multipart form upload
    boundary = "ConfluenceUploadBoundary"
    with open(path, 'rb') as f:
        file_data = f.read()

    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
        f"Content-Type: {mime}\r\n\r\n"
    ).encode() + file_data + f"\r\n--{boundary}--\r\n".encode()

    req = urllib.request.Request(
        f"{BASE_URL}/wiki/rest/api/content/{PAGE_ID}/child/attachment",
        data=body,
        headers={
            'Authorization': f'Basic {CREDS}',
            'Content-Type': f'multipart/form-data; boundary={boundary}',
            'X-Atlassian-Token': 'nocheck',
        },
        method='POST',
    )
    with urllib.request.urlopen(req) as r:
        resp = json.loads(r.read())

    att = resp['results'][0]
    # extensions.fileId is the UUID for ADF media nodes
    file_id = att.get('extensions', {}).get('fileId') or att['id']
    image_map[filename] = {
        "file_id": file_id,
        "collection": f"contentId-{PAGE_ID}",
    }
    print(f"Uploaded {filename}: fileId={file_id}")
```

## Step 6: Convert to ADF and assemble

Run the converter again with the image map, then assemble the full page ADF including any review table.

```python
sys.path.insert(0, '${CLAUDE_PLUGIN_ROOT}/scripts')
from md_to_adf import convert
from review_table_adf import build_review_table_adf, extract_review_table_adf

# Pass 2: full conversion with images resolved
result = convert(content, image_map=image_map, mention_map=mention_map, people_roster=people_roster)
doc_nodes = result["adf"]["content"]

# Prepend review table if requested
if include_review_table:
    all_nodes = review_nodes + doc_nodes
else:
    all_nodes = doc_nodes

final_adf = {"type": "doc", "version": 1, "content": all_nodes}
```

## Step 7: Publish the page

### New page (update the skeleton created in Step 4)

New pages have no existing inline comments, so no annotation preservation is needed. Just PUT the converted content.

```python
current = api('GET', f'/wiki/api/v2/pages/{PAGE_ID}')
version_number = current['version']['number']

api('PUT', f'/wiki/api/v2/pages/{PAGE_ID}', {
    "id": PAGE_ID,
    "status": "current",
    "title": "Your Page Title",
    "version": {"number": version_number + 1, "message": ""},
    "body": {
        "representation": "atlas_doc_format",
        "value": json.dumps(final_adf),
    }
})
print(f"Published: {BASE_URL}/wiki/pages/{PAGE_ID}")
```

### Existing page (republish with full preservation)

This is the full republish flow. It preserves three things:
1. Inline comment anchors (annotation marks) - so reviewer comments stay visible
2. Review table entries - so sign-offs aren't lost
3. Page-level comments - these are a separate API object and survive any PUT automatically

**How inline comment preservation works:** Confluence stores inline comments as annotation marks embedded in the ADF. Each mark has a UUID that links it to the comment thread. When you GET the current page ADF, those marks are in the response. Re-injecting them into the new ADF (at the same or closest matching text) keeps the comment threads alive after the PUT.

```python
import sys, json
sys.path.insert(0, '${CLAUDE_PLUGIN_ROOT}/scripts')
from md_to_adf import convert
from review_table_adf import build_review_table_adf, extract_review_table_adf
from annotate_adf import extract_annotations, inject_annotations

# 1. Fetch current page: version + full ADF body (needed for both annotation
#    preservation and review table recovery)
current = api('GET', f'/wiki/api/v2/pages/{PAGE_ID}?body-format=atlas_doc_format')
version_number = current['version']['number']
existing_adf = json.loads(current['body']['atlas_doc_format']['value'])

# 2. Extract annotation marks from existing ADF.
#    These are the UUIDs that link to reviewer inline comments.
annotations = extract_annotations(existing_adf)

# 3. Recover reviewer sign-offs from the review table.
review_nodes, _ = extract_review_table_adf(existing_adf)
if not review_nodes:
    review_nodes = build_review_table_adf(today)   # fresh table if none exists

# 4. Convert updated Obsidian content to ADF.
result = convert(content, image_map=image_map, mention_map=mention_map, people_roster=people_roster)
doc_nodes = result["adf"]["content"]

# 5. Assemble: review table + document body.
all_nodes = review_nodes + doc_nodes
new_adf = {"type": "doc", "version": 1, "content": all_nodes}

# 6. Re-inject annotation marks into the new ADF.
#    inject_annotations walks the new ADF and places each annotation mark
#    at the best matching text position (exact match -> LCS -> word overlap ->
#    first substantial paragraph as last resort for visibility).
annotated_adf, unanchored = inject_annotations(new_adf, annotations)

if unanchored:
    # These comments had anchor text that no longer exists anywhere in the new
    # content. They become "dangling" in Confluence (not visible, not deleted).
    # This is expected when the text a comment referenced was intentionally
    # removed. The comment is still retrievable via API if needed.
    print(f"Note: {len(unanchored)} annotation(s) could not be re-anchored "
          f"(anchor text was removed from document): {unanchored}")

# 7. PUT the new page body.
api('PUT', f'/wiki/api/v2/pages/{PAGE_ID}', {
    "id": PAGE_ID,
    "status": "current",
    "title": "Your Page Title",
    "version": {"number": version_number + 1, "message": ""},
    "body": {
        "representation": "atlas_doc_format",
        "value": json.dumps(annotated_adf),
    }
})
print(f"Updated: {BASE_URL}/wiki/pages/{PAGE_ID}")
if annotations:
    print(f"  Preserved {len(annotations) - len(unanchored)}/{len(annotations)} "
          f"inline comment anchor(s)")
```

## Step 8: Post inline comments (if any)

If the document contained `%%comment%%` blocks, post them as Confluence inline comments. Each comment in `result["comments"]` has an `anchor` (the text to attach the comment to) and `body` (the comment text).

```python
import json

def post_inline_comment(page_id, anchor_text, comment_body):
    """Post a comment attached to anchor_text on the given page."""
    comment_adf = json.dumps({
        "type": "doc", "version": 1,
        "content": [{"type": "paragraph", "content": [{"type": "text", "text": comment_body}]}]
    })
    payload = {
        "pageId": page_id,
        "body": {"representation": "atlas_doc_format", "value": comment_adf},
    }
    # Only add textSelection if we have a non-empty anchor
    if anchor_text:
        payload["inlineCommentProperties"] = {
            "textSelection": anchor_text,
            "textSelectionMatchCount": 1,
            "textSelectionMatchIndex": 0,
        }
    try:
        api('POST', f'/wiki/api/v2/pages/{page_id}/inline-comments', payload)
        print(f"Posted inline comment on: {anchor_text!r:.50s}")
    except Exception as e:
        print(f"Warning: could not post inline comment: {e}")

for c in result["comments"]:
    post_inline_comment(PAGE_ID, c["anchor"], c["body"])
```

## Step 9: Add the post-publish callout to the Obsidian note

After a successful publish, add this block to the Obsidian document immediately after the H1 heading to lock the document and direct future editors to Confluence.

```markdown
> [!WARNING] Published to Confluence (edit there)
> This document was published to Confluence on YYYY-MM-DD. All future edits should happen in Confluence, not here.
> **Confluence page:** [Page Title](https://datadoghq.atlassian.net/wiki/spaces/.../pages/PAGE_ID/Title)
```

## Step 10: Add discovery links (new pages only)

A net-new page has no inbound links yet, so nobody browsing from the parent or an index page will find it. Before finishing, check:

1. **The parent page's Related/related-references section**, if it has one. Fetch its current ADF, find the relevant list and offer to insert a new list item linking to the new page, matching the existing items' format exactly (same link style, same trailing description pattern).
2. **A series index page**, if the parent page links up to one (for example, an "Engineering Documents" or "Related" list on a top-level project page). Same treatment: match the existing entries' format, including any status-pill conventions like `NEW` badges.

Always show the exact before/after text for each proposed insertion and get explicit approval before applying, per the standard Confluence edit process (`confluence-write` skill, surgical ADF edits, never a full-page rewrite). Skip this step for republishes of an existing page since inbound links already exist.

---

## Converter design notes

These are non-obvious decisions that burned time to discover.

**ADF body.value is a JSON string.** The v2 API requires `body.value` to be a string containing JSON, not a raw JSON object. Always pass `json.dumps(adf_dict)` not `adf_dict` directly.

**Images use v1 for upload, v2 for page.** The v2 REST API has no attachment upload endpoint. Use `/wiki/rest/api/content/{pageId}/child/attachment` (v1) with the `X-Atlassian-Token: nocheck` header. The upload returns `extensions.fileId` (a UUID) which goes in the ADF `media` node's `id` field, and `collection` is `contentId-{PAGE_ID}`.

**ADF media.id is not the attachment REST id.** The `att12345` ID from the v1 response is NOT what goes in `media.attrs.id`. Use `extensions.fileId` (UUID format). If `fileId` is absent, fall back to the raw `id` field.

**`spaceId` is numeric, not the space key.** The v2 pages endpoint requires `spaceId` as a number (e.g., `163971073`), not the string key (e.g., `"CSiem"`). Fetch it from the parent page's v2 response.

**`parentId` replaces `ancestors`.** The v1 API used `"ancestors": [{"id": "..."}]`. The v2 API uses a flat `"parentId": "PAGE_ID"` string.

**Review table sentinel is the first `rule` node.** `extract_review_table_adf` finds the first `rule` (horizontal divider) node and treats everything before it as the review section. The convention is: always end the review section with a `rule` node. `build_review_table_adf` already does this.

**Wikilinks become plain text or mentions.** `[[Page Name]]` becomes the literal text "Page Name" by default. If `mention_map` is provided and contains `Page Name` as a key, it becomes an ADF `mention` node (Confluence user tag) instead. `[[Page Name|Display]]` follows the same logic but falls back to "Display" for plain text. Note that `mention` nodes are peer nodes in a paragraph, not text nodes with marks, so `_apply_mark` does not affect them.

**Smart-link embeds from bare URLs.** Confluence does not auto-detect URLs posted as paragraph text via the ADF v2 API. To get an interactive embed (live FigJam, Figma file, etc.), the ADF must contain an `embedCard` node. The converter checks each flushed paragraph against `EMBED_URL_PATTERN`. If the entire paragraph is a single URL matching that pattern, the converter emits an `embedCard` node instead of a `paragraph`. Today the pattern matches Figma URLs only. Adding providers (YouTube, Loom, etc.) is a one-line change to the regex. A URL that does not match the pattern still becomes a regular linked paragraph.

**Date pills from ISO dates.** Confluence renders `date` ADF nodes as styled date pills that respect the viewer's locale. Plain text dates do not. The converter has two entry points. Explicit `:date:YYYY-MM-DD:` inline markup always becomes a date node. Bare `YYYY-MM-DD` strings are auto-promoted to date nodes only when they fill an entire table cell (a post-processing pass walks every `tableCell` and `tableHeader` after conversion). Auto-promotion is intentionally scoped to table cells. Metadata tables at the top of design docs (`Author`, `Published`, `Date`) get rich rendering without needing source-side markup, while ISO dates in narrative prose stay as text where converting them would be surprising.

**Noon UTC for date node timestamps.** ADF date timestamps are UNIX milliseconds. The converter uses noon UTC for the chosen calendar date rather than midnight. Confluence renders the timestamp in the viewer's local time zone. Midnight UTC of 2026-05-13 renders as 2026-05-12 for any viewer in the Americas, which is the wrong calendar date. Noon UTC keeps the rendered day stable for every viewer between roughly UTC-11 and UTC+11.

**Status pills via `:status:` markup.** Confluence's `Status` macro produces a small colored pill. In ADF, this is the inline `status` node with `text`, `color` and `localId` attributes. The converter exposes two markdown forms: `:status:LABEL:` defaults to green, and `:status:LABEL:COLOR:` lets the author pick from `neutral`, `purple`, `blue`, `red`, `yellow` or `green`. Each emitted node gets a fresh UUID `localId` so Confluence treats it as a stable element. Use these pills on index pages, status tables, and anywhere the bare label text would lose meaning without visual differentiation.

**The NEW pill convention on index pages.** Engineering index pages (UEBA, Entity Resolution) mark recently published documents with a green `NEW` status pill so readers can find what changed at a glance. The convention is: NEW pills are 2-week badges. When an index page is updated, audit existing NEW pills and remove any whose linked document was created more than 14 days ago. The page's `createdAt` timestamp from `GET /wiki/api/v2/pages/{id}` is the authoritative source. Stripping a pill is a surgical ADF edit: remove the `status` node from its parent paragraph (and the surrounding whitespace text if it was emitted alongside the pill). This rule is index-page maintenance, not part of the converter, since the converter has no cross-page context.

**Obsidian callout type mapping** (all lowercase matching):
- `note`, `info`, `todo` -> `info` panel
- `tip`, `hint`, `important`, `success`, `check`, `done` -> `tip` panel
- `warning`, `caution`, `attention` -> `warning` panel
- `danger`, `error`, `bug`, `failure`, `fail`, `missing` -> `error` panel
- `question`, `help`, `faq`, `example`, `quote`, `abstract`, `summary`, `tldr` -> `note` panel

**Inline comments from `%%...%%`.** The converter strips Obsidian comments from the visible body and returns them in `result["comments"]` as `{"anchor": str, "body": str}` pairs. The anchor is the 80 chars of visible text preceding the comment, stripped of markdown syntax. Post each via `POST /wiki/api/v2/pages/{id}/inline-comments` after the page exists.

**Annotation marks are in the ADF GET response.** When you GET a page with `?body-format=atlas_doc_format`, annotation marks appear inline in the text nodes. Each annotation mark has an `id` (UUID) that is the same value as the comment's `properties.inlineMarkerRef`. Annotation marks look like:
```json
{"type": "annotation", "attrs": {"id": "uuid", "annotationType": "inlineComment"}}
```
They appear as an additional entry in the `marks` array of a text node alongside `strong`, `em`, etc.

**Re-injecting annotation marks on republish.** `annotate_adf.py` handles this. Call `extract_annotations(existing_adf)` to get all marks from the current page, then `inject_annotations(new_adf, annotations)` to place them in the new content. The injection tries exact text match first, then longest-common-substring, then word overlap, then falls back to the first substantial paragraph. If PUT includes the annotation marks at matching UUIDs, Confluence keeps the comment threads alive. If a mark cannot be placed (its anchor text was removed from the document), the comment becomes `dangling` - not visible but not deleted.

**Dangling vs. resolved.** The `resolutionStatus` field on inline comments has four values: `open`, `reopened`, `resolved`, and `dangling`. Dangling comments cannot be updated via API. They persist in the system but are hidden from readers. When republishing changes that intentionally removed text a comment was on, this is the expected outcome.

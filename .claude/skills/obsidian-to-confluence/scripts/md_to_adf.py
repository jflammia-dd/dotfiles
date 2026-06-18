#!/usr/bin/env python3
"""
Obsidian Markdown -> Atlassian Document Format (ADF) converter.

Usage:
    python3 md_to_adf.py path/to/document.md

Output (stdout): JSON with three keys:
  {
    "adf":      {...},   # ADF document (pass as body.value in Confluence v2 API)
    "images":   [...],   # filenames of embedded images that need uploading
    "comments": [...]    # inline comment data to post after page creation
  }

Pass image_map to a second invocation once you have uploaded attachments and
have their file IDs:
    result = convert(content, image_map={"image.png": {"file_id": "uuid", "collection": "contentId-12345"}})

Inline comments come from Obsidian %%...%% syntax. Post each one after publish:
    POST /wiki/api/v2/pages/{pageId}/inline-comments
    {
      "pageId": "...",
      "inlineCommentProperties": {"textSelection": comment["anchor"], ...},
      "body": {"representation": "atlas_doc_format", "value": "..."}
    }
"""

import re
import sys
import json
import uuid

# ---------------------------------------------------------------------------
# Callout type -> Confluence panel type
# ---------------------------------------------------------------------------

CALLOUT_MAP = {
    "note": "info", "info": "info", "todo": "info",
    "tip": "tip", "hint": "tip", "important": "tip",
    "success": "tip", "check": "tip", "done": "tip",
    "warning": "warning", "caution": "warning", "attention": "warning",
    "danger": "error", "error": "error", "bug": "error",
    "failure": "error", "fail": "error", "missing": "error",
    "question": "note", "help": "note", "faq": "note",
    "example": "note", "quote": "note", "abstract": "note",
    "summary": "note", "tldr": "note",
}

# ---------------------------------------------------------------------------
# Smart-link embed URLs
# ---------------------------------------------------------------------------
#
# When a single URL from one of these providers appears alone on its own line,
# the converter emits an ADF embedCard node instead of a plain paragraph.
# Confluence renders embedCards as interactive iframes (live FigJam boards,
# YouTube players, etc.) rather than as text links.
#
# Add providers conservatively. The auto-embed behavior is opinionated and may
# surprise readers if a passing URL becomes a full-width interactive embed.
EMBED_URL_PATTERN = re.compile(
    r"^https?://(?:www\.)?(?:figma\.com)/\S+$"
)

# ---------------------------------------------------------------------------
# ADF node constructors
# ---------------------------------------------------------------------------

def _doc(content):
    return {"type": "doc", "version": 1, "content": content}

def _paragraph(inline_content):
    if not inline_content:
        inline_content = [_text("")]
    return {"type": "paragraph", "content": inline_content}

def _heading(level, inline_content):
    return {"type": "heading", "attrs": {"level": level}, "content": inline_content}

def _text(t, marks=None):
    node = {"type": "text", "text": t}
    if marks:
        node["marks"] = marks
    return node

def _code_block(language, text_content):
    node = {"type": "codeBlock", "attrs": {}}
    if language:
        node["attrs"]["language"] = language
    node["content"] = [{"type": "text", "text": text_content}]
    return node

def _rule():
    return {"type": "rule"}

def _bullet_list(items):
    return {"type": "bulletList", "content": items}

def _ordered_list(items):
    return {"type": "orderedList", "content": items}

def _list_item(content):
    return {"type": "listItem", "content": content}

def _table(rows):
    return {"type": "table", "content": rows}

def _table_row(cells):
    return {"type": "tableRow", "content": cells}

def _table_header(inline_content):
    return {"type": "tableHeader", "attrs": {}, "content": [_paragraph(inline_content)]}

def _table_cell(inline_content):
    return {"type": "tableCell", "attrs": {}, "content": [_paragraph(inline_content)]}

def _panel(panel_type, content):
    return {"type": "panel", "attrs": {"panelType": panel_type}, "content": content}

def _blockquote(content):
    return {"type": "blockquote", "content": content}

def _embed_card(url):
    """ADF embedCard node for smart-link providers (Figma, etc.).

    When a single URL from a known smart-link provider appears alone on a line
    in markdown, the converter emits this node instead of a paragraph. Confluence
    renders it as an interactive iframe embed rather than a plain text link.
    """
    return {
        "type": "embedCard",
        "attrs": {"url": url, "layout": "center", "width": 100},
    }


def _iso_date_to_timestamp_ms(date_str):
    """Convert an ISO date YYYY-MM-DD to a Unix millisecond timestamp at noon
    UTC. Noon UTC keeps the rendered calendar date stable across viewer
    timezones; midnight UTC would render as the previous day for viewers in
    the Americas.
    """
    import datetime as _dt
    y, m, d = (int(x) for x in date_str.split("-"))
    return str(int(_dt.datetime(y, m, d, 12, 0, 0, tzinfo=_dt.timezone.utc).timestamp() * 1000))


def _date(date_str):
    """ADF date node. Confluence renders this as a styled date pill."""
    return {"type": "date", "attrs": {"timestamp": _iso_date_to_timestamp_ms(date_str)}}


_STATUS_COLORS = {"neutral", "purple", "blue", "red", "yellow", "green"}


def _status(text, color="green"):
    """ADF status node. Confluence renders this as the colored pill produced
    by the / Status macro in the editor. Valid colors: neutral, purple, blue,
    red, yellow, green. Defaults to green, which is the standard color for the
    NEW convention used on index pages.
    """
    if color not in _STATUS_COLORS:
        color = "green"
    return {
        "type": "status",
        "attrs": {
            "text": text.strip(),
            "color": color,
            "localId": str(uuid.uuid4()),
        },
    }


def _media_single(file_id, collection):
    return {
        "type": "mediaSingle",
        "attrs": {"layout": "center"},
        "content": [{
            "type": "media",
            "attrs": {"id": file_id, "type": "file", "collection": collection},
        }],
    }

def _mention(account_id, display_name):
    """ADF mention node for a tagged Confluence user."""
    return {
        "type": "mention",
        "attrs": {
            "id": account_id,
            "text": f"@{display_name}",
            "accessLevel": "",
        }
    }

# ---------------------------------------------------------------------------
# Inline parser
# ---------------------------------------------------------------------------

def _apply_mark(nodes, mark):
    """Return copies of text nodes with the given mark appended."""
    result = []
    for node in nodes:
        if node.get("type") == "text":
            n = dict(node)
            n["marks"] = list(node.get("marks", [])) + [mark]
            result.append(n)
        else:
            result.append(node)
    return result

# Patterns are tried in order; the earliest (leftmost) match wins each round.
# More-specific patterns must appear before more-general ones.
_INLINE_PATTERNS = [
    ("comment",          re.compile(r"%%(.+?)%%", re.DOTALL)),
    ("code",             re.compile(r"`([^`\n]+)`")),
    ("bold_italic",      re.compile(r"\*\*\*(.+?)\*\*\*", re.DOTALL)),
    ("bold",             re.compile(r"\*\*(.+?)\*\*", re.DOTALL)),
    ("italic_star",      re.compile(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", re.DOTALL)),
    ("italic_under",     re.compile(r"(?<!_)_(?!_)(.+?)(?<!_)_(?!_)", re.DOTALL)),
    ("strike",           re.compile(r"~~(.+?)~~", re.DOTALL)),
    ("highlight",        re.compile(r"==(.+?)==", re.DOTALL)),
    # Explicit date marker: :date:YYYY-MM-DD: -> ADF date pill
    ("date",             re.compile(r":date:(\d{4}-\d{2}-\d{2}):")),
    # Status pill: :status:LABEL: (green) or :status:LABEL:COLOR:
    ("status_color",     re.compile(r":status:([^:]+):(neutral|purple|blue|red|yellow|green):")),
    ("status",           re.compile(r":status:([^:]+):")),
    # Wikilinks: most specific first
    ("wikilink_disp",    re.compile(r"\[\[([^\]|#][^\]|]*)\|([^\]]+)\]\]")),
    ("wikilink_anc_disp",re.compile(r"\[\[#([^\]|]+)\|([^\]]+)\]\]")),
    ("wikilink_anc",     re.compile(r"\[\[#([^\]]+)\]\]")),
    ("wikilink",         re.compile(r"\[\[([^\]#][^\]]*)\]\]")),
    ("link",             re.compile(r"\[([^\]]+)\]\(([^)]+)\)")),
]

# Bare ISO date that fills an entire table cell. Used to auto-convert
# metadata-table dates (Author / Published / Date columns) without requiring
# explicit :date:...: markup in the source.
_BARE_ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _heading_slug(text):
    """Convert heading text to an anchor slug (matches Confluence's auto-generated anchors)."""
    return re.sub(r"[^a-z0-9_\-]+", "-", text.lower()).strip("-")


def parse_inline(text_content, comment_collector=None, mention_map=None):
    """
    Parse inline Obsidian markdown and return a list of ADF inline nodes.

    Handles: bold, italic, bold+italic, strikethrough, inline code, highlight
    (->bold), wikilinks (->plain text, anchor link, or Confluence mention), standard
    links, and %%comments%% (stripped, optionally collected for inline comment posting).

    mention_map: optional dict mapping person name -> {"account_id": str, "display_name": str}.
                 When a [[Person Name]] wikilink matches a key, emits an ADF mention node
                 instead of plain text.
    """
    nodes = []
    pos = 0

    while pos < len(text_content):
        earliest_start = len(text_content)
        earliest_match = None
        earliest_type = None

        for pat_type, pattern in _INLINE_PATTERNS:
            m = pattern.search(text_content, pos)
            if m and m.start() < earliest_start:
                earliest_start = m.start()
                earliest_match = m
                earliest_type = pat_type

        # Plain text before the match
        if earliest_start > pos:
            nodes.append(_text(text_content[pos:earliest_start]))

        if earliest_match is None:
            break

        pos = earliest_match.end()

        if earliest_type == "comment":
            body = earliest_match.group(1).strip()
            if comment_collector is not None and body:
                # Anchor: strip markdown from the 80 chars of visible text before the comment.
                preceding = text_content[:earliest_match.start()]
                anchor = re.sub(r"\*\*?|~~|==|`|_|\[\[.*?\]\]", "", preceding).strip()[-80:]
                comment_collector.append({"anchor": anchor.strip(), "body": body})
            # Comment is invisible; nothing added to nodes.

        elif earliest_type == "code":
            nodes.append(_text(earliest_match.group(1), marks=[{"type": "code"}]))

        elif earliest_type == "bold_italic":
            inner = parse_inline(earliest_match.group(1), comment_collector, mention_map)
            inner = _apply_mark(inner, {"type": "strong"})
            inner = _apply_mark(inner, {"type": "em"})
            nodes.extend(inner)

        elif earliest_type == "bold":
            inner = parse_inline(earliest_match.group(1), comment_collector, mention_map)
            nodes.extend(_apply_mark(inner, {"type": "strong"}))

        elif earliest_type in ("italic_star", "italic_under"):
            inner = parse_inline(earliest_match.group(1), comment_collector, mention_map)
            nodes.extend(_apply_mark(inner, {"type": "em"}))

        elif earliest_type == "strike":
            inner = parse_inline(earliest_match.group(1), comment_collector, mention_map)
            nodes.extend(_apply_mark(inner, {"type": "strike"}))

        elif earliest_type == "highlight":
            # Obsidian highlights -> bold (Confluence has no highlight mark in ADF)
            inner = parse_inline(earliest_match.group(1), comment_collector, mention_map)
            nodes.extend(_apply_mark(inner, {"type": "strong"}))

        elif earliest_type == "date":
            # :date:YYYY-MM-DD: -> ADF date node (Confluence date pill)
            nodes.append(_date(earliest_match.group(1)))

        elif earliest_type == "status_color":
            # :status:LABEL:COLOR: -> ADF status node with explicit color
            nodes.append(_status(earliest_match.group(1), earliest_match.group(2)))

        elif earliest_type == "status":
            # :status:LABEL: -> ADF status node (defaults to green)
            nodes.append(_status(earliest_match.group(1)))

        elif earliest_type == "wikilink_disp":
            # [[Page Name|Display Text]] -> mention if person known, else display text
            page_name = earliest_match.group(1)
            display = earliest_match.group(2)
            if mention_map and page_name in mention_map:
                info = mention_map[page_name]
                nodes.append(_mention(info["account_id"], info.get("display_name", page_name)))
            else:
                nodes.append(_text(display))

        elif earliest_type == "wikilink_anc_disp":
            # [[#Heading|Display Text]] -> link to anchor
            slug = _heading_slug(earliest_match.group(1))
            nodes.append(_text(
                earliest_match.group(2),
                marks=[{"type": "link", "attrs": {"href": f"#{slug}"}}],
            ))

        elif earliest_type == "wikilink_anc":
            # [[#Heading]] -> link to anchor
            anchor_text = earliest_match.group(1)
            slug = _heading_slug(anchor_text)
            nodes.append(_text(
                anchor_text,
                marks=[{"type": "link", "attrs": {"href": f"#{slug}"}}],
            ))

        elif earliest_type == "wikilink":
            # [[Page Name]] -> mention if person known, else plain text
            page_name = earliest_match.group(1)
            if mention_map and page_name in mention_map:
                info = mention_map[page_name]
                nodes.append(_mention(info["account_id"], info.get("display_name", page_name)))
            else:
                nodes.append(_text(page_name))

        elif earliest_type == "link":
            label = earliest_match.group(1)
            href = earliest_match.group(2)
            # Only create link marks for real URLs and anchor links.
            # Local .md file paths would produce broken links in Confluence.
            if href.startswith(("#", "http://", "https://", "ftp://")):
                nodes.append(_text(label, marks=[{"type": "link", "attrs": {"href": href}}]))
            else:
                nodes.append(_text(label))

    return nodes or [_text("")]


# ---------------------------------------------------------------------------
# Block-level helpers
# ---------------------------------------------------------------------------

def _is_table_row(line):
    s = line.strip()
    return s.startswith("|") and s.endswith("|") and len(s) > 2


def _is_separator_row(line):
    s = line.strip()
    if not (s.startswith("|") and s.endswith("|")):
        return False
    cells = s[1:-1].split("|")
    return all(re.match(r"^\s*:?-+:?\s*$", c) for c in cells)


def _get_list_kind(line):
    if re.match(r"^\s*[-*]\s+", line):
        return "ul"
    if re.match(r"^\s*\d+\.\s+", line):
        return "ol"
    return None


def _get_indent(line):
    return len(line) - len(line.lstrip(" "))


# ---------------------------------------------------------------------------
# Table parser
# ---------------------------------------------------------------------------

def _parse_table(lines, start_i, mention_map=None):
    """Parse a GFM table. Returns (table_node, next_i)."""
    i = start_i
    raw_rows = []

    while i < len(lines) and _is_table_row(lines[i]):
        raw_rows.append(lines[i].strip())
        i += 1

    header_rows = []
    data_rows = []
    found_sep = False

    for row in raw_rows:
        if _is_separator_row(row):
            found_sep = True
            continue
        cells = [c.strip() for c in row[1:-1].split("|")]
        if not found_sep:
            header_rows.append(cells)
        else:
            data_rows.append(cells)

    # No separator: treat first row as header
    if not found_sep and header_rows:
        data_rows = header_rows[1:]
        header_rows = [header_rows[0]]

    adf_rows = []
    for hr in header_rows:
        adf_rows.append(_table_row([_table_header(parse_inline(c, mention_map=mention_map)) for c in hr]))
    for dr in data_rows:
        adf_rows.append(_table_row([_table_cell(parse_inline(c, mention_map=mention_map)) for c in dr]))

    return _table(adf_rows), i


# ---------------------------------------------------------------------------
# List parser
# ---------------------------------------------------------------------------

def _parse_list(lines, start_i, comment_collector=None, mention_map=None):
    """
    Parse a potentially nested list starting at start_i.
    Returns (list_node, next_i).

    Supports:
    - Unordered lists (- or *)
    - Ordered lists (1.)
    - Task checkboxes (- [ ] / - [x] / - [~]) treated as plain list items
    - Nested lists via indentation (2 or 4 space indent)
    - Blank lines between same-level items (continue) vs. across levels (end)
    """
    kind = _get_list_kind(lines[start_i])
    if kind is None:  # pragma: no cover
        return None, start_i

    base_indent = _get_indent(lines[start_i])
    items = []
    i = start_i

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Blank line: look ahead to decide whether to continue
        if not stripped:
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1  # pragma: no cover
            if j >= len(lines):  # pragma: no cover
                i = j  # pragma: no cover
                break  # pragma: no cover
            next_indent = _get_indent(lines[j])
            next_kind = _get_list_kind(lines[j])
            # Continue if same level, same kind
            if next_kind == kind and next_indent == base_indent:
                i = j
                continue
            else:
                i = j
                break

        current_indent = _get_indent(line)

        if current_indent < base_indent:
            break

        if current_indent > base_indent:  # pragma: no cover
            # Nested content without a preceding item to attach to; skip
            i += 1  # pragma: no cover
            continue  # pragma: no cover

        # Same-level item
        item_kind = _get_list_kind(line)
        if item_kind != kind:
            break

        # Extract item text
        if kind == "ul":
            m = re.match(r"^\s*[-*]\s+(.*)", line)
        else:
            m = re.match(r"^\s*\d+\.\s+(.*)", line)
        if not m:  # pragma: no cover
            i += 1  # pragma: no cover
            continue  # pragma: no cover

        item_text = m.group(1)

        # Strip task checkbox (- [ ], - [x], - [~], etc.) -> plain list item
        task_m = re.match(r"^\[[ xX~\-]\]\s*(.*)", item_text)
        if task_m:
            item_text = task_m.group(1)

        item_content = [_paragraph(parse_inline(item_text, comment_collector, mention_map))]

        # Look ahead for continuation lines and nested lists
        j = i + 1
        while j < len(lines):
            next_line = lines[j]
            ns = next_line.strip()

            if not ns:
                # Blank line inside item: look further
                k = j + 1
                while k < len(lines) and not lines[k].strip():
                    k += 1
                if k >= len(lines):
                    j = k
                    break
                inner_indent = _get_indent(lines[k])
                if inner_indent > base_indent:
                    j = k
                    continue
                else:
                    break

            inner_indent = _get_indent(next_line)

            if inner_indent <= base_indent:
                break

            # Nested list
            if _get_list_kind(next_line):
                nested, j = _parse_list(lines, j, comment_collector, mention_map)
                if nested:
                    item_content.append(nested)
                continue

            # Continuation text (indented prose under a list item). Separate it
            # from the preceding line with a hard break so a standalone bold
            # header and its description render on their own lines rather than
            # running together.
            if item_content and item_content[0]["type"] == "paragraph":
                extra = parse_inline(ns, comment_collector, mention_map)
                para = item_content[0]["content"]
                if para and extra:
                    para.append({"type": "hardBreak"})
                para.extend(extra)
            j += 1

        items.append(_list_item(item_content))
        i = j

    if not items:  # pragma: no cover
        return None, i  # pragma: no cover

    if kind == "ul":
        return _bullet_list(items), i
    else:
        return _ordered_list(items), i


# ---------------------------------------------------------------------------
# Callout parser
# ---------------------------------------------------------------------------

def _parse_callout(lines, start_i, comment_collector=None, mention_map=None):
    """
    Parse an Obsidian callout: > [!TYPE] optional title
                                > body line
    Returns (panel_node, next_i).
    """
    m = re.match(r"^>\s*\[!(\w+)\][\-+]?\s*(.*)", lines[start_i])
    if not m:
        return None, start_i

    panel_type = CALLOUT_MAP.get(m.group(1).lower(), "info")
    title = m.group(2).strip()

    body_lines = []
    if title:
        body_lines.append(title)

    i = start_i + 1
    while i < len(lines) and lines[i].startswith(">"):
        body_lines.append(re.sub(r"^>\s?", "", lines[i]))
        i += 1

    # Build panel content: group non-blank lines into paragraphs
    panel_content = []
    para_lines = []
    for bl in body_lines:
        if bl.strip():
            para_lines.append(bl.strip())
        else:
            if para_lines:
                panel_content.append(_paragraph(parse_inline(" ".join(para_lines), comment_collector, mention_map)))
                para_lines = []
    if para_lines:
        panel_content.append(_paragraph(parse_inline(" ".join(para_lines), comment_collector, mention_map)))

    if not panel_content:
        panel_content = [_paragraph([_text("")])]

    return _panel(panel_type, panel_content), i


# ---------------------------------------------------------------------------
# Blockquote parser
# ---------------------------------------------------------------------------

def _parse_blockquote(lines, start_i, comment_collector=None, mention_map=None):
    """
    Parse a plain blockquote (lines starting with >).
    Returns (blockquote_node, next_i).
    """
    body_lines = []
    i = start_i
    while i < len(lines) and lines[i].startswith(">"):
        body_lines.append(re.sub(r"^>\s?", "", lines[i]))
        i += 1

    content = []
    para_lines = []
    for bl in body_lines:
        if bl.strip():
            para_lines.append(bl.strip())
        else:
            if para_lines:
                content.append(_paragraph(parse_inline(" ".join(para_lines), comment_collector, mention_map)))
                para_lines = []
    if para_lines:
        content.append(_paragraph(parse_inline(" ".join(para_lines), comment_collector, mention_map)))

    if not content:
        content = [_paragraph([_text("")])]

    return _blockquote(content), i


# ---------------------------------------------------------------------------
# Main converter
# ---------------------------------------------------------------------------

def convert(content, image_map=None, mention_map=None, people_roster=None):
    """
    Convert Obsidian markdown to ADF.

    Args:
        content:       Raw markdown string from the .md file.
        image_map:     Optional dict mapping filename -> {"file_id": str, "collection": str}.
                       Pass None on a first pass to discover which images need uploading.
                       Pass the populated map on a second pass once images are uploaded.
        mention_map:   Optional dict mapping person name -> {"account_id": str, "display_name": str}.
                       When provided, [[Person Name]] wikilinks that match a key are converted to
                       ADF mention nodes (Confluence user tags) instead of plain text.
        people_roster: Optional dict mapping "First Last" -> {"account_id": str, "display_name": str}.
                       When provided, exact full-name matches in body prose are converted to ADF
                       mention nodes. Text inside code blocks, inline code and links is left alone.

    Returns:
        {
            "adf":      dict,   # ADF document, ready to JSON-serialize
            "images":   list,   # filenames that need uploading (only populated when image_map=None)
            "comments": list,   # [{"anchor": str, "body": str}, ...] for inline comment posting
        }
    """
    if image_map is None:
        image_map = {}
    if mention_map is None:
        mention_map = {}

    comment_collector = []
    images_needed = []

    # Strip YAML frontmatter
    content = re.sub(r"^---\n.*?\n---\n\n?", "", content, flags=re.DOTALL)

    # Strip/collect block-level Obsidian comments (%%\n...\n%%)
    def _handle_block_comment(m):
        body = m.group(1).strip()
        if body:
            comment_collector.append({"anchor": "", "body": body})
        return ""
    content = re.sub(r"%%\n(.*?)\n%%", _handle_block_comment, content, flags=re.DOTALL)

    lines = content.split("\n")
    nodes = []
    i = 0
    in_code = False
    code_lang = ""
    code_lines = []
    pending_para = []  # Lines being accumulated into a paragraph

    def flush_para():
        if not pending_para:
            return
        para_lines = [l.strip() for l in pending_para if l.strip()]
        pending_para.clear()
        if not para_lines:
            return
        # Smart-link embed: a single URL from a known provider on its own line
        # becomes an embedCard so Confluence renders it interactively.
        if len(para_lines) == 1 and EMBED_URL_PATTERN.match(para_lines[0]):
            nodes.append(_embed_card(para_lines[0]))
            return
        # Multiple source lines in one paragraph block are intentional breaks,
        # a standalone bold header with its description below. Separate each
        # line with a hard break rather than collapsing them onto one line.
        inline = []
        for idx, pl in enumerate(para_lines):
            if idx:
                inline.append({"type": "hardBreak"})
            inline.extend(parse_inline(pl, comment_collector, mention_map))
        nodes.append(_paragraph(inline))

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # ── Code block ──────────────────────────────────────────────────
        if stripped.startswith("```") and not in_code:
            flush_para()
            code_lang = stripped[3:].strip()
            code_lines = []
            in_code = True
            i += 1
            continue

        if stripped.startswith("```") and in_code:
            nodes.append(_code_block(code_lang, "\n".join(code_lines)))
            in_code = False
            code_lang = ""
            code_lines = []
            i += 1
            continue

        if in_code:
            code_lines.append(line)
            i += 1
            continue

        # ── Blank line ───────────────────────────────────────────────────
        if not stripped:
            flush_para()
            i += 1
            continue

        # ── Horizontal rule ──────────────────────────────────────────────
        if re.match(r"^(---|\*\*\*|___)\s*$", stripped):
            flush_para()
            nodes.append(_rule())
            i += 1
            continue

        # ── Heading ──────────────────────────────────────────────────────
        m = re.match(r"^(#{1,6})\s+(.+)$", line)
        if m:
            flush_para()
            level = len(m.group(1))
            nodes.append(_heading(level, parse_inline(m.group(2), comment_collector, mention_map)))
            i += 1
            continue

        # ── Image: ![[filename]] or ![alt](path) ─────────────────────────
        img_wiki = re.match(r"^!\[\[([^\]|]+?)(?:\|\d+)?\]\]\s*$", stripped)
        img_md   = re.match(r"^!\[([^\]]*)\]\(([^)]+)\)\s*$", stripped)
        if img_wiki or img_md:
            flush_para()
            filename = img_wiki.group(1) if img_wiki else img_md.group(2)
            basename = filename.rsplit("/", 1)[-1]
            if basename in image_map:
                info = image_map[basename]
                nodes.append(_media_single(info["file_id"], info["collection"]))
            else:
                images_needed.append(basename)
                # Placeholder paragraph; will be replaced on second pass
                nodes.append(_paragraph([_text(f"[Image: {basename}]")]))
            i += 1
            continue

        # ── Obsidian callout: > [!TYPE] ───────────────────────────────────
        if re.match(r"^>\s*\[!", line):
            flush_para()
            callout_node, i = _parse_callout(lines, i, comment_collector, mention_map)
            if callout_node:
                nodes.append(callout_node)
            continue

        # ── Blockquote ────────────────────────────────────────────────────
        if line.startswith(">"):
            flush_para()
            bq_node, i = _parse_blockquote(lines, i, comment_collector, mention_map)
            nodes.append(bq_node)
            continue

        # ── Table ─────────────────────────────────────────────────────────
        if _is_table_row(line):
            flush_para()
            tbl_node, i = _parse_table(lines, i, mention_map)
            nodes.append(tbl_node)
            continue

        # ── List ──────────────────────────────────────────────────────────
        if _get_list_kind(line):
            flush_para()
            list_node, i = _parse_list(lines, i, comment_collector, mention_map)
            if list_node:
                nodes.append(list_node)
            continue

        # ── Paragraph ─────────────────────────────────────────────────────
        pending_para.append(line)
        i += 1

    flush_para()

    _convert_bare_dates_in_table_cells(nodes)
    if people_roster:
        _inject_text_mentions(nodes, people_roster)

    return {
        "adf": _doc(nodes),
        "images": images_needed,
        "comments": comment_collector,
    }


def _convert_bare_dates_in_table_cells(nodes):
    """Walk every tableCell / tableHeader and replace any paragraph whose sole
    inline content is a single bare ISO date (YYYY-MM-DD) with a paragraph
    containing an ADF date node. Metadata tables (Author / Published / Date)
    get rendered as styled date pills without requiring explicit :date:...:
    markup in the source markdown.
    """
    for node in nodes:
        if not isinstance(node, dict):
            continue
        ntype = node.get("type")
        if ntype in ("tableCell", "tableHeader"):
            for child in node.get("content") or []:
                if child.get("type") != "paragraph":
                    continue
                inline = child.get("content") or []
                if len(inline) != 1:
                    continue
                only = inline[0]
                if only.get("type") != "text":
                    continue
                if only.get("marks"):
                    continue
                text = only.get("text", "").strip()
                if _BARE_ISO_DATE.match(text):
                    child["content"] = [_date(text)]
        # Recurse into any container that holds further block content.
        if node.get("content"):
            _convert_bare_dates_in_table_cells(node["content"])


def _split_text_node_on_names(node, pattern, roster):
    """Split one text node on exact full-name matches, returning a list of
    text and mention nodes. Returns [node] unchanged when there is no match.
    Existing marks are preserved on the surrounding text segments.
    """
    text = node.get("text", "")
    marks = node.get("marks")
    out = []
    last = 0
    for m in pattern.finditer(text):
        start, end = m.span()
        if start > last:
            seg = {"type": "text", "text": text[last:start]}
            if marks:
                seg["marks"] = marks
            out.append(seg)
        info = roster[m.group(0)]
        out.append(_mention(info["account_id"], info["display_name"]))
        last = end
    if last == 0:
        return [node]
    if last < len(text):
        seg = {"type": "text", "text": text[last:]}
        if marks:
            seg["marks"] = marks
        out.append(seg)
    return out


def _inject_text_mentions(nodes, roster):
    """Walk block content and replace exact 'First Last' matches in plain body
    text with ADF mention nodes. roster maps the full name to
    {"account_id": str, "display_name": str}.

    Text is left untouched inside code blocks, inline code (text carrying a
    `code` mark) and links (text carrying a `link` mark), so identifiers and
    link labels are never rewritten. Names are matched whole-word and
    longest-first so a full name wins over any shorter overlapping entry.
    """
    if not roster:
        return
    names = sorted(roster.keys(), key=len, reverse=True)
    pattern = re.compile(r"\b(?:" + "|".join(re.escape(n) for n in names) + r")\b")

    def process(content):
        rebuilt = []
        for node in content:
            if not isinstance(node, dict):
                rebuilt.append(node)
                continue
            if node.get("type") == "codeBlock":
                rebuilt.append(node)
                continue
            if node.get("type") == "text":
                if any(mk.get("type") in ("code", "link") for mk in node.get("marks", [])):
                    rebuilt.append(node)
                else:
                    rebuilt.extend(_split_text_node_on_names(node, pattern, roster))
                continue
            if node.get("content"):
                node["content"] = process(node["content"])
            rebuilt.append(node)
        return rebuilt

    nodes[:] = process(nodes)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":  # pragma: no cover
    if len(sys.argv) < 2:
        print("Usage: md_to_adf.py <file.md>", file=sys.stderr)
        sys.exit(1)

    with open(sys.argv[1], encoding="utf-8") as f:
        raw = f.read()

    result = convert(raw)
    print(json.dumps(result["adf"], ensure_ascii=False, indent=2))

    if result["images"]:
        print(f"\n# Images needing upload ({len(result['images'])}):", file=sys.stderr)
        for img in result["images"]:
            print(f"  - {img}", file=sys.stderr)

    if result["comments"]:
        print(f"\n# Inline comments to post ({len(result['comments'])}):", file=sys.stderr)
        for c in result["comments"]:
            print(f"  anchor: {c['anchor']!r}", file=sys.stderr)
            print(f"  body:   {c['body'][:60]!r}", file=sys.stderr)

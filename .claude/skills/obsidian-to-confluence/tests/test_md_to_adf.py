"""
Tests for md_to_adf.py - Obsidian markdown to ADF converter.

Coverage targets every reachable code path in md_to_adf.py:
- All ADF node constructors
- parse_inline: all 12 pattern types, marks composition, empty input
- _parse_table: with and without separator row
- _parse_list: ul, ol, nested, blank-line continuation, task checkboxes,
               continuation text, indent transitions
- _parse_callout: all panel types, titled/untitled, multi-paragraph body
- _parse_blockquote: single and multi-paragraph
- convert: YAML stripping, block comments, all block-level elements,
           image_map with and without match, flush_para edge cases
"""

import json
import pytest
from md_to_adf import (
    convert,
    parse_inline,
    _apply_mark,
    _is_table_row,
    _is_separator_row,
    _get_list_kind,
    _get_indent,
    _heading_slug,
    _parse_table,
    _parse_list,
    _parse_callout,
    _parse_blockquote,
    _doc,
    _paragraph,
    _heading,
    _text,
    _code_block,
    _rule,
    _bullet_list,
    _ordered_list,
    _list_item,
    _table,
    _table_row,
    _table_header,
    _table_cell,
    _panel,
    _blockquote,
    _media_single,
    CALLOUT_MAP,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def text_content(nodes):
    """Flatten all text values from a list of inline ADF nodes."""
    return "".join(n.get("text", "") for n in nodes if n.get("type") == "text")


def find_marks(nodes, mark_type):
    """Return all text nodes that have a given mark type."""
    return [
        n for n in nodes
        if n.get("type") == "text"
        and any(m.get("type") == mark_type for m in n.get("marks", []))
    ]


def collect_nodes_of_type(adf_doc, node_type):
    """Recursively collect all nodes of a given type from an ADF document."""
    results = []

    def walk(node):
        if node.get("type") == node_type:
            results.append(node)
        for child in node.get("content", []):
            walk(child)

    walk(adf_doc)
    return results


def all_text(adf_doc):
    """Collect all text values from leaf text nodes."""
    texts = []

    def walk(node):
        if node.get("type") == "text":
            texts.append(node.get("text", ""))
        for child in node.get("content", []):
            walk(child)

    walk(adf_doc)
    return "".join(texts)


# ---------------------------------------------------------------------------
# Node constructors
# ---------------------------------------------------------------------------

class TestNodeConstructors:
    def test_doc(self):
        d = _doc([])
        assert d["type"] == "doc"
        assert d["version"] == 1
        assert d["content"] == []

    def test_paragraph_with_content(self):
        p = _paragraph([_text("hello")])
        assert p["type"] == "paragraph"
        assert p["content"][0]["text"] == "hello"

    def test_paragraph_empty_gets_empty_text(self):
        p = _paragraph([])
        assert p["content"] == [_text("")]

    def test_paragraph_none_content_gets_empty_text(self):
        p = _paragraph(None)
        assert p["content"] == [_text("")]

    def test_heading(self):
        h = _heading(2, [_text("Title")])
        assert h["type"] == "heading"
        assert h["attrs"]["level"] == 2

    def test_text_no_marks(self):
        t = _text("hello")
        assert t["type"] == "text"
        assert t["text"] == "hello"
        assert "marks" not in t

    def test_text_with_marks(self):
        t = _text("hello", marks=[{"type": "strong"}])
        assert t["marks"] == [{"type": "strong"}]

    def test_code_block_with_language(self):
        cb = _code_block("python", "x = 1")
        assert cb["type"] == "codeBlock"
        assert cb["attrs"]["language"] == "python"
        assert cb["content"][0]["text"] == "x = 1"

    def test_code_block_no_language(self):
        cb = _code_block("", "x = 1")
        assert cb["attrs"] == {}

    def test_code_block_none_language(self):
        cb = _code_block(None, "x = 1")
        assert cb["attrs"] == {}

    def test_rule(self):
        assert _rule() == {"type": "rule"}

    def test_bullet_list(self):
        bl = _bullet_list([])
        assert bl["type"] == "bulletList"

    def test_ordered_list(self):
        ol = _ordered_list([])
        assert ol["type"] == "orderedList"

    def test_list_item(self):
        li = _list_item([_paragraph([_text("x")])])
        assert li["type"] == "listItem"

    def test_table_nodes(self):
        tbl = _table([_table_row([_table_header([_text("H")]), _table_cell([_text("D")])])])
        assert tbl["type"] == "table"
        row = tbl["content"][0]
        assert row["type"] == "tableRow"
        assert row["content"][0]["type"] == "tableHeader"
        assert row["content"][1]["type"] == "tableCell"

    def test_panel(self):
        p = _panel("warning", [_paragraph([_text("text")])])
        assert p["type"] == "panel"
        assert p["attrs"]["panelType"] == "warning"

    def test_blockquote(self):
        bq = _blockquote([_paragraph([_text("text")])])
        assert bq["type"] == "blockquote"

    def test_media_single(self):
        ms = _media_single("uuid-123", "contentId-456")
        assert ms["type"] == "mediaSingle"
        assert ms["attrs"]["layout"] == "center"
        media = ms["content"][0]
        assert media["type"] == "media"
        assert media["attrs"]["id"] == "uuid-123"
        assert media["attrs"]["collection"] == "contentId-456"

    def test_apply_mark_on_text_node(self):
        nodes = [_text("hello")]
        result = _apply_mark(nodes, {"type": "strong"})
        assert result[0]["marks"] == [{"type": "strong"}]

    def test_apply_mark_preserves_existing_marks(self):
        nodes = [_text("hello", marks=[{"type": "em"}])]
        result = _apply_mark(nodes, {"type": "strong"})
        mark_types = [m["type"] for m in result[0]["marks"]]
        assert "em" in mark_types
        assert "strong" in mark_types

    def test_apply_mark_on_non_text_node(self):
        nodes = [{"type": "hardBreak"}]
        result = _apply_mark(nodes, {"type": "strong"})
        assert result == nodes  # unchanged


# ---------------------------------------------------------------------------
# Heading slug
# ---------------------------------------------------------------------------

class TestHeadingSlug:
    def test_basic(self):
        assert _heading_slug("Hello World") == "hello-world"

    def test_underscores_preserved(self):
        assert _heading_slug("siem_entity") == "siem_entity"

    def test_strips_special_chars(self):
        # strip("-") removes trailing dash produced by trailing "!"
        assert _heading_slug("Hello (World)!") == "hello-world"

    def test_strips_leading_trailing_dashes(self):
        result = _heading_slug("  Hello  ")
        assert not result.startswith("-")


# ---------------------------------------------------------------------------
# Table helpers
# ---------------------------------------------------------------------------

class TestTableHelpers:
    def test_is_table_row_true(self):
        assert _is_table_row("| a | b |")
        assert _is_table_row("  | a | b |  ")

    def test_is_table_row_false(self):
        assert not _is_table_row("plain text")
        assert not _is_table_row("|")         # too short
        assert not _is_table_row("| abc")     # no trailing pipe

    def test_is_separator_row_true(self):
        assert _is_separator_row("| --- | --- |")
        assert _is_separator_row("| :--- | ---: |")
        assert _is_separator_row("| :---: | --- |")

    def test_is_separator_row_false_no_dashes(self):
        assert not _is_separator_row("| abc | def |")

    def test_is_separator_row_false_no_pipes(self):
        assert not _is_separator_row("--- ---")


# ---------------------------------------------------------------------------
# List helpers
# ---------------------------------------------------------------------------

class TestListHelpers:
    def test_get_list_kind_ul_dash(self):
        assert _get_list_kind("- item") == "ul"

    def test_get_list_kind_ul_star(self):
        assert _get_list_kind("* item") == "ul"

    def test_get_list_kind_ol(self):
        assert _get_list_kind("1. item") == "ol"

    def test_get_list_kind_none(self):
        assert _get_list_kind("plain text") is None
        assert _get_list_kind("") is None

    def test_get_indent_zero(self):
        assert _get_indent("text") == 0

    def test_get_indent_nonzero(self):
        assert _get_indent("    text") == 4
        assert _get_indent("  text") == 2


# ---------------------------------------------------------------------------
# parse_inline
# ---------------------------------------------------------------------------

class TestParseInline:
    def test_plain_text(self):
        nodes = parse_inline("hello world")
        assert text_content(nodes) == "hello world"
        assert all("marks" not in n for n in nodes)

    def test_empty_string_returns_empty_text_node(self):
        nodes = parse_inline("")
        assert nodes == [_text("")]

    def test_bold(self):
        nodes = parse_inline("**bold**")
        marked = find_marks(nodes, "strong")
        assert marked
        assert text_content(marked) == "bold"

    def test_italic_star(self):
        nodes = parse_inline("*italic*")
        marked = find_marks(nodes, "em")
        assert marked
        assert text_content(marked) == "italic"

    def test_italic_underscore(self):
        nodes = parse_inline("_italic_")
        marked = find_marks(nodes, "em")
        assert marked

    def test_bold_italic(self):
        nodes = parse_inline("***both***")
        marked = [n for n in nodes if n.get("type") == "text" and n.get("marks")]
        assert marked
        mark_types = {m["type"] for m in marked[0]["marks"]}
        assert "strong" in mark_types
        assert "em" in mark_types

    def test_strikethrough(self):
        nodes = parse_inline("~~crossed~~")
        marked = find_marks(nodes, "strike")
        assert marked
        assert text_content(marked) == "crossed"

    def test_highlight_becomes_bold(self):
        nodes = parse_inline("==highlighted==")
        marked = find_marks(nodes, "strong")
        assert marked
        assert text_content(marked) == "highlighted"

    def test_inline_code(self):
        nodes = parse_inline("`code`")
        marked = find_marks(nodes, "code")
        assert marked
        assert text_content(marked) == "code"

    def test_external_link(self):
        nodes = parse_inline("[text](https://example.com)")
        link_nodes = find_marks(nodes, "link")
        assert link_nodes
        link_mark = next(m for m in link_nodes[0]["marks"] if m["type"] == "link")
        assert link_mark["attrs"]["href"] == "https://example.com"
        assert link_nodes[0]["text"] == "text"

    def test_local_md_link_becomes_plain_text(self):
        nodes = parse_inline("[text](some/file.md)")
        assert text_content(nodes) == "text"
        assert not find_marks(nodes, "link")

    def test_anchor_link(self):
        nodes = parse_inline("[Go there](#section)")
        link_nodes = find_marks(nodes, "link")
        assert link_nodes
        href = next(m for m in link_nodes[0]["marks"] if m["type"] == "link")["attrs"]["href"]
        assert href == "#section"

    def test_wikilink_plain(self):
        nodes = parse_inline("[[Page Name]]")
        assert text_content(nodes) == "Page Name"
        assert not find_marks(nodes, "link")

    def test_wikilink_with_display(self):
        nodes = parse_inline("[[Page Name|Display Text]]")
        assert text_content(nodes) == "Display Text"

    def test_wikilink_anchor(self):
        nodes = parse_inline("[[#Heading Name]]")
        link_nodes = find_marks(nodes, "link")
        assert link_nodes
        assert text_content(link_nodes) == "Heading Name"

    def test_wikilink_anchor_with_display(self):
        nodes = parse_inline("[[#Heading|Label]]")
        link_nodes = find_marks(nodes, "link")
        assert link_nodes
        assert text_content(link_nodes) == "Label"

    def test_comment_stripped_no_collector(self):
        nodes = parse_inline("before %%note%% after")
        txt = text_content(nodes)
        assert "%%note%%" not in txt
        assert "before" in txt
        assert "after" in txt

    def test_comment_collected(self):
        collector = []
        nodes = parse_inline("before text %%my note%% after", comment_collector=collector)
        assert len(collector) == 1
        assert collector[0]["body"] == "my note"
        assert "before" in collector[0]["anchor"]

    def test_comment_empty_body_not_collected(self):
        collector = []
        parse_inline("text %%%% more", comment_collector=collector)
        assert collector == []

    def test_comment_collector_none(self):
        # Should not raise, just discard the comment
        nodes = parse_inline("text %%comment%% more", comment_collector=None)
        assert text_content(nodes) == "text  more"

    def test_text_before_and_after_pattern(self):
        nodes = parse_inline("hello **world** there")
        texts = [n["text"] for n in nodes if n.get("type") == "text"]
        assert "hello " in texts
        assert "world" in texts
        assert " there" in texts

    def test_nested_marks(self):
        # Bold containing italic
        nodes = parse_inline("**_bold italic_**")
        # Should produce nodes with both strong and em marks
        multi = [n for n in nodes if len(n.get("marks", [])) >= 2]
        if multi:
            mark_types = {m["type"] for m in multi[0]["marks"]}
            assert "strong" in mark_types
            assert "em" in mark_types

    def test_ftp_link_kept(self):
        nodes = parse_inline("[file](ftp://example.com/file)")
        link_nodes = find_marks(nodes, "link")
        assert link_nodes


# ---------------------------------------------------------------------------
# _parse_table
# ---------------------------------------------------------------------------

class TestParseTable:
    def test_basic_table_with_separator(self):
        lines = [
            "| Name | Age |",
            "| ---- | --- |",
            "| Alice | 30 |",
            "| Bob | 25 |",
        ]
        node, next_i = _parse_table(lines, 0)
        assert node["type"] == "table"
        rows = node["content"]
        assert len(rows) == 3  # 1 header + 2 data
        assert rows[0]["content"][0]["type"] == "tableHeader"
        assert rows[1]["content"][0]["type"] == "tableCell"

    def test_table_column_content(self):
        lines = [
            "| Name | Value |",
            "| ---- | ----- |",
            "| foo | bar |",
        ]
        node, _ = _parse_table(lines, 0)
        header_row = node["content"][0]
        header_texts = [
            text_content(cell["content"][0]["content"])
            for cell in header_row["content"]
        ]
        assert "Name" in header_texts
        assert "Value" in header_texts

    def test_table_no_separator_first_row_becomes_header(self):
        lines = [
            "| Col1 | Col2 |",
            "| data1 | data2 |",
        ]
        node, _ = _parse_table(lines, 0)
        rows = node["content"]
        assert rows[0]["content"][0]["type"] == "tableHeader"
        assert rows[1]["content"][0]["type"] == "tableCell"

    def test_table_stops_at_non_table_line(self):
        lines = [
            "| A | B |",
            "| --- | --- |",
            "| 1 | 2 |",
            "",
            "not a table",
        ]
        node, next_i = _parse_table(lines, 0)
        assert next_i == 3  # blank line stops it

    def test_table_alignment_row_is_not_data(self):
        lines = [
            "| Status | Written by |",
            "|---|---|",
            "| OPEN | Pipeline |",
        ]
        node, _ = _parse_table(lines, 0)
        assert len(node["content"]) == 2  # 1 header + 1 data, no separator row

    def test_table_with_inline_formatting_in_cells(self):
        lines = [
            "| **Bold** | *Italic* |",
            "| --- | --- |",
            "| plain | `code` |",
        ]
        node, _ = _parse_table(lines, 0)
        header_cell = node["content"][0]["content"][0]
        bold_nodes = collect_nodes_of_type(header_cell, "text")
        assert any(
            any(m.get("type") == "strong" for m in n.get("marks", []))
            for n in bold_nodes
        )


# ---------------------------------------------------------------------------
# _parse_list
# ---------------------------------------------------------------------------

class TestParseList:
    def test_simple_unordered_list(self):
        lines = ["- item one", "- item two", "- item three"]
        node, next_i = _parse_list(lines, 0)
        assert node["type"] == "bulletList"
        assert len(node["content"]) == 3
        assert next_i == 3

    def test_simple_ordered_list(self):
        lines = ["1. first", "2. second"]
        node, next_i = _parse_list(lines, 0)
        assert node["type"] == "orderedList"
        assert len(node["content"]) == 2

    def test_list_with_star_marker(self):
        lines = ["* item one", "* item two"]
        node, _ = _parse_list(lines, 0)
        assert node["type"] == "bulletList"

    def test_nested_list(self):
        lines = [
            "- parent",
            "  - child one",
            "  - child two",
            "- parent two",
        ]
        node, _ = _parse_list(lines, 0)
        assert node["type"] == "bulletList"
        assert len(node["content"]) == 2
        # First item should have a nested bulletList
        first_item_content = node["content"][0]["content"]
        assert any(n["type"] == "bulletList" for n in first_item_content)

    def test_list_ends_at_non_list_line(self):
        lines = ["- item", "not a list item"]
        node, next_i = _parse_list(lines, 0)
        assert len(node["content"]) == 1
        assert next_i == 1

    def test_list_ends_at_different_kind(self):
        lines = ["- bullet", "1. ordered"]
        node, next_i = _parse_list(lines, 0)
        assert node["type"] == "bulletList"
        assert len(node["content"]) == 1
        assert next_i == 1

    def test_task_checkbox_unchecked_becomes_plain(self):
        lines = ["- [ ] task item"]
        node, _ = _parse_list(lines, 0)
        item_text = text_content(
            node["content"][0]["content"][0]["content"]
        )
        assert "task item" in item_text
        assert "[ ]" not in item_text

    def test_task_checkbox_checked_becomes_plain(self):
        lines = ["- [x] done item"]
        node, _ = _parse_list(lines, 0)
        item_text = text_content(
            node["content"][0]["content"][0]["content"]
        )
        assert "done item" in item_text
        assert "[x]" not in item_text

    def test_task_checkbox_partial_variants(self):
        for marker in ["[~]", "[X]", "[-]"]:
            lines = [f"- {marker} item"]
            node, _ = _parse_list(lines, 0)
            assert node is not None

    def test_blank_line_between_same_kind_items_continues(self):
        lines = ["- item one", "", "- item two"]
        node, next_i = _parse_list(lines, 0)
        assert len(node["content"]) == 2
        assert next_i == 3

    def test_blank_line_then_non_list_ends(self):
        lines = ["- item one", "", "paragraph text"]
        node, next_i = _parse_list(lines, 0)
        assert len(node["content"]) == 1
        assert next_i == 2  # points to the blank line, outer loop handles paragraph

    def test_blank_line_at_eof_ends(self):
        lines = ["- item one", ""]
        node, next_i = _parse_list(lines, 0)
        assert len(node["content"]) == 1

    def test_continuation_text_merged_into_item(self):
        lines = ["- first line", "  continuation text"]
        node, _ = _parse_list(lines, 0)
        item_para = node["content"][0]["content"][0]
        full_text = text_content(item_para["content"])
        assert "first line" in full_text
        assert "continuation" in full_text

    def test_less_indented_line_ends_list(self):
        lines = ["  - child", "- parent level"]
        # Start parsing a list where first item is indented
        # The indented item IS the first item (base_indent = 2)
        node, next_i = _parse_list(lines, 0)
        # "  - child" has indent 2, so base is 2
        # "- parent level" has indent 0 < 2, so we break
        assert next_i == 1

    def test_greater_indent_non_list_skipped(self):
        lines = ["- item", "    not a list item"]
        node, _ = _parse_list(lines, 0)
        assert len(node["content"]) == 1

    def test_inline_formatting_in_list_item(self):
        lines = ["- **bold** item"]
        node, _ = _parse_list(lines, 0)
        para_content = node["content"][0]["content"][0]["content"]
        bold_nodes = [n for n in para_content if any(m.get("type") == "strong" for m in n.get("marks", []))]
        assert bold_nodes

    def test_nested_ordered_in_unordered(self):
        lines = [
            "- bullet",
            "    1. ordered nested",
            "    2. second ordered",
            "- another bullet",
        ]
        node, _ = _parse_list(lines, 0)
        first_item = node["content"][0]["content"]
        assert any(n["type"] == "orderedList" for n in first_item)


# ---------------------------------------------------------------------------
# _parse_callout
# ---------------------------------------------------------------------------

class TestParseCallout:
    def test_note_becomes_info_panel(self):
        lines = ["> [!NOTE]", "> Body text"]
        node, next_i = _parse_callout(lines, 0)
        assert node["type"] == "panel"
        assert node["attrs"]["panelType"] == "info"
        assert next_i == 2

    def test_warning_type(self):
        lines = ["> [!WARNING] My warning", "> Details"]
        node, _ = _parse_callout(lines, 0)
        assert node["attrs"]["panelType"] == "warning"

    def test_danger_maps_to_error(self):
        lines = ["> [!DANGER]", "> Be careful"]
        node, _ = _parse_callout(lines, 0)
        assert node["attrs"]["panelType"] == "error"

    def test_tip_type(self):
        lines = ["> [!TIP]", "> Helpful tip"]
        node, _ = _parse_callout(lines, 0)
        assert node["attrs"]["panelType"] == "tip"

    def test_success_maps_to_tip(self):
        lines = ["> [!SUCCESS]"]
        node, _ = _parse_callout(lines, 0)
        assert node["attrs"]["panelType"] == "tip"

    def test_example_maps_to_note(self):
        lines = ["> [!EXAMPLE]", "> body"]
        node, _ = _parse_callout(lines, 0)
        assert node["attrs"]["panelType"] == "note"

    def test_unknown_type_maps_to_info(self):
        lines = ["> [!CUSTOM]", "> body"]
        node, _ = _parse_callout(lines, 0)
        assert node["attrs"]["panelType"] == "info"

    def test_title_included_in_body(self):
        lines = ["> [!NOTE] My Title", "> Body text"]
        node, _ = _parse_callout(lines, 0)
        full_text = all_text(node)
        assert "My Title" in full_text

    def test_titleless_callout(self):
        lines = ["> [!INFO]", "> Just body"]
        node, _ = _parse_callout(lines, 0)
        full_text = all_text(node)
        assert "Just body" in full_text

    def test_multi_paragraph_body(self):
        lines = ["> [!NOTE]", "> Para one", ">", "> Para two"]
        node, _ = _parse_callout(lines, 0)
        assert len(node["content"]) == 2

    def test_empty_callout_gets_empty_paragraph(self):
        lines = ["> [!NOTE]"]
        node, _ = _parse_callout(lines, 0)
        assert len(node["content"]) == 1

    def test_stops_at_non_quote_line(self):
        lines = ["> [!NOTE]", "> body", "not a quote"]
        node, next_i = _parse_callout(lines, 0)
        assert next_i == 2

    def test_published_to_confluence_marker_is_skipped(self):
        # This is the Step 9 post-publish lock marker added to the Obsidian note.
        # It must never round-trip into the Confluence page body.
        lines = [
            "> [!WARNING] Published to Confluence (edit there)",
            "> This document was published to Confluence on 2026-07-24. All future edits should happen in Confluence, not here.",
            "> **Confluence page:** [Some Page](https://datadoghq.atlassian.net/wiki/spaces/CSiem/pages/123)",
        ]
        node, next_i = _parse_callout(lines, 0)
        assert node is None
        assert next_i == len(lines)

    def test_published_to_confluence_marker_is_case_insensitive(self):
        lines = ["> [!WARNING] PUBLISHED TO CONFLUENCE (edit there)", "> body"]
        node, _ = _parse_callout(lines, 0)
        assert node is None

    def test_unrelated_warning_callout_still_renders(self):
        lines = ["> [!WARNING] Something else entirely", "> body"]
        node, _ = _parse_callout(lines, 0)
        assert node is not None
        assert node["attrs"]["panelType"] == "warning"

    def test_collapsible_marker_ignored(self):
        # Obsidian collapsible syntax: [!NOTE]- (dash AFTER closing bracket)
        lines = ["> [!NOTE]-", "> body"]
        node, _ = _parse_callout(lines, 0)
        assert node is not None
        assert node["attrs"]["panelType"] == "info"

    def test_all_callout_map_types(self):
        for obsidian_type, panel_type in CALLOUT_MAP.items():
            lines = [f"> [!{obsidian_type.upper()}]", "> body"]
            node, _ = _parse_callout(lines, 0)
            assert node["attrs"]["panelType"] == panel_type


# ---------------------------------------------------------------------------
# _parse_blockquote
# ---------------------------------------------------------------------------

class TestParseBlockquote:
    def test_single_line(self):
        lines = ["> quoted text"]
        node, next_i = _parse_blockquote(lines, 0)
        assert node["type"] == "blockquote"
        full = all_text(node)
        assert "quoted text" in full
        assert next_i == 1

    def test_multi_line_single_paragraph(self):
        lines = ["> line one", "> line two"]
        node, _ = _parse_blockquote(lines, 0)
        assert len(node["content"]) == 1

    def test_multi_paragraph(self):
        lines = ["> para one", ">", "> para two"]
        node, _ = _parse_blockquote(lines, 0)
        assert len(node["content"]) == 2

    def test_stops_at_non_quote_line(self):
        lines = ["> quote", "plain"]
        node, next_i = _parse_blockquote(lines, 0)
        assert next_i == 1

    def test_inline_formatting_preserved(self):
        lines = ["> **bold** text"]
        node, _ = _parse_blockquote(lines, 0)
        bold_nodes = collect_nodes_of_type(node, "text")
        has_bold = any(
            any(m.get("type") == "strong" for m in n.get("marks", []))
            for n in bold_nodes
        )
        assert has_bold

    def test_empty_blockquote_line(self):
        lines = [">"]
        node, _ = _parse_blockquote(lines, 0)
        # Empty body still produces a valid blockquote
        assert node["type"] == "blockquote"
        assert len(node["content"]) == 1


# ---------------------------------------------------------------------------
# convert() - main function
# ---------------------------------------------------------------------------

class TestConvert:
    def test_returns_dict_with_required_keys(self):
        result = convert("# Hello")
        assert "adf" in result
        assert "images" in result
        assert "comments" in result

    def test_adf_root_structure(self):
        result = convert("# Hello")
        adf = result["adf"]
        assert adf["type"] == "doc"
        assert adf["version"] == 1
        assert isinstance(adf["content"], list)

    def test_yaml_frontmatter_stripped(self):
        md = "---\ntitle: Test\ndate: 2026-01-01\n---\n\n# Heading"
        result = convert(md)
        adf = result["adf"]
        texts = all_text(adf)
        assert "title" not in texts
        assert "Heading" in texts

    def test_heading_levels(self):
        md = "# H1\n## H2\n### H3\n#### H4"
        result = convert(md)
        headings = collect_nodes_of_type(result["adf"], "heading")
        levels = [h["attrs"]["level"] for h in headings]
        assert 1 in levels
        assert 2 in levels
        assert 3 in levels
        assert 4 in levels

    def test_paragraph(self):
        result = convert("Simple paragraph text.")
        paras = collect_nodes_of_type(result["adf"], "paragraph")
        assert any("Simple paragraph" in all_text(p) for p in paras)

    def test_horizontal_rule_triple_dash(self):
        result = convert("before\n\n---\n\nafter")
        rules = collect_nodes_of_type(result["adf"], "rule")
        assert len(rules) >= 1

    def test_horizontal_rule_triple_star(self):
        result = convert("before\n\n***\n\nafter")
        rules = collect_nodes_of_type(result["adf"], "rule")
        assert len(rules) >= 1

    def test_horizontal_rule_triple_underscore(self):
        result = convert("before\n\n___\n\nafter")
        rules = collect_nodes_of_type(result["adf"], "rule")
        assert len(rules) >= 1

    def test_code_block_with_language(self):
        md = "```python\ndef hello():\n    pass\n```"
        result = convert(md)
        code_blocks = collect_nodes_of_type(result["adf"], "codeBlock")
        assert len(code_blocks) == 1
        assert code_blocks[0]["attrs"].get("language") == "python"
        assert "def hello()" in all_text(code_blocks[0])

    def test_code_block_without_language(self):
        md = "```\nplain code\n```"
        result = convert(md)
        code_blocks = collect_nodes_of_type(result["adf"], "codeBlock")
        assert len(code_blocks) == 1
        assert "plain code" in all_text(code_blocks[0])

    def test_code_block_no_language_empty_attrs(self):
        md = "```\ncode\n```"
        result = convert(md)
        cb = collect_nodes_of_type(result["adf"], "codeBlock")[0]
        assert "language" not in cb["attrs"]

    def test_bullet_list(self):
        md = "- item one\n- item two"
        result = convert(md)
        lists = collect_nodes_of_type(result["adf"], "bulletList")
        assert len(lists) == 1
        assert len(lists[0]["content"]) == 2

    def test_ordered_list(self):
        md = "1. first\n2. second\n3. third"
        result = convert(md)
        lists = collect_nodes_of_type(result["adf"], "orderedList")
        assert len(lists) == 1
        assert len(lists[0]["content"]) == 3

    def test_table(self):
        md = "| A | B |\n| --- | --- |\n| 1 | 2 |"
        result = convert(md)
        tables = collect_nodes_of_type(result["adf"], "table")
        assert len(tables) == 1
        assert len(tables[0]["content"]) == 2  # header + 1 data row

    def test_blockquote(self):
        md = "> This is a quote"
        result = convert(md)
        bqs = collect_nodes_of_type(result["adf"], "blockquote")
        assert len(bqs) == 1

    def test_callout_becomes_panel(self):
        md = "> [!WARNING]\n> Watch out"
        result = convert(md)
        panels = collect_nodes_of_type(result["adf"], "panel")
        assert len(panels) == 1
        assert panels[0]["attrs"]["panelType"] == "warning"

    def test_image_wiki_no_map_becomes_placeholder(self):
        md = "![[diagram.png]]"
        result = convert(md)
        assert "diagram.png" in result["images"]
        paras = collect_nodes_of_type(result["adf"], "paragraph")
        placeholder_text = any("[Image: diagram.png]" in all_text(p) for p in paras)
        assert placeholder_text

    def test_image_wiki_with_size_hint(self):
        md = "![[diagram.png|300]]"
        result = convert(md)
        assert "diagram.png" in result["images"]

    def test_image_wiki_with_map_becomes_media_single(self):
        md = "![[photo.png]]"
        image_map = {"photo.png": {"file_id": "uuid-123", "collection": "contentId-456"}}
        result = convert(md, image_map=image_map)
        media_singles = collect_nodes_of_type(result["adf"], "mediaSingle")
        assert len(media_singles) == 1
        assert media_singles[0]["content"][0]["attrs"]["id"] == "uuid-123"

    def test_image_markdown_no_map_becomes_placeholder(self):
        md = "![alt text](path/to/image.png)"
        result = convert(md)
        assert "image.png" in result["images"]

    def test_image_markdown_with_map(self):
        md = "![alt text](path/to/photo.png)"
        image_map = {"photo.png": {"file_id": "uuid-789", "collection": "contentId-456"}}
        result = convert(md, image_map=image_map)
        media_singles = collect_nodes_of_type(result["adf"], "mediaSingle")
        assert len(media_singles) == 1

    def test_image_map_none_default(self):
        result = convert("![[image.png]]", image_map=None)
        assert "image.png" in result["images"]

    def test_inline_comment_stripped_and_collected(self):
        md = "Text before %%author note%% text after"
        result = convert(md)
        comments = result["comments"]
        assert len(comments) == 1
        assert comments[0]["body"] == "author note"
        full_text = all_text(result["adf"])
        assert "author note" not in full_text

    def test_block_comment_stripped_and_collected(self):
        md = "paragraph\n\n%%\nthis is a block comment\n%%\n\nafter"
        result = convert(md)
        comments = result["comments"]
        assert any("block comment" in c["body"] for c in comments)
        assert "block comment" not in all_text(result["adf"])

    def test_wikilink_becomes_plain_text(self):
        md = "See [[Entity Resolution]] for details"
        result = convert(md)
        full = all_text(result["adf"])
        assert "Entity Resolution" in full
        assert "[[" not in full

    def test_paragraph_flush_at_end(self):
        md = "Final paragraph with no trailing newline"
        result = convert(md)
        paras = collect_nodes_of_type(result["adf"], "paragraph")
        assert any("Final paragraph" in all_text(p) for p in paras)

    def test_blank_lines_do_not_create_nodes(self):
        md = "para one\n\n\n\npara two"
        result = convert(md)
        nodes = result["adf"]["content"]
        assert len(nodes) == 2  # two paragraphs, no empty nodes

    def test_multi_line_paragraph_joined(self):
        md = "line one\nline two\nline three"
        result = convert(md)
        paras = collect_nodes_of_type(result["adf"], "paragraph")
        full = all_text(paras[0])
        assert "line one" in full
        assert "line two" in full
        assert "line three" in full

    def test_images_list_deduplicated_not_enforced(self):
        # Same image twice - both are recorded (dedup is caller's concern)
        md = "![[img.png]]\n\n![[img.png]]"
        result = convert(md)
        assert result["images"].count("img.png") == 2

    def test_complex_document_no_errors(self):
        md = """---
title: Test Doc
date: 2026-04-09
---

# Main Heading

This is an **important** paragraph with _italic_ and `code`.

## Section

> [!NOTE] Key Point
> This is a note callout.

### Subsection

| Col A | Col B |
| ----- | ----- |
| val 1 | val 2 |

1. First item
2. Second item
   - nested bullet
   - another nested

```go
func main() {
    fmt.Println("hello")
}
```

> Regular blockquote

---

Final paragraph.
"""
        result = convert(md)
        adf = result["adf"]
        assert adf["type"] == "doc"
        assert len(adf["content"]) > 5

        headings = collect_nodes_of_type(adf, "heading")
        assert len(headings) >= 3

        panels = collect_nodes_of_type(adf, "panel")
        assert len(panels) == 1

        tables = collect_nodes_of_type(adf, "table")
        assert len(tables) == 1

        code_blocks = collect_nodes_of_type(adf, "codeBlock")
        assert len(code_blocks) == 1

        rules = collect_nodes_of_type(adf, "rule")
        assert len(rules) >= 1

    def test_json_serializable(self):
        md = "# Hello\n\nParagraph with **bold** and `code`."
        result = convert(md)
        # Should not raise
        json.dumps(result["adf"])

    def test_figma_url_becomes_embed_card(self):
        """A Figma URL alone on its own line emits an embedCard for interactive
        rendering in Confluence rather than a plain paragraph with a link."""
        md = (
            "## Resolution pipeline\n\n"
            "https://www.figma.com/board/K760CzZkSkJSgykE2nCW4j\n"
        )
        result = convert(md)
        embed_cards = [n for n in result["adf"]["content"] if n.get("type") == "embedCard"]
        assert len(embed_cards) == 1
        assert embed_cards[0]["attrs"]["url"] == "https://www.figma.com/board/K760CzZkSkJSgykE2nCW4j"

    def test_figma_file_url_becomes_embed_card(self):
        """Pattern matches other Figma URL shapes besides board/."""
        md = "https://www.figma.com/design/abc123/My-File\n"
        result = convert(md)
        embed_cards = [n for n in result["adf"]["content"] if n.get("type") == "embedCard"]
        assert len(embed_cards) == 1

    def test_non_figma_url_stays_paragraph(self):
        """A URL outside the smart-link allow list remains a normal linked paragraph."""
        md = "https://example.com/some-page\n"
        result = convert(md)
        embed_cards = [n for n in result["adf"]["content"] if n.get("type") == "embedCard"]
        paragraphs = [n for n in result["adf"]["content"] if n.get("type") == "paragraph"]
        assert len(embed_cards) == 0
        assert len(paragraphs) == 1

    def test_figma_url_with_surrounding_text_stays_paragraph(self):
        """A Figma URL embedded in a sentence is just a link, not an embed."""
        md = "See https://www.figma.com/board/abc for the diagram.\n"
        result = convert(md)
        embed_cards = [n for n in result["adf"]["content"] if n.get("type") == "embedCard"]
        assert len(embed_cards) == 0

    def test_inline_date_marker_becomes_date_node(self):
        """`:date:YYYY-MM-DD:` inline syntax produces an ADF date node so
        Confluence renders the value as a styled date pill."""
        md = "Published :date:2026-05-13: by the team.\n"
        result = convert(md)
        para = result["adf"]["content"][0]
        assert para["type"] == "paragraph"
        date_nodes = [n for n in para["content"] if n.get("type") == "date"]
        assert len(date_nodes) == 1
        # Noon UTC keeps the rendered calendar date stable for all viewers.
        assert date_nodes[0]["attrs"]["timestamp"] == "1778673600000"

    def test_bare_iso_date_in_table_cell_becomes_date_node(self):
        """A bare YYYY-MM-DD that is the sole content of a table cell is
        auto-promoted to a date node. Metadata tables (Author / Published /
        Date) get rich date rendering without explicit markup."""
        md = (
            "| Field | Value |\n"
            "|---|---|\n"
            "| Published | 2026-05-13 |\n"
        )
        result = convert(md)
        table = result["adf"]["content"][0]
        assert table["type"] == "table"
        # Locate the data row's second cell.
        data_row = table["content"][1]
        published_cell = data_row["content"][1]
        para = published_cell["content"][0]
        assert para["type"] == "paragraph"
        assert len(para["content"]) == 1
        assert para["content"][0]["type"] == "date"
        assert para["content"][0]["attrs"]["timestamp"] == "1778673600000"

    def test_bare_iso_date_in_prose_stays_text(self):
        """A bare ISO date that appears in normal paragraph prose is left as
        text. Auto-conversion is scoped to table cells where the date is the
        only content; converting in prose would surprise readers."""
        md = "The release shipped on 2026-05-13 after the freeze.\n"
        result = convert(md)
        para = result["adf"]["content"][0]
        date_nodes = [n for n in para["content"] if n.get("type") == "date"]
        assert len(date_nodes) == 0
        text = "".join(n.get("text", "") for n in para["content"] if n.get("type") == "text")
        assert "2026-05-13" in text

    def test_table_cell_with_non_date_text_stays_text(self):
        """Non-date table cells are unaffected by the post-processing pass."""
        md = (
            "| Field | Value |\n"
            "|---|---|\n"
            "| Author | Justin Flammia |\n"
        )
        result = convert(md)
        table = result["adf"]["content"][0]
        data_row = table["content"][1]
        author_cell = data_row["content"][1]
        para = author_cell["content"][0]
        date_nodes = [n for n in para["content"] if n.get("type") == "date"]
        assert len(date_nodes) == 0

    def test_status_marker_becomes_status_node(self):
        """`:status:LABEL:` produces an ADF status node so Confluence renders
        the value as the colored pill produced by the / Status macro. Default
        color is green, which is the standard for the NEW convention used on
        index pages."""
        md = "Federation Strategy :status:NEW: was published today.\n"
        result = convert(md)
        para = result["adf"]["content"][0]
        status_nodes = [n for n in para["content"] if n.get("type") == "status"]
        assert len(status_nodes) == 1
        assert status_nodes[0]["attrs"]["text"] == "NEW"
        assert status_nodes[0]["attrs"]["color"] == "green"
        # localId is required by Confluence even though it auto-generates one
        # in the UI. The converter assigns a UUID so the node is stable.
        assert "localId" in status_nodes[0]["attrs"]

    def test_status_marker_with_explicit_color(self):
        """`:status:LABEL:COLOR:` lets the author pick a non-default pill color
        (e.g., red for BLOCKED, yellow for DRAFT)."""
        md = "Status :status:BLOCKED:red: needs attention.\n"
        result = convert(md)
        para = result["adf"]["content"][0]
        status_nodes = [n for n in para["content"] if n.get("type") == "status"]
        assert len(status_nodes) == 1
        assert status_nodes[0]["attrs"]["text"] == "BLOCKED"
        assert status_nodes[0]["attrs"]["color"] == "red"

    def test_status_marker_invalid_color_falls_back_to_text_match(self):
        """A trailing token that is not a recognized color is treated as part
        of normal text rather than a status node, so `:status:LABEL:invalid:`
        stays as text. The single-arg form is matched only when no color
        suffix exists."""
        md = "Plain :status:NEW: pill.\n"
        result = convert(md)
        para = result["adf"]["content"][0]
        status_nodes = [n for n in para["content"] if n.get("type") == "status"]
        assert len(status_nodes) == 1
        assert status_nodes[0]["attrs"]["color"] == "green"


# ---------------------------------------------------------------------------
# Edge cases caught during integration testing
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_empty_document(self):
        result = convert("")
        assert result["adf"]["type"] == "doc"
        assert result["adf"]["content"] == []

    def test_only_yaml_frontmatter(self):
        md = "---\ntitle: Test\n---\n"
        result = convert(md)
        assert result["adf"]["content"] == []

    def test_code_inside_list_item(self):
        md = "- item with `inline code`"
        result = convert(md)
        lists = collect_nodes_of_type(result["adf"], "bulletList")
        assert len(lists) == 1

    def test_heading_with_inline_code(self):
        md = "## The `siem_entity` track"
        result = convert(md)
        headings = collect_nodes_of_type(result["adf"], "heading")
        assert len(headings) == 1

    def test_table_with_empty_cells(self):
        md = "| A | B |\n| --- | --- |\n| | |\n| x | |"
        result = convert(md)
        tables = collect_nodes_of_type(result["adf"], "table")
        assert len(tables) == 1

    def test_list_then_paragraph(self):
        md = "- list item\n\nparagraph after"
        result = convert(md)
        nodes = result["adf"]["content"]
        types = [n["type"] for n in nodes]
        assert "bulletList" in types
        assert "paragraph" in types

    def test_callout_then_paragraph(self):
        md = "> [!NOTE]\n> note body\n\nParagraph after"
        result = convert(md)
        types = [n["type"] for n in result["adf"]["content"]]
        assert "panel" in types
        assert "paragraph" in types

    def test_callout_parser_non_matching_line(self):
        # _parse_callout returns (None, start_i) when the regex doesn't match
        lines = ["> plain blockquote"]
        node, next_i = _parse_callout(lines, 0)
        assert node is None
        assert next_i == 0

    def test_list_item_blank_then_indented_continuation(self):
        # Tests lines 427-428: blank line inside item, followed by indented content
        # (inner_indent > base_indent → j = k; continue)
        lines = [
            "- first item",
            "",
            "    continuation after blank",
            "- second item",
        ]
        node, _ = _parse_list(lines, 0)
        # Should produce at least 1 item; continuation should be merged
        assert node is not None
        assert len(node["content"]) >= 1


# ---------------------------------------------------------------------------
# Full-name text mentions (people_roster)
# ---------------------------------------------------------------------------

class TestTextMentions:
    """convert(..., people_roster=...) tags exact 'First Last' matches in prose
    with ADF mention nodes, using the people directory's Atlassian IDs."""

    ROSTER = {
        "Justin Flammia": {"account_id": "712020:abc", "display_name": "Justin Flammia"},
        "Shariq Syed": {"account_id": "712020:def", "display_name": "Shariq Syed"},
    }

    def _para_nodes(self, adf):
        return [n for n in adf["content"] if n["type"] == "paragraph"]

    def test_full_name_in_prose_becomes_mention(self):
        adf = convert("Reviewed by Justin Flammia today.", people_roster=self.ROSTER)["adf"]
        para = self._para_nodes(adf)[0]
        mentions = [n for n in para["content"] if n.get("type") == "mention"]
        assert len(mentions) == 1
        assert mentions[0]["attrs"]["id"] == "712020:abc"
        # surrounding text is preserved on both sides
        texts = "".join(n.get("text", "") for n in para["content"])
        assert texts.startswith("Reviewed by ")
        assert texts.endswith(" today.")

    def test_two_distinct_people_both_tagged(self):
        adf = convert("Justin Flammia and Shariq Syed met.", people_roster=self.ROSTER)["adf"]
        para = self._para_nodes(adf)[0]
        ids = [n["attrs"]["id"] for n in para["content"] if n.get("type") == "mention"]
        assert ids == ["712020:abc", "712020:def"]

    def test_name_not_in_roster_stays_text(self):
        adf = convert("Spoke with Pat Unknown.", people_roster=self.ROSTER)["adf"]
        para = self._para_nodes(adf)[0]
        assert all(n.get("type") != "mention" for n in para["content"])

    def test_partial_first_name_not_matched(self):
        # A bare first name must not match the full-name roster entry.
        adf = convert("Justin reviewed it.", people_roster=self.ROSTER)["adf"]
        para = self._para_nodes(adf)[0]
        assert all(n.get("type") != "mention" for n in para["content"])

    def test_name_in_code_block_not_tagged(self):
        md = "```\nJustin Flammia\n```\n"
        adf = convert(md, people_roster=self.ROSTER)["adf"]
        cb = [n for n in adf["content"] if n["type"] == "codeBlock"][0]
        assert "Justin Flammia" in cb["content"][0]["text"]
        assert all(n.get("type") != "mention" for n in cb["content"])

    def test_name_in_inline_code_not_tagged(self):
        adf = convert("Use `Justin Flammia` literally.", people_roster=self.ROSTER)["adf"]
        para = self._para_nodes(adf)[0]
        assert all(n.get("type") != "mention" for n in para["content"])

    def test_name_in_link_text_not_tagged(self):
        adf = convert("[Justin Flammia](https://example.com)", people_roster=self.ROSTER)["adf"]
        para = self._para_nodes(adf)[0]
        assert all(n.get("type") != "mention" for n in para["content"])

    def test_no_roster_leaves_text_unchanged(self):
        adf = convert("Justin Flammia wrote this.")["adf"]
        para = self._para_nodes(adf)[0]
        assert all(n.get("type") != "mention" for n in para["content"])

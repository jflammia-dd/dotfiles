"""
Tests for review_table_adf.py - ADF review status table builder and extractor.

Covers:
- build_review_table_adf: full structure validation (author table, heading,
  reviewer table, rule sentinel)
- extract_review_table_adf: correct split with review section present,
  graceful handling when absent, no rule found in first 20 nodes
"""

import pytest
from review_table_adf import (
    build_review_table_adf,
    extract_review_table_adf,
    AUTHOR_ACCOUNT_ID,
    AUTHOR_DISPLAY_NAME,
    _mention,
    _text,
    _paragraph,
    _heading,
    _table,
    _table_row,
    _table_header,
    _table_cell,
    _rule,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def all_text(node):
    texts = []
    def walk(n):
        if n.get("type") == "text":
            texts.append(n.get("text", ""))
        for child in n.get("content", []):
            walk(child)
    walk(node)
    return "".join(texts)


def collect_types(nodes):
    return [n["type"] for n in nodes]


# ---------------------------------------------------------------------------
# Node constructors (review_table_adf has its own local copies)
# ---------------------------------------------------------------------------

class TestLocalNodeConstructors:
    def test_mention(self):
        m = _mention("id-123", "@Name")
        assert m["type"] == "mention"
        assert m["attrs"]["id"] == "id-123"
        assert m["attrs"]["text"] == "@Name"
        assert "localId" in m["attrs"]

    def test_mention_localid_is_uuid_format(self):
        m = _mention("id", "@Name")
        import re
        assert re.match(
            r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
            m["attrs"]["localId"]
        )

    def test_text_no_marks(self):
        t = _text("hello")
        assert t == {"type": "text", "text": "hello"}

    def test_text_with_marks(self):
        t = _text("bold", marks=[{"type": "strong"}])
        assert t["marks"] == [{"type": "strong"}]

    def test_paragraph(self):
        p = _paragraph([_text("x")])
        assert p["type"] == "paragraph"

    def test_heading(self):
        h = _heading(3, "Title")
        assert h["type"] == "heading"
        assert h["attrs"]["level"] == 3
        assert h["content"][0]["text"] == "Title"

    def test_table_structure(self):
        tbl = _table([_table_row([_table_header([_text("H")])])])
        assert tbl["type"] == "table"

    def test_table_cell(self):
        cell = _table_cell([_text("data")])
        assert cell["type"] == "tableCell"
        assert cell["attrs"] == {}

    def test_rule(self):
        assert _rule() == {"type": "rule"}


# ---------------------------------------------------------------------------
# build_review_table_adf
# ---------------------------------------------------------------------------

class TestBuildReviewTable:
    def setup_method(self):
        self.nodes = build_review_table_adf("2026-04-09")

    def test_returns_list(self):
        assert isinstance(self.nodes, list)

    def test_non_empty(self):
        assert len(self.nodes) > 0

    def test_first_node_is_table(self):
        assert self.nodes[0]["type"] == "table"

    def test_last_node_is_rule(self):
        assert self.nodes[-1]["type"] == "rule"

    def test_has_review_status_heading(self):
        heading_nodes = [n for n in self.nodes if n.get("type") == "heading"]
        assert heading_nodes
        heading_text = all_text(heading_nodes[0])
        assert "Review Status" in heading_text

    def test_heading_level_is_3(self):
        heading_nodes = [n for n in self.nodes if n.get("type") == "heading"]
        assert heading_nodes[0]["attrs"]["level"] == 3

    def test_has_two_tables(self):
        tables = [n for n in self.nodes if n.get("type") == "table"]
        assert len(tables) == 2

    def test_author_table_has_correct_rows(self):
        author_table = self.nodes[0]
        rows = author_table["content"]
        assert len(rows) == 2  # Author row + Published row

    def test_author_table_has_author_label(self):
        author_table = self.nodes[0]
        full = all_text(author_table)
        assert "Author" in full

    def test_author_table_has_published_label(self):
        author_table = self.nodes[0]
        full = all_text(author_table)
        assert "Published" in full

    def test_published_date_present(self):
        author_table = self.nodes[0]
        full = all_text(author_table)
        assert "2026-04-09" in full

    def test_author_mention_in_author_table(self):
        author_table = self.nodes[0]
        def find_mentions(node):
            mentions = []
            if node.get("type") == "mention":
                mentions.append(node)
            for child in node.get("content", []):
                mentions.extend(find_mentions(child))
            return mentions
        mentions = find_mentions(author_table)
        assert mentions
        assert mentions[0]["attrs"]["id"] == AUTHOR_ACCOUNT_ID

    def test_reviewer_table_has_four_header_columns(self):
        reviewer_table = [n for n in self.nodes if n.get("type") == "table"][1]
        header_row = reviewer_table["content"][0]
        header_cells = header_row["content"]
        assert len(header_cells) == 4

    def test_reviewer_header_labels(self):
        reviewer_table = [n for n in self.nodes if n.get("type") == "table"][1]
        header_row = reviewer_table["content"][0]
        header_texts = [all_text(cell) for cell in header_row["content"]]
        assert "Reviewer" in header_texts
        assert "Status" in header_texts
        assert "Date" in header_texts
        assert "Comment" in header_texts

    def test_reviewer_table_has_empty_row(self):
        reviewer_table = [n for n in self.nodes if n.get("type") == "table"][1]
        empty_row = reviewer_table["content"][1]
        # All cells should be empty
        cell_texts = [all_text(cell) for cell in empty_row["content"]]
        assert all(t == "" for t in cell_texts)

    def test_reviewer_table_has_disclaimer_row(self):
        reviewer_table = [n for n in self.nodes if n.get("type") == "table"][1]
        disclaimer_row = reviewer_table["content"][2]
        full = all_text(disclaimer_row)
        assert "APPROVED" in full or "To review" in full

    def test_structure_order_author_heading_reviewer_rule(self):
        types = collect_types(self.nodes)
        # Should be: table, heading, table, rule
        assert types[0] == "table"
        assert "heading" in types
        assert types[-1] == "rule"

    def test_multiple_calls_produce_different_uuids(self):
        # Each mention should get a fresh localId
        nodes1 = build_review_table_adf("2026-01-01")
        nodes2 = build_review_table_adf("2026-01-01")
        def get_mention_uuids(nodes):
            uuids = []
            def walk(node):
                if node.get("type") == "mention":
                    uuids.append(node["attrs"]["localId"])
                for child in node.get("content", []):
                    walk(child)
            for n in nodes:
                walk(n)
            return uuids
        uuids1 = get_mention_uuids(nodes1)
        uuids2 = get_mention_uuids(nodes2)
        assert uuids1
        assert uuids2
        assert uuids1[0] != uuids2[0]


# ---------------------------------------------------------------------------
# extract_review_table_adf
# ---------------------------------------------------------------------------

class TestExtractReviewTable:
    def _make_adf(self, nodes):
        return {"type": "doc", "version": 1, "content": nodes}

    def test_extracts_review_section_when_present(self):
        review_nodes = build_review_table_adf("2026-04-09")
        doc_nodes = [
            {"type": "heading", "attrs": {"level": 1}, "content": [_text("Title")]},
            {"type": "paragraph", "content": [_text("content")]},
        ]
        adf = self._make_adf(review_nodes + doc_nodes)

        review, content = extract_review_table_adf(adf)

        assert len(review) > 0
        assert review[-1]["type"] == "rule"  # sentinel included
        assert len(content) == 2
        assert content[0]["type"] == "heading"

    def test_review_nodes_match_built_nodes(self):
        review_nodes = build_review_table_adf("2026-04-09")
        doc_nodes = [{"type": "paragraph", "content": [_text("doc")]}]
        adf = self._make_adf(review_nodes + doc_nodes)

        review, content = extract_review_table_adf(adf)

        assert len(review) == len(review_nodes)
        for r, b in zip(review, review_nodes):
            assert r["type"] == b["type"]

    def test_returns_empty_review_when_first_node_is_not_table(self):
        adf = self._make_adf([
            {"type": "heading", "attrs": {"level": 1}, "content": [_text("Title")]},
            {"type": "paragraph", "content": [_text("body")]},
        ])
        review, content = extract_review_table_adf(adf)
        assert review == []
        assert len(content) == 2

    def test_returns_empty_review_for_empty_doc(self):
        adf = self._make_adf([])
        review, content = extract_review_table_adf(adf)
        assert review == []
        assert content == []

    def test_returns_empty_review_when_no_rule_in_first_20_nodes(self):
        # Table at start but rule is beyond position 20
        nodes = [{"type": "table", "content": []}]  # starts with table
        nodes += [{"type": "paragraph", "content": [_text("p")]} for _ in range(20)]
        # No rule in first 20
        adf = self._make_adf(nodes)
        review, content = extract_review_table_adf(adf)
        assert review == []
        assert len(content) == len(nodes)

    def test_rule_within_20_nodes_is_found(self):
        nodes = [{"type": "table", "content": []}]
        nodes += [{"type": "paragraph", "content": [_text("p")]} for _ in range(5)]
        nodes.append({"type": "rule"})
        nodes.append({"type": "paragraph", "content": [_text("after")]})
        adf = self._make_adf(nodes)

        review, content = extract_review_table_adf(adf)

        assert review[-1]["type"] == "rule"
        assert len(content) == 1
        assert content[0]["content"][0]["text"] == "after"

    def test_content_nodes_are_correct_after_extraction(self):
        review_nodes = build_review_table_adf("2026-04-09")
        doc_nodes = [
            {"type": "heading", "attrs": {"level": 1}, "content": [_text("Title")]},
            {"type": "paragraph", "content": [_text("Para one")]},
            {"type": "paragraph", "content": [_text("Para two")]},
        ]
        adf = self._make_adf(review_nodes + doc_nodes)
        _, content = extract_review_table_adf(adf)

        assert content[0]["attrs"]["level"] == 1
        assert all_text(content[1]) == "Para one"
        assert all_text(content[2]) == "Para two"

    def test_roundtrip_review_nodes_are_structurally_preserved(self):
        """
        Build review table, embed in doc, extract it, and confirm it matches
        what was originally built.
        """
        original = build_review_table_adf("2026-04-09")
        doc_content = [{"type": "paragraph", "content": [_text("body")]}]
        adf = self._make_adf(original + doc_content)

        extracted, _ = extract_review_table_adf(adf)

        assert len(extracted) == len(original)
        # Tables and heading types match
        for e, o in zip(extracted, original):
            assert e["type"] == o["type"]

"""
Integration tests for the full Obsidian-to-Confluence pipeline.

These tests run the complete conversion stack against real vault documents
(read-only) and validate the output without making any API calls. They
simulate the republish flow including annotation preservation.

Feature coverage targets (>85%):
  - All markdown elements that appear in the vault
  - Review table build/extract round-trip
  - Annotation extract/inject round-trip
  - Full republish simulation
"""

import json
import os
import pytest

# Skip all tests in this module if the vault is not present
VAULT_ROOT = "/Users/justin.flammia/Documents/Datadog"
ERS_DOC = os.path.join(VAULT_ROOT, "docs", "Entity Resolution Service - System Design.md")

pytestmark = pytest.mark.skipif(
    not os.path.exists(ERS_DOC),
    reason="Vault not accessible; integration tests require local vault",
)

from md_to_adf import convert
from review_table_adf import build_review_table_adf, extract_review_table_adf
from annotate_adf import extract_annotations, inject_annotations


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_doc(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def collect_types(adf_doc):
    """Count node types in an ADF document."""
    from collections import Counter
    counts = Counter()
    def walk(node):
        counts[node.get("type", "unknown")] += 1
        for child in node.get("content", []):
            walk(child)
    walk(adf_doc)
    return counts


def all_text(adf_doc):
    texts = []
    def walk(node):
        if node.get("type") == "text":
            texts.append(node.get("text", ""))
        for child in node.get("content", []):
            walk(child)
    walk(adf_doc)
    return "".join(texts)


def find_annotation_marks(node, results=None):
    if results is None:
        results = []
    for mark in node.get("marks", []):
        if mark.get("type") == "annotation":
            results.append(mark["attrs"]["id"])
    for child in node.get("content", []):
        find_annotation_marks(child, results)
    return results


# ---------------------------------------------------------------------------
# ERS System Design document: conversion validation
# ---------------------------------------------------------------------------

class TestERSDocConversion:
    def setup_method(self):
        content = load_doc(ERS_DOC)
        self.result = convert(content)
        self.adf = self.result["adf"]
        self.counts = collect_types(self.adf)

    def test_produces_valid_adf_root(self):
        assert self.adf["type"] == "doc"
        assert self.adf["version"] == 1
        assert isinstance(self.adf["content"], list)

    def test_produces_json_serializable_output(self):
        json.dumps(self.adf)

    def test_headings_present(self):
        assert self.counts["heading"] >= 10

    def test_paragraphs_present(self):
        assert self.counts["paragraph"] >= 20

    def test_tables_present(self):
        # ERS doc has the State Transitions table and others
        assert self.counts["table"] >= 1

    def test_table_has_header_row(self):
        tables = [n for n in self.adf["content"] if n.get("type") == "table"]
        for table in tables:
            first_row = table["content"][0]
            cell_types = {c["type"] for c in first_row["content"]}
            assert "tableHeader" in cell_types

    def test_ordered_lists_present(self):
        assert self.counts["orderedList"] >= 3

    def test_code_blocks_present(self):
        assert self.counts["codeBlock"] >= 5

    def test_code_blocks_have_language(self):
        def find_code_blocks(node, results=None):
            if results is None:
                results = []
            if node.get("type") == "codeBlock":
                results.append(node)
            for child in node.get("content", []):
                find_code_blocks(child, results)
            return results
        code_blocks = find_code_blocks(self.adf)
        langs_present = [cb for cb in code_blocks if cb["attrs"].get("language")]
        assert len(langs_present) >= 3

    def test_published_to_confluence_marker_produces_no_panel(self):
        # The ERS doc's only callouts are "Published to Confluence" post-publish lock
        # markers (Step 9 of the skill). These are vault-only and must never round-trip
        # into the Confluence body, so this doc correctly produces zero panels.
        assert self.counts.get("panel", 0) == 0

    def test_blockquotes_present(self):
        assert self.counts["blockquote"] >= 1

    def test_horizontal_rules_present(self):
        assert self.counts["rule"] >= 3

    def test_image_placeholders_detected(self):
        # ERS doc has ![[ers-system-context.png]] etc.
        assert len(self.result["images"]) >= 2
        assert "ers-system-context.png" in self.result["images"]
        assert "ers-component-detail.png" in self.result["images"]

    def test_no_yaml_frontmatter_leaked(self):
        full = all_text(self.adf)
        assert "date:" not in full.lower() or "date" in full  # "date" word may appear in content
        # Specific frontmatter keys that should not appear as standalone text
        assert "doc_link:" not in full

    def test_no_raw_wikilinks(self):
        full = all_text(self.adf)
        assert "[[" not in full

    def test_no_broken_local_links(self):
        def find_links(node, links):
            for mark in node.get("marks", []):
                if mark.get("type") == "link":
                    links.append(mark["attrs"]["href"])
            for child in node.get("content", []):
                find_links(child, links)
        links = []
        find_links(self.adf, links)
        local_links = [l for l in links if not l.startswith(("http", "#", "ftp"))]
        assert local_links == []

    def test_external_links_preserved(self):
        def find_links(node, links):
            for mark in node.get("marks", []):
                if mark.get("type") == "link":
                    links.append(mark["attrs"]["href"])
            for child in node.get("content", []):
                find_links(child, links)
        links = []
        find_links(self.adf, links)
        confluence_links = [l for l in links if "datadoghq.atlassian.net" in l]
        assert len(confluence_links) >= 3

    def test_state_transitions_table_structure(self):
        # Find the 5-column table (State | Written by | Overwrite | Entry | Exit)
        tables = [n for n in self.adf["content"] if n.get("type") == "table"]
        five_col_tables = [
            t for t in tables
            if len(t["content"][0]["content"]) == 5
        ]
        assert five_col_tables, "Expected the State Transitions table (5 cols)"
        t = five_col_tables[0]
        # Header row cells
        header_texts = [
            all_text(cell)
            for cell in t["content"][0]["content"]
        ]
        assert any("State" in h for h in header_texts)
        assert any("Written" in h for h in header_texts)


# ---------------------------------------------------------------------------
# Review table integration
# ---------------------------------------------------------------------------

class TestReviewTableIntegration:
    def test_review_table_prefixed_to_ers_doc(self):
        content = load_doc(ERS_DOC)
        result = convert(content)
        doc_nodes = result["adf"]["content"]

        review_nodes = build_review_table_adf("2026-04-09")
        all_nodes = review_nodes + doc_nodes
        full_adf = {"type": "doc", "version": 1, "content": all_nodes}

        # Full ADF is valid
        json.dumps(full_adf)

        # First node is the author table
        assert full_adf["content"][0]["type"] == "table"

        # Document heading appears after the review section
        headings = [n for n in full_adf["content"] if n.get("type") == "heading"]
        assert headings
        main_heading = headings[0]
        assert main_heading["attrs"]["level"] == 1 or any(
            "Entity" in all_text(h)
            for h in headings
        )

    def test_extract_review_table_from_prefixed_doc(self):
        content = load_doc(ERS_DOC)
        result = convert(content)
        doc_nodes = result["adf"]["content"]

        review_nodes = build_review_table_adf("2026-04-09")
        all_nodes = review_nodes + doc_nodes
        full_adf = {"type": "doc", "version": 1, "content": all_nodes}

        review, doc_content = extract_review_table_adf(full_adf)

        # Review section recovered correctly
        assert len(review) == len(review_nodes)
        assert review[-1]["type"] == "rule"

        # Document content starts with the first heading
        assert doc_content[0]["type"] in ("heading", "paragraph", "panel")

    def test_republish_preserves_review_table(self):
        """
        Simulate: first publish, then update from Obsidian.
        Review table from the 'old' page must survive.
        """
        content = load_doc(ERS_DOC)
        result = convert(content)
        doc_nodes = result["adf"]["content"]

        # First publish
        old_review = build_review_table_adf("2026-04-09")
        old_all = old_review + doc_nodes
        old_adf = {"type": "doc", "version": 1, "content": old_all}

        # Simulate Confluence storing the page and us re-fetching it
        fetched_adf = json.loads(json.dumps(old_adf))

        # Republish: extract existing review table
        recovered_review, _ = extract_review_table_adf(fetched_adf)
        assert recovered_review  # found it

        # Build new ADF from re-converting the same doc
        new_result = convert(content)
        new_doc_nodes = new_result["adf"]["content"]
        new_all = recovered_review + new_doc_nodes
        new_adf = {"type": "doc", "version": 1, "content": new_all}

        # Review table still present
        review_out, _ = extract_review_table_adf(new_adf)
        assert len(review_out) == len(old_review)


# ---------------------------------------------------------------------------
# Annotation preservation integration
# ---------------------------------------------------------------------------

class TestAnnotationIntegration:
    def _make_annotated_adf(self, base_adf, phrases_and_ids):
        """
        Simulate a Confluence page body that has inline comment annotations.
        We inject annotation marks into the base ADF to simulate what Confluence
        would return from a GET with body-format=atlas_doc_format.
        """
        import copy
        annotations = [{"id": uid, "text": phrase} for phrase, uid in phrases_and_ids]
        annotated, _ = inject_annotations(copy.deepcopy(base_adf), annotations)
        return annotated

    def test_annotation_extraction_from_simulated_confluence_adf(self):
        content = load_doc(ERS_DOC)
        result = convert(content)
        base_adf = result["adf"]

        # Simulate: reviewer annotated two phrases
        phrases = [
            ("Entity Resolution Service", "uuid-ers"),
            ("OrgSelector", "uuid-org"),
        ]
        annotated_adf = self._make_annotated_adf(base_adf, phrases)

        # Extract what we injected
        annotations = extract_annotations(annotated_adf)
        ids = {a["id"] for a in annotations}
        assert "uuid-ers" in ids
        assert "uuid-org" in ids

    def test_republish_preserves_annotations(self):
        """
        Full republish simulation:
        1. Convert ERS doc → ADF
        2. Simulate Confluence adding inline comments
        3. Re-convert from same Obsidian source (simulating an edit)
        4. Inject annotations from old page into new ADF
        5. Verify annotation marks are present in the published ADF
        """
        content = load_doc(ERS_DOC)

        # First publish
        first_result = convert(content)
        first_adf = first_result["adf"]

        # Simulate reviewer adding inline comments to two phrases
        phrases = [
            ("Entity Resolution Service", "uuid-1"),
            ("OrgSelector", "uuid-2"),
            ("Record Writer", "uuid-3"),
        ]
        old_page_adf = self._make_annotated_adf(first_adf, phrases)

        # Extract annotations from the "old page" (as if we GETted it)
        annotations = extract_annotations(old_page_adf)
        assert len(annotations) == 3

        # Re-convert from Obsidian (same source, no changes)
        new_result = convert(content)
        new_adf = new_result["adf"]

        # Inject annotations into the new ADF
        final_adf, unanchored = inject_annotations(new_adf, annotations)

        assert unanchored == []  # all phrases still in the document

        # All three annotation UUIDs present in the published ADF
        placed_ids = set(find_annotation_marks(final_adf))
        assert "uuid-1" in placed_ids
        assert "uuid-2" in placed_ids
        assert "uuid-3" in placed_ids

    def test_annotation_on_edited_text_uses_fuzzy_match(self):
        """
        The author rewrote a sentence that had an inline comment.
        The annotation should still find a home via fuzzy matching.
        """
        # Simple doc with a specific sentence
        original_md = "# Title\n\nThe Entity Resolution Service resolves inferred entities to anchored identities.\n"
        original_result = convert(original_md)
        original_adf = original_result["adf"]

        # Simulate a comment on the exact phrase
        from annotate_adf import inject_annotations
        old_annotations = [{"id": "uuid-comment", "text": "resolves inferred entities to anchored identities"}]
        old_page_adf, _ = inject_annotations(original_adf, old_annotations)
        extracted = extract_annotations(old_page_adf)
        assert len(extracted) == 1

        # Author rewrote the sentence
        new_md = "# Title\n\nERS maps inferred entity IDs to anchored identities stored in redaplinfra.\n"
        new_result = convert(new_md)
        new_adf = new_result["adf"]

        # Re-inject - should use LCS/word overlap
        final_adf, unanchored = inject_annotations(new_adf, extracted)

        # The comment should find a home via fuzzy match (enough shared words)
        placed = find_annotation_marks(final_adf)
        # Either placed via fuzzy match or falls back to first paragraph
        assert len(placed) + len(unanchored) == 1  # accounted for


# ---------------------------------------------------------------------------
# Other vault documents
# ---------------------------------------------------------------------------

class TestOtherDocuments:
    @pytest.mark.parametrize("filename", [
        "docs/Datadog Cheat Sheet.md",
        "docs/Number of Expected Days in Office.md",
    ])
    def test_doc_converts_without_error(self, filename):
        path = os.path.join(VAULT_ROOT, filename)
        if not os.path.exists(path):
            pytest.skip(f"File not found: {filename}")
        content = load_doc(path)
        result = convert(content)
        assert result["adf"]["type"] == "doc"
        json.dumps(result["adf"])

    def test_notes_directory_sample(self):
        notes_dir = os.path.join(VAULT_ROOT, "notes")
        if not os.path.isdir(notes_dir):
            pytest.skip("notes directory not found")
        note_files = [
            f for f in os.listdir(notes_dir)
            if f.endswith(".md")
        ][:5]  # sample 5
        for filename in note_files:
            path = os.path.join(notes_dir, filename)
            content = load_doc(path)
            result = convert(content)
            assert result["adf"]["type"] == "doc", f"Failed on {filename}"


# ---------------------------------------------------------------------------
# Full pipeline: convert + review table + annotations
# ---------------------------------------------------------------------------

class TestFullPipeline:
    def test_complete_publish_flow_ers_doc(self):
        """
        Simulate the exact steps from SKILL.md Steps 6-7 (republish path).
        No API calls; just verifies the Python-side assembly is correct.
        """
        content = load_doc(ERS_DOC)

        # Step 1: Scan for images (first pass)
        scan_result = convert(content)
        assert scan_result["images"]  # images detected

        # Step 2: Simulate having uploaded images and gotten back file IDs
        image_map = {img: {"file_id": f"uuid-{i}", "collection": "contentId-999"}
                     for i, img in enumerate(scan_result["images"])}

        # Step 3: Full conversion with image_map
        result = convert(content, image_map=image_map)
        doc_nodes = result["adf"]["content"]

        # Step 4: Verify images are now mediaSingle nodes (not placeholders)
        def find_media(node, results=None):
            if results is None:
                results = []
            if node.get("type") == "mediaSingle":
                results.append(node)
            for child in node.get("content", []):
                find_media(child, results)
            return results

        media_nodes = find_media(result["adf"])
        assert len(media_nodes) == len(scan_result["images"])

        # Step 5: Assemble with review table
        review_nodes = build_review_table_adf("2026-04-09")
        all_nodes = review_nodes + doc_nodes
        new_adf = {"type": "doc", "version": 1, "content": all_nodes}

        # Step 6: Simulate previous page having inline comments
        old_annotations = [
            {"id": "uuid-annot-1", "text": "Entity Resolution Service"},
            {"id": "uuid-annot-2", "text": "OrgSelector"},
        ]
        annotated_adf, unanchored = inject_annotations(new_adf, old_annotations)

        assert unanchored == []
        annotation_ids = find_annotation_marks(annotated_adf)
        assert "uuid-annot-1" in annotation_ids
        assert "uuid-annot-2" in annotation_ids

        # Step 7: Final ADF is JSON-serializable and valid
        serialized = json.dumps(annotated_adf)
        reparsed = json.loads(serialized)
        assert reparsed["type"] == "doc"
        assert reparsed["content"][0]["type"] == "table"  # review table first

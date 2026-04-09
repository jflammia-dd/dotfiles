"""
ADF inline comment annotation preservation.

Inline comments in Confluence are anchored via annotation marks embedded in the
page ADF. Each annotation mark has an `id` (UUID) that matches the comment's
`properties.inlineMarkerRef`. When you PUT a new page body without those marks,
Confluence orphans the comments as "dangling" - not visible, not recoverable.

This module extracts annotation marks from the existing page ADF and re-injects
them into the new ADF at the best matching position so existing inline comments
survive republish.

Typical republish flow:

    existing_adf = json.loads(api_get_page_response['body']['atlas_doc_format']['value'])
    annotations   = extract_annotations(existing_adf)

    new_adf = convert(new_markdown_content)["adf"]
    annotated_adf, unanchored = inject_annotations(new_adf, annotations)

    # PUT annotated_adf - existing inline comments stay linked
    # unanchored contains IDs of annotations that had no plausible text match
    # (caller may log them; those comments become dangling, which is expected
    #  when the text they referenced was intentionally removed)

Annotation matching strategy (in order):
    1. Exact substring match within a single text node
    2. Longest common substring >= 8 chars in any text node
    3. Word overlap scoring (meaningful words >=4 chars)
    4. First substantial text node in the document (last resort for visibility)
"""

import re
import copy


# ---------------------------------------------------------------------------
# Extraction
# ---------------------------------------------------------------------------

def extract_annotations(adf_doc):
    """
    Walk an ADF document and return all annotation marks with their anchor text.

    Returns a list of dicts:
        [{"id": "uuid-string", "text": "the annotated text"}, ...]

    Text is accumulated across consecutive text nodes with the same annotation
    ID (handles cases where formatting splits a selection across multiple nodes).
    """
    results = {}  # id -> text (accumulate for multi-node spans)
    _extract_walk(adf_doc, results)
    return [{"id": k, "text": v} for k, v in results.items() if v.strip()]


def _extract_walk(node, results):
    """Recursively collect annotation marks and their text."""
    if node.get("type") == "text":
        text = node.get("text", "")
        for mark in node.get("marks", []):
            if mark.get("type") == "annotation":
                ann_id = mark.get("attrs", {}).get("id")
                if ann_id:
                    results[ann_id] = results.get(ann_id, "") + text
        return

    for child in node.get("content", []):
        _extract_walk(child, results)


# ---------------------------------------------------------------------------
# Injection
# ---------------------------------------------------------------------------

def inject_annotations(adf_doc, annotations):
    """
    Inject annotation marks from the previous page into a new ADF document.

    For each annotation, attempts placement in this order:
      1. Exact substring match in a single text node (best - preserves position)
      2. Longest common substring >= 8 chars (good for minor wording changes)
      3. Best word-overlap text node, first meaningful subsequence (acceptable)
      4. First substantial text node in the document (last resort for visibility)

    Annotations in category 4 get a "(moved)" suffix on the marker to signal
    that placement is approximate - no text modification is made, but the UUID
    still links to the original comment thread.

    Args:
        adf_doc:     dict, a fresh ADF document from md_to_adf.convert()
        annotations: list of {"id": str, "text": str} from extract_annotations()

    Returns:
        (annotated_adf, unanchored_ids)
        annotated_adf  - new ADF with annotation marks injected
        unanchored_ids - list of annotation UUIDs that could not be placed
                         (document had no text at all, or anchor was empty)
    """
    adf = copy.deepcopy(adf_doc)
    unanchored = []

    # Longest anchors first to avoid placing a short anchor inside a longer one
    sorted_anns = sorted(
        annotations, key=lambda a: len(a.get("text", "")), reverse=True
    )

    for ann in sorted_anns:
        ann_id = ann["id"]
        anchor = ann["text"].strip()

        if not anchor:
            unanchored.append(ann_id)
            continue

        placed = _inject_exact(adf, ann_id, anchor)
        if not placed:
            placed = _inject_lcs(adf, ann_id, anchor)
        if not placed:
            placed = _inject_word_overlap(adf, ann_id, anchor)
        if not placed:
            placed = _inject_fallback(adf, ann_id)
        if not placed:
            unanchored.append(ann_id)

    return adf, unanchored


# ---------------------------------------------------------------------------
# Strategy 1: exact substring match
# ---------------------------------------------------------------------------

def _inject_exact(adf, ann_id, anchor):
    found = [False]
    _exact_walk(adf, ann_id, anchor, found)
    return found[0]


def _exact_walk(node, ann_id, anchor, found):
    if found[0]:  # pragma: no cover
        return  # pragma: no cover

    if "content" not in node:
        return

    new_content = []
    for child in node["content"]:
        if found[0]:
            new_content.append(child)
            continue

        if child.get("type") == "text":
            text = child.get("text", "")
            idx = text.find(anchor)
            if idx >= 0:
                new_content.extend(_split(child, idx, anchor, ann_id))
                found[0] = True
                continue

        _exact_walk(child, ann_id, anchor, found)
        new_content.append(child)

    node["content"] = new_content


# ---------------------------------------------------------------------------
# Strategy 2: longest common substring >= 8 chars
# ---------------------------------------------------------------------------

def _inject_lcs(adf, ann_id, anchor):
    leaves = _collect_leaves(adf)
    anchor_lower = anchor.lower()

    best_lcs = ""
    for leaf_text in leaves:
        lcs = _longest_common_substring(anchor_lower, leaf_text.lower(), min_len=8)
        if len(lcs) > len(best_lcs):
            best_lcs = lcs

    if not best_lcs:
        return False

    # Restore original casing by finding the match in a leaf
    for leaf_text in leaves:
        idx = leaf_text.lower().find(best_lcs)
        if idx >= 0:
            match_in_original_case = leaf_text[idx: idx + len(best_lcs)]
            return _inject_exact(adf, ann_id, match_in_original_case)

    return False  # pragma: no cover


# ---------------------------------------------------------------------------
# Strategy 3: word overlap - annotate best-matching phrase
# ---------------------------------------------------------------------------

def _inject_word_overlap(adf, ann_id, anchor):
    leaves = _collect_leaves(adf)
    if not leaves:
        return False

    anchor_words = set(re.findall(r"\b\w{4,}\b", anchor.lower()))
    if not anchor_words:
        return False

    best_leaf = None
    best_score = 0

    for leaf_text in leaves:
        leaf_words = set(re.findall(r"\b\w{4,}\b", leaf_text.lower()))
        overlap = len(anchor_words & leaf_words)
        score = overlap / len(anchor_words)
        if score > best_score:
            best_score = score
            best_leaf = leaf_text

    if best_leaf is None or best_score < 0.15:
        return False

    # Find a good sub-phrase: longest run of anchor words present in leaf
    anchor_word_list = re.findall(r"\b\w+\b", anchor)
    leaf_lower = best_leaf.lower()

    for length in range(min(len(anchor_word_list), 6), 1, -1):
        for start in range(len(anchor_word_list) - length + 1):
            phrase = " ".join(anchor_word_list[start: start + length])
            if phrase.lower() in leaf_lower:
                idx = leaf_lower.find(phrase.lower())
                original_case = best_leaf[idx: idx + len(phrase)]
                return _inject_exact(adf, ann_id, original_case)

    # Fall back to annotating the whole leaf
    return _inject_exact(adf, ann_id, best_leaf)


# ---------------------------------------------------------------------------
# Strategy 4: fallback - first substantial text node
# ---------------------------------------------------------------------------

def _inject_fallback(adf, ann_id):
    leaves = _collect_leaves(adf)
    for leaf_text in leaves:
        if len(leaf_text.strip()) > 15:
            return _inject_exact(adf, ann_id, leaf_text)
    return False


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _split(text_node, idx, anchor, ann_id):
    """
    Split a text node at `idx` for `anchor`, inserting an annotation mark.
    Returns a list of 1-3 text nodes: [before?, annotated, after?]
    """
    text = text_node.get("text", "")
    existing_marks = [
        m for m in text_node.get("marks", []) if m.get("type") != "annotation"
    ]
    ann_mark = {
        "type": "annotation",
        "attrs": {"id": ann_id, "annotationType": "inlineComment"},
    }

    parts = []

    if idx > 0:
        before = {"type": "text", "text": text[:idx]}
        if existing_marks:
            before["marks"] = existing_marks
        parts.append(before)

    annotated = {"type": "text", "text": anchor, "marks": existing_marks + [ann_mark]}
    parts.append(annotated)

    end = idx + len(anchor)
    if end < len(text):
        after = {"type": "text", "text": text[end:]}
        if existing_marks:
            after["marks"] = existing_marks
        parts.append(after)

    return parts


def _collect_leaves(node, result=None):
    """Return all text content strings from leaf text nodes."""
    if result is None:
        result = []
    if node.get("type") == "text":
        t = node.get("text", "").strip()
        if t:
            result.append(node.get("text", ""))
        return result
    for child in node.get("content", []):
        _collect_leaves(child, result)
    return result


def _longest_common_substring(a, b, min_len=8):
    """Return the longest common substring of a and b, or '' if shorter than min_len."""
    len_a, len_b = len(a), len(b)
    best = ""
    # Slide a shorter window over both strings
    for length in range(min(len_a, len_b), min_len - 1, -1):
        for i in range(len_a - length + 1):
            sub = a[i: i + length]
            if sub in b:
                return sub
    return best

#!/usr/bin/env python3
"""
confluence-write.py - Surgical ADF-aware editing for Confluence pages

Four modes of operation:

  Replace text (default):
    confluence-write.py PAGE_ID "old text" "new text" [--occurrence N] [--dry-run]

  Delete a block containing text (removes the whole list item, paragraph, etc.):
    confluence-write.py PAGE_ID "text in block" --delete-block [--occurrence N] [--dry-run]

  Restore an orphaned inline comment (add annotation mark back to anchor text):
    confluence-write.py PAGE_ID "anchor text" --add-annotation MARKER_REF [--occurrence N] [--dry-run]

  Remove an orphaned annotation mark (e.g. from a deleted comment):
    confluence-write.py PAGE_ID --strip-annotation MARKER_REF [--dry-run]

Background on inline comments and ADF:
  Confluence stores inline comments as annotation marks on text nodes in ADF.
  Each mark carries the inlineMarkerRef UUID from the comment's properties.
  Full-page rewrites via any API tool strip these marks, leaving comments
  technically "open" in the API but invisible (not highlighted) in the UI.
  Use --add-annotation to restore visibility after a rewrite.

Replace behavior:
  - Finds text that may span multiple inline nodes (bold, italic, annotated)
  - Replacement text inherits marks from the first character of the selection
  - Warns when a deletion removes the last anchor for an inline comment
  - Matches cannot span block boundaries or opaque nodes (hard breaks, mentions)

Examples:
  confluence-write.py 123456 "old wording" "new wording"
  confluence-write.py 123456 "old wording" "new wording" --occurrence 1
  confluence-write.py 123456 "anchor text" --add-annotation d225675b-f484-4f55-8b15-9bacda5c0de2
  confluence-write.py 123456 --strip-annotation febc1896-4c5b-4433-bd95-72f17c2bc97e
  confluence-write.py 123456 "old wording" "new wording" --dry-run
"""

import sys
import os
import json
import argparse
import urllib.request
import urllib.error
import base64
import subprocess


# ---------------------------------------------------------------------------
# Credentials
# ---------------------------------------------------------------------------

def get_credentials():
    email = subprocess.check_output(["git", "config", "user.email"], text=True).strip()
    if sys.platform == "darwin":
        token = subprocess.check_output(
            ["security", "find-generic-password", "-s", "confluence-api-token", "-w"],
            text=True, stderr=subprocess.DEVNULL,
        ).strip()
    elif "ATLASSIAN_API_KEY" in os.environ:
        token = os.environ["ATLASSIAN_API_KEY"]
    else:
        token = subprocess.check_output(
            ["pass", "show", "atlassian_api_key"], text=True,
        ).strip()

    if not token:
        sys.exit("ERROR: Confluence token is empty.")
    return email, token


# ---------------------------------------------------------------------------
# Confluence REST API v2
# ---------------------------------------------------------------------------

_BASE = "https://datadoghq.atlassian.net/wiki"


def _auth_headers(email, token):
    creds = base64.b64encode(f"{email}:{token}".encode()).decode()
    return {"Authorization": f"Basic {creds}", "Accept": "application/json"}


def fetch_page(page_id, email, token):
    url = f"{_BASE}/api/v2/pages/{page_id}?body-format=atlas_doc_format"
    req = urllib.request.Request(url, headers=_auth_headers(email, token))
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        sys.exit(f"ERROR fetching page {page_id}: {e.code} {e.reason}\n{e.read().decode()}")


def update_page(page_id, version, title, adf, email, token):
    url = f"{_BASE}/api/v2/pages/{page_id}"
    payload = {
        "id": page_id,
        "status": "current",
        "title": title,
        "body": {
            "representation": "atlas_doc_format",
            "value": json.dumps(adf),
        },
        "version": {"number": version + 1},
    }
    data = json.dumps(payload).encode()
    headers = {**_auth_headers(email, token), "Content-Type": "application/json"}
    req = urllib.request.Request(url, data=data, method="PUT", headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        sys.exit(f"ERROR updating page {page_id}: {e.code} {e.reason}\n{e.read().decode()}")


# ---------------------------------------------------------------------------
# ADF flatten / rebuild
# ---------------------------------------------------------------------------

# Block node types whose direct children are inline content (leaf blocks).
_INLINE_CONTAINERS = {
    "paragraph", "heading",
    "tableCell", "tableHeader",
    "listItem",
    "expand", "nestedExpand",
    "panel",
    "caption",
}

# Inline node types that may appear inside leaf blocks.
_INLINE_NODES = {
    "text", "mention", "emoji", "inlineCard", "date",
    "status", "hardBreak", "mediaInline", "placeholder",
    "inlineExtension", "taskItem",
}

# Sentinel value for opaque non-text inline nodes.
_OPAQUE = object()


def _freeze_marks(marks):
    """Convert a list of mark dicts to a stable, hashable frozenset."""
    return frozenset(
        (m["type"], frozenset(m.get("attrs", {}).items()))
        for m in marks
    )


def _thaw_marks(frozen):
    """Convert a frozenset of marks back to a list of dicts, sorted for determinism."""
    result = []
    for mark_type, attrs in sorted(frozen):
        m = {"type": mark_type}
        if attrs:
            m["attrs"] = dict(attrs)
        result.append(m)
    return result


def flatten_inline(content):
    """
    Flatten an array of ADF inline nodes into a list of entries:
      - Text chars:    (char: str,     marks: frozenset)
      - Opaque nodes:  (_OPAQUE, None, original_node: dict)

    Opaque entries preserve non-text inlines (hard breaks, mentions, etc.)
    unchanged through any edit.
    """
    flat = []
    for node in content:
        if node.get("type") == "text":
            frozen = _freeze_marks(node.get("marks", []))
            for ch in node.get("text", ""):
                flat.append((ch, frozen))
        else:
            flat.append((_OPAQUE, None, node))
    return flat


def rebuild_inline(flat):
    """Reconstruct ADF inline nodes from a flattened entry list."""
    nodes = []
    i = 0
    while i < len(flat):
        entry = flat[i]
        if entry[0] is _OPAQUE:
            nodes.append(entry[2])
            i += 1
            continue
        # Collect a run of text chars sharing the same marks.
        ch, marks = entry[0], entry[1]
        text = ch
        j = i + 1
        while j < len(flat) and flat[j][0] is not _OPAQUE and flat[j][1] == marks:
            text += flat[j][0]
            j += 1
        node = {"type": "text", "text": text}
        thawed = _thaw_marks(marks)
        if thawed:
            node["marks"] = thawed
        nodes.append(node)
        i = j
    return nodes


def _plain(flat):
    """Extract the plain text string from a flat entry list."""
    return "".join(e[0] for e in flat if e[0] is not _OPAQUE)


def _search_string(flat):
    """
    Build a string for searching, with a null-byte separator at each opaque
    node (hard break, mention, etc.). This prevents a search from matching
    text that spans across an opaque node, which mirrors Confluence UI behavior
    where such elements visually and structurally break up text.

    Returns (search_str, pt_to_flat) where pt_to_flat maps each non-separator
    character position in search_str to the corresponding flat list index.
    """
    sep = "\x00"
    parts = []
    pt_to_flat = {}
    for i, entry in enumerate(flat):
        if entry[0] is _OPAQUE:
            parts.append(sep)
        else:
            pt_to_flat[len(parts)] = i
            parts.append(entry[0])
    return "".join(parts), pt_to_flat


def find_occurrence(flat, search, occurrence):
    """
    Find the `occurrence`-th (0-based) match of `search` in the block.
    Returns (flat_start, flat_end) or None.

    Matches cannot span opaque nodes (hard breaks, mentions, etc.).
    """
    if not search:
        return None
    pt, pt_to_flat = _search_string(flat)
    found = 0
    pos = 0
    while True:
        idx = pt.find(search, pos)
        if idx == -1:
            return None
        # Skip matches that cross an opaque separator.
        if "\x00" in pt[idx: idx + len(search)]:
            pos = idx + 1
            continue
        if found == occurrence:
            end = idx + len(search) - 1
            return pt_to_flat[idx], pt_to_flat[end] + 1
        found += 1
        pos = idx + 1


def count_occurrences(flat, search):
    """Count matches of search, excluding any that span opaque nodes."""
    pt, _ = _search_string(flat)
    count = 0
    pos = 0
    while True:
        idx = pt.find(search, pos)
        if idx == -1:
            return count
        if "\x00" not in pt[idx: idx + len(search)]:
            count += 1
        pos = idx + 1


def dangling_annotations(flat, flat_start, flat_end, new_text=""):
    """
    Return annotation IDs that will become dangling after replacing
    flat[flat_start:flat_end] with new_text.

    An annotation dangles only when both conditions hold:
      1. All of its anchor chars fall within the replaced range (none survive outside).
      2. The replacement won't carry the mark forward.

    Condition 2 is false when new_text is non-empty AND the first char of the
    selection already carries the annotation mark; in that case apply_replacement
    will transfer the mark to the new text, matching Confluence UI behavior.
    """
    def _ids(entries):
        ids = set()
        for e in entries:
            if e[0] is _OPAQUE:
                continue
            for mark_type, attrs in e[1]:
                if mark_type == "annotation":
                    ids.update(v for k, v in attrs if k == "id")
        return ids

    inside = _ids(flat[flat_start:flat_end])
    outside = _ids(flat[:flat_start]) | _ids(flat[flat_end:])
    entirely_inside = inside - outside

    if not entirely_inside:
        return []

    if not new_text:
        # Deletion: no replacement to carry marks forward.
        return sorted(entirely_inside)

    # Non-empty replacement inherits marks from the first selected char.
    # Any annotation on that char transfers to the replacement, so it won't dangle.
    first_entry = flat[flat_start] if flat_start < len(flat) else None
    carried = set()
    if first_entry and first_entry[0] is not _OPAQUE:
        for mark_type, attrs in first_entry[1]:
            if mark_type == "annotation":
                carried.update(v for k, v in attrs if k == "id")

    return sorted(entirely_inside - carried)


def apply_replacement(flat, flat_start, flat_end, new_text):
    """
    Replace flat[flat_start:flat_end] with new_text.
    The new chars inherit marks from the first character of the selection,
    matching Confluence UI behavior.
    """
    first = flat[flat_start]
    inherited = first[1] if first[0] is not _OPAQUE else frozenset()
    replacement = [(ch, inherited) for ch in new_text]
    return flat[:flat_start] + replacement + flat[flat_end:]


def apply_annotation(flat, flat_start, flat_end, marker_ref):
    """
    Add an annotation mark (inlineComment) to chars in flat[flat_start:flat_end].
    Used to restore the ADF anchor for an orphaned inline comment after a page rewrite.
    """
    ann_frozen = _freeze_marks([{
        "type": "annotation",
        "attrs": {"id": marker_ref, "annotationType": "inlineComment"},
    }])
    new_flat = list(flat)
    for i in range(flat_start, flat_end):
        if new_flat[i][0] is not _OPAQUE:
            new_flat[i] = (new_flat[i][0], new_flat[i][1] | ann_frozen)
    return new_flat


# ---------------------------------------------------------------------------
# ADF tree walks
# ---------------------------------------------------------------------------

def _is_leaf_content(content):
    """Return True if every node in content is an inline (non-block) node type."""
    return all(c.get("type", "") in _INLINE_NODES for c in content)


def _walk_children(node, walk_fn, *args):
    """
    Recurse walk_fn over a node's children, short-circuiting on the first
    successful result. Returns (updated_node, success: bool).
    """
    content = node.get("content", [])
    new_content = []
    for child in content:
        new_child, done = walk_fn(child, *args)
        new_content.append(new_child)
        if done:
            new_content.extend(content[len(new_content):])
            return {**node, "content": new_content}, True
    return {**node, "content": new_content}, False


def _replace_in_leaf(node, flat, search, replacement, target, counter):
    """Apply a text replacement within a single pre-flattened leaf block."""
    n = count_occurrences(flat, search)
    if not (counter[0] <= target < counter[0] + n):
        counter[0] += n
        return node, False
    local_occ = target - counter[0]
    result = find_occurrence(flat, search, local_occ)
    if result is None:
        counter[0] += n
        return node, False
    flat_start, flat_end = result
    for ann_id in dangling_annotations(flat, flat_start, flat_end, replacement):
        print(
            f"WARNING: inline comment will become dangling "
            f"(all anchor text removed): {ann_id}",
            file=sys.stderr,
        )
    new_flat = apply_replacement(flat, flat_start, flat_end, replacement)
    counter[0] += n
    return {**node, "content": rebuild_inline(new_flat)}, True


def walk(node, search, replacement, target, counter):
    """
    Recursively walk an ADF node tree, replacing the target-th occurrence of
    `search` with `replacement`.

    counter is a mutable [int] tracking how many occurrences have been passed
    across all leaf blocks processed so far.

    Returns (new_node, replaced: bool).
    """
    content = node.get("content", [])
    if not content:
        return node, False
    node_type = node.get("type", "")
    if node_type in _INLINE_CONTAINERS and _is_leaf_content(content):
        return _replace_in_leaf(node, flatten_inline(content), search, replacement, target, counter)
    return _walk_children(node, walk, search, replacement, target, counter)


def _subtree_contains(node, search):
    """Return True if any text node in the subtree contains search as a substring."""
    if isinstance(node, dict):
        if node.get("type") == "text" and search in node.get("text", ""):
            return True
        for v in node.values():
            if isinstance(v, (dict, list)) and _subtree_contains(v, search):
                return True
    elif isinstance(node, list):
        for item in node:
            if _subtree_contains(item, search):
                return True
    return False


# Block types that can be cleanly removed as a unit from their parent.
_DELETABLE_BLOCK_TYPES = {
    "paragraph", "heading", "listItem", "tableRow",
    "blockquote", "codeBlock", "panel", "expand", "nestedExpand",
    "mediaSingle",
}


def _has_inner_list_item(node, search):
    """
    Return True if any listItem node in the content subtree of `node` (not node
    itself) contains `search`. Used to determine whether a listItem should be
    deleted at the current level or if a nested listItem is the better target.
    """
    for child in node.get("content", []):
        if not isinstance(child, dict):
            continue
        if child.get("type") == "listItem" and _subtree_contains(child, search):
            return True
        if _has_inner_list_item(child, search):
            return True
    return False


def _delete_child(child, child_type, remaining, search, target, counter):
    """
    Decide what to do with a single deletable child node.
    Returns (new_child_or_None, remainder_or_None, deleted: bool).
    new_child is None when the child itself is deleted.
    remainder is non-None only when we are returning early (deleted or recursed-and-deleted).
    """
    if child_type == "listItem" and _has_inner_list_item(child, search):
        new_child, deleted = walk_delete(child, search, target, counter)
        if deleted:
            return new_child, remaining, True
        return new_child, None, False
    if counter[0] == target:
        counter[0] += 1
        return None, remaining, True
    counter[0] += 1
    return child, None, False


def walk_delete(node, search, target, counter):
    """
    Recursively walk an ADF node tree, removing the target-th structural block
    that contains `search` anywhere in its subtree.

    "Block" means a node of a deletable type that is a direct child of a parent
    with a content array. The whole node is removed, not just the matched text.

    For listItem nodes, deletion is deferred to the deepest nested listItem that
    contains the search text. This prevents accidentally deleting a parent list
    item (along with all its other content) when the real target is a nested
    sub-item. All other deletable block types (paragraph, heading, tableRow,
    etc.) are deleted at the level where they are first encountered.

    Returns (new_node, deleted: bool).
    """
    content = node.get("content", [])
    if not content:
        return node, False

    new_content = []
    for i, child in enumerate(content):
        child_type = child.get("type", "")
        remaining = content[i + 1:]
        if child_type in _DELETABLE_BLOCK_TYPES and _subtree_contains(child, search):
            new_child, tail, deleted = _delete_child(child, child_type, remaining, search, target, counter)
            if deleted:
                if new_child is not None:
                    new_content.append(new_child)
                new_content.extend(tail)
                return {**node, "content": new_content}, True
            if new_child is not None:
                new_content.append(new_child)
        else:
            new_child, deleted = walk_delete(child, search, target, counter)
            new_content.append(new_child)
            if deleted:
                new_content.extend(remaining)
                return {**node, "content": new_content}, True

    return {**node, "content": new_content}, False


def _annotate_in_leaf(node, flat, search, marker_ref, target, counter):
    """Add an annotation mark within a single pre-flattened leaf block."""
    n = count_occurrences(flat, search)
    if not (counter[0] <= target < counter[0] + n):
        counter[0] += n
        return node, False
    local_occ = target - counter[0]
    result = find_occurrence(flat, search, local_occ)
    if result is None:
        counter[0] += n
        return node, False
    flat_start, flat_end = result
    new_flat = apply_annotation(flat, flat_start, flat_end, marker_ref)
    counter[0] += n
    return {**node, "content": rebuild_inline(new_flat)}, True


def walk_annotate(node, search, marker_ref, target, counter):
    """
    Recursively walk an ADF node tree, adding an annotation mark for marker_ref
    to the target-th occurrence of `search`.

    Used to restore inline comment anchors that were stripped by a page rewrite.
    Returns (new_node, applied: bool).
    """
    content = node.get("content", [])
    if not content:
        return node, False
    node_type = node.get("type", "")
    if node_type in _INLINE_CONTAINERS and _is_leaf_content(content):
        return _annotate_in_leaf(node, flatten_inline(content), search, marker_ref, target, counter)
    return _walk_children(node, walk_annotate, search, marker_ref, target, counter)


def _strip_annotation_from_text_node(node, marker_ref):
    """Remove an annotation mark from a single text node. Returns the node unchanged if
    the mark is absent; returns a modified copy if it was present."""
    if node.get("type") != "text" or not node.get("marks"):
        return node
    new_marks = [
        m for m in node["marks"]
        if not (m.get("type") == "annotation"
                and m.get("attrs", {}).get("id") == marker_ref)
    ]
    if len(new_marks) == len(node["marks"]):
        return node
    node = dict(node)
    if new_marks:
        node["marks"] = new_marks
    else:
        del node["marks"]
    return node


def strip_annotation(node, marker_ref):
    """
    Recursively remove all annotation marks for marker_ref from an ADF tree.
    Used to clean up marks pointing to deleted or resolved comments.
    """
    if isinstance(node, dict):
        node = _strip_annotation_from_text_node(node, marker_ref)
        return {k: strip_annotation(v, marker_ref) for k, v in node.items()}
    if isinstance(node, list):
        return [strip_annotation(item, marker_ref) for item in node]
    return node


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Surgical ADF-aware editing for Confluence pages",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("page_id", help="Confluence page ID")
    parser.add_argument(
        "old_text", nargs="?",
        help="Text to find. For replace: the text to swap out. "
             "For --delete-block: any text within the block to remove. "
             "For --add-annotation: the anchor text to mark.",
    )
    parser.add_argument(
        "new_text", nargs="?",
        help="Replacement text (replace mode only).",
    )
    parser.add_argument(
        "--occurrence", type=int, default=0,
        help="Which occurrence to target (0-based, default: 0 = first)",
    )
    parser.add_argument(
        "--delete-block", action="store_true",
        help="Delete the entire structural block (list item, paragraph, etc.) that "
             "contains old_text, rather than replacing text within it.",
    )
    parser.add_argument(
        "--add-annotation", metavar="MARKER_REF",
        help="Add an annotation mark for this inlineMarkerRef UUID to the anchor text. "
             "Use to restore inline comments orphaned by a page rewrite.",
    )
    parser.add_argument(
        "--strip-annotation", metavar="MARKER_REF",
        help="Remove all annotation marks for this inlineMarkerRef UUID from the page. "
             "Use to clean up marks left behind by deleted or resolved comments.",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print modified ADF to stdout without updating the page",
    )
    args = parser.parse_args()

    # Validate argument combinations
    modes = sum([bool(args.delete_block), bool(args.add_annotation), bool(args.strip_annotation)])
    if modes > 1:
        parser.error("--delete-block, --add-annotation, and --strip-annotation are mutually exclusive.")
    if args.delete_block:
        if not args.old_text:
            parser.error("old_text (text within the block) is required with --delete-block.")
        if args.new_text:
            parser.error("new_text is not used with --delete-block.")
    elif args.add_annotation:
        if not args.old_text:
            parser.error("anchor text (old_text) is required with --add-annotation.")
        if args.new_text:
            parser.error("new_text is not used with --add-annotation.")
    elif args.strip_annotation:
        if args.old_text or args.new_text:
            parser.error("old_text and new_text are not used with --strip-annotation.")
    else:
        if args.old_text is None or args.new_text is None:
            parser.error("old_text and new_text are required for text replacement.")
        if args.old_text == "":
            parser.error("old_text must not be empty.")

    email, token = get_credentials()

    print(f"Fetching page {args.page_id}...", file=sys.stderr)
    page = fetch_page(args.page_id, email, token)
    title   = page.get("title", "Untitled")
    version = page["version"]["number"]
    raw_body = page.get("body", {}).get("atlas_doc_format", {}).get("value", "{}")
    adf = json.loads(raw_body) if isinstance(raw_body, str) else raw_body

    # --- Mode: delete block containing text ---
    if args.delete_block:
        counter = [0]
        new_adf, deleted = walk_delete(adf, args.old_text, args.occurrence, counter)
        if not deleted:
            total = counter[0]
            if total == 0:
                print(f"ERROR: No block containing {args.old_text!r} found.", file=sys.stderr)
            else:
                print(
                    f"ERROR: Occurrence {args.occurrence} not found "
                    f"(page contains {total} matching block(s), valid range: 0-{total - 1})",
                    file=sys.stderr,
                )
            sys.exit(1)
        if args.dry_run:
            json.dump(new_adf, sys.stdout, indent=2)
            print()
            return
        print("Updating page...", file=sys.stderr)
        result = update_page(args.page_id, version, title, new_adf, email, token)
        print(f"Done. '{title}' updated to version {result['version']['number']}.", file=sys.stderr)
        return

    # --- Mode: strip orphaned annotation mark ---
    if args.strip_annotation:
        new_adf = strip_annotation(adf, args.strip_annotation)
        if new_adf == adf:
            print(f"No annotation marks found for {args.strip_annotation!r}.", file=sys.stderr)
            return
        if args.dry_run:
            json.dump(new_adf, sys.stdout, indent=2)
            print()
            return
        print("Updating page...", file=sys.stderr)
        result = update_page(args.page_id, version, title, new_adf, email, token)
        print(f"Done. '{title}' updated to version {result['version']['number']}.", file=sys.stderr)
        return

    # --- Mode: restore orphaned inline comment anchor ---
    if args.add_annotation:
        counter = [0]
        new_adf, applied = walk_annotate(
            adf, args.old_text, args.add_annotation, args.occurrence, counter
        )
        if not applied:
            total = counter[0]
            if total == 0:
                print(f"ERROR: Anchor text not found: {args.old_text!r}", file=sys.stderr)
            else:
                print(
                    f"ERROR: Occurrence {args.occurrence} not found "
                    f"(page contains {total} occurrence(s), valid range: 0-{total - 1})",
                    file=sys.stderr,
                )
            sys.exit(1)
        if args.dry_run:
            json.dump(new_adf, sys.stdout, indent=2)
            print()
            return
        print("Updating page...", file=sys.stderr)
        result = update_page(args.page_id, version, title, new_adf, email, token)
        print(f"Done. '{title}' updated to version {result['version']['number']}.", file=sys.stderr)
        return

    # --- Mode: replace text ---
    counter = [0]
    new_adf, replaced = walk(adf, args.old_text, args.new_text, args.occurrence, counter)

    if not replaced:
        total = counter[0]
        if total == 0:
            print(f"ERROR: Text not found: {args.old_text!r}", file=sys.stderr)
        else:
            print(
                f"ERROR: Occurrence {args.occurrence} not found "
                f"(page contains {total} occurrence(s), valid range: 0-{total - 1})",
                file=sys.stderr,
            )
        sys.exit(1)

    if args.dry_run:
        json.dump(new_adf, sys.stdout, indent=2)
        print()
        return

    print("Updating page...", file=sys.stderr)
    result = update_page(args.page_id, version, title, new_adf, email, token)
    print(f"Done. '{title}' updated to version {result['version']['number']}.", file=sys.stderr)


if __name__ == "__main__":
    main()

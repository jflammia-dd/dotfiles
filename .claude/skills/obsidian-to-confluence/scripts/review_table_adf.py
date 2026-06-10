"""
Confluence Review Status Table: ADF builder and extractor.

The review section is placed at the top of the page and ends with a rule node
(horizontal divider). The rule acts as the sentinel that separates the review
section from the document content when republishing.

Convention on republish:
  - GET the existing page ADF
  - Call extract_review_table_adf() to recover the existing reviewer entries
  - Prepend those nodes (+ the rule) to the new document ADF nodes
  - PUT the updated page

If the page has no review section (first node is not a table), extract returns
empty review_nodes and all existing nodes as content_nodes.
"""

import datetime as _dt
import uuid

AUTHOR_ACCOUNT_ID = "712020:12e11061-cd2b-4940-acd0-af1b111dd526"
AUTHOR_DISPLAY_NAME = "@Justin Flammia"


def _date(date_str):
    """ADF date node from an ISO YYYY-MM-DD string. Confluence renders this as
    a styled date pill. The timestamp uses noon UTC so the rendered calendar
    date stays stable across viewer time zones.
    """
    y, m, d = (int(x) for x in date_str.split("-"))
    ts = int(_dt.datetime(y, m, d, 12, 0, 0, tzinfo=_dt.timezone.utc).timestamp() * 1000)
    return {"type": "date", "attrs": {"timestamp": str(ts)}}


def _mention(account_id, display_name):
    """ADF mention node (user @mention)."""
    return {
        "type": "mention",
        "attrs": {
            "id": account_id,
            "localId": str(uuid.uuid4()),
            "text": display_name,
        },
    }


def _text(t, marks=None):
    node = {"type": "text", "text": t}
    if marks:
        node["marks"] = marks
    return node


def _paragraph(content):
    return {"type": "paragraph", "content": content}


def _heading(level, text_content):
    return {
        "type": "heading",
        "attrs": {"level": level},
        "content": [_text(text_content)],
    }


def _table(rows):
    return {"type": "table", "content": rows}


def _table_row(cells):
    return {"type": "tableRow", "content": cells}


def _table_header(content):
    return {"type": "tableHeader", "attrs": {}, "content": [_paragraph(content)]}


def _table_cell(content):
    return {"type": "tableCell", "attrs": {}, "content": [_paragraph(content)]}


def _rule():
    return {"type": "rule"}


def build_review_table_adf(date_str):
    """
    Build the review status table section as a list of ADF nodes.

    Structure:
      - Author info table (2 rows: Author, Published)
      - "Review Status" heading
      - Reviewer sign-off table (4 cols: Reviewer, Status, Date, Comment)
        with one empty row and a how-to-use disclaimer row
      - Horizontal rule (acts as sentinel for extract_review_table_adf)

    Returns a list of ADF nodes to prepend to the document content.
    """
    # Author info table
    author_table = _table([
        _table_row([
            _table_header([_text("Author", marks=[{"type": "strong"}])]),
            _table_cell([_mention(AUTHOR_ACCOUNT_ID, AUTHOR_DISPLAY_NAME)]),
        ]),
        _table_row([
            _table_header([_text("Published", marks=[{"type": "strong"}])]),
            _table_cell([_date(date_str)]),
        ]),
    ])

    # Review Status heading
    review_heading = _heading(3, "Review Status")

    # Reviewer sign-off table
    # Status column: reviewers type "APPROVED", "IN REVIEW", or "CHANGES REQUESTED"
    # Confluence will auto-enrich if the user applies a status lozenge in the editor.
    header_row = _table_row([
        _table_header([_text("Reviewer", marks=[{"type": "strong"}])]),
        _table_header([_text("Status", marks=[{"type": "strong"}])]),
        _table_header([_text("Date", marks=[{"type": "strong"}])]),
        _table_header([_text("Comment", marks=[{"type": "strong"}])]),
    ])

    # One empty row for first reviewer to fill in
    empty_row = _table_row([
        _table_cell([_text("")]),
        _table_cell([_text("")]),
        _table_cell([_text("")]),
        _table_cell([_text("")]),
    ])

    # Disclaimer row spanning all 4 columns
    # ADF does not support colspan natively; use a single cell with colspan attr
    disclaimer_row = _table_row([
        {
            "type": "tableCell",
            "attrs": {"colspan": 4},
            "content": [_paragraph([
                _text("To review: add your name, set status to "),
                _text("APPROVED", marks=[{"type": "strong"}]),
                _text(", "),
                _text("IN REVIEW", marks=[{"type": "strong"}]),
                _text(", or "),
                _text("CHANGES REQUESTED", marks=[{"type": "strong"}]),
                _text(", then add the date and any comments."),
            ])],
        }
    ])

    reviewer_table = _table([header_row, empty_row, disclaimer_row])

    return [author_table, review_heading, reviewer_table, _rule()]


def extract_review_table_adf(adf_doc):
    """
    Extract the review section from an existing ADF document.

    The review section is identified as everything up to and including the
    first 'rule' node, provided that the first node is a table (the author
    info table). If the page does not have a review section, returns
    ([], all content nodes).

    Args:
        adf_doc: dict, the full ADF document (as returned by the Confluence v2
                 GET pages endpoint with body-format=atlas_doc_format, after
                 JSON-parsing the body.value string).

    Returns:
        (review_nodes, content_nodes): two lists of ADF node dicts.
        review_nodes includes the sentinel rule node.
        content_nodes is everything after the sentinel.
    """
    content = adf_doc.get("content", [])

    if not content or content[0].get("type") != "table":
        # No review section detected
        return [], content

    # Find the first rule node within the first 20 nodes
    for idx, node in enumerate(content[:20]):
        if node.get("type") == "rule":
            return content[: idx + 1], content[idx + 1 :]

    # Rule not found in first 20 nodes; no sentinel, treat as no review section
    return [], content

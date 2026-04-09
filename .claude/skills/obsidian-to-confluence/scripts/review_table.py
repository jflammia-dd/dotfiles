"""
Confluence Review Status Table — builder and extractor.

The review table is always placed at the top of the page.
A sentinel anchor (review-status-table-end) is injected after the table
so it can be reliably found and preserved on republish.
"""

SENTINEL_ANCHOR = "review-status-table-end"
AUTHOR_ACCOUNT_ID = "712020:12e11061-cd2b-4940-acd0-af1b111dd526"

def _status_macro(colour, title):
    """Generate a Confluence status lozenge macro."""
    return (
        f'<ac:structured-macro ac:name="status" ac:schema-version="1">'
        f'<ac:parameter ac:name="colour">{colour}</ac:parameter>'
        f'<ac:parameter ac:name="title">{title}</ac:parameter>'
        f'</ac:structured-macro>'
    )

def _user_mention(account_id):
    """Generate a Confluence user mention."""
    return f'<ac:link><ri:user ri:account-id="{account_id}"/></ac:link>'

def _sentinel():
    return (
        f'<ac:structured-macro ac:name="anchor" ac:schema-version="1">'
        f'<ac:parameter ac:name="">{SENTINEL_ANCHOR}</ac:parameter>'
        f'</ac:structured-macro>'
    )

def build_review_table(date_str):
    """
    Build a fresh review status table.

    The author is shown in a small attribution block above the reviewer table.
    This keeps the author distinct from reviewers — the author should not
    appear to be reviewing their own document.
    """
    disclaimer = None  # replaced by inline pills below
    # Author attribution block — separate from the reviewer sign-off table
    author_block = (
        '<table data-table-width="760">'
        '<colgroup>'
        '<col style="width:120px"/>'
        '<col style="width:640px"/>'
        '</colgroup>'
        '<tbody>'
        '<tr>'
        '<th style="background-color:#f0f1f2"><p><strong>Author</strong></p></th>'
        f'<td><p>{_user_mention(AUTHOR_ACCOUNT_ID)}</p></td>'
        '</tr>'
        '<tr>'
        '<th style="background-color:#f0f1f2"><p><strong>Published</strong></p></th>'
        f'<td><p>{date_str}</p></td>'
        '</tr>'
        '</tbody>'
        '</table>'
    )
    # Reviewer sign-off table — readers add themselves here
    reviewer_table = (
        '<h3><strong>Review Status</strong></h3>'
        '<table data-table-width="760">'
        '<colgroup>'
        '<col style="width:200px"/>'
        '<col style="width:140px"/>'
        '<col style="width:120px"/>'
        '<col style="width:300px"/>'
        '</colgroup>'
        '<tbody>'
        '<tr>'
        '<th style="background-color:#f0f1f2"><p><strong>Reviewer</strong></p></th>'
        '<th style="background-color:#f0f1f2"><p><strong>Status</strong></p></th>'
        '<th style="background-color:#f0f1f2"><p><strong>Date</strong></p></th>'
        '<th style="background-color:#f0f1f2"><p><strong>Comment</strong></p></th>'
        '</tr>'
        '<tr>'
        '<td><p></p></td><td><p></p></td><td><p></p></td><td><p></p></td>'
        '</tr>'
        '<tr>'
        f'<td colspan="4"><p>'
        '<em>To review: add your name, set status to</em> '
        f'{_status_macro("Blue", "IN REVIEW")} '
        f'{_status_macro("Green", "APPROVED")} '
        f'{_status_macro("Yellow", "CHANGES REQUESTED")} '
        '<em>, then add the date and any comments.</em>'
        '</p></td>'
        '</tr>'
        '</tbody>'
        '</table>'
    )
    return author_block + reviewer_table + f'{_sentinel()}' + '<hr/>'


def extract_review_table(page_body):
    """
    Extract the review status table section from an existing page body.
    Returns the table HTML (including the sentinel and trailing <hr/>)
    if found, or None if the page has no review table.
    """
    sentinel = SENTINEL_ANCHOR
    # Find the sentinel anchor in the body
    idx = page_body.find(sentinel)
    if idx == -1:
        return None
    # Find the end of the sentinel macro
    end_macro = page_body.find('</ac:structured-macro>', idx)
    if end_macro == -1:
        return None
    end_macro += len('</ac:structured-macro>')
    # Include the <hr/> that follows the sentinel
    rest = page_body[end_macro:]
    hr_idx = rest.find('<hr/>')
    if hr_idx != -1:
        end_pos = end_macro + hr_idx + len('<hr/>')
    else:
        end_pos = end_macro
    # The review section is everything from the start to end_pos
    return page_body[:end_pos]

if __name__ == '__main__':
    import sys
    if '--test' in sys.argv:
        table = build_review_table('2026-03-25')
        print("=== Generated table ===")
        print(table[:500], "...")
        extracted = extract_review_table(table + '<h1>Rest of page</h1>')
        print("\n=== Extracted (should match) ===")
        print(extracted[:200])
        print("\nMatch:", extracted == table)

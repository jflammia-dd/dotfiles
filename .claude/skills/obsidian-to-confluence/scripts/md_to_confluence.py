import re
import sys
import html

def convert_inline(text):
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<em>\1</em>', text)
    text = re.sub(r'`([^`\n]+)`', lambda m: f'<code>{html.escape(m.group(1))}</code>', text)
    # Internal anchor links: [text](#anchor) -> ac:link macro
    def replace_link(m):
        label, href = m.group(1), m.group(2)
        if href.startswith('#'):
            anchor = href[1:]
            return (
                f'<ac:link ac:anchor="{anchor}">'
                f'<ac:plain-text-link-body><![CDATA[{label}]]></ac:plain-text-link-body>'
                f'</ac:link>'
            )
        # Confluence page link → native ri:page reference
        # Uses ri:content-title + ri:space-key (NOT ri:content-id, which Confluence silently drops)
        # Fetches the exact title via API using the page ID in the URL
        import re as _re, urllib.request as _req, json as _json, base64 as _b64, subprocess as _sp
        m2 = _re.search(r'datadoghq\.atlassian\.net/wiki/spaces/([^/]+)/pages/(\d+)', href)
        if m2:
            space_key, page_id = m2.group(1), m2.group(2)
            try:
                _email = _sp.run(['git','config','user.email'],capture_output=True,text=True).stdout.strip()
                _token = _sp.run(['security','find-generic-password','-s','confluence-api-token','-w'],capture_output=True,text=True).stdout.strip()
                _creds = _b64.b64encode(f'{_email}:{_token}'.encode()).decode()
                _r = _req.Request(
                    f'https://datadoghq.atlassian.net/wiki/rest/api/content/{page_id}',
                    headers={'Authorization': f'Basic {_creds}', 'Accept': 'application/json'})
                with _req.urlopen(_r) as _resp:
                    _d = _json.loads(_resp.read())
                    page_title = _d['title']
                return (
                    f'<ac:link>'
                    f'<ri:page ri:space-key="{space_key}" ri:content-title="{page_title}"/>'
                    f'<ac:plain-text-link-body><![CDATA[{label}]]></ac:plain-text-link-body>'
                    f'</ac:link>'
                )
            except Exception:
                pass  # Fall through to plain href if API call fails
        return f'<a href="{href}">{label}</a>'
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', replace_link, text)
    return text

def next_nonblank(lines, i):
    j = i
    while j < len(lines):
        if lines[j].strip():
            return j
        j += 1
    return -1

def is_list_item(line, kind):
    if kind == 'ol':
        return bool(re.match(r'^\d+\.\s+', line))
    if kind == 'ul':
        return bool(re.match(r'^[-*]\s+', line))
    return False

def convert_md_to_storage(content):
    # Strip YAML frontmatter
    content = re.sub(r'^---\n.*?\n---\n\n?', '', content, flags=re.DOTALL)

    # Strip Obsidian WARNING callout block (lines starting with "> ")
    content = re.sub(r'(?m)^> .*\n', '', content)

    # Obsidian anchor link → Confluence anchor link
    content = content.replace(
        '[[#Proposal Overview]]',
        '<ac:link ac:anchor="proposal-overview"><ac:plain-text-link-body><![CDATA[Proposal Overview]]></ac:plain-text-link-body></ac:link>'
    )

    # Obsidian RFC wikilink → plain prose (reworded)
    content = content.replace(
        'The full Entity Resolution design lives in [[RFC - Entity Resolution v1]], which is still in draft. Reading it is not required to review this proposal; it exists as broader context.',
        'The full Entity Resolution design lives in a separate RFC that is still in draft. Reading it is not required to review this proposal.'
    )

    lines = content.split('\n')
    output = []
    i = 0
    in_code_block = False
    code_lang = ''
    code_lines = []
    in_list = None
    pending_para_lines = []

    def flush_para():
        if pending_para_lines:
            text = ' '.join(pending_para_lines).strip()
            if text:
                output.append(f'<p>{convert_inline(text)}</p>')
            pending_para_lines.clear()

    def close_list():
        nonlocal in_list
        if in_list:
            output.append(f'</{in_list}>')
            in_list = None

    while i < len(lines):
        line = lines[i]

        if line.startswith('```') and not in_code_block:
            flush_para()
            close_list()
            code_lang = line[3:].strip()
            code_lines = []
            in_code_block = True
            i += 1
            continue

        if line.startswith('```') and in_code_block:
            code_content = '\n'.join(code_lines)
            if code_lang:
                output.append(
                    f'<ac:structured-macro ac:name="code">'
                    f'<ac:parameter ac:name="language">{html.escape(code_lang)}</ac:parameter>'
                    f'<ac:plain-text-body><![CDATA[{code_content}]]></ac:plain-text-body>'
                    f'</ac:structured-macro>'
                )
            else:
                output.append(
                    f'<ac:structured-macro ac:name="code">'
                    f'<ac:plain-text-body><![CDATA[{code_content}]]></ac:plain-text-body>'
                    f'</ac:structured-macro>'
                )
            in_code_block = False
            code_lang = ''
            code_lines = []
            i += 1
            continue

        if in_code_block:
            code_lines.append(line)
            i += 1
            continue

        if line.strip() == '---':
            flush_para()
            close_list()
            output.append('<hr/>')
            i += 1
            continue

        m = re.match(r'^(#{1,4})\s+(.+)$', line)
        if m:
            flush_para()
            close_list()
            level = len(m.group(1))
            text = convert_inline(m.group(2))
            anchor = re.sub(r'[^a-z0-9_]+', '-', m.group(2).lower()).strip('-')
            anchor_macro = (
                f'<ac:structured-macro ac:name="anchor">'
                f'<ac:parameter ac:name="">{anchor}</ac:parameter>'
                f'</ac:structured-macro>'
            )
            output.append(f'<h{level}>{anchor_macro}{text}</h{level}>')
            i += 1
            continue

        m = re.match(r'^(\d+)\.\s+(.+)$', line)
        if m:
            flush_para()
            if in_list != 'ol':
                close_list()
                output.append('<ol>')
                in_list = 'ol'
            item_text = convert_inline(m.group(2))
            j = i + 1
            while j < len(lines) and lines[j].startswith('   ') and not re.match(r'^\d+\.', lines[j].strip()):
                item_text += ' ' + convert_inline(lines[j].strip())
                j += 1
            output.append(f'<li><p>{item_text}</p></li>')
            i = j
            continue

        m = re.match(r'^[-*]\s+(.+)$', line)
        if m:
            flush_para()
            if in_list != 'ul':
                close_list()
                output.append('<ul>')
                in_list = 'ul'
            output.append(f'<li><p>{convert_inline(m.group(1))}</p></li>')
            i += 1
            continue

        # Markdown table: header row starts with '|', next non-blank line is separator
        if line.strip().startswith('|') and (i + 1 < len(lines)) and re.match(r'^\s*\|[\s\-:|]+\|', lines[i + 1]):
            flush_para()
            close_list()

            def parse_row(row_line):
                """Split a markdown table row into cells, stripping surrounding pipes."""
                row_line = row_line.strip()
                if row_line.startswith('|'):
                    row_line = row_line[1:]
                if row_line.endswith('|'):
                    row_line = row_line[:-1]
                return [cell.strip() for cell in row_line.split('|')]

            header_cells = parse_row(line)
            i += 1  # skip separator row
            i += 1  # advance past separator

            data_rows = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                data_rows.append(parse_row(lines[i]))
                i += 1

            table_html = ['<table><tbody>']
            table_html.append('<tr>')
            for cell in header_cells:
                table_html.append(f'<th><p>{convert_inline(cell)}</p></th>')
            table_html.append('</tr>')
            for row in data_rows:
                table_html.append('<tr>')
                for cell in row:
                    table_html.append(f'<td><p>{convert_inline(cell)}</p></td>')
                table_html.append('</tr>')
            table_html.append('</tbody></table>')
            output.append('\n'.join(table_html))
            continue

        if line.strip() == '':
            flush_para()
            if in_list:
                nxt = next_nonblank(lines, i + 1)
                if nxt == -1 or not is_list_item(lines[nxt], in_list):
                    close_list()
            i += 1
            continue

        if in_list:
            close_list()
        pending_para_lines.append(line.strip())
        i += 1

    flush_para()
    close_list()
    return '\n'.join(output)

if __name__ == '__main__':
    with open(sys.argv[1], 'r') as f:
        content = f.read()
    print(convert_md_to_storage(content))

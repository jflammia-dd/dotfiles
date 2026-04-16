#!/usr/bin/env bash
# work-os-check: fires at SessionStart.
# Scans project status pages for overdue waiting items and stale next actions.
# Outputs additionalContext if any alerts exist.

VAULT="$HOME/Documents/Datadog"
DOCS="$VAULT/docs"

command -v jq &>/dev/null || exit 0
[ -d "$DOCS" ] || exit 0

ALERTS=$(VAULT="$VAULT" uv run python3 - <<'PYEOF'
import os, re
from pathlib import Path
from datetime import date

vault_docs = Path(os.environ['VAULT']) / 'docs'
today = date.today()
alerts = []

for f in sorted(vault_docs.glob('*.md')):
    text = f.read_text(encoding='utf-8', errors='ignore')
    if 'project' not in text or 'active' not in text:
        continue

    parts = text.split('---', 2)
    if len(parts) < 3:
        continue
    fm = parts[1]

    title_m = re.search(r'^title:\s*(.+)', fm, re.MULTILINE)
    title = title_m.group(1).strip().strip('"') if title_m else f.stem

    whats = re.findall(r'what:\s*"?([^"\n]+)"?', fm)
    dues = re.findall(r'follow_up_if_no_response_by:\s*(\d{4}-\d{2}-\d{2})', fm)

    for i, due_str in enumerate(dues):
        try:
            due = date.fromisoformat(due_str)
            what = whats[i].strip()[:55] if i < len(whats) else 'unknown item'
            days_over = (today - due).days
            if days_over > 0:
                alerts.append(f"OVERDUE {days_over}d | {title}: {what}")
            elif days_over == 0:
                alerts.append(f"DUE TODAY | {title}: {what}")
        except ValueError:
            continue

    since_m = re.search(r'^next_action_since:\s*(\d{4}-\d{2}-\d{2})', fm, re.MULTILINE)
    urgency_m = re.search(r'^urgency:\s*(\S+)', fm, re.MULTILINE)
    if since_m and urgency_m:
        try:
            since = date.fromisoformat(since_m.group(1))
            urgency = urgency_m.group(1).strip()
            days_stale = (today - since).days
            if days_stale >= 5 and urgency not in ('deferred',):
                na_m = re.search(r'^next_action:\s*"?([^"\n]+)"?', fm, re.MULTILINE)
                na = na_m.group(1).strip()[:55] if na_m else 'unknown'
                alerts.append(f"STALE {days_stale}d | {title}: {na}")
        except ValueError:
            continue

for a in alerts[:8]:
    print(a)
PYEOF
)

[ -z "$ALERTS" ] && exit 0

COUNT=$(printf '%s\n' "$ALERTS" | wc -l | tr -d ' ')
MSG="## Work OS: ${COUNT} item(s) need attention

\`\`\`
${ALERTS}
\`\`\`

Run \`/now\` for full context and draft follow-ups."

jq -n --arg msg "$MSG" \
  '{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":$msg}}'

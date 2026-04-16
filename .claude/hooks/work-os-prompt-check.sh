#!/usr/bin/env bash
# work-os-prompt-check: fires on UserPromptSubmit.
# Silently checks for overdue waiting items. Only speaks up when something
# is past its follow_up_if_no_response_by date, at most once per hour.

VAULT="$HOME/Documents/Datadog"
DOCS="$VAULT/docs"
CACHE="$HOME/.claude/.wos-prompt-cache"

command -v jq &>/dev/null || exit 0
[ -d "$DOCS" ] || exit 0

# Check cooldown: suppress if cache is less than 60 minutes old
if [ -f "$CACHE" ]; then
    last=$(cat "$CACHE" 2>/dev/null || echo 0)
    now=$(date +%s)
    age=$((now - last))
    [ "$age" -lt 3600 ] && exit 0
fi

COUNT=$(VAULT="$VAULT" uv run python3 - <<'PYEOF'
import os, re
from pathlib import Path
from datetime import date

vault_docs = Path(os.environ['VAULT']) / 'docs'
today = date.today()
overdue = 0

for f in sorted(vault_docs.glob('*.md')):
    text = f.read_text(encoding='utf-8', errors='ignore')
    if 'project' not in text or 'active' not in text:
        continue
    parts = text.split('---', 2)
    if len(parts) < 3:
        continue
    fm = parts[1]
    dues = re.findall(r'follow_up_if_no_response_by:\s*(\d{4}-\d{2}-\d{2})', fm)
    for due_str in dues:
        try:
            if date.fromisoformat(due_str) < today:
                overdue += 1
        except ValueError:
            continue

print(overdue)
PYEOF
)

# Stay silent if nothing is overdue
[ -z "$COUNT" ] || [ "$COUNT" -eq 0 ] && exit 0

# Update cache timestamp
date +%s > "$CACHE"

WORD="item"
[ "$COUNT" -gt 1 ] && WORD="items"

MSG="Work OS: ${COUNT} overdue ${WORD}. Run \`/now\` for context and draft follow-ups."

jq -n --arg msg "$MSG" \
  '{"hookSpecificOutput":{"hookEventName":"UserPromptSubmit","additionalContext":$msg}}'

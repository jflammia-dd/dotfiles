#!/usr/bin/env bash
# Shows a Claude permission request in Bits's thought bubble and waits (up to
# 90s) for you to click Allow once / Always allow / Deny. Whatever you pick is
# sent back to Claude. If the pet is off or you don't click, Claude falls back
# to its own prompt.
INPUT=$(cat)

DECISION=$(curl --silent --max-time 90 \
  -H 'Content-Type: application/json' \
  --data "$INPUT" \
  http://127.0.0.1:4242/permission 2>/dev/null)

case "$DECISION" in
  allow)
    echo '{"hookSpecificOutput":{"hookEventName":"PermissionRequest","decision":{"behavior":"allow"}}}'
    ;;
  allow-always)
    # Persist the rule Claude suggested, then allow (so it won't re-prompt).
    BITS_INPUT="$INPUT" python3 - <<'PY' 2>/dev/null
import os, json
inp = json.loads(os.environ.get("BITS_INPUT", "{}"))
cwd = inp.get("cwd") or os.getcwd()
home = os.path.expanduser("~")
def target(dest):
    return {
        "localSettings": os.path.join(cwd, ".claude", "settings.local.json"),
        "projectSettings": os.path.join(cwd, ".claude", "settings.json"),
        "userSettings": os.path.join(home, ".claude", "settings.json"),
    }.get(dest)
for s in inp.get("permission_suggestions", []) or []:
    if s.get("type") != "addRules" or s.get("behavior") != "allow":
        continue
    p = target(s.get("destination"))
    if not p:
        continue
    try:
        with open(p) as f: data = json.load(f)
    except Exception:
        data = {}
    allow = data.setdefault("permissions", {}).setdefault("allow", [])
    for r in s.get("rules", []):
        tool, content = r.get("toolName", ""), r.get("ruleContent", "")
        entry = f"{tool}({content})" if content else tool
        if entry and entry not in allow:
            allow.append(entry)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w") as f: json.dump(data, f, indent=2)
PY
    echo '{"hookSpecificOutput":{"hookEventName":"PermissionRequest","decision":{"behavior":"allow"}}}'
    ;;
  deny)
    echo '{"hookSpecificOutput":{"hookEventName":"PermissionRequest","decision":{"behavior":"deny"}}}'
    ;;
  *)
    : # no decision — Claude shows its own prompt
    ;;
esac
exit 0

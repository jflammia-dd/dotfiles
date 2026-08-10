#!/usr/bin/env python3
"""commit-format-guard: checks a git commit subject against the format rules
in docs/Git Commit Message Standards.md (Datadog Obsidian vault):
`[TICKET]`/`[NOJIRA]` bracket, no trailing period, no `type(scope):` prefix,
50 char soft target / 72 hard cap.

Fires PreToolUse on Bash. Three commit-related hooks exist and each checks a
different thing:
  - git-commit-message-guard.sh: a message exists at all (blocks no -m/-F).
  - voice-git-gate.sh: prose style of the message (em dashes, Oxford commas).
  - this hook: the STRUCTURE of the subject line specifically.

Assumes a message is present, since git-commit-message-guard.sh runs first
and blocks the no-message case. Only looks at the first line of the message
(the subject); body content is out of scope here.

Escape hatch: export COMMIT_FORMAT_GATE_OFF=1 before launching Claude.
Rules: docs/Git Commit Message Standards.md in the Datadog Obsidian vault.
"""

import json
import os
import re
import shlex
import sys
from pathlib import Path

SOFT_LIMIT = 50
HARD_LIMIT = 72
BRACKET_RE = re.compile(r"^\[([A-Z][A-Z0-9]*-\d+|NOJIRA)\]")
TYPE_PREFIX_RE = re.compile(
    r"\b(feat|fix|docs|style|refactor|perf|test|chore|build|ci)(\([^)]*\))?!?:",
    re.IGNORECASE,
)


def emit_block(reason):
    print(json.dumps({"continue": False, "stopReason": reason}))
    sys.exit(0)


def emit_warning(text):
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "additionalContext": text}}))


def heredoc_body(cmd):
    m = re.search(r"<<-?\s*'?\"?(\w+)'?\"?\s*\n(.*?)\n\s*\1\s*$", cmd, re.S | re.M)
    return m.group(2) if m else None


def read_file(token, cwd):
    try:
        p = Path(token)
        if not p.is_absolute():
            p = Path(cwd or ".") / p
        return p.read_text()
    except OSError:
        return None


def flag_values(tokens, names):
    out = []
    for i, t in enumerate(tokens):
        for n in names:
            if t == n and i + 1 < len(tokens):
                out.append(tokens[i + 1])
            elif t.startswith(n + "="):
                out.append(t[len(n) + 1:])
    return out


def extract_subject(cmd, cwd):
    """First line of the commit message, whichever flag carried it."""
    try:
        tokens = shlex.split(cmd, comments=False)
    except ValueError:
        return None

    msgs = flag_values(tokens, ["-m", "--message"])
    if msgs:
        raw = msgs[0]
        if raw.lstrip().startswith("$("):
            # shlex captured the unexpanded `$(cat <<'EOF' ...)` substitution
            # itself, not what bash would actually pass at runtime. Recover
            # the real message from the heredoc body instead.
            body = heredoc_body(cmd)
            if body is not None:
                raw = body
        return raw.splitlines()[0] if raw.splitlines() else None

    files = flag_values(tokens, ["-F", "--file"])
    if files:
        content = heredoc_body(cmd) if files[0] == "-" else read_file(files[0], cwd)
        if content:
            lines = content.splitlines()
            return lines[0] if lines else None

    return None


def check(subject):
    """(hard_violations, warning) for a subject line."""
    hard = []

    if not BRACKET_RE.match(subject):
        hard.append(
            "Subject must start with a bracketed tag: `[TICKET-123]` or "
            "`[NOJIRA]`, e.g. `[SEC-1234] Fix nil pointer in session cleanup`."
        )

    if subject.rstrip().endswith("."):
        hard.append("Subject must not end with a trailing period.")

    if TYPE_PREFIX_RE.search(subject):
        hard.append(
            "Subject must not carry a `type(scope):` or `type:` prefix "
            "(feat/fix/refactor/etc). That convention was evaluated and "
            "rejected; use the bracketed tag alone."
        )

    length = len(subject)
    if length > HARD_LIMIT:
        hard.append(f"Subject is {length} chars, over the {HARD_LIMIT} hard cap. "
                     "This commit is probably not atomic. Split it rather than truncating.")

    warning = None
    if not hard and length > SOFT_LIMIT:
        warning = (f"Subject is {length} chars, over the {SOFT_LIMIT} char soft "
                    f"target (hard cap is {HARD_LIMIT}). Consider tightening it.")

    return hard, warning


def main():
    if os.environ.get("COMMIT_FORMAT_GATE_OFF"):
        return

    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return

    cmd = (payload.get("tool_input") or {}).get("command") or ""
    if not cmd or not re.search(r"(^|[;&|]\s*)(git|dd-git)\s+commit\b", cmd):
        return

    cwd = payload.get("cwd") or os.getcwd()
    subject = extract_subject(cmd, cwd)
    if not subject or not subject.strip():
        return  # No message found, fail open. git-commit-message-guard.sh owns that case.

    hard, warning = check(subject.strip())

    if hard:
        emit_block(
            "Blocked: this commit subject doesn't match "
            "docs/Git Commit Message Standards.md.\n\n"
            + "\n".join(f"- {v}" for v in hard)
            + f"\n\nSubject checked: {subject.strip()!r}"
        )
        return

    if warning:
        emit_warning(warning + " Rules: docs/Git Commit Message Standards.md")


if __name__ == "__main__":
    main()

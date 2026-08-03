#!/usr/bin/env python3
"""voice-git-gate: style-checks commit messages and PR text before they land.

Fires PreToolUse on Bash. Covers `git commit` messages and the body of
`gh pr create`, `gh pr edit`, `gh pr comment` and `gh pr review`. Every one of
these publishes prose that nothing else checks: prose-style-check.sh sees only
Write and Edit output, and voice-publish-gate.sh covers only Atlassian.

Distinct from git-commit-message-guard.sh, which enforces that a message exists
at all and says nothing about its content. That hook runs first and blocks the
no-message case, so this one only ever sees a message it can read.

Escape hatch: export VOICE_GATE_OFF=1 before launching Claude.
Rules and calibration: agents/skills/voice/SKILL.md
"""

import json
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path

CHECKER = Path.home() / ".claude/skills/voice/style_check.py"


def emit_block(reason):
    print(json.dumps({"continue": False, "stopReason": reason}))
    sys.exit(0)


def heredoc_body(cmd):
    """Content of a `<<'EOF' ... EOF` heredoc, which is how a multi-line commit
    message reaches the shell."""
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
    """Values for --flag X and --flag=X, in order."""
    out = []
    for i, t in enumerate(tokens):
        for n in names:
            if t == n and i + 1 < len(tokens):
                out.append(tokens[i + 1])
            elif t.startswith(n + "="):
                out.append(t[len(n) + 1:])
    return out


def jobs_for(cmd, cwd):
    """(target, body, subject, label) for each lintable piece of this command."""
    try:
        tokens = shlex.split(cmd, comments=False)
    except ValueError:
        return []

    out = []
    is_git_commit = re.search(r"(^|[;&|]\s*)(git|dd-git)\s+commit\b", cmd) is not None
    gh_pr = re.search(r"(^|[;&|]\s*)gh\s+pr\s+(create|edit|comment|review)\b", cmd)

    if is_git_commit:
        msgs = flag_values(tokens, ["-m", "--message"])
        files = flag_values(tokens, ["-F", "--file"])
        body = None
        if msgs:
            body = "\n\n".join(msgs)
        elif files and files[0] != "-":
            body = read_file(files[0], cwd)
        elif files and files[0] == "-":
            body = heredoc_body(cmd)
        if body:
            out.append(("commit", body, None, "commit message"))

    if gh_pr:
        sub = gh_pr.group(2)
        target = "pr" if sub in ("create", "edit") else "pr-comment"
        titles = flag_values(tokens, ["-t", "--title"])
        bodies = flag_values(tokens, ["-b", "--body"])
        bfiles = flag_values(tokens, ["-F", "--body-file"])
        body = bodies[0] if bodies else None
        if body is None and bfiles:
            body = heredoc_body(cmd) if bfiles[0] == "-" else read_file(bfiles[0], cwd)
        subject = titles[0] if titles and target == "pr" else None
        if body or subject:
            out.append((target, body or "", subject, f"gh pr {sub}"))

    return out


def lint(target, body, subject):
    cmd = [sys.executable, str(CHECKER), "--stdin", "--target", target]
    if subject:
        cmd += ["--subject", subject]
    r = subprocess.run(cmd, input=body, capture_output=True, text=True)
    return r.returncode, r.stdout.strip()


def main():
    if os.environ.get("VOICE_GATE_OFF"):
        return
    if not CHECKER.is_file():
        return  # Fail open. A broken linter must not block every commit.

    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return
    cmd = (payload.get("tool_input") or {}).get("command") or ""
    if not cmd:
        return
    cwd = payload.get("cwd") or os.getcwd()

    reports, warnings = [], []
    for target, body, subject, label in jobs_for(cmd, cwd):
        if not body.strip() and not subject:
            continue
        code, report = lint(target, body, subject)
        if not report:
            continue
        if code != 0:
            reports.append(f"--- {label} (target={target}) ---\n{report}")
        else:
            # Exit 0 with output means warnings only. Surface them rather than
            # dropping them, otherwise a warn-level rule is invisible.
            warnings.append(f"--- {label} (target={target}) ---\n{report}")

    if not reports and warnings:
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "additionalContext": "Style warnings on this command. Not blocking, but "
                                 "worth a look before it lands.\n\n" + "\n\n".join(warnings)}}))
        return

    if reports:
        emit_block(
            "Blocked: this text has not passed the style check. It is all newly "
            "written, so each error is yours to fix. Correct it and re-run the "
            "command.\n\n" + "\n\n".join(reports) +
            "\n\nWarnings do not block. If an error is a false positive, say so with "
            "the rule id rather than editing rules.json. Rules: agents/skills/voice/SKILL.md")


if __name__ == "__main__":
    main()

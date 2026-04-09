# Codex Delegate — Learnings Log

Append one entry per use (Step 8a). Patterns appearing in 3+ entries should
be promoted to SKILL.md (Step 8b/8c). Oldest entries at top, newest at bottom.

---

## 2026-03-19 — list markdown files in docs/ directory (initial test run)
- **Mode:** read-only
- **Domain skill loaded:** none
- **Code location:** local (/Users/justin.flammia/Documents/Datadog/docs)
- **Outcome:** success
- **What worked well:** prompt-via-file approach avoided all quoting issues; Codex self-validated count with wc -l
- **Friction or failure:** first run failed because `codex exec` requires a git repo by default — added `--skip-git-repo-check` to the script
- **Proposed improvement:** none (fix already applied)

---

## 2026-03-19 — dd-research pre-materialized verification prompt (integration test)
- **Mode:** read-only
- **Domain skill loaded:** none (fast path — pre-materialized prompt, Steps 2–4 skipped)
- **Code location:** local (/tmp/dd-research-test-doc.md + /Users/justin.flammia/dd/dd-source)
- **Outcome:** success
- **What worked well:** fast-path detection fired correctly on the three section headers; Codex ran the sed spot-check command verbatim and caught a genuine precision gap (trailing spaces in prefix literals); all 5 checks produced structured findings
- **Friction or failure:** none
- **Proposed improvement:** none

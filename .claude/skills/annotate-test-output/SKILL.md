---
name: annotate-test-output
description: Run a test command, capture its output, and produce a structured analysis of every scenario. For each subtest, the skill presents what is being tested, a table mapping each log line to its meaning, and a conclusion. A summary table appears at the end. Use this skill whenever the user wants to run a test and understand what the output means, walk through test results line by line, validate that a test exercises the right code paths, or explain structured log output to someone who did not write the test. Trigger on phrases like "run the test and explain", "annotate the output", "walk me through the test results", "show me what this test is proving" or similar.
---

## What this skill produces

For each subtest scenario:

1. **Scenario heading.** A paragraph describing what the test is trying to prove and what the expected outcome is.
2. **Log table.** A two-column markdown table. The left column contains the exact log line (structured log or `t.Logf` output, stripped of timestamps and source-file prefixes). The right column explains what that line tells the reader about the system's behaviour.
3. **Conclusion.** A paragraph stating what was demonstrated and whether the observed behaviour matches the intent.

After all scenarios: a summary table with one row per scenario showing pass/fail.

---

## Workflow

### Step 1: Determine the test command

If the user provided a test command, use it. If not, ask:

> "Which test should I run? For example: `go test -v -count=1 -run TestName .` from a specific directory."

Confirm the working directory if it matters.

### Step 2: Run the test and capture output

Run the command with Bash and capture all output (stdout and stderr combined). Use `2>&1`. Do not filter or truncate the output. The full log is the raw material for the analysis.

### Step 3: Parse the output into scenarios

Identify subtest boundaries using `=== RUN` and `--- PASS`/`--- FAIL` markers. Each `=== RUN ParentTest/subtest_name` line begins a new scenario. Collect all log lines between the start and end of each subtest, including structured log lines (lines beginning with a timestamp) and `t.Logf` output (lines with the `file:line:` prefix).

If the test has no subtests, treat the entire test as a single scenario.

### Step 4: For each scenario, produce the analysis

**Scenario heading.** Write one to three sentences covering what behaviour the scenario is designed to verify, what inputs or conditions are in play, and what the expected outcome is. Keep it factual and specific. Do not pad with generic language about "testing" or "verifying".

**Log table.** Strip timestamps (the leading ISO-8601 datetime) and source-file references (the `(file.go:NN)` segment) from structured log lines before putting them in the table. Keep the message name and all key=value fields. For `t.Logf` output, strip the `file:line:` prefix. Every log line that appears in the scenario's output gets a row. Do not skip lines because each one was emitted deliberately.

Explain what each log line tells the reader about the system, not what the words say. "The handler began processing the request" is not useful. "The handler received `org_id=1` and `idp_providers={google-workspace}`, confirming the planner will have these inputs when it selects strategies" is useful. Connect each line to the code path it represents.

**Conclusion.** One paragraph. State what the scenario demonstrated and confirm whether the observed behaviour matches what the scenario was designed to prove. If the test passed, say so directly. If there is anything notable in the output (unexpected states, edge cases hit, fields worth attention), name them.

### Step 5: Write the summary table

After all scenarios, write:

```
## Summary

| Scenario | Result |
|----------|--------|
| scenario name | PASS |
| scenario name | PASS |
```

Derive pass/fail from the `--- PASS` and `--- FAIL` markers in the raw output.

---

## Formatting rules

- Use `##` for the overall test name, `###` for each scenario heading.
- Table columns are "Log line" and "What it tells you".
- Keep table rows to one line each. If a log line carries many fields, describe the most significant ones and note that the remaining fields are present.
- The conclusion is prose, not a list.
- Do not invent explanations. If a log line's meaning is not clear from the surrounding code context, say so rather than guessing.
- Do not include raw timestamps in the final output. They add noise without value for this analysis.

---

## Example output shape

### Scenario: matching IdP selects a strategy

The org passes `google-workspace` as an IdP provider. The planner should recognise it and select `EmailExactStrategy`. With a strategy in the chain the handler fetches entities, runs the pipeline and produces resolutions across all four possible states.

| Log line | What it tells you |
|----------|-------------------|
| `resolve_begin … idp_providers={google-workspace} csp_providers={aws-cloudtrail}` | The request entered the handler with one IdP and one CSP configured. These are the inputs the planner will use. |
| `resolve_strategy_plan … within_trust={} cross_trust={EmailExactStrategy}` | The planner intersected `google-workspace` against its registry and selected `EmailExactStrategy`. Within-trust is empty because no CSP strategies are registered. |
| `resolve_fetch_start … source=entityrisk window=24h0m0s` | Because the chain is non-empty the handler proceeds to fetch inferred entities. |
| `resolve_complete … resolved=1 partial=3 ambiguous=1 unresolved=1` | All six entities were processed and all four resolution states appear. |

A recognised IdP provider causes the planner to select the appropriate strategy. The handler fetches entities, runs the full pipeline and produces differentiated resolution outcomes. All four states appear, confirming the pipeline executes end-to-end.

---

## Notes on structured log formats

This skill is format-agnostic. Adapt the parsing to whatever logging format the repo uses:

- **Zap / dd-source**: `YYYY-MM-DDTHH:MM:SS.NNNNNN-TZ INFO (file.go:NN) - message_name key=value …`
- **logrus**: `time="..." level=info msg="..." key=value …`
- **stdlib**: `YYYY/MM/DD HH:MM:SS message`
- **t.Logf output**: `    file_test.go:NN: message`

Strip the time and source prefix in all cases. Keep the message name and fields.

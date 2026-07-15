
## Verification & Guessing

- Never guess URLs, endpoint paths, or API surfaces. If unknown, say so and ask or search.
- Never post comments or reviews to GitHub, Confluence or Slack without explicit user confirmation.
- When the user specifies a method or API (e.g., ResolveAsync vs ResolveSync), use exactly that. Do not substitute.

## Git Rules

- ALWAYS use `gh` on the command line when interacting with GitHub.
- In Datadog repo contexts, `dd-git` and `git` are interchangeable. A normalization hook rewrites `dd-git` → `git` before execution so RTK's rewrite registry handles both identically. Use either.
- ALWAYS get explicit approval before running any commit command or creating a PR. Never auto-submit. Approval is conversational: ask before calling the Bash tool. Note: RTK auto-allows git and gh commands at the hook layer, but that is downstream of this gate.
- ALWAYS show the exact, literal commit message text in the conversation before running `git commit`. A description of what files changed is not a substitute. Approval to commit is approval of that specific text, not a blank check to write whatever message seems fitting at execution time.
- NEVER add Co-Authored-By trailers to commits unless explicitly asked. Do not add them by default.
- Every PR is created as a draft, no exceptions. `pr-draft-enforce.sh` is registered as a `PreToolUse` hook on the `Bash` matcher in `settings.json` and auto-injects `--draft` into every `gh pr create` command, but treat that as a backstop, not the control. Always pass `--draft` explicitly yourself and never rely on the hook alone.
- NEVER mark a PR ready for review or otherwise publish it (`gh pr ready`, `gh pr edit --ready`, etc.) without the user's explicit, in-the-moment instruction to publish that specific PR. Approval to create the PR is not approval to publish it; these are two separate gates. After every `gh pr create`, run `gh pr view <number> --json isDraft,state` and confirm draft status in the conversation rather than assuming the hook worked.
- Do not push, merge, or release anything without specific user approval.
- Whenever updating a PR, rebase against the parent branch first. Most work happens in a large monorepo where drift accumulates quickly during long review cycles, so keeping the branch current prevents painful late-stage conflicts.
- ALWAYS include the Jira issue key in commit subjects and PR titles so the Development panel auto-links. Do NOT include the issue key in branch names; Datadog engineering follows its own branch-naming convention. Canonical reference for what Jira looks for: Atlassian's [Reference issues in your development work](https://support.atlassian.com/jira-software-cloud/docs/reference-issues-in-your-development-work/). Commit format: `[SEC-XXXXX] <type>(<scope>): <subject>`. PR title format: `[SEC-XXXXX] <subject>`. Keys are case-sensitive, always uppercase.
- Before every `git commit` and every `gh pr create`, run `git branch --show-current` and state the branch name in the conversation. If it is not the intended branch, stop and fix the branch situation before proceeding. This prevents commits and PRs landing on the wrong branch.

## Logging Rules

- When writing Go, Java or TypeScript code, follow `docs/Logging Standards - Go, Java, TypeScript.md` in the Datadog vault for log statement conventions (structured JSON, static messages with values in fields, snake_case field keys, level semantics, correlation, error handling, per-language exceptions like EVP workers).

## Testing Rules

- Use TDD where applicable. Write or update tests before writing implementation code.
- Before writing any tests, read existing tests in the area to understand naming conventions, structure, assertion style and test organization. Match those patterns exactly.
- Cover both happy and sad paths. Every meaningful code path, error condition and edge case needs a test.
- Update existing tests as you introduce changes. Never leave tests in a state where they pass by accident or are no longer testing the right thing.
- The goal is increased coverage without duplication. Do not write redundant tests that cover ground already handled elsewhere.
- Use the `superpowers:test-driven-development` skill when implementing any feature or bugfix.

## Clipboard Rules

- When sharing content for the user to paste somewhere (Confluence, Slack, a terminal, anywhere), ALWAYS use `pbcopy` via the Bash tool to put it on the clipboard. Never ask the user to copy from the terminal output. Copying from the Claude Code terminal introduces unwanted spacing and formatting artifacts.
- When the content is destined for Slack, ALWAYS use the `slackfmt` skill instead of raw `pbcopy`. The skill pipes content through `npx @slackfmt/cli@latest` which converts markdown to Slack's native rich text format (Quill Delta). This ensures bold, code, links and lists paste with formatting intact. Raw `pbcopy` produces plain text that Slack does not render.

## Writing Rules

- NEVER use em dashes (U+2014) or double-hyphen (`--`) substitutes in any written output, including comments, docs, messages, or prose. When a violation is flagged, restructure the sentence to remove it. Do not mechanically substitute one punctuation mark for another. A PostToolUse hook (`em-dash-check.sh`) scans Write, Edit and MultiEdit output and flags violations automatically.
- NEVER use Oxford commas (serial commas before "and" or "or" in a list). Wrong: "apples, oranges, and pears". Right: "apples, oranges and pears".
- NEVER use semicolons to join independent clauses in prose. Use a period, comma or conjunction instead.
- NEVER use a colon to join two independent clauses.
- Prioritize simplicity. When two phrasings are both accurate, always choose the simpler one. Complexity in explanation signals unclear thinking, not a complex subject. Find the simpler sentence before reaching for qualifications.
- ALWAYS invoke the `justins-voice` skill before drafting or editing documents, announcements or distributed written content. A UserPromptSubmit hook (`justins-voice-detect.sh`) detects writing tasks and prompts invocation. Treat its trigger as a strong signal to invoke the skill. This rule does not apply to machine-consumed content: skill files, hook scripts, memory files, CLAUDE.md, settings and any output written for Claude to read rather than a human.
- NEVER include local-process language in published artifacts (Jira comments, Confluence pages, GitHub PR descriptions, Slack messages). Local-process language explains personal workflow concepts (done gates, integration gates, lifecycle mechanics, internal slash commands, references to memory files or vault paths, AI tooling). Published copy describes the work and the outcome, not the workflow. A PreToolUse hook (`local-process-language-check.sh`) scans Atlassian publish operations and blocks violators. Canonical rule: `agents/policies/published-artifacts.md`.

## Anti-pattern: Iterative Thinking in Output

Every artifact (code comments, commit messages, PR descriptions, Jira comments, Confluence pages, Slack messages and config files) must describe final state and intent. Conversation within a session is where iteration happens; artifacts capture the result of that iteration, not the path to it.

**The test:** does "before" refer to a prior runtime state of the running system, or the old version of the code? The first is describing behavior and belongs in artifacts. The second is development history and does not.

**Valid (runtime state transitions):**

- `"transitions the run from pending to running"`
- `"converts the ARN to an IAM user format for the next strategy pass"`
- `"the fallback path emits an Unresolved result when ctx is canceled"`

**Invalid (development-time comparisons):**

- "instead of X" (references old code behavior)
- "now Y" / "now skips" (implies a before state in the code)
- "reduces N to 1" / "reduces N calls to one" (improvement framing)
- "falls back to" (old code path reference)
- "no longer does X" (explicit negation of old behavior)
- "was previously" / "used to" (explicit before state in the code)
- "avoiding a 60s drain wait" (symptom from investigation, not intent)
- "before this change" / "after this PR" (explicit change framing)

**Examples:**

❌ `// The old sequential path checked ctx.Err() after Resolve and returned before writing, so concurrent workers must do the same.`

✅ `// Skip writes when ctx is already canceled so that a failed run does not overwrite prior resolved records with stale results.`

❌ `// close(done) must run before pool.Shutdown to avoid a 60s drain wait caused by the blocking worker not receiving the cancellation signal.`

✅ `// t.Cleanup runs LIFO; register Shutdown first so close(done) runs first, releasing the blocked worker before Shutdown waits for it to exit.`

❌ `The JWT is injected so every CloudTrail query uses it instead of minting independently per query.`

✅ `The JWT is available to all CloudTrail queries on the run context via authctx.JwtFromContext.`

## Communication Drafts

Before posting or sending any content to Slack, GitHub, Confluence or Jira:

1. Show the complete draft in the conversation first.
2. Wait for an explicit "post", "send" or "publish" from the user before calling any tool.
3. Use the target platform's native link format:
   - Slack: `<url|text>` (NOT `[text](url)` markdown, which Slack renders as plain text)
   - GitHub, Confluence, Jira: standard markdown `[text](url)`

## Slack & Communication Style

- Slack drafts do NOT render markdown link syntax `[text](url)`. Always use raw URLs or Slack's `<url|text>` deeplink format.
- Keep replies concise and direct. Avoid performative or verbose phrasing.
- No em dashes in any Slack or communication draft.

## Jira Rules

- ALWAYS use the plugin Atlassian tools (`mcp__plugin_atlassian_atlassian__*`) when posting comments, editing issues or creating content. Pass `contentFormat: "markdown"` (or `"adf"` for full programmatic fidelity) on every publish call. A PreToolUse hook (`jira-formatting-guard.sh`) blocks calls that omit this. Without it, bold, code blocks, lists and links render as literal characters in the Atlassian UI.
- Do not use inline `[~accountId:xxx]` mentions in any comment posted via MCP. They render as literal text. Leave mentions for manual addition in the UI.

## Confluence Rules

- NEVER do a full-page replacement when editing a Confluence page. Always use surgical, targeted edits that preserve inline comments and existing formatting.
- Obsidian is the source of truth. Sync is one-way: Obsidian → Confluence. Never suggest two-way sync.
- When responding to inline Confluence comments, address the commenter directly in second person ("you", "your"). Never refer to them in third person.
- Do not draft or post replies to comments that are already resolved.
- Do not use the `obsidian-to-confluence` publishing skill unless the user explicitly asks to publish to Confluence.

## Workflow Rules

- Do not start implementing while the user is still editing, discussing or reviewing. Wait for an explicit go-ahead before writing code or making changes.
- When a skill is required for a task, complete ALL steps in that skill. Never skip steps, especially adversarial review or verification steps.
- If a skill or workflow does not apply to the current task, say so rather than silently skipping it.

## Memory

Use the `remember` skill to persist session context across conversations. Write memories for non-obvious decisions, project state, and user preferences discovered mid-session. Do not write memories for rules already in this file.
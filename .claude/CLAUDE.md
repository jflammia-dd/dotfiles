
## Verification & Guessing

- Never guess URLs, endpoint paths, or API surfaces. If unknown, say so and ask or search.
- Never post comments or reviews to GitHub, Confluence or Slack without explicit user confirmation.
- When the user specifies a method or API (e.g., ResolveAsync vs ResolveSync), use exactly that. Do not substitute.

## Git Rules

- ALWAYS use `gh` on the command line when interacting with GitHub.
- In Datadog git repos, never run `git fetch` or `git pull` directly. `git-dd-enforce.sh` blocks those and bare `git rebase` onto the main branch, and its message names the `git dd` replacement to run. Full command set and the `git dd switch` scope limit: `project_git_dd_adoption.md` in auto memory.
- In Datadog repo contexts, always write `git`, never `dd-git`. `dd-git` is an interactive shell alias, so it does not resolve in the non-interactive shell the Bash tool runs.
- ALWAYS get explicit approval before running any commit command or creating a PR. Never auto-submit. Approval is conversational: ask before calling the Bash tool. A permission allow-rule on a git or gh command is not approval, since it only decides whether the tool prompts.
- ALWAYS show the exact, literal commit message text in the conversation before running `git commit`. A description of what files changed is not a substitute. Approval to commit is approval of that specific text, not a blank check to write whatever message seems fitting at execution time.
- NEVER add Claude attribution unless explicitly asked. That covers Co-Authored-By trailers on commits and "Generated with Claude Code" lines in PR bodies. Do not add either by default.
- Every PR is created as a draft, no exceptions. `pr-draft-enforce.sh` auto-injects `--draft`, but treat that as a backstop rather than the control. Always pass `--draft` explicitly yourself.
- NEVER mark a PR ready for review or otherwise publish it (`gh pr ready`, `gh pr edit --ready`, etc.) without the user's explicit, in-the-moment instruction to publish that specific PR. Approval to create the PR is not approval to publish it; these are two separate gates. After every `gh pr create`, run `gh pr view <number> --json isDraft,state` and confirm draft status in the conversation rather than assuming the hook worked.

<!--
Provenance for the two rules above. A PR was published without approval because
pr-draft-enforce.sh was registered in settings.json while the session was reading
settings.local.json, so the hook never fired and the prose rule was the only control.
That is why the verification step exists and why the hook is described as a backstop
rather than the control. Do not collapse these two rules back into one.
-->

- Whenever updating a PR, rebase against the parent branch first. Run `git dd sync-and-rebase` when the parent is the repo's main branch. For a PR stacked on another feature branch, rebase manually onto that branch instead, since `git dd sync-and-rebase` only targets main.
- ALWAYS include the Jira issue key in commit subjects and PR titles, uppercase. Do NOT put it in branch names, since Datadog engineering follows its own branch-naming convention. Reference: Atlassian's [Reference issues in your development work](https://support.atlassian.com/jira-software-cloud/docs/reference-issues-in-your-development-work/).
- For commit subject/body format, atomicity, fixup handling, and revert conventions, follow `docs/Git Commit Message Standards.md` in the Datadog vault.
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

- When sharing content for the user to paste anywhere, ALWAYS `pbcopy` it. Never ask the user to copy from terminal output, which introduces spacing and formatting artifacts.
- For Slack specifically, use the `slackfmt` skill rather than raw `pbcopy`, since Slack does not render markdown source.
- Never send Slack messages through the Slack MCP tools. They append "Sent using Claude", and both send tools are denied in `settings.json`. Hand the text over for manual paste.

## Writing Rules

- NEVER use em dashes (U+2014) or double-hyphen (`--`) substitutes in any written output, including comments, docs, messages, or prose. When a violation is flagged, restructure the sentence to remove it. Do not mechanically substitute one punctuation mark for another. A PostToolUse hook (`prose-style-check.sh`) scans Write, Edit and MultiEdit output for three things: em dashes, double-hyphen dash substitutes in prose and commas before coordinating conjunctions. The semicolon and colon rules below are not hook-enforced. Note the hook cannot tell naming a pattern from using one, so quoting a banned character to describe it will flag.
- NEVER use Oxford commas (serial commas before "and" or "or" in a list). Wrong: "apples, oranges, and pears". Right: "apples, oranges and pears".
- NEVER use semicolons to join independent clauses in prose. Use a period, comma or conjunction instead.
- NEVER use a colon to join two independent clauses.
- Prioritize simplicity. When two phrasings are both accurate, always choose the simpler one. Complexity in explanation signals unclear thinking, not a complex subject. Find the simpler sentence before reaching for qualifications.
- ALWAYS invoke the `justins-voice` skill before drafting or editing documents, announcements or distributed written content. A UserPromptSubmit hook (`justins-voice-detect.sh`) detects writing tasks and prompts invocation. Treat its trigger as a strong signal to invoke the skill. This rule does not apply to machine-consumed content: skill files, hook scripts, memory files, CLAUDE.md, settings and any output written for Claude to read rather than a human.
- NEVER include local-process language in published artifacts. Published copy describes the work and the outcome, never your workflow, tooling or internal commands. `local-process-language-check.sh` blocks Atlassian publishes that violate this. What counts as local-process language: `agents/policies/published-artifacts.md`.

## Anti-pattern: Iterative Thinking in Output

Every artifact (code comments, commit messages, PR descriptions, Jira comments, Confluence pages, Slack messages and config files) must describe final state and intent. Conversation within a session is where iteration happens. Artifacts capture the result of that iteration, not the path to it.

**The test:** does "before" refer to a prior runtime state of the running system, or the old version of the code? The first is describing behavior and belongs in artifacts. The second is development history and does not.

Banned phrasings and worked examples: `agents/policies/final-state-artifacts.md`.

## Communication Drafts

Before posting or sending any content to Slack, GitHub, Confluence or Jira:

1. Show the complete draft in the conversation first. For a PR that means the title and body, drafts included.
2. Wait for an explicit "post", "send" or "publish" from the user before calling any tool.
3. Use the target platform's native link format. GitHub, Confluence and Jira take standard markdown `[text](url)`. Slack never renders that markdown, so it needs one of two forms depending on delivery. Use `<url|text>` when the message goes through a tool or the `slackfmt` skill. Use a bare full URL when handing text over for Justin to paste by hand, since the angle-bracket form can arrive as literal characters.

## Slack & Communication Style

- Keep replies concise and direct. Avoid performative or verbose phrasing.

## Jira Rules

- ALWAYS use the plugin Atlassian tools (`mcp__plugin_atlassian_atlassian__*`) when posting comments, editing issues or creating content. Pass `contentFormat: "markdown"` (or `"adf"` for full programmatic fidelity) on every publish call. The older `add_comment` tool does not render markdown at all, so use `addCommentToJiraIssue`. A PreToolUse hook (`jira-formatting-guard.sh`) blocks calls that omit this. Without it, bold, code blocks, lists and links render as literal characters in the Atlassian UI.
- Do not use inline `[~accountId:xxx]` mentions in any comment posted via MCP. They render as literal text. Leave mentions for manual addition in the UI.

## Confluence Rules

- NEVER do a full-page replacement when editing a Confluence page. Surgical edits only, so inline comments survive. Edit mechanics and comment-reply rules: `agents/policies/confluence-writes.md`.
- Obsidian is the source of truth. Sync is one-way: Obsidian → Confluence. Never suggest two-way sync.
- Do not use the `obsidian-to-confluence` publishing skill unless the user explicitly asks to publish to Confluence.

## Workflow Rules

- Do not start implementing while the user is still editing, discussing or reviewing. Wait for an explicit go-ahead before writing code or making changes.
- When a skill is required for a task, complete ALL steps in that skill. Never skip steps, especially adversarial review or verification steps.
- If a skill or workflow does not apply to the current task, say so rather than silently skipping it.

## Memory

Use the `remember` skill to persist session context across conversations. Write memories for non-obvious decisions, project state, and user preferences discovered mid-session. Do not write memories for rules already in this file.
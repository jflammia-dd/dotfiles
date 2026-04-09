@RTK.md

## Git Rules

- ALWAYS use `gh` on the command line when interacting with GitHub.
- In Datadog repo contexts, `dd-git` and `git` are interchangeable. A normalization hook rewrites `dd-git` → `git` before execution so RTK's rewrite registry handles both identically. Use either.
- ALWAYS get explicit approval before running any commit command or creating a PR. Never auto-submit. Approval is conversational: ask before calling the Bash tool. Note: RTK auto-allows git and gh commands at the hook layer, but that is downstream of this gate.
- NEVER add Co-Authored-By trailers to commits unless explicitly asked. Do not add them by default.
- PRs are hook-enforced as drafts. `pr-draft-enforce.sh` auto-injects `--draft` into every `gh pr create` command before RTK runs.
- Do not push, merge, or release anything without specific user approval.
- Whenever updating a PR, rebase against the parent branch first. Most work happens in a large monorepo where drift accumulates quickly during long review cycles, so keeping the branch current prevents painful late-stage conflicts.

## Testing Rules

- Use TDD where applicable. Write or update tests before writing implementation code.
- Before writing any tests, read existing tests in the area to understand naming conventions, structure, assertion style and test organization. Match those patterns exactly.
- Cover both happy and sad paths. Every meaningful code path, error condition and edge case needs a test.
- Update existing tests as you introduce changes. Never leave tests in a state where they pass by accident or are no longer testing the right thing.
- The goal is increased coverage without duplication. Do not write redundant tests that cover ground already handled elsewhere.
- Use the `superpowers:test-driven-development` skill when implementing any feature or bugfix.

## Clipboard Rules

- When sharing content for the user to paste somewhere (Confluence, Slack, a terminal, anywhere), ALWAYS use `pbcopy` via the Bash tool to put it on the clipboard. Never ask the user to copy from the terminal output. Copying from the Claude Code terminal introduces unwanted spacing and formatting artifacts.

## Writing Rules

- NEVER use em dashes (U+2014) or double-hyphen (`--`) substitutes in any written output, including comments, docs, messages, or prose. When a violation is flagged, restructure the sentence to remove it. Do not mechanically substitute one punctuation mark for another. A PostToolUse hook (`em-dash-check.sh`) scans Write, Edit and MultiEdit output and flags violations automatically.
- NEVER use Oxford commas (serial commas before "and" or "or" in a list). Wrong: "apples, oranges, and pears". Right: "apples, oranges and pears".
- NEVER use semicolons to join independent clauses in prose. Use a period, comma or conjunction instead.
- NEVER use a colon to join two independent clauses.
- Prioritize simplicity. When two phrasings are both accurate, always choose the simpler one. Complexity in explanation signals unclear thinking, not a complex subject. Find the simpler sentence before reaching for qualifications.
- ALWAYS invoke the `justins-voice` skill before drafting or editing documents, announcements or distributed written content. A UserPromptSubmit hook (`justins-voice-detect.sh`) detects writing tasks and prompts invocation. Treat its trigger as a strong signal to invoke the skill. This rule does not apply to machine-consumed content: skill files, hook scripts, memory files, CLAUDE.md, settings and any output written for Claude to read rather than a human.

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

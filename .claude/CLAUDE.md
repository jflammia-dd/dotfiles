# Global rules

Grouped by residency, not by topic. Every rule here is a gate, a fact, an output-style rule,
a delivery mechanic or a pointer to something loaded on demand. When adding a rule, decide
which of those it is. If it is a multi-step procedure or only matters for one kind of task,
it belongs in a policy file or a skill, not here.

## Approval gates

Almost nothing is hard-blocked. The permission layer prompts instead. `deny` is reserved for
bypassing pre-commit hooks. Everything else mutating is an `ask`. A prompt Justin answers
**is** the explicit confirmation the rules below require, so treat the prompt as the gate
rather than looking for a separate one.

Two consequences.

Never route around a prompt. Do not look for an unprompted equivalent of a gated command, and
do not batch a gated action into a larger command to avoid the prompt firing.

Never leave a mistake standing because cleaning it up looked blocked. Remediating something
done in this session gets the same gate as the original action, never a stricter one. If a
rollback path really is blocked, say so plainly, name the exact command needed and ask. A
half-corrected mistake is worse than the original.

The gates themselves are conversational. No hook can enforce them, because they depend on the
state of the conversation rather than on tool arguments.

- ALWAYS get explicit approval before running any commit command or creating a PR. Never auto-submit. Approval is conversational: ask before calling the Bash tool. A permission allow-rule on a git or gh command is not approval, since it only decides whether the tool prompts.
- ALWAYS show the exact, literal commit message text in the conversation before running `git commit`. A description of what files changed is not a substitute. Approval to commit is approval of that specific text, not a blank check to write whatever message seems fitting at execution time.
- NEVER mark a PR ready for review or otherwise publish it (`gh pr ready`, `gh pr edit --ready`, etc.) without the user's explicit, in-the-moment instruction to publish that specific PR. Approval to create the PR is not approval to publish it. These are two separate gates. After every `gh pr create`, run `gh pr view <number> --json isDraft,state` and confirm draft status in the conversation rather than assuming the hook worked.
- Every PR is created as a draft, no exceptions. `pr-draft-enforce.sh` auto-injects `--draft`. Treat that as a backstop rather than the control. Always pass `--draft` explicitly yourself.
- Never post comments or reviews to GitHub, Confluence or Slack without explicit user confirmation.
- Do not start implementing while the user is still editing, discussing or reviewing. Wait for an explicit go-ahead before writing code or making changes.
- NEVER add Claude attribution unless explicitly asked. That covers Co-Authored-By trailers on commits and "Generated with Claude Code" lines in PR bodies. Do not add either by default.
- When a skill is required for a task, complete ALL steps in that skill. Never skip steps, especially adversarial review or verification steps.

<!--
Provenance for the draft-PR and publish rules. A PR was published without approval because
pr-draft-enforce.sh was registered in settings.json while the session was reading
settings.local.json, so the hook never fired and the prose rule was the only control. That
is why the verification step exists and why the hook is described as a backstop rather than
the control. Do not collapse those two rules back into one.
-->

## Always-true facts

Invariants about this environment. No procedure, no rationale.

- ALWAYS use `gh` on the command line when interacting with GitHub.
- In Datadog repo contexts, always write `git`, never `dd-git`. `dd-git` is an interactive shell alias, so it does not resolve in the non-interactive shell the Bash tool runs.
- In Datadog git repos, never run `git fetch` or `git pull` directly. `git-dd-enforce.sh` blocks those and bare `git rebase` onto the main branch. Its message names the `git dd` replacement to run.
- Whenever updating a PR, rebase against the parent branch first. Run `git dd sync-and-rebase` when the parent is the repo's main branch. For a PR stacked on another feature branch, rebase manually onto that branch instead, since `git dd sync-and-rebase` only targets main.
- ALWAYS include the Jira issue key in commit subjects and PR titles, uppercase. Do NOT put it in branch names, since Datadog engineering follows its own branch-naming convention. Reference: Atlassian's [Reference issues in your development work](https://support.atlassian.com/jira-software-cloud/docs/reference-issues-in-your-development-work/).
- Before every `git commit` and every `gh pr create`, run `git branch --show-current` and state the branch name in the conversation. If it is not the intended branch, stop and fix the branch situation before proceeding. This prevents commits and PRs landing on the wrong branch.
- Obsidian is the source of truth. Sync is one-way: Obsidian → Confluence. Never suggest two-way sync.
- Never guess URLs, endpoint paths or API surfaces. If unknown, say so and ask or search.
- When the user specifies a method or API (e.g., ResolveAsync vs ResolveSync), use exactly that. Do not substitute.

## Output style

Applies to every piece of prose written for a human reader.

- NEVER use em dashes (U+2014) or double-hyphen (`--`) substitutes in any written output, including comments, docs, messages or prose. When a violation is flagged, restructure the sentence to remove it. Do not mechanically substitute one punctuation mark for another.
- NEVER use Oxford commas (serial commas before "and" or "or" in a list). Wrong: "apples, oranges, and pears". Right: "apples, oranges and pears".
- NEVER use semicolons to join independent clauses in prose. Use a period, comma or conjunction instead.
- NEVER use a colon to join two independent clauses.
- Keep replies concise and direct. Avoid performative or verbose phrasing.
- ALWAYS invoke the `justins-voice` skill before drafting or editing documents, announcements or distributed written content. A UserPromptSubmit hook (`justins-voice-detect.sh`) detects writing tasks and prompts invocation. Treat its trigger as a strong signal to invoke the skill. This rule does not apply to machine-consumed content: skill files, hook scripts, memory files, CLAUDE.md, settings and any output written for Claude to read rather than a human.
- NEVER include local-process language in published artifacts. Published copy describes the work and the outcome, never your workflow, tooling or internal commands. `local-process-language-check.sh` blocks Atlassian publishes that violate this.
- Every artifact (code comments, commit messages, PR descriptions, Jira comments, Confluence pages, Slack messages and config files) must describe final state and intent. Conversation within a session is where iteration happens. Artifacts capture the result of that iteration, not the path to it. **The test:** does "before" refer to a prior runtime state of the running system or the old version of the code? The first is describing behavior and belongs in artifacts. The second is development history and does not.

Enforcement: `prose-style-check.sh` scans Write, Edit and MultiEdit output for three of these, being em dashes, double-hyphen dash substitutes in prose and commas before coordinating conjunctions. The semicolon and colon rules are not hook-enforced. The hook cannot tell naming a pattern from using one, so quoting a banned character in order to describe it will flag.

## Delivery mechanics

Before posting or sending any content to Slack, GitHub, Confluence or Jira:

1. Show the complete draft in the conversation first. For a PR that means the title and body, drafts included.
2. Wait for an explicit "post", "send" or "publish" from the user before calling any tool.
3. Use the target platform's native link format. GitHub, Confluence and Jira take standard markdown `[text](url)`. Slack never renders that markdown, so it needs one of two forms depending on delivery. Use `<url|text>` when the message goes through a tool or the `slackfmt` skill. Use a bare full URL when handing text over for Justin to paste by hand, since the angle-bracket form can arrive as literal characters.

- When sharing content for the user to paste anywhere, ALWAYS `pbcopy` it. Never ask the user to copy from terminal output, which introduces spacing and formatting artifacts.
- For Slack specifically, use the `slackfmt` skill rather than raw `pbcopy`, since Slack does not render markdown source.
- Never send Slack messages through the Slack MCP tools. They append "Sent using Claude". Both send tools are denied in `settings.json`. Hand the text over for manual paste.
- ALWAYS use the plugin Atlassian tools (`mcp__plugin_atlassian_atlassian__*`) when posting comments, editing issues or creating content. Pass `contentFormat: "markdown"` (or `"adf"` for full programmatic fidelity) on every publish call. The older `add_comment` tool does not render markdown at all, so use `addCommentToJiraIssue`. A PreToolUse hook (`jira-formatting-guard.sh`) blocks calls that omit this.
- Do not use inline `[~accountId:xxx]` mentions in any comment posted via MCP. They render as literal text. Leave mentions for manual addition in the UI.
- NEVER do a full-page replacement when editing a Confluence page. Surgical edits only, so inline comments survive.
- Do not use the `obsidian-to-confluence` publishing skill unless the user explicitly asks to publish to Confluence.

## On-demand pointers

Not loaded by default. Read when the task calls for it.

| When | Read |
|---|---|
| Full `git dd` command set plus the `git dd switch` scope limit | `project_git_dd_adoption.md` in auto memory |
| Commit subject and body format, atomicity, fixup handling, revert conventions | `docs/Git Commit Message Standards.md` in the vault |
| Banned phrasings and worked examples for final-state artifacts | `agents/policies/final-state-artifacts.md` |
| What counts as local-process language | `agents/policies/published-artifacts.md` |
| Confluence edit mechanics and comment-reply rules | `agents/policies/confluence-writes.md` |
| Go, Java or TypeScript logging conventions | loads automatically from `~/.claude/rules/logging.md` |
| Test authoring and TDD | loads automatically from `~/.claude/rules/testing.md` |

## Memory

Use the `remember` skill to persist session context across conversations. Write memories for non-obvious decisions, project state and user preferences discovered mid-session. Do not write memories for rules already in this file.

## Compact Instructions

When compacting, carry these forward verbatim rather than summarising them away:

- Any approval still outstanding, plus exactly what it was for. An unanswered gate must not be lost, because losing it reads as approval.
- The current branch name, plus whether the working tree is dirty and in which repo.
- Any draft text shown but not yet posted or sent, plus where it was destined.
- For multi-step work, which step is done, which is in progress, plus what the next verification is.
- Any correction the user made to my reasoning or output, since those do not survive as artifacts.

---
name: pr-review
description: Full PR review combining adaptive code review with codebase learning and teammate context. Use whenever Justin wants to review a PR, understand what a PR does, learn about the author's current work, or select a PR from a list of pending reviews. Trigger on PR URLs, PR numbers, "review this PR", "what does this PR do", "who wrote this", "tell me about this PR", "check this PR", or any GitHub PR link. Files insights to Obsidian automatically. Never posts to GitHub without explicit approval.
---

# PR Review

Two goals: catch real bugs and build understanding of what teammates are building and how it fits the codebase. The learning section and vault filing matter as much as the code findings.

## Step 1: Eligibility Check

```
gh pr view <PR> --repo <owner>/<repo> --json state,isDraft,title,author,comments
```

Stop if the PR is closed, is a draft or already has a comment from you containing "Code review".

## Step 2: Gather Context (parallel)

Run all of these at the same time.

**PR content:**
```
gh pr view <PR> --repo <owner>/<repo> --json title,body,author,files,additions,deletions
gh pr diff <PR> --repo <owner>/<repo>
```

**Author lookup:**
- Check `people/<First Last>.md` in the vault for their role, team and current work
- If not in the vault, run whoisthis for role/team/org and their Slack profile for contact info:
  ```
  cd /Users/justin.flammia/dd/dd-source && bzl run //domains/language_tools/apps/whoisthis:whoisthis -- email <email>
  ```
  Note: if bzl fails in this session (python3 shim issue), skip whoisthis and use what's in the vault or PR context.
- Get their recent PRs in the same repo:
  ```
  gh search prs --repo <owner>/<repo> --author <github_username> --state all --limit 5 --json number,title,url,state,createdAt
  ```

**Ticket context:**
- If the PR title or body references a Jira ticket (e.g. SEC-31179), fetch it via the Atlassian MCP to understand the parent epic and goal.

**Your work overlap:**
- Scan the list of modified files for paths in areas you own: entity-resolution, siem, cloud-siem, security-monitoring. If any modified file falls in those areas, that's relevant overlap worth calling out.

## Step 3: Assess Review Depth

**Lightweight (2 agents)** when:
- Fewer than 50 lines changed, OR
- The change is clearly mechanical: path renames, config updates, dependency bumps, test additions without logic changes

**Full (5 agents)** when:
- 50+ lines changed, OR
- New abstractions, new APIs, logic changes, or architectural decisions

## Step 4: Code Review

### Lightweight: 2 parallel agents

**Agent A: Bug scan.** Read the diff only. Look for real bugs: wrong logic, missing error handling, incorrect variable usage, broken invariants. Ignore style and anything CI would catch. Return concrete issues with file and line references.

**Agent B: Code comment compliance.** Read the modified files. Flag any violation of constraints or invariants expressed in existing inline comments.

### Full: 5 parallel agents

**Agent 1: CLAUDE.md compliance.** Find CLAUDE.md files in the repo (root + modified directories). Check the diff against them. CLAUDE.md is guidance for Claude writing code, so not every rule applies to review. Flag direct violations only.

**Agent 2: Bug scan.** Same as the lightweight bug scan above.

**Agent 3: Git history.** For the 2-3 most substantively changed files, fetch recent commits:
```
gh api repos/<owner>/<repo>/commits?path=<file>&per_page=10
```
Look for recent changes that make the current PR risky or surprising in context.

**Agent 4: Previous PR comments.** Search for merged PRs touching the same files. Check if reviewer comments on those PRs also apply here.

**Agent 5: Code comment compliance.** Same as the lightweight compliance check above.

### Scoring

For each issue, launch a Haiku agent to score it 0-100:
- **0**: False positive or pre-existing issue
- **25**: Possible but unverified; stylistic and not in CLAUDE.md
- **50**: Real but minor or infrequent
- **75**: Verified, important, directly affects functionality or is in CLAUDE.md
- **100**: Certain, happens in practice

Keep only issues scoring 80+. If nothing clears the threshold, the review is clean.

## Step 5: Compose the Review

Re-check eligibility before writing anything. Then invoke `justins-voice` before drafting the prose sections.

### Output format

---

**Code Review**

[Issues as a numbered list with links to exact lines using the full commit SHA:
`1. <description>: https://github.com/<owner>/<repo>/blob/<sha>/<file>#L100-L105`
If no issues: "No issues found. Checked for bugs and CLAUDE.md compliance."]

**What This Is**

[2-4 sentences. What problem does this solve? What pattern or abstraction does it introduce or extend? Explain the architectural significance rather than restating the diff. Draw on the ticket and PR description.]

**[Author First Name]'s Work**

[2-3 sentences. Their role and team. What they're currently building, based on their recent PRs and the ticket this belongs to.]

**Relevance to Your Work**

[Include only if the PR touches systems, patterns or code you own or actively depend on. Be specific. Omit this section entirely if there's no meaningful overlap.]

---

## Step 6: Approval Gate

Present the full output above in conversation. Then ask explicitly: "Should I post the code review section to the PR?"

Post only with an explicit yes. Post only the Code Review section. The learning sections stay in conversation. No attribution footer.

```
gh pr comment <PR> --repo <owner>/<repo> --body "### Code review\n\n<findings>"
```

## Step 7: File to Obsidian

File after presenting the review, regardless of whether the user approves posting. Use the `obsidian` skill for vault writes.

**Author's people note** (`people/<First Last>.md`):
Add or update a `## Current Work` section noting what they're working on and linking to this PR. Only update if the note already exists. Do not create new people notes from a PR review alone.

**Project/epic doc** (`docs/`):
If the PR's ticket maps to an active project doc (e.g. an ERS PR when `docs/Entity Resolution*.md` exists), append a one-line note about what this PR contributes.

**PR Review Log** (`docs/PR Review Log.md`, create if missing):
```
## YYYY-MM-DD: [PR Title]
Repo: [owner/repo] #[number] by [[Author Name]]
What: [one sentence on what it does]
Learned: [one sentence on what this taught you about the codebase or team]
```

**Daily note** (`notes/YYYY-MM-DD - Daily Note.md`):
Append under a `### PR Reviews` header:
`- [#number PR title](URL) by [[Author Name]]: [one-line summary]`

---
name: code-review skill auto-posts without approval
description: The code-review:code-review skill automatically posts a GitHub comment at the end without asking. This violates Justin's no-post-without-approval rule.
type: feedback
originSessionId: fd848ac4-19c9-4928-8f7e-27d3578fe54a
---
Do NOT invoke the `code-review:code-review` skill. It auto-posts a comment to GitHub at the end of its workflow without prompting for approval and includes "Generated with Claude Code" attribution. Both behaviors violate Justin's explicit rules.

**Why:** Justin discovered this when the skill posted to PR #303977 without permission; the comment had to be deleted. Caused user frustration.

**How to apply:** If Justin asks for a PR code review, perform the review manually and present the findings in conversation for his approval before posting anything to GitHub.

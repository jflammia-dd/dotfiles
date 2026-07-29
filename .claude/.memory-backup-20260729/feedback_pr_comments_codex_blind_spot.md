---
name: feedback_pr_comments_codex_blind_spot
description: get-pr-comments.sh misses Codex review comments because Codex posts as plain PR comments not GraphQL review threads
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 55a57b35-5822-482b-893c-64362ef7e96b
---

The `get-pr-comments.sh` script (from the `dd:get-pr-feedback` skill) only returns GraphQL review threads. Codex posts its feedback as a plain pull request comment via a different API endpoint, so it returns `[]` even when Codex left substantive suggestions.

**Why:** GitHub has two separate comment APIs: review thread comments (inline, attached to diff lines, returned by GraphQL `pullRequest.reviewThreads`) and issue/PR comments (returned by `gh api repos/.../pulls/{n}/comments`). The skill queries only the former.

**How to apply:** After any PR review, also run:

```bash
gh api "repos/DataDog/dd-source/pulls/<PR>/comments" --jq '.[] | {path: .path, line: .line, body: .body}'
```

This catches Codex inline comments. Codex comments are tagged with author `chatgpt-codex-connector`.

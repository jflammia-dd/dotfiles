---
name: Code references must be GitHub deeplinks
description: Any file path + line number reference in a doc must be a clickable GitHub link, not plain text
type: feedback
originSessionId: 1dbbbd89-9019-4fa0-bf47-14c364ae385e
---
When a document references a specific file and line number in code, always render it as a GitHub link. Use the format `[`path/to/file.go:36-67`](https://github.com/DataDog/dd-source/blob/main/full/path/to/file.go#L36-L67)`.

**Why:** Plain text file references are dead ends. Clickable links let the reader jump directly to the code. The user flagged bare code references as an error pattern that should never appear in docs.

**How to apply:** Before finalizing any document section that names a file and line number, resolve the full repo path (all referenced files so far live under `DataDog/dd-source`) and insert the GitHub link. Use `main` as the branch. For line ranges use `#L36-L67`. Never leave `file.go:72` as plain text.

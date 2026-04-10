---
name: Tool limitations - investigate before claiming inability
description: Before saying a tool can't do something, check whether a Python/API script can
type: feedback
originSessionId: 102724a9-42fc-4ed1-ba26-716886af197c
---
Before claiming a tool cannot do something, investigate whether a Python script against the underlying API can accomplish it.

**Why:** The confluence-write.py script does text replacement and mark management but does not support injecting new link marks. When asked to add a hyperlink during an edit, the initial response was "the script can't do that" - which was wrong. A Python script against the Confluence ADF API can fetch the page, modify text nodes directly with link marks and save back.

**How to apply:** If a tool has a documented limitation (e.g. confluence-write.py can't add hyperlink marks), check first whether the underlying API supports it before reporting the limitation to the user. If a direct API approach exists, use it. Only report a hard limitation after confirming the API itself does not support the operation.

Common fallback pattern for Confluence: fetch ADF with the v2 pages API, modify nodes directly in Python, PUT back. This bypasses script limitations entirely.

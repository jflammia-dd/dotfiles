---
name: check-vault-before-asking-user-about-vault-state
description: Never ask the user whether a vault profile or file exists; check with obsidian tools first
metadata: 
  node_type: memory
  type: feedback
  originSessionId: a91eda59-08d2-4a88-9355-2dbc0dd04702
---

Before asking the user anything about vault state (whether a person has a profile, whether a note exists, what a file contains), check with obsidian CLI first. The user should never be asked something the vault can answer.

**Why:** Asking "does Shariq Syed have a vault profile?" when you can run `obsidian files folder=people | grep -i shariq` is unnecessary friction. The vault is queryable; use it.

**How to apply:** During ingestion or any vault-adjacent task, always look up people, files and links directly before surfacing them as questions. Only ask the user when the vault genuinely can't answer (e.g., confirming an unfamiliar name that doesn't appear in any profile).

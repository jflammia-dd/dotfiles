---
name: confluence-move-page
description: Use when needing to re-parent or move a Confluence page to a different location in the page tree, change a page's parent, reorganize Confluence hierarchy, nest pages under a different parent, or move pages after creating a new index/directory page.
allowed-tools:
  - Bash(/Users/justin.flammia/.claude/skills/confluence-move-page/scripts/confluence-move.sh:*)
---

# Confluence Move Page

Re-parent a Confluence page to a different parent without modifying its content. Works for any page size. The Confluence REST API v1 `PUT /rest/api/content/{id}` allows changing `ancestors` without specifying a `body`, so existing content is fully preserved.

## Usage

```bash
~/.claude/skills/confluence-move-page/scripts/confluence-move.sh PAGE_ID NEW_PARENT_ID
```

Both arguments are numeric Confluence page IDs (visible in the page URL or from search results).

## Quick Reference

| Scenario | Command |
|---|---|
| Move page under new parent | `confluence-move.sh 6525748475 6531219996` |
| Move multiple pages | Run the command once per page |

## Prerequisites

An Atlassian API token stored in macOS Keychain:

```bash
security add-generic-password -a "$(git config user.email)" -s "confluence-api-token" -w "YOUR_TOKEN" -U
```

Tokens are generated at https://id.atlassian.com/manage-profile/security/api-tokens (expires after 1 year).

## How It Works

The script:
1. Fetches the current page title and version number via `GET /rest/api/content/{id}`
2. Issues `PUT /rest/api/content/{id}` with `ancestors: [{id: NEW_PARENT_ID}]` and no `body` field
3. The API preserves all existing content, inline comments and version history

The MCP `updateConfluencePage` tool marks `body` as required, making re-parenting impractical via MCP for large pages. This script calls the REST API directly and skips the body entirely.

## Common Mistakes

- Providing page URLs instead of IDs. Use the numeric ID from the URL (`/pages/6525748475/`) not the slug.
- Running while someone is actively editing. The version number check will fail. Wait for the edit session to close.

## Fallback: Confluence UI

If the script fails for any reason, the Confluence UI is reliable for any page size:

1. Open the page in Confluence
2. Click `...` (Actions menu, top right)
3. Click **Move**
4. Search for and select the new parent page by name
5. Click **Move**

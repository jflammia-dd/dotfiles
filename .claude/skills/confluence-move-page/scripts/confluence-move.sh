#!/bin/bash
# confluence-move.sh - Re-parent a Confluence page without modifying its content
# Usage: confluence-move.sh PAGE_ID NEW_PARENT_ID

set -eo pipefail

PAGE_ID="$1"
NEW_PARENT_ID="$2"

if [ -z "$PAGE_ID" ] || [ -z "$NEW_PARENT_ID" ]; then
    echo "Usage: confluence-move.sh PAGE_ID NEW_PARENT_ID" >&2
    echo "  PAGE_ID       - Numeric ID of the page to move" >&2
    echo "  NEW_PARENT_ID - Numeric ID of the new parent page" >&2
    exit 1
fi

CONFLUENCE_BASE="https://datadoghq.atlassian.net/wiki"
CONFLUENCE_EMAIL=$(git config user.email)

# Resolve credentials
if [[ "$(uname)" == "Darwin" ]]; then
    CONFLUENCE_TOKEN=$(security find-generic-password -s "confluence-api-token" -w)
elif [ -n "$ATLASSIAN_API_KEY" ]; then
    CONFLUENCE_TOKEN="$ATLASSIAN_API_KEY"
elif command -v pass &>/dev/null; then
    CONFLUENCE_TOKEN=$(pass show atlassian_api_key)
else
    echo "Error: No Confluence credentials found. Set ATLASSIAN_API_KEY, store in pass, or add token to macOS Keychain." >&2
    exit 1
fi

if [ -z "$CONFLUENCE_TOKEN" ]; then
    echo "Error: Confluence token resolved to empty string." >&2
    exit 1
fi

# Fetch current page metadata to get title and version number
PAGE_META=$(curl -fsSL \
    -u "$CONFLUENCE_EMAIL:$CONFLUENCE_TOKEN" \
    "$CONFLUENCE_BASE/rest/api/content/$PAGE_ID?expand=version,ancestors")

TITLE=$(echo "$PAGE_META" | jq -r '.title')
CURRENT_PARENT=$(echo "$PAGE_META" | jq -r '.ancestors[-1].id // "none"')
CURRENT_VERSION=$(echo "$PAGE_META" | jq -r '.version.number')
NEXT_VERSION=$((CURRENT_VERSION + 1))

if [ "$TITLE" = "null" ] || [ -z "$TITLE" ]; then
    echo "Error: Could not fetch page metadata for ID $PAGE_ID" >&2
    echo "$PAGE_META" >&2
    exit 1
fi

echo "Page:        $TITLE (ID: $PAGE_ID)" >&2
echo "Current parent: $CURRENT_PARENT" >&2
echo "New parent:     $NEW_PARENT_ID" >&2
echo "Version:     $CURRENT_VERSION -> $NEXT_VERSION" >&2

# Re-parent the page using the Confluence REST API v1
# The 'ancestors' field changes the parent; omitting 'body' preserves existing content
RESPONSE=$(curl -fsSL -X PUT \
    -u "$CONFLUENCE_EMAIL:$CONFLUENCE_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{
        \"version\": {\"number\": $NEXT_VERSION},
        \"title\": $(echo "$TITLE" | jq -R .),
        \"type\": \"page\",
        \"ancestors\": [{\"id\": \"$NEW_PARENT_ID\"}]
    }" \
    "$CONFLUENCE_BASE/rest/api/content/$PAGE_ID")

MOVED_TITLE=$(echo "$RESPONSE" | jq -r '.title // empty')
if [ -z "$MOVED_TITLE" ]; then
    echo "Error: Move failed." >&2
    echo "$RESPONSE" | jq . >&2
    exit 1
fi

echo "Done: '$MOVED_TITLE' moved to parent $NEW_PARENT_ID" >&2
echo "$RESPONSE" | jq '{id, title, "version": .version.number, "new_parent": .ancestors[-1].id}'

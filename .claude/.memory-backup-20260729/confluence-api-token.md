---
name: confluence-api-token-expiry
description: Atlassian API token expiry date for the confluence-api plugin
type: project
---

The Atlassian API token stored in macOS Keychain (service: `confluence-api-token`) expires on 2027-03-22.

**Why:** API tokens have a 1-year TTL from creation date.

**How to apply:** Remind the user to refresh the token before that date. To update it, generate a new token at https://id.atlassian.com/manage-profile/security/api-tokens and run:

```sh
security add-generic-password -a "justin.flammia@datadoghq.com" -s "confluence-api-token" -w "NEW_TOKEN" -U
```

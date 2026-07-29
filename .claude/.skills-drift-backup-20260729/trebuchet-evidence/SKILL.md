---
name: dd:trebuchet-evidence
description: >
  Generate a "Tested in staging" PR evidence block for logs-backend or similar
  services deployed via Trebuchet. Use when you are about to write or update a PR
  description for a service that runs in staging and requires curl-based validation
  evidence. Composes with dd:trebuchet (for pod context) and aaa:authn-api-testing
  (for authenticated requests). Trigger on: "generate staging evidence", "write the
  tested in staging section", "run the happy/sad path tests", "scaffold the PR curl
  examples". Do NOT use for: local dev testing, unit tests or services not deployed
  via Trebuchet.
---

# Trebuchet PR Evidence Scaffold

Generate authenticated happy/sad path curl evidence for a PR description from a
service deployed to staging via Trebuchet.

---

## Inputs Required

Gather these before running requests. Ask the user if any are missing:

1. **Endpoint path** - e.g. `/api/v2/security_monitoring/entity_context`
2. **HTTP method** - usually `POST` for logs-backend entity endpoints
3. **Org ID** - the staging org ID to use for auth (ask user or find from context)
4. **Happy path request body** - the valid JSON payload that should return 2xx
5. **Sad path scenario** - what should fail: missing required field, invalid value, wrong type, etc.
6. **Staging pod URL** - if not known, run `dd:trebuchet` first to deploy and get it

---

## Workflow

### Step 1: Confirm staging deployment

Check if the user already has a Trebuchet session running. Ask: "Is your service
already deployed to staging via Trebuchet or do you need to deploy first?"

If they need to deploy: invoke `/dd:trebuchet` before continuing.

Once deployed, get the pod URL. It typically looks like:
`http://logs-api-{pod-hash}.logs-general.svc.cluster.local:9091`
or is accessed via `kubectl port-forward`.

### Step 2: Run the happy path request

Use `aaa:authn-api-testing` to run an authenticated request with the valid payload.

Capture:
- HTTP status code
- Response body (formatted JSON)
- Request that was sent

If `aaa:authn-api-testing` is not available, construct the curl manually:
```bash
curl -s -X {METHOD} \
  -H "Content-Type: application/json" \
  -H "DD-API-KEY: $(dd-auth-token)" \
  http://localhost:9091{ENDPOINT_PATH} \
  -d '{HAPPY_PAYLOAD}' | jq .
```

### Step 3: Run the sad path request

Modify the happy path payload to trigger the error scenario. Common patterns:
- Remove a required field
- Send an empty body `{}`
- Use an invalid enum value
- Send the wrong type (string where int expected)

Run with the same auth, capture status code and error response.

### Step 4: Format as PR evidence block

Use this template. Fill in actual captured output, not placeholders:

```markdown
## Tested in Staging

Deployed via Trebuchet to `{POD_NAME_OR_SESSION}`.

### Happy path: {brief description of valid case}

```bash
curl -X {METHOD} http://localhost:9091{ENDPOINT_PATH} \
  -H "Content-Type: application/json" \
  -d '{HAPPY_PAYLOAD}'
```

Response (`{STATUS_CODE}`):
```json
{HAPPY_RESPONSE}
```

### Sad path: {brief description of error case}

```bash
curl -X {METHOD} http://localhost:9091{ENDPOINT_PATH} \
  -H "Content-Type: application/json" \
  -d '{SAD_PAYLOAD}'
```

Response (`{STATUS_CODE}`):
```json
{SAD_RESPONSE}
```
```

### Step 5: Deliver to clipboard

Run `pbcopy` on the formatted evidence block so the user can paste it directly
into the PR description without copying from terminal output.

```bash
pbcopy << 'EOF'
{FORMATTED_EVIDENCE_BLOCK}
EOF
```

Confirm: "Evidence block copied to clipboard. Paste it into your PR description."

---

## Notes

- Always use real captured output, never fabricated JSON responses
- If the endpoint requires port-forwarding, remind the user to keep the
  `kubectl port-forward` running while you make requests
- For endpoints that require a valid entity in staging, ask the user to provide
  a known-good entity ID or create one first
- Truncate response bodies longer than ~30 lines with `| head -n 30` to keep
  the PR description readable

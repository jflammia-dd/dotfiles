---
name: mcp-repair
description: Repairs OAuth authentication for configured MCP servers by clearing rejected credentials, starting the active harness's login flow, opening authorization pages, waiting for user approval, and guiding MCP reload. Use when MCP startup or tool calls report invalid_grant, reauthenticationRequired, OAuth token refresh failure, authorization required, or when the user says "repair MCP auth", "reconnect my MCPs", "fix ODP", or "fix DDCI".
---

# MCP OAuth Repair

Repair OAuth-backed MCP credentials from the current session. Treat opening the
browser authorization page as the start of OAuth, not its completion. Leave the
Authorize action to the user and handle everything around that click.

## Invocation and confirmation

When the user explicitly asks to repair, reconnect, log in to, or reauthenticate
an MCP server, treat that request as authorization to start this workflow.

When this skill loads only because visible startup or tool output identifies an
MCP OAuth failure, name the exact server or servers that need repair and ask the
user to confirm before running logout or login commands. A startup warning that
appears only in the host UI may not reach the model, so also trigger on "repair
MCP auth" or "reconnect my MCPs."

Do not ask the user to copy and run commands that the active harness can run
directly.

Do not run this workflow on every session start. Do not use a `SessionStart` hook
as a substitute for an observed failure.

## Select the harness and servers

Use only the current harness's credential store:

- Codex: `codex mcp`
- Claude Code: `claude mcp`

Do not repair both harnesses unless the user explicitly asks. Their credentials
are separate.

Select servers from the error text or the user's request. In this environment,
"both internal MCPs" means `odp` and `ddci-mcp-prod`. Never reauthenticate every
OAuth server as a fallback.

Confirm each selected server exists with the harness's `mcp get` or `mcp list`
command before changing credentials. Treat a returned configuration record as
proof of existence even when its health check reports unreachable or failed.

## Repair each server

Process servers sequentially so each callback and browser page stays unambiguous.

1. If the failure includes `invalid_grant`, rejected refresh token, or expired
   credentials, run `<harness> mcp logout <server>`. Otherwise try login first.
2. Start `<harness> mcp login <server>` as a long-lived interactive process.
   Request the narrow permissions needed for network access or the browser.
3. Keep the process alive while it discovers OAuth metadata. When it prints an
   authorization URL, open that exact one-time URL in the system browser.
4. Tell the user which server is waiting for approval. Poll the login process at
   intervals no longer than 30 seconds and keep the user updated at least once a
   minute. Do not impose the MCP startup timeout on this wait.
5. Wait until the command reports success, the user cancels, or the command
   returns a real error. Do not click Authorize through browser automation.
6. Continue with the next server only after the current login completes.

If the login command exits before the user approves, start a new login. Never
reuse an authorization URL from a completed or failed attempt.

## Finish and reload

After all logins succeed:

1. Run the harness's `mcp list` command and confirm each repaired server reports
   OAuth authentication. This confirms stored credential presence, not token
   validity.
2. Use the host's MCP restart or reload control if one is available.
3. If the current session still lacks the tools or repeats `invalid_grant`, tell
   the user to restart the affected MCP in Settings or begin a new session. Do
   not claim that an active session reloaded credentials unless a tool call
   proves it.

Do not launch a nested model session solely to verify MCP startup.

## Boundaries

- `startup_timeout_sec` controls MCP initialization, not time spent waiting for
  browser approval. Do not edit timeout settings during an auth-only repair.
- Never print, inspect, copy, or persist access tokens or refresh tokens.
- Treat authorization URLs as ephemeral. Do not save them in notes or include
  them in the final response.
- Never remove an MCP server definition as part of credential repair.
- If successful credentials repeatedly become invalid after switching harnesses
  or sessions, report probable refresh-token rotation or stale-session caching
  rather than creating an automatic login loop.

## Runtime compatibility

Read [runtime compatibility](references/runtime-compatibility.md) before changing
command syntax, when the installed CLI version differs from the verified
versions, or when the documented login flow does not start.

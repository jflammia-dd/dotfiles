# Runtime compatibility

Last verified: 2026-07-28

Verified runtimes:

- Codex CLI 0.145.0
- Claude Code 2.1.220

Use the active harness only unless the user explicitly asks to repair both
credential stores.

| Operation | Codex | Claude Code |
| --- | --- | --- |
| Inspect one server | `codex mcp get <server>` | `claude mcp get <server>` |
| List servers | `codex mcp list` | `claude mcp list` |
| Start OAuth | `codex mcp login <server>` | `claude mcp login <server>` |
| Clear rejected OAuth state | `codex mcp logout <server>` | `claude mcp logout <server>` |

The two harnesses keep OAuth state separately. Logging in successfully with one
does not prove that the other has usable credentials. Browser approval is an
interactive user action in both flows.

Codex's `startup_timeout_sec` controls MCP startup, not the time available for
browser authorization.

Before relying on these commands with a different runtime version, run
`<harness> mcp --help` and consult the current vendor documentation:

- Codex: <https://learn.chatgpt.com/docs/extend/mcp>
- Claude Code: <https://code.claude.com/docs/en/mcp>

If the current command semantics are unclear, stop before logout or login and
explain the mismatch to the user. Never inspect or migrate raw credential-store
contents.

---
name: reference_ccstatusline_npx_hook_timeout
description: "Root cause and fix for recurring \"UserPromptSubmit hook timed out after 30s\" errors caused by ccstatusline-cached.sh"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 779e6f9c-1e4b-415e-8cc7-2642e5728113
  modified: 2026-08-07T14:01:05.363Z
---

`ccstatusline-cached.sh` (`~/dotfiles/.claude/hooks/ccstatusline-cached.sh`, symlinked into `~/.claude/hooks/`) used to `exec npx -y "ccstatusline@${VERSION}"` on every invocation. It backs all three ccstatusline call sites in `settings.json`: the `UserPromptSubmit` hook, a `PreToolUse` Skill-matcher hook and the `statusLine` renderer. `npx` hits the npm registry to resolve/verify the package even with a version pinned, so any VPN/AppGate flakiness (a recurring issue, see [[feedback_ground_connectivity_diagnosis_empirically]]) stalled the call and burned the whole 30s hook timeout. That produced "UserPromptSubmit hook timed out after 30s, output discarded."

Fixed 2026-08-07: ran `npm install -g ccstatusline` (homebrew-managed node, no sudo needed) and rewrote the script to `command -v ccstatusline >/dev/null 2>&1 && exec ccstatusline "$@"`, with no npm/npx call at all. Deleted the now-dead `~/.claude/.ccstatusline-version-cache`. Verified consistent ~110-140ms latency across both the `--hook` and bare invocation paths.

Same failure class as [[reference_claude_startup_hooks]] (marketplace-auto-update plugin blocking startup on a network call). Pattern to watch for: any hook wired into `UserPromptSubmit` or `PreToolUse` that does synchronous package-registry resolution (npx, pip, etc.) instead of using a locally-installed binary is a latent timeout risk on this network. To update ccstatusline going forward, run `npm update -g ccstatusline` manually rather than reintroducing auto-resolution.

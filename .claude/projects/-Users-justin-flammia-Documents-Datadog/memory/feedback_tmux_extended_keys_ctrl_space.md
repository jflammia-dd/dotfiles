---
name: feedback-tmux-extended-keys-ctrl-space
description: tmux extended-keys must be on for Ctrl-Space (and similar no-standard-representation chords) to reach nvim distinguishably
metadata: 
  node_type: memory
  type: project
  originSessionId: 83958206-e069-4795-aaa4-98fde293027f
---

`set -g extended-keys on` in `~/.tmux.conf` is required for Ctrl-modified keys with no standard xterm representation (e.g. Ctrl-Space) to reach nvim as a distinguishable sequence. Default is `off`, which only reports "standard" keys, so Ctrl-Space collapses to a NUL byte indistinguishable from `<C-@>`.

Why: tmux's `extended-keys` option is the equivalent of xterm's `modifyOtherKeys` resource (confirmed via `man tmux`). With it off, this looked like inconsistent/flaky Ctrl-Space behavior and was initially misdiagnosed as macOS eating the shortcut at the OS level (checked `com.apple.symbolichotkeys`, but input-source-switching hotkeys were already disabled there, so that was a dead end). The real fix was found by reading `man tmux` directly rather than guessing.

How to apply: any nvim/tmux/Ghostty keybinding investigation involving Ctrl+ or Shift+ chords that "sometimes works" should check `tmux show-options -g extended-keys` before looking elsewhere. After changing it, attached tmux clients need to detach/reattach (or open a new window) for the terminal to renegotiate the capability.

Related: [[reference_ghostty_settings_editor]]

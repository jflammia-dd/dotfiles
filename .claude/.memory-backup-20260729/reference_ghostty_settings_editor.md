---
name: Ghostty Settings Editor
description: Ghostty does not support a config option to set the editor for "Ghostty -> Settings..." menu item; use CLI instead
type: reference
originSessionId: 478d974c-a9e8-430d-8261-6c9c8478fd6e
---
The `config-editor` config key does not exist in Ghostty. "Ghostty -> Settings..." uses macOS `openURL()`, so it always opens with the system default app for plain text files. There is no supported config option to override this.

Use `ghostty +edit-config` instead. It respects `$VISUAL` / `$EDITOR` environment variables, so with `EDITOR=nvim` in your shell config it opens the file in nvim.

The GUI settings panel is still under development (GitHub issue #441).

#!/usr/bin/env bash
# session-end-remind: writes a reminder marker at session end so the next
# session is prompted to save any important context via the remember skill.
# SessionEnd cannot surface additionalContext to Claude (session is closing),
# so this writes a file that a SessionStart hook picks up next session.

MARKER="$HOME/.claude/.pending-remember"

cat > "$MARKER" <<'EOF'
A previous session ended. Check if any non-obvious decisions, user preferences, or project state from that session were worth persisting. If so, invoke the 'remember' skill now. If nothing meaningful carries over, delete this file and move on.
EOF

#!/usr/bin/env bash
# Detects writing tasks and injects a reminder to invoke the justins-voice skill.
# Fires on UserPromptSubmit. Outputs additionalContext JSON only when writing is detected.

if ! command -v jq &>/dev/null; then
  exit 0
fi

INPUT=$(cat)
prompt=$(echo "$INPUT" | jq -r '.prompt // ""')

# Skip if the user is already explicitly invoking justins-voice
if echo "$prompt" | grep -qi 'justins.voice'; then
  exit 0
fi

# Check for writing intent first — writing verbs win even if review/analysis verbs are also present.
# This ensures "review and rewrite this doc" triggers, not just "write this doc".
if echo "$prompt" | grep -qiE \
  '\b(write|draft|edit|revise|compose|rewrite|announce|announcement|update|improve|polish|sharpen|clean)\b|obsidian|confluence page|slack message|engineering doc|adr|changelog|readme|blog post|meeting notes|daily note|landscape doc'; then
  printf '{"hookSpecificOutput":{"hookEventName":"UserPromptSubmit","additionalContext":"Writing task detected. Invoke the justins-voice skill before producing any prose content (notes, messages, Confluence pages, Slack messages, announcements, docs, etc.)."}}'
  exit 0
fi

# Skip prompts that are purely review, analysis or question tasks with no writing intent
if echo "$prompt" | grep -qiE \
  '\b(review|optimize|debug|fix|check|analyze|analyse|suggest|explain|summarize|summarise|investigate|diagnose|find|search|why|how|what|show me)\b'; then
  exit 0
fi

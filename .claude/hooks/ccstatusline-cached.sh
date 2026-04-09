#!/usr/bin/env bash
# ccstatusline-cached: runs ccstatusline with a daily version cache.
# Resolves @latest from npm at most once per 24 hours, then reuses the
# cached version. Balances update freshness vs per-prompt latency.

CACHE_FILE="${HOME}/.claude/.ccstatusline-version-cache"
MAX_AGE_SECONDS=86400  # 24 hours

get_cached_version() {
  [ -f "$CACHE_FILE" ] || return 1
  local cache_time now
  # macOS: stat -f %m; Linux: stat -c %Y
  cache_time=$(stat -f %m "$CACHE_FILE" 2>/dev/null || stat -c %Y "$CACHE_FILE" 2>/dev/null)
  now=$(date +%s)
  [ $((now - cache_time)) -lt $MAX_AGE_SECONDS ] || return 1
  cat "$CACHE_FILE"
}

VERSION=$(get_cached_version)
if [ -z "$VERSION" ]; then
  VERSION=$(npm view ccstatusline version 2>/dev/null)
  if [ -n "$VERSION" ]; then
    echo "$VERSION" > "$CACHE_FILE"
  else
    VERSION="latest"  # fallback if npm is unreachable
  fi
fi

exec npx -y "ccstatusline@${VERSION}" "$@"

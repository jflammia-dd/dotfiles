#!/usr/bin/env bash
# Tests for backup.sh
#
# Runs backup.sh against a sandboxed HOME with a local bare git repo as
# the remote. No real files are touched and nothing is pushed to GitHub.
#
# Usage: bash tests/test_backup.sh
set -euo pipefail

DOTFILES="$(cd "$(dirname "$0")/.." && pwd)"
PASS=0
FAIL=0

pass() { printf "  PASS  %s\n" "$1"; ((PASS++)) || true; }
fail() { printf "  FAIL  %s\n" "$1"; ((FAIL++)) || true; }

in_repo()     { [ -f "$FAKE_REPO/.claude-dotfiles/$1" ]; }
not_in_repo() { [ ! -e "$FAKE_REPO/.claude-dotfiles/$1" ]; }

assert_synced()   {
  in_repo "$1"     && pass "synced:   $1" || fail "MISSING:  $1 (should have been synced)"
}
assert_excluded() {
  not_in_repo "$1" && pass "excluded: $1" || fail "PRESENT:  $1 (should have been excluded)"
}

# ── Setup ──────────────────────────────────────────────────────────────────────

FAKE_HOME="$(mktemp -d)"
FAKE_REMOTE="$(mktemp -d)"
FAKE_REPO="$(mktemp -d)"

cleanup() { rm -rf "$FAKE_HOME" "$FAKE_REMOTE" "$FAKE_REPO"; }
trap cleanup EXIT

echo "Setting up sandboxed environment ..."

# Local bare repo acts as the git remote
git init --bare "$FAKE_REMOTE/dotfiles.git" -q

# Seed the fake working repo from the real dotfiles repo
git clone "$FAKE_REMOTE/dotfiles.git" "$FAKE_REPO/.claude-dotfiles" -q 2>/dev/null || true
rsync -a --exclude='.git/' "$DOTFILES/" "$FAKE_REPO/.claude-dotfiles/"
cd "$FAKE_REPO/.claude-dotfiles"
git config user.email "test@test.com"
git config user.name "Test User"
git config push.autoSetupRemote true   # needed for backup.sh's bare "git push"
git add -A
git commit -m "initial seed" -q
git push -u origin HEAD -q             # push and set upstream regardless of branch name

# Build fake HOME: files that SHOULD be synced
mkdir -p \
  "$FAKE_HOME/.claude/hooks" \
  "$FAKE_HOME/.claude/projects/my-project/memory" \
  "$FAKE_HOME/.config/git" \
  "$FAKE_HOME/.config/gitsign"

echo "# zshrc"              > "$FAKE_HOME/.zshrc"
echo "# zshenv"             > "$FAKE_HOME/.zshenv"
echo "# zprofile"           > "$FAKE_HOME/.zprofile"
printf "[user]\n\temail = test@test.com\n\tname = Test\n" > "$FAKE_HOME/.gitconfig"
echo "*.DS_Store"           > "$FAKE_HOME/.config/git/ignore"
printf "[gpg]\n\tformat = ssh\n" > "$FAKE_HOME/.config/gitsign/gitconfig"
echo '{"version":"1"}'     > "$FAKE_HOME/.claude/settings.json"
echo "hook content"         > "$FAKE_HOME/.claude/hooks/em-dash-check.sh"
echo "# memory"             > "$FAKE_HOME/.claude/projects/my-project/memory/MEMORY.md"
echo "# memory note"        > "$FAKE_HOME/.claude/projects/my-project/memory/feedback.md"

# Files that SHOULD NOT be synced
echo "credentials"          > "$FAKE_HOME/.claude/.credentials.json"
echo "history"              > "$FAKE_HOME/.claude/history.jsonl"
mkdir -p "$FAKE_HOME/.claude/sessions"  && echo "s" > "$FAKE_HOME/.claude/sessions/s1.json"
mkdir -p "$FAKE_HOME/.claude/cache"     && echo "c" > "$FAKE_HOME/.claude/cache/cache1"
mkdir -p "$FAKE_HOME/.claude/telemetry" && echo "t" > "$FAKE_HOME/.claude/telemetry/t1"
mkdir -p "$FAKE_HOME/.claude/plugins"   && echo "p" > "$FAKE_HOME/.claude/plugins/plugin1"
mkdir -p "$FAKE_HOME/.claude/skills/my-tool-workspace" && echo "w" > "$FAKE_HOME/.claude/skills/my-tool-workspace/file"
echo '{"session":"data"}'  > "$FAKE_HOME/.claude/projects/my-project/session.jsonl"
echo "private key"          > "$FAKE_HOME/.config/gitsign/signing-key"
echo "public key"           > "$FAKE_HOME/.config/gitsign/signing-key.pub"
echo "install-id"           > "$FAKE_HOME/.config/gitsign/.install_id"

# ── Test 1: Sync coverage ──────────────────────────────────────────────────────

echo ""
echo "--- Test 1: Sync coverage ---"
HOME="$FAKE_HOME" bash "$FAKE_REPO/.claude-dotfiles/backup.sh" > /dev/null

# Should be synced
assert_synced ".zshrc"
assert_synced ".zshenv"
assert_synced ".zprofile"
assert_synced ".gitconfig"
assert_synced ".config/git/ignore"
assert_synced ".config/gitsign/gitconfig"
assert_synced ".claude/settings.json"
assert_synced ".claude/hooks/em-dash-check.sh"
assert_synced ".claude/projects/my-project/memory/MEMORY.md"
assert_synced ".claude/projects/my-project/memory/feedback.md"

# Should be excluded
assert_excluded ".claude/.credentials.json"
assert_excluded ".claude/history.jsonl"
assert_excluded ".claude/sessions/s1.json"
assert_excluded ".claude/cache/cache1"
assert_excluded ".claude/telemetry/t1"
assert_excluded ".claude/plugins/plugin1"
assert_excluded ".claude/skills/my-tool-workspace/file"
assert_excluded ".claude/projects/my-project/session.jsonl"
assert_excluded ".config/gitsign/signing-key"
assert_excluded ".config/gitsign/signing-key.pub"
assert_excluded ".config/gitsign/.install_id"

# ── Test 2: Deletions propagate ───────────────────────────────────────────────

echo ""
echo "--- Test 2: Deletions propagate ---"

# Delete the hook from HOME and verify the next backup removes it from the repo
rm "$FAKE_HOME/.claude/hooks/em-dash-check.sh"
HOME="$FAKE_HOME" bash "$FAKE_REPO/.claude-dotfiles/backup.sh" > /dev/null
if not_in_repo ".claude/hooks/em-dash-check.sh"; then
  pass "deleted file removed from repo"
else
  fail "deleted file still present in repo after backup"
fi

# Restore it for subsequent tests
echo "hook content" > "$FAKE_HOME/.claude/hooks/em-dash-check.sh"
HOME="$FAKE_HOME" bash "$FAKE_REPO/.claude-dotfiles/backup.sh" > /dev/null

# ── Test 3: Idempotency ────────────────────────────────────────────────────────

echo ""
echo "--- Test 3: Idempotency ---"
output="$(HOME="$FAKE_HOME" bash "$FAKE_REPO/.claude-dotfiles/backup.sh" 2>&1)"
if echo "$output" | grep -q "Nothing changed"; then
  pass "second run with no changes exits cleanly without committing"
else
  fail "second run committed unexpectedly"
  echo "    output: $output"
fi

# Modify a file and verify the third run DOES commit
echo "updated zshrc" > "$FAKE_HOME/.zshrc"
output="$(HOME="$FAKE_HOME" bash "$FAKE_REPO/.claude-dotfiles/backup.sh" 2>&1)"
if echo "$output" | grep -q "Backup pushed"; then
  pass "run after file change commits and pushes"
else
  fail "run after file change did not push"
  echo "    output: $output"
fi

# ── Test 3: Secret guard blocks hardcoded tokens ───────────────────────────────

echo ""
echo "--- Test 4: Secret guard ---"

# Plant a fake GitHub PAT
echo 'export GH="github_pat_11ABCDEFGHIJKLMNOPQRSTUVWXYZ12345678901234"' >> "$FAKE_HOME/.zshrc"
output="$(HOME="$FAKE_HOME" bash "$FAKE_REPO/.claude-dotfiles/backup.sh" 2>&1 || true)"
if echo "$output" | grep -q "ERROR: Possible secret"; then
  pass "guard fires on hardcoded github_pat_ token"
else
  fail "guard DID NOT fire on github_pat_ token"
fi

# Restore clean zshrc (also clears the bad content from the dotfiles working tree)
echo "updated zshrc" > "$FAKE_HOME/.zshrc"
HOME="$FAKE_HOME" bash "$FAKE_REPO/.claude-dotfiles/backup.sh" > /dev/null

# Plant a fake Figma token
echo 'export FIG="figd_ABCDEFGHIJKLMNOPQRSTUVWXYZ12345678"' >> "$FAKE_HOME/.zshrc"
output="$(HOME="$FAKE_HOME" bash "$FAKE_REPO/.claude-dotfiles/backup.sh" 2>&1 || true)"
if echo "$output" | grep -q "ERROR: Possible secret"; then
  pass "guard fires on hardcoded figd_ token"
else
  fail "guard DID NOT fire on figd_ token"
fi

# Restore again
echo "updated zshrc" > "$FAKE_HOME/.zshrc"
HOME="$FAKE_HOME" bash "$FAKE_REPO/.claude-dotfiles/backup.sh" > /dev/null

# ── Test 4: op read pattern passes the guard ───────────────────────────────────

echo ""
echo "--- Test 5: op read pattern is allowed ---"
printf 'export GH="$(op read '"'"'op://Employee/github-pat/credential'"'"' 2>/dev/null)"\n' >> "$FAKE_HOME/.zshrc"
output="$(HOME="$FAKE_HOME" bash "$FAKE_REPO/.claude-dotfiles/backup.sh" 2>&1)"
if echo "$output" | grep -q "ERROR"; then
  fail "guard incorrectly blocked op read pattern"
else
  pass "op read pattern is allowed through"
fi

# ── Results ────────────────────────────────────────────────────────────────────

echo ""
echo "=============================="
printf "  %d passed, %d failed\n" "$PASS" "$FAIL"
echo "=============================="
[ "$FAIL" -eq 0 ]

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
RESTORE_HOME="$(mktemp -d)"
FAKE_BIN="$(mktemp -d)"

cleanup() { rm -rf "$FAKE_HOME" "$FAKE_REMOTE" "$FAKE_REPO" "$RESTORE_HOME" "$FAKE_BIN"; }
trap cleanup EXIT

echo "Setting up sandboxed environment ..."

# Avoid invoking the real Claude CLI when backup.sh generates test commit messages.
printf '#!/usr/bin/env bash\nprintf "test backup\\n"\n' > "$FAKE_BIN/claude"
chmod +x "$FAKE_BIN/claude"
export PATH="$FAKE_BIN:$PATH"

# Local bare repo acts as the git remote
git init --bare "$FAKE_REMOTE/dotfiles.git" -q
git --git-dir="$FAKE_REMOTE/dotfiles.git" config core.hooksPath /dev/null

# Seed the fake working repo from the real dotfiles repo
git clone "$FAKE_REMOTE/dotfiles.git" "$FAKE_REPO/.claude-dotfiles" -q 2>/dev/null || true
rsync -a --exclude='.git/' "$DOTFILES/" "$FAKE_REPO/.claude-dotfiles/"
cd "$FAKE_REPO/.claude-dotfiles"
git config user.email "test@test.com"
git config user.name "Test User"
git config commit.gpgsign false
git config core.hooksPath /dev/null
git config push.autoSetupRemote true   # needed for backup.sh's bare "git push"
git add -A
git commit -m "initial seed" -q
git push -u origin HEAD -q             # push and set upstream regardless of branch name

# Build fake HOME: files that SHOULD be synced
mkdir -p \
  "$FAKE_HOME/.claude/hooks" \
  "$FAKE_HOME/.claude/projects/my-project/memory" \
  "$FAKE_HOME/.agents/skills/mcp-repair/agents" \
  "$FAKE_HOME/.agents/skills/mcp-repair/references" \
  "$FAKE_HOME/.agents/skills/vendor-skill" \
  "$FAKE_HOME/.config/git" \
  "$FAKE_HOME/.config/gitsign"

# Give every allowlisted skill a minimal source so future manifest additions are
# covered by the generic backup path without rewriting this fixture.
while IFS= read -r skill || [ -n "$skill" ]; do
  [[ -z "$skill" || "$skill" =~ ^[[:space:]]*# ]] && continue
  mkdir -p "$FAKE_HOME/.agents/skills/$skill"
  printf '# %s\n' "$skill" > "$FAKE_HOME/.agents/skills/$skill/SKILL.md"
done < "$FAKE_REPO/.claude-dotfiles/.agents/owned-skills.txt"

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
echo "# MCP Repair"         > "$FAKE_HOME/.agents/skills/mcp-repair/SKILL.md"
echo "interface:"           > "$FAKE_HOME/.agents/skills/mcp-repair/agents/openai.yaml"
echo "# Runtime notes"      > "$FAKE_HOME/.agents/skills/mcp-repair/references/runtime-compatibility.md"
echo "do not back up"       > "$FAKE_HOME/.agents/skills/mcp-repair/.env"
mkdir -p "$FAKE_HOME/.agents/skills/mcp-repair/__pycache__"
echo "cache"                > "$FAKE_HOME/.agents/skills/mcp-repair/__pycache__/state.pyc"
mkdir -p "$FAKE_HOME/.agents/skills/mcp-repair/.git"
echo "nested repo"          > "$FAKE_HOME/.agents/skills/mcp-repair/.git/config"
echo "credentials"         > "$FAKE_HOME/.agents/skills/mcp-repair/credentials.json"
ln -s "$FAKE_HOME/.claude/.credentials.json" "$FAKE_HOME/.agents/skills/mcp-repair/credentials-link"
echo "# Vendor skill"       > "$FAKE_HOME/.agents/skills/vendor-skill/SKILL.md"

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
if ! output="$(HOME="$FAKE_HOME" bash "$FAKE_REPO/.claude-dotfiles/backup.sh" 2>&1)"; then
  fail "initial backup completed successfully"
  echo "    output: $output"
  exit 1
fi
pass "initial backup completed successfully"

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
assert_synced ".agents/skills/mcp-repair/SKILL.md"
assert_synced ".agents/skills/mcp-repair/agents/openai.yaml"
assert_synced ".agents/skills/mcp-repair/references/runtime-compatibility.md"

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
assert_excluded ".agents/skills/mcp-repair/.env"
assert_excluded ".agents/skills/mcp-repair/__pycache__/state.pyc"
assert_excluded ".agents/skills/mcp-repair/.git/config"
assert_excluded ".agents/skills/mcp-repair/credentials.json"
assert_excluded ".agents/skills/mcp-repair/credentials-link"
assert_excluded ".agents/skills/vendor-skill/SKILL.md"

# ── Test 2: Deletions propagate ───────────────────────────────────────────────

echo ""
echo "--- Test 2: Deletions propagate ---"

# Delete the hook from HOME and verify the next backup removes it from the repo
rm "$FAKE_HOME/.claude/hooks/em-dash-check.sh"
rm "$FAKE_HOME/.agents/skills/mcp-repair/references/runtime-compatibility.md"
HOME="$FAKE_HOME" bash "$FAKE_REPO/.claude-dotfiles/backup.sh" > /dev/null
if not_in_repo ".claude/hooks/em-dash-check.sh"; then
  pass "deleted file removed from repo"
else
  fail "deleted file still present in repo after backup"
fi
if not_in_repo ".agents/skills/mcp-repair/references/runtime-compatibility.md"; then
  pass "deleted owned-skill file removed from repo"
else
  fail "deleted owned-skill file still present in repo after backup"
fi

# Restore it for subsequent tests
echo "hook content" > "$FAKE_HOME/.claude/hooks/em-dash-check.sh"
echo "# Runtime notes" > "$FAKE_HOME/.agents/skills/mcp-repair/references/runtime-compatibility.md"
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

# Plant a fake OpenAI-style token in an owned skill's Markdown
echo 'token: sk-ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890' >> "$FAKE_HOME/.agents/skills/mcp-repair/SKILL.md"
output="$(HOME="$FAKE_HOME" bash "$FAKE_REPO/.claude-dotfiles/backup.sh" 2>&1 || true)"
if echo "$output" | grep -q "ERROR: Possible secret"; then
  pass "guard scans Markdown in owned agent skills"
else
  fail "guard DID NOT scan Markdown in owned agent skills"
fi

# Restore again
echo "# MCP Repair" > "$FAKE_HOME/.agents/skills/mcp-repair/SKILL.md"
HOME="$FAKE_HOME" bash "$FAKE_REPO/.claude-dotfiles/backup.sh" > /dev/null

# ── Test 5: op read pattern passes the guard ───────────────────────────────────

echo ""
echo "--- Test 5: op read pattern is allowed ---"
printf 'export GH="$(op read '"'"'op://Employee/github-pat/credential'"'"' 2>/dev/null)"\n' >> "$FAKE_HOME/.zshrc"
output="$(HOME="$FAKE_HOME" bash "$FAKE_REPO/.claude-dotfiles/backup.sh" 2>&1)"
if echo "$output" | grep -q "ERROR"; then
  fail "guard incorrectly blocked op read pattern"
else
  pass "op read pattern is allowed through"
fi

# ── Test 6: Restore preserves canonical ownership and Claude adapter ──────────

echo ""
echo "--- Test 6: Owned skill restore ---"
HOME="$RESTORE_HOME" DOTFILES="$FAKE_REPO/.claude-dotfiles" \
  bash -c 'source "$DOTFILES/lib/owned-agent-skills.sh"; restore_owned_agent_skills false' > /dev/null

if [ -f "$RESTORE_HOME/.agents/skills/mcp-repair/SKILL.md" ]; then
  pass "owned skill restored to canonical ~/.agents location"
else
  fail "owned skill was not restored to canonical ~/.agents location"
fi
if [ -L "$RESTORE_HOME/.claude/skills/mcp-repair" ] && \
   [ "$(readlink "$RESTORE_HOME/.claude/skills/mcp-repair")" = "../../.agents/skills/mcp-repair" ]; then
  pass "Claude adapter points to canonical shared skill"
else
  fail "Claude adapter was not created correctly"
fi
if [ ! -e "$RESTORE_HOME/.agents/skills/vendor-skill" ]; then
  pass "non-allowlisted skill was not restored"
else
  fail "non-allowlisted skill was restored"
fi

echo "# Local newer copy" > "$RESTORE_HOME/.agents/skills/mcp-repair/SKILL.md"
HOME="$RESTORE_HOME" DOTFILES="$FAKE_REPO/.claude-dotfiles" \
  bash -c 'source "$DOTFILES/lib/owned-agent-skills.sh"; restore_owned_agent_skills false' > /dev/null 2>&1
if grep -q "Local newer copy" "$RESTORE_HOME/.agents/skills/mcp-repair/SKILL.md"; then
  pass "restore preserves an existing local skill"
else
  fail "restore overwrote an existing local skill"
fi

# ── Test 7: Missing allowlisted source fails safely ────────────────────────────

echo ""
echo "--- Test 7: Missing allowlisted source ---"
mv "$FAKE_HOME/.agents/skills/mcp-repair" "$FAKE_HOME/.agents/skills/mcp-repair.missing"
output="$(HOME="$FAKE_HOME" bash "$FAKE_REPO/.claude-dotfiles/backup.sh" 2>&1 || true)"
if echo "$output" | grep -q "Allowlisted agent skill is missing"; then
  pass "missing allowlisted source aborts backup"
else
  fail "missing allowlisted source did not abort backup"
fi
if [ -f "$FAKE_REPO/.claude-dotfiles/.agents/skills/mcp-repair/SKILL.md" ]; then
  pass "existing backup survives a missing source"
else
  fail "existing backup was removed when source was missing"
fi
mv "$FAKE_HOME/.agents/skills/mcp-repair.missing" "$FAKE_HOME/.agents/skills/mcp-repair"

# ── Results ────────────────────────────────────────────────────────────────────

echo ""
echo "=============================="
printf "  %d passed, %d failed\n" "$PASS" "$FAIL"
echo "=============================="
[ "$FAIL" -eq 0 ]

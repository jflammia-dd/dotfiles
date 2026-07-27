#!/usr/bin/env python3
"""Resolve obsidian:// URIs in a prompt to absolute vault file paths.

Fires on UserPromptSubmit. Emits additionalContext naming the file Obsidian
itself would open (and the line number of any #heading or ^block subpath) so the
file can be read without decoding the URI by hand. Silent when a prompt has no
obsidian:// link.

Parsing and resolution mirror the shipped Obsidian bundle
(Obsidian.app/Contents/Resources/obsidian.asar), transcribed from v1.12.7:

  main.js  $e()                  URI parse + vault selection (main process)
  app.js   Ek()                  URI parse (renderer, same grammar)
  app.js   "open" handler        parseLinktext -> normalizePath -> getFirstLinkpathDest
  app.js   getLinkpathDest()     candidate lookup and tie-break
  main.js  Re()                  vault name-or-id lookup
  app.js   cu()/uu()/tu()        path normalization
  app.js   VL                    tie-break comparator (shortest path wins)

Run with --selftest to exercise the resolver against a temporary vault.
"""

import json
import os
import re
import sys
import unicodedata

SCHEME = "obsidian://"
OBSIDIAN_CONFIG = os.path.expanduser(
    "~/Library/Application Support/obsidian/obsidian.json"
)

# Actions that name a file to open. Everything else is reported without resolving.
CREATE_ACTIONS = {"new", "daily", "unique"}
KNOWN_ACTIONS = {
    "open",
    "search",
    "choose-vault",
    "sync-setup",
    "vault-setup",
    "hook-get-address",
    "show-plugin",
    "show-theme",
    "show-release-notes",
    "debug-info",
    "publish-sites",
} | CREATE_ACTIONS

# decodeURI leaves escapes for reserved characters intact; decodeURIComponent
# decodes everything. The three-slash shorthand uses the former, query values
# use the latter.
RESERVED = ";/?:@&=+$,#"

LINK_RE = re.compile(r"obsidian://[^\s<>\"'`)\]}]+")
HEX2 = re.compile(r"[0-9A-Fa-f]{2}")


def nfc(text):
    return unicodedata.normalize("NFC", text)


def decode_component(text):
    """decodeURIComponent: every escape decoded, '+' stays a literal plus."""
    out = bytearray()
    i = 0
    while i < len(text):
        if text[i] == "%" and HEX2.fullmatch(text[i + 1 : i + 3] or ""):
            out.append(int(text[i + 1 : i + 3], 16))
            i += 3
        else:
            out += text[i].encode("utf-8")
            i += 1
    return out.decode("utf-8", "replace")


def decode_uri(text):
    """decodeURI: like the above, but escapes for reserved characters survive."""
    out = bytearray()
    i = 0
    while i < len(text):
        if text[i] == "%" and HEX2.fullmatch(text[i + 1 : i + 3] or ""):
            byte = int(text[i + 1 : i + 3], 16)
            if byte < 0x80 and chr(byte) in RESERVED:
                out += text[i : i + 3].encode("ascii")
            else:
                out.append(byte)
            i += 3
        else:
            out += text[i].encode("utf-8")
            i += 1
    return out.decode("utf-8", "replace")


def find_links(prompt):
    """Extract obsidian:// URIs, dropping shell escaping and trailing punctuation."""
    links = []
    for raw in LINK_RE.findall(prompt):
        link = re.sub(r"\\(.)", r"\1", raw).rstrip(".,;:!?")
        while link.endswith(")") and link.count(")") > link.count("("):
            link = link[:-1]
        if link not in links:
            links.append(link)
    return links


def parse_uri(uri):
    """Parse an obsidian:// URI into action and parameters, mirroring main.js $e()."""
    if not uri.startswith(SCHEME):
        return None
    rest = uri[len(SCHEME) :]
    params = {}

    if rest.startswith("/"):
        # obsidian:///absolute/path/to/note — on Windows one leading slash is dropped.
        params["action"] = "open"
        params["path"] = decode_uri(rest)
        return params

    if rest.startswith("vault/"):
        # obsidian://vault/<vault name>/<path/to/note>, each segment decoded alone.
        segments = [decode_component(s) for s in rest[6:].split("/")]
        params["action"] = "open"
        params["vault"] = segments[0]
        params["file"] = "/".join(segments[1:])
        return params

    query = ""
    question = rest.find("?")
    # The '#' search starts at the '?', so a '#' in the action itself is not a hash.
    hash_at = rest.find("#", max(0, question))
    if hash_at >= 0:
        params["hash"] = rest[hash_at + 1 :]
        rest = rest[:hash_at]
    if question >= 0:
        query = rest[question + 1 :]
        rest = rest[:question]
    for pair in query.split("&"):
        if not pair:
            continue
        key, sep, value = pair.partition("=")
        # A param with no '=' is the string "true"; a repeated param takes the last value.
        params[decode_component(key)] = decode_component(value) if sep else "true"
    params["action"] = re.sub(r"/+$", "", rest)
    return params


def registered_vaults():
    """Return [(vault_id, path)] from Obsidian's own vault registry."""
    try:
        with open(OBSIDIAN_CONFIG) as handle:
            vaults = json.load(handle).get("vaults", {})
    except (OSError, ValueError, AttributeError):
        return []
    return [(vid, v["path"]) for vid, v in vaults.items() if v.get("path")]


def vault_for_name_or_id(token):
    """Match a vault by its id, or by folder name case-insensitively."""
    for vault_id, path in registered_vaults():
        if vault_id == token:
            return path
        if os.path.basename(path.rstrip("/")).upper() == token.upper():
            return path
    return None


def vault_for_path(absolute):
    """Return (vault path, vault-relative remainder) for the longest containing vault."""
    absolute = os.path.abspath(absolute)
    best = None
    for _, path in registered_vaults():
        # ponytail: prefix test only, matching Obsidian's own startsWith check, so
        # /vaults/Foo also claims /vaults/Foobar. Faithful beats tidy here.
        if absolute.startswith(path) and (best is None or len(path) > len(best)):
            best = path
    if best is None:
        return None, None
    return best, absolute[len(best) :]


def default_vault():
    """Obsidian falls back to the focused window; approximate that from the session."""
    vaults = registered_vaults()
    if len(vaults) == 1:
        return vaults[0][1]
    project = os.environ.get("CLAUDE_PROJECT_DIR", "")
    for _, path in vaults:
        if project and os.path.abspath(project) == os.path.abspath(path):
            return path
    return None


def normalize_path(ref):
    """Obsidian's cu(): collapse separators, trim slashes, NBSP to space, NFC."""
    ref = re.sub(r"[\\/]+", "/", ref).strip("/")
    if ref == "":
        ref = "/"
    return nfc(ref.replace("\u00A0", " ").replace("\u202F", " "))


def parse_linktext(ref):
    """Obsidian's parseLinktext(): split at the first '#'; subpath keeps the '#'."""
    at = ref.find("#")
    if at < 0:
        return ref, ""
    return ref[:at], ref[at:]


def build_index(root):
    """Map lowercased NFC basename to vault-relative paths, skipping hidden entries."""
    index = {}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        for filename in sorted(filenames):
            if filename.startswith("."):
                continue
            rel = os.path.relpath(os.path.join(dirpath, filename), root)
            index.setdefault(nfc(filename).lower(), []).append(rel)
    return index


def linkpath_dest(index, ref):
    """Obsidian's getLinkpathDest() with an empty source path, best match first.

    Candidates are every vault file sharing the basename, matched case-insensitively.
    An exact full-path match wins; otherwise suffix matches sort shortest-path first.
    """
    ref = normalize_path(ref)
    lowered = ref.lower()
    base = lowered.rsplit("/", 1)[-1]
    candidates = index.get(base) if "." in base else None
    if not candidates:
        lowered = (ref + ".md").lower()
        base = lowered.rsplit("/", 1)[-1]
        candidates = index.get(base)
    if not candidates:
        return []

    def key(rel):
        return nfc(rel).replace(os.sep, "/").lower()

    # A bare basename with exactly one holder resolves immediately.
    if base == lowered and len(candidates) == 1:
        return list(candidates)
    for rel in candidates:
        if key(rel) == lowered:
            return [rel]
    matches = [rel for rel in candidates if key(rel).endswith(lowered)]
    # VL sorts by path length. Sorting by key first keeps equal lengths reproducible,
    # where Obsidian's order falls out of its own scan order.
    return sorted(sorted(matches, key=key), key=lambda rel: len(key(rel)))
    # Obsidian also has a leading-slash guard here. normalize_path strips leading
    # slashes before this function sees the ref, so that branch is unreachable.


def fragment_line(path, fragment):
    """Return the 1-indexed line of a heading or ^block-id, or None."""
    if not fragment:
        return None
    block = fragment.startswith("^")
    wanted = nfc(fragment.lstrip("^").strip()).lower()
    try:
        with open(path, encoding="utf-8", errors="replace") as handle:
            for number, line in enumerate(handle, 1):
                line = nfc(line)
                if block:
                    if "^" + wanted in line.lower():
                        return number
                elif line.startswith("#"):
                    text = line.lstrip("#").strip().rstrip("#").strip()
                    if text.lower() == wanted:
                        return number
    except OSError:
        return None
    return None


def describe_open(root, ref, hash_param):
    """Resolve an open action's file reference to a context line."""
    ref, subpath = parse_linktext(ref)
    fragment = subpath[1:] if subpath else ""
    note = ""
    if not fragment and hash_param:
        # Obsidian's open handler reads the subpath from `file` and ignores a
        # top-level #hash, so name the target but say the app would not jump.
        fragment = hash_param
        note = " (Obsidian itself ignores a top-level #hash; encode it as %23 in file)"

    matches = linkpath_dest(build_index(root), ref)
    if not matches:
        return (
            "Obsidian link unresolved: no file matching {!r} in vault {}. "
            "Invoke the obsidian-link skill.".format(ref, root)
        )

    path = os.path.join(root, matches[0])
    line = "Obsidian link resolved: {}".format(path)
    if fragment:
        number = fragment_line(path, fragment)
        if number:
            line += ' (fragment "{}" at line {}; read the whole file, lead with that section)'.format(
                fragment, number
            )
        else:
            line += ' (fragment "{}" not found in the file; read the whole file)'.format(
                fragment
            )
    line += note
    if len(matches) > 1:
        line += ". Obsidian picks this one by shortest path; also matching: {}".format(
            ", ".join(matches[1:])
        )
    return line


def describe(uri):
    """Turn one obsidian:// URI into a line of context for the model."""
    params = parse_uri(uri)
    if params is None:
        return None
    action = params.get("action", "")

    absolute = params.get("path")
    if absolute:
        # `path` overrides vault and file, resolving against the most specific vault.
        root, remainder = vault_for_path(absolute)
        if root is None:
            return (
                "Obsidian link unresolved: path={} is not inside any registered "
                "vault.".format(absolute)
            )
        if action in CREATE_ACTIONS:
            return "Obsidian link is a {!r} action targeting {} (no file opened).".format(
                action, os.path.join(root, (remainder or "").lstrip("/"))
            )
        # The remainder keeps its leading slash, as Obsidian's own substr does.
        # normalize_path owns stripping it.
        return describe_open(root, remainder or "", params.get("hash", ""))

    vault = params.get("vault")
    if vault:
        root = vault_for_name_or_id(vault)
        if root is None:
            return (
                "Obsidian link unresolved: vault {!r} is not registered in "
                "Obsidian (matched by name or 16-char id).".format(vault)
            )
    else:
        root = default_vault()
        if root is None:
            return (
                "Obsidian link has no vault parameter and several vaults are "
                "registered; Obsidian would use the focused window. Invoke the "
                "obsidian-link skill."
            )

    if action == "open":
        ref = params.get("file", "")
        if not ref:
            return "Obsidian link opens vault {} with no file.".format(root)
        return describe_open(root, ref, params.get("hash", ""))

    if action in CREATE_ACTIONS:
        target = params.get("file") or params.get("name") or ""
        if not target:
            return "Obsidian link is a {!r} action in vault {}.".format(action, root)
        matches = linkpath_dest(build_index(root), parse_linktext(target)[0])
        where = (
            os.path.join(root, matches[0])
            if matches
            else "{} (does not exist yet)".format(os.path.join(root, target))
        )
        return "Obsidian link is a {!r} action targeting {}; it creates or appends rather than just opening.".format(
            action, where
        )

    if action == "search":
        return "Obsidian link is a search in vault {} for {!r}.".format(
            root, params.get("query", "")
        )

    if action in KNOWN_ACTIONS:
        return "Obsidian link is a {!r} action in vault {}; no file to open.".format(
            action, root
        )
    return "Obsidian link uses unknown action {!r}; Obsidian would reject it.".format(
        action
    )


def context_for(prompt):
    lines = [line for line in (describe(uri) for uri in find_links(prompt)) if line]
    return "\n".join(lines)


def selftest():
    import shutil
    import tempfile

    global OBSIDIAN_CONFIG
    root = tempfile.mkdtemp(suffix="-Datadog")
    name = os.path.basename(root)
    try:
        os.makedirs(os.path.join(root, "docs"))
        os.makedirs(os.path.join(root, "agents", "workflows"))
        os.makedirs(os.path.join(root, ".claude", "commands"))
        os.makedirs(os.path.join(root, "attachments"))
        note = os.path.join(root, "docs", "Foo Bar - Review Feedback.md")
        with open(note, "w") as handle:
            handle.write("# Title\n\ntext\n\n## Action Items\n\n- thing ^abc123\n")
        for rel in [
            "docs/log.md",
            "agents/workflows/log.md",
            ".claude/commands/log.md",
            "attachments/diagram.png",
            "docs/v1.2 spec.md",
        ]:
            with open(os.path.join(root, rel), "w") as handle:
                handle.write("x\n")

        config = os.path.join(root, "obsidian.json")
        with open(config, "w") as handle:
            json.dump(
                {
                    "vaults": {
                        "ef6ca3e3b524d22f": {"path": root},
                        "0000000000000000": {"path": "/nonexistent/Other"},
                    }
                },
                handle,
            )
        OBSIDIAN_CONFIG = config
        index = build_index(root)

        # --- URI grammar (main.js $e / app.js Ek) ---
        assert parse_uri("http://example.com") is None
        assert parse_uri("obsidian://open/?file=a")["action"] == "open"
        assert parse_uri("obsidian://search?query=x")["action"] == "search"
        assert parse_uri("obsidian://open?file=a&file=b")["file"] == "b"
        assert parse_uri("obsidian://open?file=a&silent")["silent"] == "true"
        assert parse_uri("obsidian://open?file=a+b")["file"] == "a+b"
        assert parse_uri("obsidian://open?file=a#Head")["hash"] == "Head"
        assert parse_uri("obsidian://open?file=a#Head")["file"] == "a"
        assert parse_uri("obsidian://open?file=docs%2FFoo%23Bar")["file"] == (
            "docs/Foo#Bar"
        )
        shorthand = parse_uri("obsidian://vault/" + name + "/docs/Foo%20Bar")
        assert shorthand == {"action": "open", "vault": name, "file": "docs/Foo Bar"}
        # decodeURI keeps reserved escapes; %20 still decodes.
        assert parse_uri("obsidian:///tmp/a%20b%2Fc")["path"] == "/tmp/a b%2Fc"
        assert decode_component("%E2%9C%93") == "✓"

        # --- path normalization (cu / uu / tu) ---
        assert normalize_path("/docs//Foo/") == "docs/Foo"
        assert normalize_path("docs\\Foo") == "docs/Foo"
        assert normalize_path("a\u00A0b") == "a b"
        assert normalize_path("Loïc") == nfc("Loïc")

        # --- linkpath resolution (getLinkpathDest, source path "") ---
        assert linkpath_dest(index, "docs/Foo Bar - Review Feedback") == [
            "docs/Foo Bar - Review Feedback.md"
        ]
        assert linkpath_dest(index, "docs/Foo Bar - Review Feedback.md") == [
            "docs/Foo Bar - Review Feedback.md"
        ]
        assert linkpath_dest(index, "Foo Bar - Review Feedback") == [
            "docs/Foo Bar - Review Feedback.md"
        ]
        assert linkpath_dest(index, "DOCS/foo bar - REVIEW feedback") == [
            "docs/Foo Bar - Review Feedback.md"
        ]
        # Shortest path wins; hidden directories are outside the vault index.
        assert linkpath_dest(index, "log") == ["docs/log.md", "agents/workflows/log.md"]
        assert linkpath_dest(index, "agents/workflows/log") == [
            "agents/workflows/log.md"
        ]
        # A dotted basename is looked up as given, then retried with .md appended.
        assert linkpath_dest(index, "docs/v1.2 spec") == ["docs/v1.2 spec.md"]
        assert linkpath_dest(index, "diagram.png") == ["attachments/diagram.png"]
        assert linkpath_dest(index, "Nope") == []
        assert linkpath_dest(index, "docs") == []

        # --- vault selection (Re, path prefix, fallback) ---
        assert vault_for_name_or_id("ef6ca3e3b524d22f") == root
        assert vault_for_name_or_id(name.upper()) == root
        assert vault_for_name_or_id("no-such-vault") is None
        assert vault_for_path(note) == (root, "/docs/Foo Bar - Review Feedback.md")
        assert vault_for_path("/elsewhere/x.md") == (None, None)

        # --- subpath targeting ---
        assert parse_linktext("docs/Foo#Bar") == ("docs/Foo", "#Bar")
        assert fragment_line(note, "Action Items") == 5
        assert fragment_line(note, "^abc123") == 7
        assert fragment_line(note, "Missing") is None

        # --- end to end ---
        escaped = (
            r"obsidian://open\?vault=" + name + r"\&file=docs%2FFoo%20Bar%20-"
            r"%20Review%20Feedback%23Action%20Items"
        )
        assert find_links("see " + escaped + ".") == [escaped.replace("\\", "")]
        out = context_for("open " + escaped)
        assert out.startswith("Obsidian link resolved: " + note), out
        assert 'fragment "Action Items" at line 5' in out, out

        out = context_for("obsidian://open?vault=" + name + "&file=log")
        assert os.path.join(root, "docs/log.md") in out
        assert "also matching: agents/workflows/log.md" in out, out

        out = context_for("obsidian://vault/" + name + "/docs/log")
        assert os.path.join(root, "docs/log.md") in out, out

        out = context_for("obsidian:///" + note.lstrip("/").replace(" ", "%20"))
        assert out.startswith("Obsidian link resolved: " + note), out

        out = context_for("obsidian://open?path=" + note.replace(" ", "%20"))
        assert out.startswith("Obsidian link resolved: " + note), out

        out = context_for("obsidian://new?vault=" + name + "&file=docs/Fresh")
        assert "'new' action" in out and "does not exist yet" in out, out

        out = context_for("obsidian://search?vault=" + name + "&query=risk%20score")
        assert "search in vault" in out and "risk score" in out, out

        out = context_for("obsidian://open?vault=" + name + "&file=Ghost")
        assert out.startswith("Obsidian link unresolved:"), out

        out = context_for("obsidian://open?vault=Missing&file=x")
        assert "is not registered" in out, out

        out = context_for("obsidian://frobnicate?vault=" + name)
        assert "unknown action" in out, out

        out = context_for("obsidian://open?vault=" + name + "&file=docs%2Flog#Bar")
        assert "Obsidian itself ignores a top-level #hash" in out, out

        assert context_for("no links here") == ""
        assert context_for("[note](obsidian://open?vault=" + name + "&file=log)") != ""
    finally:
        shutil.rmtree(root)
    print("ok")


def main():
    if "--selftest" in sys.argv:
        selftest()
        return
    try:
        prompt = json.load(sys.stdin).get("prompt", "")
    except (ValueError, OSError, AttributeError):
        return
    context = context_for(prompt)
    if context:
        json.dump(
            {
                "hookSpecificOutput": {
                    "hookEventName": "UserPromptSubmit",
                    "additionalContext": context,
                }
            },
            sys.stdout,
        )


if __name__ == "__main__":
    main()

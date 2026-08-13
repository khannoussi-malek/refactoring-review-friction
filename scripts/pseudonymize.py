#!/usr/bin/env python3
"""
pseudonymize.py — identity firewall for closed-source subject repos.

Some subjects in this study are private industrial codebases reported under a
pseudonym ("Private Project 1", slug pp1). Nothing that identifies the owner,
its people, or its product may reach a committed file — this repo is public.

Two zones, enforced by .git/info/exclude (local-only, never pushed):

    private/            raw clone, salt, alias map, unscrubbed extracts
    pp1_*.json          scrubbed aggregates — safe to commit

Design choices worth keeping:

  * Aliases are HMAC(salt, raw), NOT a first-seen counter. A counter leaks
    processing order — A1 would be whoever committed first, i.e. the founder.
  * The salt is 32 random bytes in private/salt.txt. Without it, an unsalted
    hash of an author email is brute-forceable: the candidate space is one
    company's staff directory, not the internet.
  * scrub() is a WHITELIST. Free text (commit messages, branch names) is
    dropped, never regex-redacted. Redacting prose is a game you lose the first
    time someone writes a customer name in a commit message.
  * assert_clean() is the backstop, not the mechanism. Belt and braces.

Usage:
    from pseudonymize import alias, scrub, assert_clean, write_public
    write_public("pp1_episodes.json", rows, keep=("n_files", "lead_time_h"))

Self-check:
    python3 scripts/pseudonymize.py
"""
import hashlib
import hmac
import json
import os
import pathlib

PRIVATE = pathlib.Path(__file__).resolve().parent.parent / "private"
SALT_FILE = PRIVATE / "salt.txt"
MAP_FILE = PRIVATE / "alias_map.json"
NEEDLE_FILE = PRIVATE / "needles.txt"

# Alias prefixes by entity kind. Short, so they read cleanly in a paper table.
PREFIX = {"author": "A", "module": "M", "ticket": "T", "file": "F", "branch": "B"}

_ALIAS_HEX = 8  # 4.3e9 space; collision-free for any realistic team/module count


def _salt():
    """Read the per-machine salt. Refuse to run unsalted — that is the whole point."""
    if not SALT_FILE.exists():
        raise SystemExit(
            f"missing {SALT_FILE}. Generate once:\n"
            f"  python3 -c \"import secrets,pathlib;"
            f"pathlib.Path('{SALT_FILE}').write_text(secrets.token_hex(32))\""
        )
    salt = SALT_FILE.read_text().strip()
    if len(salt) < 32:
        raise SystemExit(f"{SALT_FILE} is too short to be a real salt")
    return salt.encode()


def alias(kind, raw, _cache={}):
    """Stable pseudonym for one identity. Same input+salt -> same alias, forever."""
    if kind not in PREFIX:
        raise ValueError(f"unknown kind {kind!r}; expected one of {sorted(PREFIX)}")
    raw = (raw or "").strip().lower()  # git records the same human many ways
    key = (kind, raw)
    if key not in _cache:
        digest = hmac.new(_salt(), f"{kind}:{raw}".encode(), hashlib.sha256).hexdigest()
        _cache[key] = PREFIX[kind] + digest[:_ALIAS_HEX]
    return _cache[key]


def record_map(kind, raw):
    """Alias + remember the mapping locally, so you can debug 'which module is M1a2b3c4d'.

    The map lives in private/ and is never committed. It is a convenience, not a
    dependency: alias() is stateless and does not read it back.
    """
    a = alias(kind, raw)
    m = json.loads(MAP_FILE.read_text()) if MAP_FILE.exists() else {}
    m.setdefault(kind, {})[a] = raw
    PRIVATE.mkdir(exist_ok=True)
    MAP_FILE.write_text(json.dumps(m, indent=1, sort_keys=True))
    return a


def scrub(row, keep):
    """Project a record down to whitelisted numeric/categorical fields.

    `keep` is an explicit tuple of field names. Anything not named is dropped —
    including fields added upstream later, which is the failure mode a blacklist
    would miss.
    """
    missing = [k for k in keep if k not in row]
    if missing:
        raise KeyError(f"whitelisted fields absent from record: {missing}")
    return {k: row[k] for k in keep}


def _needles():
    """Forbidden substrings (org, domain, product names), one per line, local-only."""
    if not NEEDLE_FILE.exists():
        return []
    return [
        ln.strip().lower()
        for ln in NEEDLE_FILE.read_text().splitlines()
        if ln.strip() and not ln.startswith("#")
    ]


def assert_clean(obj, extra_needles=()):
    """Backstop: raise if any identifying substring survived into `obj`."""
    blob = json.dumps(obj, default=str).lower()
    hits = [n for n in list(_needles()) + list(extra_needles) if n and n in blob]
    if hits:
        raise AssertionError(f"identifying strings would be written: {sorted(set(hits))}")
    return True


def write_public(path, rows, keep):
    """Scrub, verify, then write a committable artifact. The only sanctioned writer."""
    if not os.path.basename(path).startswith("pp1_"):
        raise ValueError(f"public artifacts must be named pp1_*: got {path!r}")
    scrubbed = [scrub(r, keep) for r in rows]
    assert_clean(scrubbed)
    pathlib.Path(path).write_text(json.dumps(scrubbed, indent=1))
    return len(scrubbed)


def demo():
    """Self-check: python3 scripts/pseudonymize.py"""
    a1, a2 = alias("author", "Jane Doe <jane@example.com>"), alias("author", "jane doe <JANE@EXAMPLE.COM>")
    assert a1 == a2, "alias must be case/whitespace stable"
    assert a1.startswith("A") and len(a1) == 1 + _ALIAS_HEX
    assert alias("module", "jane doe <jane@example.com>") != a1, "kind must namespace the alias"

    # No ordering leak: aliases carry no information about assignment sequence.
    assert not alias("author", "first@x.com").endswith("1")

    row = {"author": "jane@example.com", "module": "billing", "lead_time_h": 42, "msg": "fix ACME bug"}
    kept = scrub(row, ("lead_time_h",))
    assert kept == {"lead_time_h": 42}, "scrub must drop everything not whitelisted"
    try:
        scrub(row, ("nonexistent",))
        raise SystemExit("scrub should have raised on a missing whitelisted field")
    except KeyError:
        pass

    try:
        assert_clean({"note": "built by ACME Corp"}, extra_needles=("acme",))
        raise SystemExit("assert_clean should have caught the needle")
    except AssertionError:
        pass
    assert assert_clean({"lead_time_h": 42}, extra_needles=("acme",))

    try:
        write_public("leaky.json", [row], ("lead_time_h",))
        raise SystemExit("write_public should reject a non-pp1_ filename")
    except ValueError:
        pass

    print("pseudonymize self-check OK")


if __name__ == "__main__":
    demo()

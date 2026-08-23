#!/usr/bin/env python3
"""
pseudonymize_caches.py — replace real email addresses in the frozen Jira
cache files with deterministic salted pseudonyms.

Background: the v1 Zenodo deposit (10.5281/zenodo.21846139) shipped
jira-caches.zip with a description claiming developer email addresses were
"replaced with salted pseudonyms." That step was never run before upload.
1,525 occurrences of 18 real addresses (e.g. dev-a1b2c3d4e5f6@example.invalid
as a stand-in here for the kind of address found — personal Gmail/Yahoo/
corporate addresses) were found live in the .jira_assignee and .jira_cache
JSON. This script is the step that should have run first.

Scope: only values that look like email addresses (RFC-5322-ish pattern —
this covers the flat "assignee"/"reporter" string fields in .jira_assignee,
and any email-shaped string anywhere else in the tree). It does NOT touch
displayName or Jira username ("name") fields — the same archive also carries
14,272 displayName occurrences (190 distinct real people, e.g. "Steve
Loughran") and 14,292 username occurrences (196 distinct handles, e.g.
"snemeth"). Whether those get pseudonymized too is a separate, undecided
scope question — see deposit/V2_CORRECTION.md. This script only closes the
gap the v1 description explicitly promised: addresses.

Salt: 32 random bytes (secrets.token_bytes), generated fresh each run and
printed once to stderr. It is never written to disk, never returned by any
function here, and never logged anywhere else. Once the process exits, the
mapping from real address to pseudonym is one-way — nobody, including the
author, can recover it without having independently captured that printed
salt. That is deliberate: a retained salt defeats the purpose.

Determinism is per-run, not across runs: within one run, the same address
always maps to the same pseudonym (HMAC-SHA256(salt, address)), so
co-authorship and assignment patterns in the data survive intact. Two
separate runs use two different random salts and so produce two different
(but each internally consistent) pseudonym sets — there is no way to ask
for the same mapping twice, by design.

Idempotent in the only sense compatible with a random salt: a value already
in the synthetic form dev-<12 hex>@example.invalid is recognized and passed
through untouched, so running this script again on its OWN prior output is a
no-op. The all-pseudonymized state is a stable fixed point; the mapping that
produced it is not reproducible, and should not be.

Everything else — commit hashes, issue keys, timestamps, displayName,
usernames, and all other fields — passes through byte-unchanged.

Usage:
    python3 scripts/pseudonymize_caches.py <src_dir> <dst_dir>

    Walks every .json file under src_dir (recursively), plus the contents of
    any nested *.tar.gz archive it finds, rewriting email-shaped string
    values. Writes the result under dst_dir with the same relative layout.
    dst_dir must not already exist. src_dir is never modified.

Self-check: python3 scripts/pseudonymize_caches.py --selftest
"""
import hashlib
import hmac
import json
import os
import re
import secrets
import shutil
import sys
import tarfile

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
ALREADY_PSEUDONYMIZED = re.compile(r"^dev-[0-9a-f]{12}@example\.invalid$")


def make_pseudonym(address, salt):
    digest = hmac.new(salt, address.lower().encode("utf-8"), hashlib.sha256).hexdigest()
    return f"dev-{digest[:12]}@example.invalid"


def pseudonymize_string(s, salt, cache):
    def repl(m):
        addr = m.group(0)
        if ALREADY_PSEUDONYMIZED.match(addr):
            return addr
        if addr not in cache:
            cache[addr] = make_pseudonym(addr, salt)
        return cache[addr]

    return EMAIL_RE.sub(repl, s)


def pseudonymize_value(v, salt, cache):
    if isinstance(v, str):
        return pseudonymize_string(v, salt, cache)
    if isinstance(v, dict):
        return {k: pseudonymize_value(val, salt, cache) for k, val in v.items()}
    if isinstance(v, list):
        return [pseudonymize_value(x, salt, cache) for x in v]
    return v


def pseudonymize_json_file(src_path, dst_path, salt, cache):
    with open(src_path, encoding="utf-8") as f:
        data = json.load(f)
    data = pseudonymize_value(data, salt, cache)
    with open(dst_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
        f.write("\n")


def pseudonymize_tarball(src_tar, dst_tar, salt, cache):
    extract_dir = dst_tar + ".extract_tmp"
    out_dir = dst_tar + ".out_tmp"
    for d in (extract_dir, out_dir):
        if os.path.exists(d):
            shutil.rmtree(d)
    os.makedirs(extract_dir)
    os.makedirs(out_dir)
    with tarfile.open(src_tar, "r:gz") as tf:
        tf.extractall(extract_dir)  # trusted source: our own frozen deposit
    walk_and_pseudonymize(extract_dir, out_dir, salt, cache)
    with tarfile.open(dst_tar, "w:gz") as tf:
        for entry in sorted(os.listdir(out_dir)):
            tf.add(os.path.join(out_dir, entry), arcname=entry)
    shutil.rmtree(extract_dir)
    shutil.rmtree(out_dir)


def walk_and_pseudonymize(src_dir, dst_dir, salt, cache):
    for root, _dirs, files in os.walk(src_dir):
        rel = os.path.relpath(root, src_dir)
        out_root = dst_dir if rel == "." else os.path.join(dst_dir, rel)
        os.makedirs(out_root, exist_ok=True)
        for name in sorted(files):
            src_path = os.path.join(root, name)
            dst_path = os.path.join(out_root, name)
            if name.endswith(".json"):
                pseudonymize_json_file(src_path, dst_path, salt, cache)
            elif name.endswith(".tar.gz"):
                pseudonymize_tarball(src_path, dst_path, salt, cache)
            else:
                shutil.copy2(src_path, dst_path)


def selftest():
    salt = secrets.token_bytes(32)
    cache = {}

    # Note: this must be an address that does NOT already match
    # ALREADY_PSEUDONYMIZED, or the idempotency guard below would treat it as
    # already-done and skip transforming it, defeating this check silently.
    # "dev-a1b2c3d4e5f6@example.invalid" (used elsewhere in this file purely
    # as illustrative prose) would fail for exactly that reason if used here.
    real_input = "developer@example.org"
    a = pseudonymize_string(f"{real_input} opened this", salt, cache)
    b = pseudonymize_string(f"cc: {real_input} again", salt, cache)
    pseudonym = cache[real_input]
    assert pseudonym in a and pseudonym in b, "same address must map to the same pseudonym within a run"
    assert real_input not in a and real_input not in b, "real address must not survive"
    assert ALREADY_PSEUDONYMIZED.match(pseudonym), "pseudonym must match the declared format"

    pseudonymize_string("other@example.org", salt, cache)
    assert cache["other@example.org"] != pseudonym, "different addresses must map to different pseudonyms"

    passthrough = pseudonymize_value(
        {"sha": "abc123", "key": "HADOOP-1", "ts": "2026-07-19T00:00:00Z", "n": 5, "flag": True, "nil": None},
        salt,
        cache,
    )
    assert passthrough == {
        "sha": "abc123",
        "key": "HADOOP-1",
        "ts": "2026-07-19T00:00:00Z",
        "n": 5,
        "flag": True,
        "nil": None,
    }, "non-address fields must pass through byte-unchanged"

    once = pseudonymize_string(a, salt, cache)
    assert once == a, "an already-pseudonymized value must be a no-op (idempotent fixed point)"

    nested = pseudonymize_value({"assignee": "x@y.com", "reporter": "x@y.com"}, salt, cache)
    assert nested["assignee"] == nested["reporter"], "repeated address within one structure must stay consistent"

    print("selftest: OK", file=sys.stderr)


def main():
    if len(sys.argv) == 2 and sys.argv[1] == "--selftest":
        selftest()
        return

    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)

    src_dir, dst_dir = sys.argv[1], sys.argv[2]
    if os.path.exists(dst_dir):
        print(f"refusing to overwrite existing dst_dir: {dst_dir}", file=sys.stderr)
        sys.exit(1)
    if not os.path.isdir(src_dir):
        print(f"src_dir does not exist: {src_dir}", file=sys.stderr)
        sys.exit(1)

    salt = secrets.token_bytes(32)
    print(f"salt (printed once, not retained): {salt.hex()}", file=sys.stderr)

    cache = {}
    os.makedirs(dst_dir)
    walk_and_pseudonymize(src_dir, dst_dir, salt, cache)

    print(f"pseudonymized {len(cache)} distinct addresses", file=sys.stderr)


if __name__ == "__main__":
    main()

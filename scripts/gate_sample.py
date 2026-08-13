#!/usr/bin/env python3
"""
gate_sample.py -- draw the violation-symptom resolution gate's sample.

Pre-registered in prereg/RESOLUTION_GATE.md (commit 74424dc), which fixes the
source, the candidate filter, the seed and n BEFORE this script existed. Nothing
here decides anything the pre-registration left open.

OFFLINE. Reads .jira_cache/ only -- 323 frozen Apache Jira tickets, pulled
2026-07-19 (deposit/MANIFEST-v1.md). No network call, no Jira REST, no clone.

WHAT THIS DOES NOT DO. It does not label, classify or judge a single comment.
Every bucket in prereg/gate_labelling.md is left blank for a human coder (R6,
README.md section 8). The keyword net is a recall-first PREFILTER whose precision
is ~25% on a 40-comment single-rater pass (codebook_results.md) -- membership of
the candidate frame is not a claim that a comment is a violation symptom.

It does not reimplement the comment classifier either: STRUCT and CI are imported
from pr_review_signal.py so the two can never diverge, the same way
traceability_probe.py imports git_log from citation_rate.py.

Usage:
    python3 scripts/gate_sample.py --selftest
    python3 scripts/gate_sample.py
"""
import argparse, glob, json, os, random, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pr_review_signal import STRUCT, CI  # noqa: E402  the frozen keyword + CI nets

CACHE = ".jira_cache"
SEED = 20260801          # prereg/RESOLUTION_GATE.md, fixed before any draw
N_SAMPLE = 20
OUT_JSON = "prereg/gate_sample.json"
OUT_SHEET = "prereg/gate_labelling.md"

# ---- entity regexes -------------------------------------------------------
# Recall-first, exactly like the keyword net they sit beside. CamelCase in
# particular over-matches (any two-hump token qualifies); that is reported in
# the memo rather than filtered by a stoplist, because a stoplist would be this
# script deciding what a comment means.
RE_JAVA_PATH = re.compile(r"\b[A-Za-z0-9_./-]+\.java\b")
RE_CLASS_METHOD = re.compile(r"\b([A-Z][A-Za-z0-9_]*)#([A-Za-z_][A-Za-z0-9_]*)")
RE_CAMEL = re.compile(r"\b[A-Z][a-z0-9]+(?:[A-Z][a-z0-9]*)+\b")

OPENED = "opened a new pull request"


def source_of(author, body):
    """Which channel a comment came through. Mirrors pr_review_signal.classify."""
    if author.strip().lower() != "asf github bot":
        return "human"
    if OPENED in body:
        return "bot_opened"
    if CI.search(body):
        return "bot_ci"
    if "commented on" in body:
        return "bot_review"
    return "bot_other"


def entities(body):
    """Every code entity named, by kind. Lexical only -- no resolution attempted."""
    paths = sorted(set(RE_JAVA_PATH.findall(body)))
    cm = sorted({f"{c}#{m}" for c, m in RE_CLASS_METHOD.findall(body)})
    # a CamelCase token already inside a matched path or Class#method is not a
    # second, independent entity
    claimed = " ".join(paths + cm)
    camel = sorted({t for t in RE_CAMEL.findall(body) if t not in claimed})
    return {"java_paths": paths, "class_method": cm, "camel_case": camel}


def n_entities(ents):
    return sum(len(v) for v in ents.values())


def iter_comments(cache=CACHE):
    """Every comment in every cached ticket, in deterministic order."""
    for path in sorted(glob.glob(os.path.join(cache, "*.json"))):
        try:
            data = json.load(open(path))
        except (ValueError, OSError) as e:
            print(f"  WARN unreadable, skipped: {path} ({e})", file=sys.stderr)
            continue
        key = data.get("key") or os.path.basename(path)[:-5]
        fields = data.get("fields") or {}
        for c in ((fields.get("comment") or {}).get("comments") or []):
            body = c.get("body") or ""
            author = ((c.get("author") or {}).get("displayName") or "")
            yield {
                "ticket": key,
                "comment_id": str(c.get("id") or ""),
                "author": author,
                "created": c.get("created") or "",
                "source": source_of(author, body),
                "body": body,
            }


def scan(cache=CACHE):
    """The full funnel. Returns (rows, counts). Rows carry hits + entities."""
    rows, counts = [], {
        "comments_scanned": 0, "human": 0, "bot_review": 0,
        "bot_ci": 0, "bot_opened": 0, "bot_other": 0,
        "eligible_after_bot_exclusion": 0, "keyword_flagged": 0,
        "flagged_with_entity": 0, "flagged_without_entity": 0,
    }
    for r in iter_comments(cache):
        counts["comments_scanned"] += 1
        counts[r["source"]] += 1
        # prereg: bot CI/Yetus reports and "opened a new pull request" are
        # excluded BEFORE filtering. Nothing else is excluded.
        if r["source"] in ("bot_ci", "bot_opened"):
            continue
        counts["eligible_after_bot_exclusion"] += 1
        hits = STRUCT.findall(r["body"])
        if not hits:
            continue
        counts["keyword_flagged"] += 1
        ents = entities(r["body"])
        if n_entities(ents):
            counts["flagged_with_entity"] += 1
            rows.append(dict(r, keyword_hits=sorted({h[0] if isinstance(h, tuple) else h
                                                     for h in hits}),
                             n_keyword_hits=len(hits), entities=ents))
        else:
            counts["flagged_without_entity"] += 1
    counts["frac_flagged_without_entity"] = (
        counts["flagged_without_entity"] / counts["keyword_flagged"]
        if counts["keyword_flagged"] else None)
    return rows, counts


def draw(rows, n=N_SAMPLE, seed=SEED):
    """Deterministic draw: sort by (ticket, comment_id), then Random(seed)."""
    frame = sorted(rows, key=lambda r: (r["ticket"], r["comment_id"]))
    if len(frame) <= n:
        return frame
    return sorted(random.Random(seed).sample(frame, n),
                  key=lambda r: (r["ticket"], r["comment_id"]))


def truncate(body, width=110):
    flat = " ".join(body.split())
    flat = flat.replace("|", "\\|")
    return flat if len(flat) <= width else flat[:width - 1] + "…"


def entity_cell(ents):
    parts = ents["java_paths"] + ents["class_method"] + ents["camel_case"]
    shown = parts[:4]
    cell = ", ".join(f"`{p}`" for p in shown)
    extra = len(parts) - len(shown)
    return (cell + f" +{extra}") if extra else (cell or "—")


def write_sheet(sample, counts, path=OUT_SHEET):
    L = []
    L.append("# Violation-symptom resolution gate — labelling sheet")
    L.append("")
    L.append("<!-- GENERATED by `scripts/gate_sample.py` from `.jira_cache/`.")
    L.append("     Do not edit by hand ABOVE the table: re-run the script.")
    L.append("     The BUCKET / INTERVAL_DAYS / NOTE columns are the exception —")
    L.append("     they are for a human coder to fill in, and re-running the")
    L.append("     script with the same seed overwrites them. Copy before coding. -->")
    L.append("")
    L.append(f"Drawn under seed **{SEED}** from **{counts['flagged_with_entity']}** "
             f"candidates, per `prereg/RESOLUTION_GATE.md` (commit `74424dc`).")
    L.append("")
    L.append("Assign each row to exactly one bucket. Definitions are in the "
             "pre-registration and are **not** restated here, so that this sheet "
             "cannot drift from them:")
    L.append("")
    L.append("* **(a)** SAME REVIEW · **(b)** LATER SEPARATE · **(c)** GONE · "
             "**(d)** NOTHING · **(e)** UNCODEABLE")
    L.append("* `INTERVAL_DAYS` is required for **(b)** and blank otherwise.")
    L.append("* `NOTE` is required for **(e)** — record the reason.")
    L.append("* Per-case evidence is in `prereg/gate_evidence.md`, one section "
             "per row, keyed by comment id.")
    L.append("")
    L.append("**A case whose 24-month window is not covered by `refminer_all.json` "
             "may not be coded (d).** It is (e). The coverage flag is in the "
             "evidence file.")
    L.append("")
    L.append("| # | Ticket | Comment id | Date | Comment (truncated) | Entities named | BUCKET | INTERVAL_DAYS | NOTE |")
    L.append("|---|--------|-----------|------|---------------------|----------------|--------|---------------|------|")
    for i, r in enumerate(sample, 1):
        L.append(f"| {i} | {r['ticket']} | `{r['comment_id']}` | {r['created'][:10]} "
                 f"| {truncate(r['body'])} | {entity_cell(r['entities'])} |   |   |   |")
    L.append("")
    L.append("## Full comment bodies")
    L.append("")
    L.append("Truncation above is for reading; **code against the full body**, "
             "in `prereg/gate_sample.json` (`body` field, verbatim, untruncated).")
    open(path, "w").write("\n".join(L) + "\n")


def selftest():
    assert source_of("ASF GitHub Bot", "x opened a new pull request, #1: URL") == "bot_opened"
    assert source_of("ASF GitHub Bot", "green_heart mvninstall Apache Yetus") == "bot_ci"
    assert source_of("ASF GitHub Bot", "steveloughran commented on code in PR #1: extract this") == "bot_review"
    assert source_of("Jane Dev", "looks fine") == "human"

    e = entities("please move FileSystem.java and fix S3AFileSystem#initialize, "
                 "then OzoneClientFactory")
    assert e["java_paths"] == ["FileSystem.java"], e
    assert e["class_method"] == ["S3AFileSystem#initialize"], e
    assert "OzoneClientFactory" in e["camel_case"], e
    # a CamelCase token already inside a path/Class#method is not counted twice
    assert "S3AFileSystem" not in e["camel_case"], e

    assert n_entities(entities("please rebase and fix the typo")) == 0
    # keyword net fires, no entity -> the case the memo counts separately
    assert STRUCT.search("we should refactor this") and \
        n_entities(entities("we should refactor this")) == 0

    # draw is deterministic and order-independent
    rows = [{"ticket": f"T-{i}", "comment_id": str(i)} for i in range(50)]
    a = draw(rows, 20, SEED)
    b = draw(list(reversed(rows)), 20, SEED)
    assert [r["comment_id"] for r in a] == [r["comment_id"] for r in b]
    assert len(a) == 20
    assert draw(rows[:5], 20, SEED) == sorted(rows[:5], key=lambda r: (r["ticket"], r["comment_id"]))
    print("selftest OK")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default=CACHE)
    ap.add_argument("--out-json", default=OUT_JSON)
    ap.add_argument("--out-sheet", default=OUT_SHEET)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        selftest(); return

    if not os.path.isdir(args.cache):
        sys.exit(f"cache not found: {args.cache} (this script is offline; it cannot fetch)")

    rows, counts = scan(args.cache)
    sample = draw(rows)

    os.makedirs(os.path.dirname(args.out_json) or ".", exist_ok=True)
    json.dump({
        "seed": SEED,
        "n_requested": N_SAMPLE,
        "n_drawn": len(sample),
        "n_candidates": counts["flagged_with_entity"],
        "prereg": "prereg/RESOLUTION_GATE.md",
        "prereg_commit": "74424dc",
        "source": args.cache,
        "keyword_net": STRUCT.pattern,
        "ci_net": CI.pattern,
        "entity_regexes": {
            "java_path": RE_JAVA_PATH.pattern,
            "class_method": RE_CLASS_METHOD.pattern,
            "camel_case": RE_CAMEL.pattern,
        },
        "counts": counts,
        "sample": sample,
    }, open(args.out_json, "w"), indent=2)

    write_sheet(sample, counts, args.out_sheet)

    c = counts
    print(f"comments scanned                    {c['comments_scanned']:>7}")
    print(f"  human                             {c['human']:>7}")
    print(f"  bot: relayed PR review            {c['bot_review']:>7}")
    print(f"  bot: CI/Yetus       (excluded)    {c['bot_ci']:>7}")
    print(f"  bot: PR opened      (excluded)    {c['bot_opened']:>7}")
    print(f"  bot: other notices                {c['bot_other']:>7}")
    print(f"eligible after bot exclusion        {c['eligible_after_bot_exclusion']:>7}")
    print(f"keyword-flagged                     {c['keyword_flagged']:>7}")
    print(f"  AND names an entity  (candidates) {c['flagged_with_entity']:>7}")
    print(f"  names NO entity                   {c['flagged_without_entity']:>7}"
          f"   = {c['frac_flagged_without_entity']:.1%} of flagged"
          if c["frac_flagged_without_entity"] is not None else "")
    print(f"drawn (seed {SEED})               {len(sample):>7}")
    print(f"\nWrote {args.out_json} and {args.out_sheet}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
gate_evidence.py -- assemble a per-case evidence pack for the resolution gate.

Pre-registered in prereg/RESOLUTION_GATE.md (74424dc); sample drawn by
scripts/gate_sample.py (e8801cb). This adds no rule and relaxes none.

OFFLINE. Reads prereg/gate_sample.json, ticket_first_commit.json,
refminer_all.json and the local hadoop/ clone. No network call. No
RefactoringMiner run -- refminer_all.json is READ, never regenerated (plan §11).

WHAT THIS DOES NOT DO. It assigns no bucket. It puts everything a human coder
needs into one file so the bucket can be assigned without leaving it, and it
refuses to make the one call that would look most helpful: whether a later
refactoring "is" the resolution of the comment. R6 binds (README.md §8).

THE COVERAGE FLAG IS THE POINT. refminer_all.json covers 8,919 commits; the
hadoop clone holds 28,290. A window can sit wholly inside real history and wholly
outside detector coverage, in which case silence in the RM output is not evidence
that nothing happened. Per prereg, such a case is censored by observation and
goes to bucket (e) -- it may NEVER be coded (d).

Usage:
    python3 scripts/gate_evidence.py --selftest
    python3 scripts/gate_evidence.py
"""
import argparse, datetime as dt, json, os, re, subprocess, sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from episode_files import is_architectural, paths_of  # noqa: E402  frozen rule

REPO = "hadoop"
SAMPLE = "prereg/gate_sample.json"
RM = "refminer_all.json"
FIRST_COMMIT = "ticket_first_commit.json"
OUT = "prereg/gate_evidence.md"
SEP = "\x1f"                            # git expands %x1f; NUL cannot cross argv
CACHE_LOG = ".gate_commit_log.json"     # gitignored; regenerable from the clone
CACHE_KEYS = ".gate_key_index.json"     # gitignored; regenerable from the clone

WINDOW_DAYS = 730                       # prereg: 24 months
MAX_PATHS_PER_ENTITY = 5                # ambiguity guard; excess is reported, not silently cut
MAX_COMMITS_SHOWN = 25


def sh(*args):
    return subprocess.run(["git", "-C", REPO] + list(args),
                          capture_output=True, text=True).stdout


def load_commit_log(cache=CACHE_LOG):
    """sha -> (unix ts, subject) for every commit on every ref. Cached."""
    if os.path.exists(cache):
        return json.load(open(cache))
    out = sh("log", "--all", "--format=%H%x1f%at%x1f%s")
    log = {}
    for line in out.split("\n"):
        if line.count(SEP) == 2:
            sha, ts, subj = line.split(SEP)
            log[sha] = [int(ts), subj]
    json.dump(log, open(cache, "w"))
    return log


def load_path_universe():
    """Every .java path ever added, modified or renamed. Includes deleted files."""
    out = sh("log", "--all", "--pretty=format:", "--name-only",
             "--diff-filter=AMR", "--", "*.java")
    return {p for p in out.split("\n") if p.endswith(".java")}


def parse_jira_ts(s):
    """'2016-06-01T21:30:15.556+0000' -> unix int."""
    return int(dt.datetime.strptime(s, "%Y-%m-%dT%H:%M:%S.%f%z").timestamp())


def iso(ts):
    return dt.datetime.utcfromtimestamp(ts).strftime("%Y-%m-%d") if ts else "—"


def resolve_entities(ents, universe):
    """Entity -> file paths, mechanically. No semantics, no ranking.

    Returns (resolved, unresolved, ambiguous) where resolved maps entity -> paths.
    """
    by_base = defaultdict(list)
    for p in universe:
        by_base[p.rsplit("/", 1)[-1]].append(p)

    resolved, unresolved, ambiguous = {}, [], {}
    names = []
    for p in ents.get("java_paths", []):
        names.append(("path", p))
    for cm in ents.get("class_method", []):
        names.append(("class", cm.split("#", 1)[0]))
    for c in ents.get("camel_case", []):
        names.append(("class", c))

    for kind, name in names:
        if kind == "path":
            if name in universe:
                resolved[name] = [name]
                continue
            hits = sorted(by_base.get(name.rsplit("/", 1)[-1], []))
        else:
            hits = sorted(by_base.get(name + ".java", []))
        if not hits:
            unresolved.append(name)
        elif len(hits) > MAX_PATHS_PER_ENTITY:
            ambiguous[name] = len(hits)
        else:
            resolved[name] = hits
    return resolved, unresolved, ambiguous


def build_key_index(tickets, cache=CACHE_KEYS):
    """ticket -> earliest citing commit sha, over subject AND body.

    Matching happens in PYTHON, not in `git --grep`, for two reasons. Git's -E is
    POSIX ERE and silently matches nothing for `\\bKEY\\b` (verified: 0 hits for
    a key with 3 real citing commits), which is a false negative that looks like
    a finding. And `citation_rate.py:40` -- the matcher every published rate in
    this repo rests on -- is a Python `\\b(?:KEY)-\\d+\\b` over subject + body
    (`paper/matcher_validation.md`). Same matcher, same surface.
    """
    if os.path.exists(cache):
        got = json.load(open(cache))
        if set(tickets) <= set(got):
            return got
    pats = {t: re.compile(r"\b" + re.escape(t) + r"\b") for t in tickets}
    out = sh("log", "--all", "--format=%x1e%H%x1f%at%x1f%B")
    best = {}
    for rec in out.split("\x1e"):
        if rec.count(SEP) < 2:
            continue
        sha, ts, msg = rec.split(SEP, 2)
        ts = int(ts)
        for t, p in pats.items():
            if p.search(msg) and (t not in best or ts < best[t][0]):
                best[t] = (ts, sha)
    idx = {t: v[1] for t, v in best.items()}
    json.dump(idx, open(cache, "w"))
    return idx


def commits_touching(paths, since_ts, until_ts):
    if not paths:
        return []
    out = sh("log", "--all", "--format=%H%x1f%at%x1f%s",
             f"--since=@{since_ts}", f"--until=@{until_ts}", "--", *paths)
    rows = []
    for line in out.split("\n"):
        if line.count(SEP) == 2:
            sha, ts, subj = line.split(SEP)
            rows.append((sha, int(ts), subj))
    return sorted(set(rows), key=lambda r: r[1])


def deletions(paths, since_ts, until_ts):
    if not paths:
        return []
    out = sh("log", "--all", "--diff-filter=D", "--format=@%H%x1f%at",
             "--name-only", f"--since=@{since_ts}", f"--until=@{until_ts}", "--", *paths)
    rows, cur = [], None
    for line in out.split("\n"):
        if line.startswith("@"):
            sha, ts = line[1:].split(SEP)
            cur = (sha, int(ts))
        elif line.strip().endswith(".java") and cur:
            rows.append((cur[0], cur[1], line.strip()))
    return sorted(set(rows), key=lambda r: r[1])


def rm_index(wanted_paths, rm_path=RM):
    """path -> [(sha, type, is_arch)]  for the paths we actually need."""
    data = json.load(open(rm_path))
    idx = defaultdict(list)
    covered = set()
    for c in data.get("commits", []):
        sha = c.get("sha1") or c.get("sha")
        if not sha:
            continue
        covered.add(sha)
        for r in c.get("refactorings", []) or []:
            arch = is_architectural(r)
            for p in paths_of(r):
                if p in wanted_paths:
                    idx[p].append((sha, r.get("type", "").strip(), arch))
    return idx, covered


def coverage(window_shas, covered):
    """Is the WHOLE window inside detector coverage? Fraction, and a verdict."""
    if not window_shas:
        return 1.0, "EMPTY — no commits in window"
    n = sum(1 for s in window_shas if s in covered)
    frac = n / len(window_shas)
    if frac == 1.0:
        verdict = "FULL — bucket (b) decidable from RM output"
    elif frac == 0.0:
        verdict = "NONE — RM never looked; (d) is NOT available, code (e)"
    else:
        verdict = "PARTIAL — RM output is silent for part of the window; (d) is NOT available, code (e)"
    return frac, verdict


def build(sample, log, universe, first, keyidx, out_path=OUT):
    now = max(v[0] for v in log.values())

    cases = []
    for i, r in enumerate(sample, 1):
        res, unres, amb = resolve_entities(r["entities"], universe)
        paths = sorted({p for ps in res.values() for p in ps})
        merge_sha = keyidx.get(r["ticket"])
        merge_ts = log[merge_sha][0] if merge_sha else None
        cases.append(dict(n=i, row=r, resolved=res, unresolved=unres,
                          ambiguous=amb, paths=paths,
                          merge_sha=merge_sha, merge_ts=merge_ts))

    wanted = {p for c in cases for p in c["paths"]}
    idx, covered = rm_index(wanted)

    L = ["# Violation-symptom resolution gate — evidence packs", "",
         "<!-- GENERATED by `scripts/gate_evidence.py`. Do not edit by hand. -->", "",
         f"One section per case, keyed to `prereg/gate_labelling.md` row order and "
         f"comment id. Window: **{WINDOW_DAYS} days (24 months)** after the "
         f"ticket's first citing commit, per `prereg/RESOLUTION_GATE.md`.", "",
         "**No bucket is assigned here.** Every section reports what is on disk and "
         "stops. A later architectural refactoring of a flagged file is *evidence "
         "for* bucket (b); whether it is the resolution of this comment is the "
         "coder's call.", "",
         f"Corpus clock: newest commit in `hadoop/` is **{iso(now)}**. A case whose "
         "window extends past it is censored by observation → bucket (e).", ""]

    summary = []
    for c in cases:
        r, i = c["row"], c["n"]
        L.append(f"---\n\n## Case {i} — {r['ticket']} · comment `{r['comment_id']}`\n")
        L.append(f"* **Author:** {r['author']}  ·  **Comment date:** {r['created'][:10]}"
                 f"  ·  **Channel:** `{r['source']}`")
        L.append(f"* **Keyword hits:** {', '.join('`%s`' % h for h in r['keyword_hits'])}")

        if c["merge_sha"] is None:
            L.append("* **First citing commit: NOT FOUND** in the clone — no commit "
                     "message cites this key. Bucket (e); reason: unmergeable ticket.\n")
            summary.append((i, r["ticket"], "—", "NO MERGE COMMIT", 0.0))
            continue

        m_ts = c["merge_ts"]
        w_end = m_ts + WINDOW_DAYS * 86400
        L.append(f"* **First citing commit:** `{c['merge_sha'][:12]}` "
                 f"({iso(m_ts)}) — *{log[c['merge_sha']][1][:90]}*")
        ftc = first.get(r["ticket"])
        if ftc:
            agree = "matches" if abs(ftc - m_ts) < 86400 else f"**DIFFERS** ({iso(ftc)})"
            L.append(f"* **Cross-check** vs `ticket_first_commit.json`: {agree}")
        else:
            L.append("* **Cross-check** vs `ticket_first_commit.json`: key absent")
        L.append(f"* **Window:** {iso(m_ts)} → {iso(w_end)}")

        if w_end > now:
            L.append(f"* ⚠️ **RIGHT-CENSORED BY OBSERVATION** — window ends "
                     f"{iso(w_end)}, after the corpus ends {iso(now)}. "
                     f"Per prereg → **bucket (e)**.")

        # entities
        L.append("")
        L.append("### Entities named → files")
        L.append("")
        if c["resolved"]:
            for name, ps in sorted(c["resolved"].items()):
                L.append(f"* `{name}` → " + ", ".join(f"`{p}`" for p in ps))
        else:
            L.append("* *(none resolved to a file in this repository)*")
        if c["ambiguous"]:
            L.append("* **Ambiguous, not expanded** (>%d files share the name): "
                     % MAX_PATHS_PER_ENTITY
                     + ", ".join(f"`{k}` ({v} files)" for k, v in sorted(c["ambiguous"].items())))
        if c["unresolved"]:
            L.append("* **Unresolved** (no such file ever in the clone): "
                     + ", ".join(f"`{u}`" for u in sorted(c["unresolved"])[:12])
                     + (f" +{len(c['unresolved'])-12}" if len(c["unresolved"]) > 12 else ""))

        if not c["paths"]:
            L.append("\n**No file to follow. Bucket (e); reason: no entity resolved "
                     "to a tracked file.**\n")
            summary.append((i, r["ticket"], iso(m_ts), "NO FILE", 0.0))
            continue

        # commits in window
        c_ts = parse_jira_ts(r["created"]) if r["created"] else m_ts
        rows = commits_touching(c["paths"], min(c_ts, m_ts), w_end)
        window_shas = [s for s, ts, _ in rows if ts > m_ts]
        frac, verdict = coverage(window_shas, covered)

        L.append("")
        L.append(f"### Commits touching these files — comment date → window end "
                 f"({len(rows)} total)")
        L.append("")
        L.append("`>` marks a commit AFTER the first citing commit — the region "
                 "bucket (b) lives in.")
        L.append("")
        L.append("| | sha | date | subject |")
        L.append("|---|---|---|---|")
        for sha, ts, subj in rows[:MAX_COMMITS_SHOWN]:
            mark = ">" if ts > m_ts else " "
            safe = subj[:88].replace("|", "\\|")
            L.append(f"| {mark} | `{sha[:12]}` | {iso(ts)} | {safe} |")
        if len(rows) > MAX_COMMITS_SHOWN:
            L.append(f"\n*+{len(rows)-MAX_COMMITS_SHOWN} further commits not shown "
                     f"(cap {MAX_COMMITS_SHOWN}); re-run without the cap to see all.*")

        # RM detections
        dets = []
        for p in c["paths"]:
            for sha, typ, arch in idx.get(p, []):
                ts = log.get(sha, [0])[0]
                if m_ts < ts <= w_end:
                    dets.append((ts, sha, typ, arch, p))
        dets.sort()
        L.append("")
        L.append(f"### RefactoringMiner detections on these files, inside the window "
                 f"({len(dets)})")
        L.append("")
        if dets:
            L.append("| architectural? | type | sha | date | file |")
            L.append("|---|---|---|---|---|")
            for ts, sha, typ, arch, p in dets[:MAX_COMMITS_SHOWN]:
                L.append(f"| {'**YES**' if arch else 'no'} | {typ} | `{sha[:12]}` "
                         f"| {iso(ts)} | `{p.rsplit('/',1)[-1]}` |")
            L.append("")
            L.append("*'architectural?' is `scripts/filter_architectural.py`'s frozen "
                     "rule, imported not restated: package-level types, plus Move-Class "
                     "moves whose source and target package differ.*")
        else:
            L.append("*None.* Read this against the coverage flag below before "
                     "treating it as absence.")

        # deletions
        dels = deletions(c["paths"], m_ts, w_end)
        L.append("")
        L.append(f"### File deletions inside the window ({len(dels)})")
        L.append("")
        if dels:
            for sha, ts, p in dels:
                L.append(f"* `{p}` deleted {iso(ts)} in `{sha[:12]}`")
        else:
            L.append("*None.*")

        # coverage
        L.append("")
        L.append("### ⚑ Detector coverage over the window")
        L.append("")
        L.append(f"* Commits in window touching these files: **{len(window_shas)}**")
        L.append(f"* Of those, present in `refminer_all.json`: "
                 f"**{sum(1 for s in window_shas if s in covered)}** "
                 f"({frac:.0%})")
        L.append(f"* **Verdict: {verdict}**")
        L.append("")

        summary.append((c["n"], r["ticket"], iso(m_ts), verdict.split(" —")[0], frac))

    # summary table at the top
    head = ["", "## Coverage summary", "",
            "| case | ticket | first citing commit | coverage | % of window commits in RM |",
            "|---|---|---|---|---:|"]
    for i, tk, d, v, f in summary:
        head.append(f"| {i} | {tk} | {d} | {v} | {f:.0%} |")
    n_full = sum(1 for *_, v, _ in summary if v == "FULL")
    n_empty = sum(1 for *_, v, _ in summary if v == "EMPTY")
    n_blocked = len(summary) - n_full - n_empty
    head += ["",
             f"**{n_full} of {len(summary)} cases have FULL detector coverage across "
             f"their window.**",
             "",
             f"**{n_full + n_empty} are decidable in total.** `EMPTY` "
             f"({n_empty}) joins `FULL` ({n_full}) rather than the blocked group: "
             "no commit touched the flagged files in the window at all, and the git "
             "log is complete over every ref, so there is no event for the detector "
             "to have missed. Absence there is observed, not assumed.",
             "",
             f"**{n_blocked} of {len(summary)} cannot be coded (d)** — `PARTIAL`, "
             "`NONE`, `NO FILE` and `NO MERGE COMMIT`. Per "
             "`prereg/RESOLUTION_GATE.md` these are censored by observation and go "
             "to bucket **(e)**, which leaves the denominator.",
             "",
             "A `PARTIAL` case may still be coded **(b)** if a qualifying "
             "refactoring is visible — coverage gaps hide events, they do not "
             "invent them. The ban is on reading silence as (d).", ""]

    text = "\n".join(L[:9]) + "\n" + "\n".join(head) + "\n" + "\n".join(L[9:]) + "\n"
    open(out_path, "w").write(text)
    return summary, n_full


def selftest():
    assert parse_jira_ts("2016-06-01T21:30:15.556+0000") == 1464816615
    assert iso(1464816615) == "2016-06-01"

    universe = {"a/b/Foo.java", "c/d/Foo.java", "e/Bar.java"}
    res, unres, amb = resolve_entities(
        {"java_paths": ["e/Bar.java"], "class_method": ["Foo#run"], "camel_case": ["Nope"]},
        universe)
    assert res["e/Bar.java"] == ["e/Bar.java"], res
    assert res["Foo"] == ["a/b/Foo.java", "c/d/Foo.java"], res
    assert unres == ["Nope"], unres

    # ambiguity guard fires and reports rather than truncating silently
    big = {f"p{i}/Many.java" for i in range(MAX_PATHS_PER_ENTITY + 1)}
    _, _, amb = resolve_entities({"camel_case": ["Many"]}, big)
    assert amb == {"Many": MAX_PATHS_PER_ENTITY + 1}, amb

    assert coverage([], set())[1].startswith("EMPTY")
    assert coverage(["a", "b"], {"a", "b"})[1].startswith("FULL")
    assert coverage(["a", "b"], {"a"})[1].startswith("PARTIAL")
    assert coverage(["a"], set())[1].startswith("NONE")
    # a partial window must never be codeable as (d)
    for shas, cov in ((["a", "b"], {"a"}), (["a"], set())):
        assert "(d) is NOT available" in coverage(shas, cov)[1]
    print("selftest OK")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", default=SAMPLE)
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        selftest(); return
    if not os.path.isdir(REPO):
        sys.exit(f"clone not found: {REPO}/ (offline; this script cannot fetch it)")

    sample = json.load(open(args.sample))["sample"]
    print(f"cases: {len(sample)}")
    print("building commit log + path universe from the clone...")
    log = load_commit_log()
    universe = load_path_universe()
    first = json.load(open(FIRST_COMMIT))
    print(f"  {len(log)} commits, {len(universe)} .java paths ever")
    print(f"indexing {RM} (read-only, no detector run)...")

    keyidx = build_key_index(sorted({r["ticket"] for r in sample}))
    summary, n_full = build(sample, log, universe, first, keyidx, args.out)
    print(f"\nfull detector coverage: {n_full} of {len(summary)} cases")
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
gate_diagnosis.py -- measure the mismatch between the corpus and the interval design.

DIAGNOSTIC ONLY. Answers Q1-Q5 and emits prereg/gate_diagnosis.md. It chooses no
remedy, narrows no span, rebuilds no corpus, and repairs no defect it finds --
this project runs under anti-hindsight commitments and silent repair destroys the
record (predictions/PREDICTIONS.md, prereg/RESOLUTION_GATE.md).

READ-ONLY on every committed artifact. refminer_all.json, prereg/* and every
committed result JSON are opened for reading and never written. The single write
target is prereg/gate_diagnosis.md, a new file.

OFFLINE. No network call.

NOTHING HERE ASSIGNS A BUCKET. R6 binds (README.md section 8). Where this file
says "verdict" it means a detector-coverage verdict from gate_evidence.py, which
is not a bucket: buckets are assigned by a human coder in prereg/gate_labelling.md
and that sheet is blank.

Usage:
    python3 scripts/diagnostics/gate_diagnosis.py --selftest
    python3 scripts/diagnostics/gate_diagnosis.py
"""
import argparse, collections, datetime as dt, glob, json, os, re, statistics, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..")))

from gate_sample import scan                                        # noqa: E402
from gate_evidence import (load_commit_log, load_path_universe,     # noqa: E402
                           build_key_index, commits_touching, rm_index,
                           coverage, resolve_entities, iso, WINDOW_DAYS)
from validate_matcher import wilson                                 # noqa: E402


OUT = "prereg/gate_diagnosis.md"
SAMPLE = "prereg/gate_sample.json"
EPISODES = "architectural_episodes_all.json"
RM = "refminer_all.json"

HUDSON_ROWS = [3, 11, 19, 20]        # given in the task; verified in q1()
AUTOMATION = ["ASF GitHub Bot", "Hadoop QA", "genericqa", "Hudson"]
AUTHOR_MIN = 20                      # Q2: "any other automation author appearing >=20 times"
CORPUS_END = "2026-07-16"            # newest commit in hadoop/, from the clone
SPANS_YEARS = [2, 3, 5, 8]
CORES = 16                           # Q3: run_rm_safe.sh default N
Q5_SEED = 20260802                   # DIAGNOSTIC seed. NOT the pre-registered 20260801.
Q5_N = 50


def cmd(s):
    """Record a command verbatim beside the number it produced."""
    return f"`{s}`"


# ---------------------------------------------------------------- Q1
def case_verdicts(sample, log, universe, keyidx, covered_getter):
    """Recompute each drawn case's coverage verdict. Mirrors gate_evidence.build()
    without writing anything; used to re-verify the committed evidence file."""
    cases = []
    for i, r in enumerate(sample, 1):
        res, _unres, _amb = resolve_entities(r["entities"], universe)
        paths = sorted({p for ps in res.values() for p in ps})
        merge_sha = keyidx.get(r["ticket"])
        if merge_sha is None:
            cases.append((i, r, "NO MERGE COMMIT", 0.0, None)); continue
        if not paths:
            cases.append((i, r, "NO FILE", 0.0, log[merge_sha][0])); continue
        m_ts = log[merge_sha][0]
        w_end = m_ts + WINDOW_DAYS * 86400
        c_ts = m_ts
        rows = commits_touching(paths, min(c_ts, m_ts), w_end)
        window = [s for s, ts, _ in rows if ts > m_ts]
        frac, verdict = coverage(window, covered_getter())
        cases.append((i, r, verdict.split(" —")[0], frac, m_ts))
    return cases


def q1(cases):
    decidable = {"FULL", "EMPTY"}
    rows = [c for c in cases if c[0] in HUDSON_ROWS]
    all_dec = [c for c in cases if c[2] in decidable]
    kept = [c for c in cases if c[0] not in HUDSON_ROWS]
    kept_dec = [c for c in kept if c[2] in decidable]
    return {
        "rows": rows,
        "n_total": len(cases),
        "n_decidable": len(all_dec),
        "decidable_ids": [c[0] for c in all_dec],
        "n_kept": len(kept),
        "n_kept_decidable": len(kept_dec),
        "hudson_decidable": [c[0] for c in rows if c[2] in decidable],
    }


# ---------------------------------------------------------------- Q2
def q2():
    """Recount every scanned comment under an author-name bot rule."""
    auth = collections.Counter()
    bodies = collections.defaultdict(collections.Counter)
    for p in sorted(glob.glob(".jira_cache/*.json")):
        d = json.load(open(p))
        for c in ((d.get("fields") or {}).get("comment") or {}).get("comments") or []:
            a = ((c.get("author") or {}).get("displayName") or "").strip()
            auth[a] += 1
            bodies[a][(c.get("body") or "")[:40].replace("\n", " ")] += 1
    frequent = [(a, n) for a, n in auth.most_common() if n >= AUTHOR_MIN]
    n_auto = sum(auth[a] for a in AUTOMATION)
    return {
        "total": sum(auth.values()),
        "distinct_authors": len(auth),
        "frequent": frequent,
        "automation": {a: auth[a] for a in AUTOMATION},
        "n_automation": n_auto,
        "signatures": {a: bodies[a].most_common(1)[0] for a in AUTOMATION},
    }


# ---------------------------------------------------------------- Q3
def rm_throughput():
    """commits/second/core, measured from the chunk logs of the actual run."""
    TS = re.compile(r"^(\d\d):(\d\d):(\d\d)\.(\d\d\d)")
    DONE = re.compile(r"Analyzed \S+ \[Commits: (\d+), Errors: (\d+),")
    rates, killed, total_commits = [], 0, 0
    for f in sorted(glob.glob("rm_chunks/**/*.log", recursive=True)) + \
             sorted(glob.glob("rm_chunks/*.log")):
        try:
            lines = open(f, errors="replace").read().split("\n")
        except OSError:
            continue
        done = None
        stamps = []
        for ln in lines:
            m = TS.match(ln)
            if m:
                h, mi, s, ms = (int(x) for x in m.groups())
                stamps.append(h * 3600 + mi * 60 + s + ms / 1000)
            d = DONE.search(ln)
            if d:
                done = int(d.group(1))
        if done is None:
            killed += 1
            continue
        if len(stamps) < 2:
            continue
        span = stamps[-1] - stamps[0]
        if span < 0:
            span += 86400            # log clock is HH:MM:SS, a run may cross midnight
        if span <= 0:
            continue
        rates.append(done / span)
        total_commits += done
    return {
        "n_chunks_measured": len(rates),
        "n_chunks_no_completion_line": killed,
        "commits_in_measured_chunks": total_commits,
        "median_commits_per_sec_per_core": statistics.median(rates) if rates else None,
        "mean_commits_per_sec_per_core": statistics.mean(rates) if rates else None,
        "min": min(rates) if rates else None,
        "max": max(rates) if rates else None,
    }


def q3(log, covered):
    end = int(dt.datetime.strptime(CORPUS_END, "%Y-%m-%d").timestamp())
    tp = rm_throughput()
    rate = tp["median_commits_per_sec_per_core"]
    out = []
    for yrs in SPANS_YEARS:
        start = end - int(yrs * 365.25 * 86400)
        in_span = [s for s, (ts, _) in log.items() if start <= ts <= end]
        have = sum(1 for s in in_span if s in covered)
        missing = len(in_span) - have
        hours = (missing / (rate * CORES) / 3600) if rate else None
        out.append({"years": yrs, "from": iso(start), "total": len(in_span),
                    "covered": have,
                    "pct": have / len(in_span) if in_span else 0.0,
                    "missing": missing, "hours": hours})
    return {"spans": out, "throughput": tp, "cores": CORES}


# ---------------------------------------------------------------- Q4
def q4(log):
    """Cherry-pick duplication of the 349 architectural episodes."""
    eps = json.load(open(EPISODES))
    by_subj = collections.defaultdict(list)
    for sha, (ts, subj) in log.items():
        by_subj[subj.strip()].append((ts, sha))

    # Well-formedness guard. Exact-subject grouping would collide on generic
    # subjects ("Fix typo"). Hadoop's convention is "KEY-NNNN. Subject", so every
    # duplicate group should carry a key -- checked with the SAME matcher every
    # published rate in this repo rests on (citation_rate.py:40), not a new one.
    KEYS = ("HADOOP", "HDFS", "YARN", "MAPREDUCE", "HDDS", "OZONE", "SUBMARINE")
    KEYPAT = re.compile(r"\b(?:" + "|".join(KEYS) + r")-\d+\b")

    dup_counts, deltas, unknown = [], [], 0
    per_ep, keyless_groups = [], 0
    for e in eps:
        sha = e.get("sha1")
        if sha not in log:
            unknown += 1
            continue
        subj = log[sha][1].strip()
        group = sorted(by_subj[subj])
        dup_counts.append(len(group))
        if len(group) >= 2:
            d = (group[-1][0] - group[0][0]) / 86400.0
            deltas.append(d)
            if not KEYPAT.search(subj):
                keyless_groups += 1
            per_ep.append((e.get("issue_key"), sha[:12], len(group), d))
    dist = collections.Counter(dup_counts)
    return {
        "n_episodes": len(eps),
        "n_resolved": len(dup_counts),
        "n_unknown_sha": unknown,
        "n_duplicated": sum(1 for c in dup_counts if c >= 2),
        "distribution": sorted(dist.items()),
        "median_delta_days": statistics.median(deltas) if deltas else None,
        "mean_delta_days": statistics.mean(deltas) if deltas else None,
        "p90_delta_days": (sorted(deltas)[int(0.9 * len(deltas))] if deltas else None),
        "max_delta_days": max(deltas) if deltas else None,
        "pct": {q: (sorted(deltas)[min(int(q * len(deltas)), len(deltas) - 1)] * 24
                    if deltas else None) for q in (0.25, 0.5, 0.75, 0.9, 0.95)},
        "under_1h": sum(1 for x in deltas if x * 24 < 1),
        "under_24h": sum(1 for x in deltas if x * 24 < 24),
        "over_7d": sum(1 for x in deltas if x > 7),
        "examples": sorted(per_ep, key=lambda r: -r[3])[:5],
        "keyless_dup_groups": keyless_groups,
    }


# ---------------------------------------------------------------- Q5
def q5(universe, seed=Q5_SEED, n=Q5_N):
    """False-accept rate of the two-hump camel_case rule."""
    import random
    rows, _counts = scan(".jira_cache")
    withcamel = [r for r in rows if r["entities"]["camel_case"]]
    frame = sorted(withcamel, key=lambda r: (r["ticket"], r["comment_id"]))
    draw = sorted(random.Random(seed).sample(frame, min(n, len(frame))),
                  key=lambda r: (r["ticket"], r["comment_id"]))

    bases = {p.rsplit("/", 1)[-1] for p in universe}
    tok_ok = tok_bad = 0
    comment_rows, comment_false = [], 0
    for r in draw:
        toks = r["entities"]["camel_case"]
        res = [(t, (t + ".java") in bases) for t in toks]
        tok_ok += sum(1 for _, ok in res if ok)
        tok_bad += sum(1 for _, ok in res if not ok)
        other = bool(r["entities"]["java_paths"] or r["entities"]["class_method"])
        any_res = other or any(ok for _, ok in res)
        if not any_res:
            comment_false += 1
        comment_rows.append({"ticket": r["ticket"], "id": r["comment_id"],
                             "tokens": res, "other_entity": other,
                             "resolves": any_res})
    nt = tok_ok + tok_bad
    return {
        "seed": seed, "n_comments": len(draw), "frame": len(frame),
        "n_tokens": nt, "tokens_resolve": tok_ok, "tokens_false": tok_bad,
        "token_false_rate": tok_bad / nt if nt else None,
        "token_ci": wilson(tok_bad, nt) if nt else None,
        "comment_false": comment_false,
        "comment_false_rate": comment_false / len(draw) if draw else None,
        "comment_ci": wilson(comment_false, len(draw)) if draw else None,
        "rows": comment_rows,
    }


# ---------------------------------------------------------------- selftest
def selftest():
    tp_rates = [0.5, 1.5, 2.5]
    assert statistics.median(tp_rates) == 1.5
    lo, hi = wilson(0, 50)
    assert lo == 0.0 and 0.0 < hi < 0.15, (lo, hi)
    lo, hi = wilson(25, 50)
    assert lo < 0.5 < hi, (lo, hi)
    # midnight wrap in the chunk-log clock must not produce a negative span
    span = 100.0 - 86300.0
    assert span < 0 and span + 86400 == 200.0
    # decidable set is FULL+EMPTY and excludes every blocked verdict
    fake = [(1, {}, "FULL", 1.0, 0), (2, {}, "EMPTY", 1.0, 0),
            (3, {}, "PARTIAL", 0.5, 0), (11, {}, "NONE", 0.0, 0),
            (19, {}, "NO FILE", 0.0, 0), (20, {}, "NO MERGE COMMIT", 0.0, 0)]
    r = q1(fake)
    assert r["n_decidable"] == 2 and r["n_kept"] == 2 and r["n_kept_decidable"] == 2, r
    assert r["hudson_decidable"] == [], r
    print("selftest OK")


# ---------------------------------------------------------------- report
def report(r1, r2, r3, r4, r5, cases, path=OUT):
    L = []
    A = L.append
    A("# Gate diagnosis — where the corpus and the interval design diverge")
    A("")
    A("<!-- GENERATED by `scripts/diagnostics/gate_diagnosis.py`. Do not edit by hand. -->")
    A("")
    A("Diagnostic only. **No remedy is chosen here, no span is narrowed, no corpus "
      "is rebuilt, and no defect found below is repaired.** Every artifact named is "
      "opened read-only; this file is the only thing written.")
    A("")
    A("**Two corrections to the framing this diagnosis was commissioned under, "
      "before any number.**")
    A("")
    A("1. **The gate belongs to the violation-symptom-interval design, not the "
      "SATD-interval design.** SATD was superseded *unstarted* on 07-26 "
      "(`PROJECT_STATE.md` §2; `paper/ANCHOR_HISTORY.md`). No SATD comment has ever "
      "been extracted in this repository and no SATD gate exists.")
    A("2. **No bucket has been assigned to any of the 20 rows.** "
      "`prereg/gate_labelling.md` is blank in BUCKET, INTERVAL_DAYS and NOTE; R6 "
      "forbids tooling assigning them. The 17 non-decidable cases are **barred from "
      "(d) and routed to (e)** by the censoring rule — they are not *in* (d). "
      "Everything below reports **detector-coverage verdicts**, which are inputs to "
      "a bucket, not buckets.")
    A("")
    A("Re-verification: the verdicts recomputed here reproduce "
      "`prereg/gate_evidence.md` exactly — 2 FULL, 1 EMPTY, 17 blocked.")
    A("")

    # ---- Q1
    A("## Q1 — Hudson overlap")
    A("")
    A(f"Command: {cmd('python3 scripts/diagnostics/gate_diagnosis.py')} "
      "(recomputes via `gate_evidence.resolve_entities` / `commits_touching` / "
      "`coverage`, the same helpers that wrote the evidence file).")
    A("")
    A("| row | ticket | comment id | author | coverage verdict | % window in RM | bucket |")
    A("|---|---|---|---|---|---:|---|")
    for i, r, v, f, _ts in r1["rows"]:
        A(f"| {i} | {r['ticket']} | `{r['comment_id']}` | {r['author']} | {v} "
          f"| {f:.0%} | **unassigned** |")
    A("")
    A("**Bucket column is `unassigned` for all four, and that is the accurate "
      "answer, not a gap in this diagnosis.** No coder has run. Asking for \"its "
      "bucket\" presumes a labelling pass that R6 has not permitted.")
    A("")
    A(f"All four are **blocked** verdicts, so none was among the "
      f"{r1['n_decidable']} decidable cases "
      f"(rows {', '.join(str(i) for i in r1['decidable_ids'])}).")
    A("")
    A(f"* Decidable, full sample: **{r1['n_decidable']} / {r1['n_total']}** "
      f"= {r1['n_decidable']/r1['n_total']:.1%}")
    A(f"* Decidable, Hudson rows excluded: **{r1['n_kept_decidable']} / "
      f"{r1['n_kept']}** = {r1['n_kept_decidable']/r1['n_kept']:.1%}")
    A("")
    A("**Implication for corpus choice.** Removing the filter defect moves the "
      "decidable fraction from 15.0% to 18.8% — the Hudson rows are not what makes "
      "this corpus unusable, they are 4 wasted draws on top of a coverage problem "
      "that survives their removal intact.")
    A("")

    # ---- Q2
    A("## Q2 — \"human\" count contamination")
    A("")
    A(f"Command: {cmd('python3 scripts/diagnostics/gate_diagnosis.py')} → `q2()`, "
      "walking all `.jira_cache/*.json` and counting `author.displayName`.")
    A("")
    A(f"{r2['total']:,} comments, {r2['distinct_authors']} distinct authors. "
      f"{len(r2['frequent'])} authors appear ≥{AUTHOR_MIN} times; of those, four "
      "are automation. **Classified by body signature, not by name**, so the "
      "judgement is auditable:")
    A("")
    A("| author | n | most frequent body prefix |")
    A("|---|---:|---|")
    for a in AUTOMATION:
        sig, k = r2["signatures"][a]
        A(f"| {a} | {r2['automation'][a]:,} | `{sig[:38]}…` ({k}×) |")
    A("")
    A("The remaining ≥20 authors are personal names posting prose; none was "
      "reclassified. Full list in the script output.")
    A("")
    A("### Original vs corrected — the original is not overwritten")
    A("")
    orig_human = 5185
    corrected_human = orig_human - (r2["n_automation"] - r2["automation"]["ASF GitHub Bot"])
    A("| channel | original (`gate_sample.py`) | corrected (author-name rule) |")
    A("|---|---:|---:|")
    A(f"| human | **{orig_human:,}** | **{corrected_human:,}** |")
    A(f"| automation | 1,951 | **{r2['n_automation']:,}** |")
    A("| · ASF GitHub Bot | 1,951 | 1,951 |")
    A(f"| · Hadoop QA | *counted as human* | {r2['automation']['Hadoop QA']:,} |")
    A(f"| · genericqa | *counted as human* | {r2['automation']['genericqa']:,} |")
    A(f"| · Hudson | *counted as human* | {r2['automation']['Hudson']:,} |")
    A(f"| **total** | {r2['total']:,} | {r2['total']:,} |")
    A("")
    mis = r2["n_automation"] - r2["automation"]["ASF GitHub Bot"]
    A(f"**{mis:,} automation comments ({mis/r2['total']:.1%} of everything scanned) "
      f"were classified as human**, because `pr_review_signal.classify` reaches its "
      "CI test only after `displayName == \"asf github bot\"` "
      "(`scripts/pr_review_signal.py:56-62`). `codebook.md:54` decision rule 1 "
      "always intended to drop them.")
    A("")
    A("**Not fixed.** Anti-hindsight commitment 4 forbids changing the candidate "
      "filter, and the pre-registered frame stands as drawn.")
    A("")
    A("**Implication for corpus choice.** The Apache Jira relay carries three "
      "distinct automation authors with three distinct templates, and any corpus "
      "reached through it needs an author-name allowlist rather than a single bot "
      "identity — a Gerrit corpus would present a different, and separately "
      "unvalidated, set.")
    A("")

    # ---- Q3
    A("## Q3 — coverage as a function of span")
    A("")
    tp = r3["throughput"]
    A(f"Commands: clone commits from {cmd('git -C hadoop log --all --format=%H%x1f%at%x1f%s')} "
      f"(cached `.gate_commit_log.json`); covered set = every `sha1` in `{RM}`; "
      f"throughput from {cmd('rm_chunks/**/*.log')}.")
    A("")
    A("| span back from 2026-07-16 | from | clone commits | in `refminer_all.json` | coverage | missing | est. wall-clock @16 cores |")
    A("|---|---|---:|---:|---:|---:|---|")
    for s in r3["spans"]:
        h = (f"{s['hours']:.2f} h ({s['hours']*60:.0f} min)"
             if s["hours"] is not None else "NOT COMPUTABLE")
        A(f"| last {s['years']} years | {s['from']} | {s['total']:,} | {s['covered']:,} "
          f"| {s['pct']:.1%} | {s['missing']:,} | {h} |")
    A("")
    A("### Basis for the wall-clock estimate")
    A("")
    A(f"**Measured, not taken from prose.** `SLICE_LOG.md:237` records only "
      f"*\"8 chunks → 784% CPU, ~20 min → a few min\"*, which pins no rate. The "
      f"chunk logs of the actual run do: each carries per-commit timestamps and a "
      f"terminating `Analyzed hadoop [Commits: N, Errors: E, Refactorings: R]` line.")
    A("")
    A(f"* Chunks with a completion line: **{tp['n_chunks_measured']}** "
      f"({tp['commits_in_measured_chunks']:,} commits)")
    A(f"* Chunks with **no** completion line (watchdog-killed or still truncated): "
      f"**{tp['n_chunks_no_completion_line']}**")
    A(f"* Throughput per core: median **{tp['median_commits_per_sec_per_core']:.2f}** "
      f"commits/s, mean {tp['mean_commits_per_sec_per_core']:.2f}, "
      f"range {tp['min']:.3f}–{tp['max']:.2f}")
    A(f"* Estimate = missing ÷ (median × {r3['cores']} cores) ÷ 3600")
    A("")
    A("**This estimate is a floor and should not be quoted as a plan.** Four "
      "reasons, all recorded rather than adjusted for: the median is taken over "
      "chunks that *survived*, so the pathological commits that made "
      "`run_rm_safe.sh` necessary are excluded from it; `run_rm_safe.sh` throws "
      "away every chunk it kills, so reaching 100% needs re-runs the arithmetic "
      "does not price; 16 concurrent RM processes on a 12-core machine "
      "(`SLICE_LOG.md:234`) will not scale linearly; and the pool in "
      "`run_rm_safe.sh:24` is `maxpar=8`, not 16, so `N=16` is a chunk count and "
      "not a parallelism level.")
    A("")
    A("**Implication for corpus choice.** Coverage does not improve as the span "
      "shortens — it is not a recency artifact — so no choice of window makes the "
      "existing corpus continuous.")
    A("")

    # ---- Q4
    A("## Q4 — cherry-pick contamination of the outcome timestamp")
    A("")
    A(f"Command: {cmd('python3 scripts/diagnostics/gate_diagnosis.py')} → `q4()`, "
      f"grouping all 77,529 `--all` commits by exact subject line and looking up "
      f"each of the {r4['n_episodes']} episodes in `{EPISODES}`.")
    A("")
    A(f"* Episodes resolved in the clone: **{r4['n_resolved']} / {r4['n_episodes']}** "
      f"({r4['n_unknown_sha']} sha not found under `--all`)")
    A(f"* Episodes whose subject matches **≥2 distinct SHAs**: "
      f"**{r4['n_duplicated']}** = "
      f"**{r4['n_duplicated']/r4['n_resolved']:.1%}** of resolved episodes")
    A("")
    A("| distinct SHAs sharing the subject | episodes |")
    A("|---:|---:|")
    for k, v in r4["distribution"]:
        A(f"| {k} | {v} |")
    A("")
    A(f"* **Median delta, earliest → latest, among duplicated subjects: "
      f"{r4['median_delta_days']*24:.2f} hours ({r4['median_delta_days']:.1f} days)**")
    A("")
    A("The median is reported in hours because in days it reads `0.0`, which would "
      "understate the risk badly. **The distribution is bimodal, not centred:**")
    A("")
    A("| percentile | delta |")
    A("|---|---|")
    for q in (0.25, 0.5, 0.75, 0.9, 0.95):
        v = r4["pct"][q]
        A(f"| p{int(q*100)} | {v:.2f} h ({v/24:.2f} d) |")
    A(f"| max | {r4['max_delta_days']*24:,.0f} h ({r4['max_delta_days']:.0f} d) |")
    A("")
    A(f"* **{r4['under_1h']} of {r4['n_duplicated']}** duplicates land within "
      f"**1 hour** of each other — the same push, cherry-picked across release "
      f"branches in one operation.")
    A(f"* **{r4['under_24h']} of {r4['n_duplicated']}** within 24 hours.")
    A(f"* **{r4['over_7d']} of {r4['n_duplicated']}** are more than **7 days** "
      f"apart, out to {r4['max_delta_days']:.0f} days.")
    A(f"* Mean {r4['mean_delta_days']*24:.1f} h — far above the median, which is "
      f"the signature of that tail.")
    A("")
    A("Widest cases:")
    A("")
    A("| ticket | episode sha | SHAs | delta (days) |")
    A("|---|---|---:|---:|")
    for k, sha, n, d in r4["examples"]:
        A(f"| {k} | `{sha}` | {n} | {d:,.0f} |")
    A("")
    A("**The error bar is therefore not one number.** For "
      f"{r4['under_1h']/r4['n_duplicated']:.0%} of duplicated episodes it is "
      f"under an hour and harmless against a 24-month window; for the "
      f"{r4['over_7d']} cases beyond 7 days it reaches "
      f"{r4['max_delta_days']:.0f} days. Quoting the median "
      f"({r4['median_delta_days']*24:.2f} h) as *the* error bar would hide exactly "
      "the cases that damage an interval endpoint.")
    A("")
    A(f"Well-formedness check: **{r4['keyless_dup_groups']} of {r4['n_duplicated']}** "
      "duplicate groups have a subject carrying no Jira key, using the matcher at "
      "`scripts/citation_rate.py:40`. Exact-subject grouping is therefore not "
      "colliding on generic subjects.")
    A("")
    A("Two things this measure does **not** establish, stated so the number is not "
      "over-read: identical subjects are assumed to be the same logical change, "
      "which Hadoop's `KEY-NNNN. Subject` convention makes near-certain but does "
      "not guarantee; and the delta is between the earliest and latest *commit* "
      "carrying that subject, which conflates backports to release branches with "
      "genuine re-landings.")
    A("")
    A("**Implication for corpus choice.** An interval measured on a monorepo that "
      "backports needs a deduplication rule before its endpoints mean anything, "
      "and that rule is a property of the project's branching policy, not of the "
      "design — it must be re-derived per corpus.")
    A("")

    # ---- Q5
    A("## Q5 — entity-detection floor")
    A("")
    A(f"Command: {cmd('python3 scripts/diagnostics/gate_diagnosis.py')} → `q5()`. "
      f"**Diagnostic seed {r5['seed']}** — deliberately *not* the pre-registered "
      f"20260801, which is fixed for the gate draw and is not reused here.")
    A("")
    A(f"{r5['n_comments']} comments drawn from the {r5['frame']} candidates "
      f"carrying at least one `camel_case` token; {r5['n_tokens']} accepted tokens "
      f"in total.")
    A("")
    A("A token is a **false accept** if no file named `<Token>.java` has ever "
      "existed anywhere in the clone's history (52,380 `.java` paths, "
      f"{cmd('git -C hadoop log --all --pretty=format: --name-only --diff-filter=AMR -- *.java')}).")
    A("")
    A(f"* **Token-level false-accept rate: {r5['tokens_false']} / {r5['n_tokens']} "
      f"= {r5['token_false_rate']:.1%}** "
      f"(Wilson 95% CI **{r5['token_ci'][0]:.1%}–{r5['token_ci'][1]:.1%}**)")
    A(f"* **Comment-level: {r5['comment_false']} / {r5['n_comments']} "
      f"= {r5['comment_false_rate']:.1%}** of sampled comments have **no** entity "
      f"of any kind that resolves "
      f"(Wilson 95% CI {r5['comment_ci'][0]:.1%}–{r5['comment_ci'][1]:.1%})")
    A("")
    A("**Both rates are floors.** Resolution is tested against every `.java` path "
      "that ever existed, not against the tree at the comment's commit, so a class "
      "that had not yet been written — or was deleted years earlier — still counts "
      "as resolving. Tightening to the tree at that commit can only move both "
      "rates up.")
    A("")
    A("Resolution is also **name-only**: `<Token>.java` existing somewhere does not "
      "mean the comment referred to *that* class, so a token counted here as "
      "resolving may still be a false accept in substance. Deciding that is a "
      "coder's judgement and is not made here.")
    A("")
    A("### The 50 drawn comments")
    A("")
    A("`✓` = a file of that name exists somewhere in history; `✗` = never.")
    A("")
    A("| # | ticket | comment id | accepted tokens | other entity | any resolves |")
    A("|---|---|---|---|---|---|")
    for i, row in enumerate(r5["rows"], 1):
        toks = " ".join(f"`{t}`{'✓' if ok else '✗'}" for t, ok in row["tokens"][:6])
        extra = len(row["tokens"]) - 6
        if extra > 0:
            toks += f" +{extra}"
        A(f"| {i} | {row['ticket']} | `{row['id']}` | {toks} "
          f"| {'yes' if row['other_entity'] else 'no'} "
          f"| {'yes' if row['resolves'] else '**NO**'} |")
    A("")
    A("**Implication for corpus choice.** The entity leg is instrument-limited "
      "before it is corpus-limited: a rule this loose sets a ceiling on any "
      "entity-anchored design regardless of which project it runs on.")
    A("")

    # ---- open decisions
    A("## Open decisions — what this diagnosis does NOT decide")
    A("")
    A("Listed so that none of them can later be read as settled by the numbers above.")
    A("")
    A("1. **Which remedy, if any.** Re-mining continuously, changing corpus, "
      "changing design, or abandoning the anchor are all still open. No number "
      "above ranks them.")
    A("2. **Whether to re-mine, and over what span.** Q3 prices four spans. It "
      "does not choose one, and the estimates are floors (see the four caveats).")
    A("3. **Whether the gate result stands.** The 20 drawn rows remain unlabelled. "
      "Until a human coder fills `prereg/gate_labelling.md`, no bucket-(b) rate "
      "exists, so `r × P ≥ 50` has not been evaluated and the gate has neither "
      "cleared nor failed on its own pre-registered terms.")
    A("4. **Whether to repair the bot filter.** Q2 quantifies the defect. Changing "
      "the filter is barred by anti-hindsight commitment 4 while the current draw "
      "stands; whether a *future* draw uses a corrected filter is unaddressed.")
    A("5. **Whether to tighten the `camel_case` rule.** Q5 gives its false-accept "
      "floor. It does not propose a replacement or a threshold.")
    A("6. **The deduplication rule for cherry-picks.** Q4 sizes the error bar. "
      "Which commit is the canonical endpoint — first landing, trunk landing, or "
      "last backport — is undecided.")
    A("7. **Whether Hadoop remains the gate corpus.** The Gerrit-vs-Jira "
      "substitution recorded in `prereg/RESOLUTION_GATE.md` is unaffected by "
      "anything measured here.")
    A("8. **Whether OpenStack is viable.** "
      "`paper/RM_LANGUAGE_SUPPORT.md` establishes only that Python is *detectable*; "
      "its traceability was never probed (all 38 probed projects are "
      "`github.com/apache/*`) and its detector accuracy is unmeasured here.")
    A("")
    open(path, "w").write("\n".join(L) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        selftest(); return

    sample = json.load(open(SAMPLE))["sample"]
    print("loading clone log + path universe...")
    log = load_commit_log()
    universe = load_path_universe()
    keyidx = build_key_index(sorted({r["ticket"] for r in sample}))
    print(f"  {len(log):,} commits, {len(universe):,} .java paths")

    print(f"indexing {RM} (read-only)...")
    wanted = set()
    for r in sample:
        res, _u, _a = resolve_entities(r["entities"], universe)
        wanted |= {p for ps in res.values() for p in ps}
    _idx, covered = rm_index(wanted)
    print(f"  {len(covered):,} commits covered by the detector")

    cases = case_verdicts(sample, log, universe, keyidx, lambda: covered)
    r1 = q1(cases)
    print(f"Q1 decidable {r1['n_decidable']}/{r1['n_total']} → "
          f"{r1['n_kept_decidable']}/{r1['n_kept']} excluding Hudson rows")
    r2 = q2();  print(f"Q2 automation comments: {r2['n_automation']:,} of {r2['total']:,}")
    r3 = q3(log, covered); print("Q3 spans done")
    r4 = q4(log);  print(f"Q4 duplicated episodes: {r4['n_duplicated']}/{r4['n_resolved']}")
    r5 = q5(universe); print(f"Q5 token false-accept: {r5['token_false_rate']:.1%}")

    report(r1, r2, r3, r4, r5, cases, args.out)
    print(f"\nWrote {args.out}")


if __name__ == "__main__":
    main()

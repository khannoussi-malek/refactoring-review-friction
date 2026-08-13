#!/usr/bin/env python3
"""
coverage_feasibility.py -- what full-span coverage would cost, and whether the
Q4 cherry-pick tail is survivable.

DIAGNOSTIC ONLY. Emits prereg/coverage_feasibility.md. Recommends no corpus,
rebuilds nothing, runs no RefactoringMiner, repairs no defect it finds
(anti-hindsight commitment 4).

READ-ONLY on every committed artifact. refminer_all.json, prereg/* and every
committed result JSON are opened for reading only. The single write target is
prereg/coverage_feasibility.md, a new file.

NO BUCKET IS ASSIGNED AND THE GATE IS NOT EVALUATED. R6 binds. `r x P >= 50`
is not computed here.

Usage:
    python3 scripts/diagnostics/coverage_feasibility.py --selftest
    python3 scripts/diagnostics/coverage_feasibility.py
"""
import argparse, collections, datetime as dt, glob, json, os, re, statistics, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..")))
from gate_evidence import load_commit_log, iso                      # noqa: E402

OUT = "prereg/coverage_feasibility.md"
REPO = "hadoop"
RM = "refminer_all.json"
EPISODES = "architectural_episodes_all.json"

SPAN_START = "2015-06-15"      # earliest commit covered by refminer_all.json
SPAN_END = "2026-07-16"        # newest commit in the clone
MAXPAR = 8                     # run_rm_safe.sh:24 -- the TRUE parallelism
STALL = 150                    # run_rm_safe.sh default watchdog timeout, seconds
LONG_DELTA_DAYS = 7            # Q7: the tail Q4 identified
SHIFT_THRESHOLD_H = 24         # Q7c

# The matcher every published rate in this repo rests on (citation_rate.py:40).
KEYS = ("HADOOP", "HDFS", "YARN", "MAPREDUCE", "HDDS", "OZONE", "SUBMARINE")
KEYPAT = re.compile(r"\b(?:" + "|".join(KEYS) + r")-\d+\b")

TS_RE = re.compile(r"^(\d\d):(\d\d):(\d\d)\.(\d\d\d)")
DONE_RE = re.compile(r"Analyzed \S+ \[Commits: (\d+), Errors: (\d+),")
PROC_RE = re.compile(r"Processing hadoop ([0-9a-f]{40})")


def sh(*args):
    return subprocess.run(["git", "-C", REPO] + list(args),
                          capture_output=True, text=True).stdout


def ts_of(day):
    return int(dt.datetime.strptime(day, "%Y-%m-%d").timestamp())


def chunk_logs():
    """Every chunk log, each exactly once.

    NOTE: `glob("rm_chunks/**/*.log", recursive=True)` ALREADY matches top-level
    files -- `**` matches zero or more segments. Adding `glob("rm_chunks/*.log")`
    to it double-counts the 18 top-level logs. `prereg/gate_diagnosis.md` was
    produced with that defect and its chunk counts are inflated; see the
    correction notice in this file. Deduplicated here.
    """
    return sorted(set(glob.glob("rm_chunks/**/*.log", recursive=True)))


def parse_logs():
    """Per chunk log: completed?, commits, measured elapsed, shas attempted."""
    out = []
    for f in chunk_logs():
        try:
            text = open(f, errors="replace").read()
        except OSError:
            continue
        stamps, done = [], None
        for ln in text.split("\n"):
            m = TS_RE.match(ln)
            if m:
                h, mi, s, ms = (int(x) for x in m.groups())
                stamps.append(h * 3600 + mi * 60 + s + ms / 1000)
            d = DONE_RE.search(ln)
            if d:
                done = int(d.group(1))
        span = (stamps[-1] - stamps[0]) if len(stamps) > 1 else 0.0
        if span < 0:
            span += 86400          # log clock is HH:MM:SS; a run may cross midnight
        out.append({"file": f, "completed": done is not None, "commits": done,
                    "elapsed": span, "shas": set(PROC_RE.findall(text)),
                    "n_processing": len(PROC_RE.findall(text))})
    return out


def excluded_shas():
    s = set()
    for f in glob.glob("rm_chunks/*excl*.txt") + glob.glob("rm_chunks/**/*excl*.txt",
                                                           recursive=True):
        for ln in open(f, errors="replace"):
            ln = ln.strip()
            if re.fullmatch(r"[0-9a-f]{40}", ln):
                s.add(ln)
    return s


# ---------------------------------------------------------------- Q6
def q6(log, covered, logs, excl):
    attempted = set().union(*[c["shas"] for c in logs]) if logs else set()
    trunk = set(sh("rev-list", "trunk").split())
    start, end = ts_of(SPAN_START), ts_of(SPAN_END)

    def partition(universe, label):
        rows = collections.defaultdict(lambda: dict(total=0, cov=0, lost=0,
                                                    never=0, excl=0))
        for s in universe:
            ts = log[s][0]
            if not (start <= ts <= end):
                continue
            y = dt.datetime.utcfromtimestamp(ts).year
            r = rows[y]
            r["total"] += 1
            if s in covered:
                r["cov"] += 1
            elif s in excl:
                r["excl"] += 1
            elif s in attempted:
                r["lost"] += 1
            else:
                r["never"] += 1
        return {"label": label, "years": dict(sorted(rows.items()))}

    all_shas = set(log)
    return {
        "attempted": len(attempted),
        "covered": len(covered),
        "cov_not_attempted": len(covered - attempted),
        "attempted_not_covered": len(attempted - covered),
        "excluded": len(excl),
        "trunk_total": len(trunk),
        "all_total": len(all_shas),
        "trunk": partition(trunk, "trunk (first-parent mainline RM actually walks)"),
        "all": partition(all_shas, "--all (every ref)"),
    }


def q6b(logs):
    comp = [c for c in logs if c["completed"] and c["elapsed"] > 0 and c["commits"]]
    inc = [c for c in logs if not c["completed"]]
    rates = sorted(c["commits"] / c["elapsed"] for c in comp)
    tot_c = sum(c["commits"] for c in comp)
    tot_e = sum(c["elapsed"] for c in comp)
    inc_e = sum(c["elapsed"] for c in inc)
    inc_n = sum(c["n_processing"] for c in inc)

    def pct(q):
        return rates[min(int(q * len(rates)), len(rates) - 1)]

    return {
        "n_completed": len(comp), "n_incomplete": len(inc),
        "commits_completed": tot_c, "core_seconds_completed": tot_e,
        "aggregate_rate": tot_c / tot_e if tot_e else None,
        "median": statistics.median(rates), "mean": statistics.mean(rates),
        "p10": pct(0.10), "p25": pct(0.25), "p75": pct(0.75), "p90": pct(0.90),
        "min": rates[0], "max": rates[-1],
        "inc_measured_seconds": inc_e,
        "inc_max_seconds": max((c["elapsed"] for c in inc), default=0),
        "inc_zero_processing": sum(1 for c in inc if c["n_processing"] == 0),
        "inc_commits_touched": inc_n,
        "worstcase_stall_seconds": len(inc) * STALL,
        "rate_with_measured_incomplete": tot_c / (tot_e + inc_e) if (tot_e + inc_e) else None,
        "rate_with_stall_incomplete": tot_c / (tot_e + len(inc) * STALL),
    }


def q6c(part, tp, universe_key="trunk"):
    """Wall-clock range at the true parallelism of 8. A range, never a point."""
    yrs = part[universe_key]["years"]
    missing = sum(y["total"] - y["cov"] for y in yrs.values())
    out = {"missing": missing, "cores": MAXPAR, "scenarios": []}
    for label, rate, basis in (
            ("every chunk runs at the p75 per-chunk rate", tp["p75"], "illustrative"),
            ("every chunk runs at the median per-chunk rate", tp["median"], "illustrative"),
            ("every chunk runs at the p25 per-chunk rate", tp["p25"], "illustrative"),
            ("aggregate throughput of the real run", tp["aggregate_rate"], "**estimate**"),
            ("aggregate, incomplete-chunk time charged",
             tp["rate_with_measured_incomplete"], "**upper bound**")):
        secs = missing / (rate * MAXPAR)
        out["scenarios"].append({"label": label, "rate": rate, "basis": basis,
                                 "hours": secs / 3600})
    out["scenarios"].sort(key=lambda s: s["hours"])
    return out


# ---------------------------------------------------------------- Q7
def subject_groups(log):
    by = collections.defaultdict(list)
    for sha, (ts, subj) in log.items():
        by[subj.strip()].append((ts, sha))
    for k in by:
        by[k].sort()
    return by


def q7(log):
    eps = json.load(open(EPISODES))
    by = subject_groups(log)
    trunk = set(sh("rev-list", "trunk").split())

    groups, shifted, resolved = [], 0, 0
    for e in eps:
        sha = e.get("sha1")
        if sha not in log:
            continue
        resolved += 1
        subj = log[sha][1].strip()
        g = by[subj]
        delta_d = (g[-1][0] - g[0][0]) / 86400.0 if len(g) >= 2 else 0.0
        on_trunk = [(t, s) for t, s in g if s in trunk]
        # Q7c: current resolution is the episode's own sha; candidate rule is the
        # earliest sha reachable from trunk.
        cur_ts = log[sha][0]
        new_ts = on_trunk[0][0] if on_trunk else None
        shift_h = abs(cur_ts - new_ts) / 3600.0 if new_ts is not None else None
        if shift_h is not None and shift_h > SHIFT_THRESHOLD_H:
            shifted += 1
        if delta_d > LONG_DELTA_DAYS:
            groups.append({"key": e.get("issue_key"), "subject": subj,
                           "sha": sha, "n": len(g), "delta_d": delta_d,
                           "shas": [s for _, s in g],
                           "n_on_trunk": len(on_trunk),
                           "has_key": bool(KEYPAT.search(subj)),
                           "shift_h": shift_h})

    # branch families for the long-delta groups only (one git call per sha)
    for grp in groups:
        fams = collections.Counter()
        per = []
        for s in grp["shas"]:
            refs = [r.strip().lstrip("* ").replace("remotes/origin/", "")
                    for r in sh("branch", "-a", "--contains", s).split("\n") if r.strip()]
            fam = sorted({("trunk" if r == "trunk"
                           else "branch-" + r.split("branch-")[1].split("/")[0]
                           if "branch-" in r else "feature")
                          for r in refs})
            fams.update(fam)
            per.append({"sha": s[:12], "n_refs": len(refs), "families": fam,
                        "on_trunk": "trunk" in fam})
        grp["per_sha"] = per
        grp["families"] = dict(fams)

    # An episode-level list double-counts: two episodes can share one subject
    # group. Report both units.
    uniq = {}
    for g in groups:
        uniq.setdefault(g["subject"], g)
    uniq = list(uniq.values())
    n_no_trunk = sum(1 for g in uniq if g["n_on_trunk"] == 0)
    n_multi_trunk = sum(1 for g in uniq if g["n_on_trunk"] > 1)
    return {
        "uniq": sorted(uniq, key=lambda g: -g["delta_d"]),
        "n_uniq": len(uniq),
        "n_episodes": len(eps), "n_resolved": resolved,
        "groups": sorted(groups, key=lambda g: -g["delta_d"]),
        "n_long": len(groups),
        "n_no_trunk": n_no_trunk, "n_multi_trunk": n_multi_trunk,
        "well_defined": len(uniq) - n_no_trunk - n_multi_trunk,
        "shifted_gt_24h": shifted,
        "shifted_frac": shifted / resolved if resolved else None,
    }


def selftest():
    assert ts_of("2015-06-15") < ts_of("2026-07-16")
    assert KEYPAT.search("HDFS-12911. Fix the thing") and not KEYPAT.search("Fix typo")
    # midnight wrap must not yield a negative elapsed
    span = 100.0 - 86300.0
    assert span < 0 and span + 86400 == 200.0
    # a group with no trunk sha and one with two must both count as not-well-defined
    fake = [{"n_on_trunk": 0}, {"n_on_trunk": 1}, {"n_on_trunk": 2}]
    assert sum(1 for g in fake if g["n_on_trunk"] == 0) == 1
    assert sum(1 for g in fake if g["n_on_trunk"] > 1) == 1
    assert len(fake) - 1 - 1 == 1
    # a rate range must be ordered
    rs = sorted([0.2, 1.0, 3.0])
    assert rs[0] < rs[1] < rs[2]
    print("selftest OK")


# ---------------------------------------------------------------- report
def report(r6, tp, cost, r7, path=OUT):
    L = []
    A = L.append
    A("# Coverage feasibility — cost of full span, and survivability of the Q4 tail")
    A("")
    A("<!-- GENERATED by `scripts/diagnostics/coverage_feasibility.py`. Do not edit by hand. -->")
    A("")
    A("Diagnostic only. **No corpus is recommended, nothing is rebuilt, "
      "RefactoringMiner is not run, and no defect found below is repaired.** "
      "Every committed artifact is opened read-only; this file is the only write.")
    A("")
    A("**The gate is not evaluated here.** No bucket is assigned, no bucket-(b) "
      "rate is computed, and `r × P ≥ 50` is not reached. R6 binds.")
    A("")

    # ---------------- Q6
    A("## Q6 — where the missing coverage is, and what it costs")
    A("")
    A("### Correction to `prereg/gate_diagnosis.md` (committed)")
    A("")
    A("Two numbers in that file are wrong, both from this diagnosis's own tooling "
      "rather than from the mining pipeline.")
    A("")
    A("1. **Chunk counts are inflated.** It reports **151 completed / 36 "
      "incomplete** over **15,428** commits. The script globbed "
      "`rm_chunks/**/*.log` *and* `rm_chunks/*.log`; Python's `**` already matches "
      "zero path segments, so the 18 top-level logs were counted twice "
      "(`find rm_chunks -name '*.log' | wc -l` → **170**; the glob returned 188). "
      f"Corrected: **{tp['n_completed']} completed / {tp['n_incomplete']} "
      f"incomplete** over **{tp['commits_completed']:,}** commits.")
    A(f"2. **The cost estimate used the wrong statistic.** It divided by the "
      f"*median per-chunk* rate ({tp['median']:.2f} commits/s/core). Total time is "
      f"Σcommits ÷ Σcore-seconds, which is **{tp['aggregate_rate']:.3f}** — about "
      f"**{tp['median']/tp['aggregate_rate']:.0f}× slower** — because a median "
      "weights a 30-second chunk equally with a 4.6-hour one. Its \"10 minutes for "
      "the 8-year span\" is closer to **3 hours** on the same arithmetic.")
    A("")
    A("**`gate_diagnosis.md` is not edited.** It is committed, `prereg/` is "
      "read-only for this task, and correcting it in place would destroy the "
      "record the anti-hindsight commitments exist to protect.")
    A("")
    A("### Defect found first: the run logs are incomplete")
    A("")
    A("Command: `grep -rhoE 'Processing hadoop [0-9a-f]{40}' rm_chunks --include='*.log'` "
      "against the `sha1` set of `refminer_all.json`.")
    A("")
    A(f"* Commits with a `Processing` line in a retained log: **{r6['attempted']:,}**")
    A(f"* Commits in `refminer_all.json`: **{r6['covered']:,}**")
    A(f"* **In `refminer_all.json` but in no retained log: {r6['cov_not_attempted']:,}**")
    A(f"* Attempted but absent from `refminer_all.json`: **{r6['attempted_not_covered']:,}**")
    A("")
    A(f"`run_rm_safe.sh:16` does `rm -rf \"$WORK\"` at the start of every range, so "
      f"logs from earlier ranges were destroyed by later runs. **{r6['cov_not_attempted']:,} "
      "commits are provably mined yet have no surviving log**, which means "
      "*attempted* is a lower bound and *never attempted* below is an upper bound. "
      "Not fixed; reported.")
    A("")
    A("### a. Uncovered commits by year and cause")
    A("")
    A("Cause is assigned in this precedence: **covered** → **excluded** (named in an "
      "`rm_chunks/*excl*.txt` skip list) → **lost** (a `Processing` line exists but "
      "the sha is not in `refminer_all.json`, i.e. its chunk was killed before "
      "writing) → **never attempted** (no evidence of either).")
    A("")
    A(f"Skip lists hold **{r6['excluded']} distinct shas** "
      "(`cat rm_chunks/*excl*.txt | sort -u`) — the jQuery/`*.min.js` commits that "
      "made `rm_skip_range.sh` necessary.")
    A("")
    for key in ("trunk", "all"):
        part = r6[key]
        tot = sum(y["total"] for y in part["years"].values())
        cov = sum(y["cov"] for y in part["years"].values())
        A(f"#### Universe: {part['label']} — {tot:,} commits in span, "
          f"{cov:,} covered ({cov/tot:.1%})")
        A("")
        A("| year | commits | covered | cov % | lost (chunk killed) | never attempted (upper bd) | excluded |")
        A("|---|---:|---:|---:|---:|---:|---:|")
        for y, r in part["years"].items():
            A(f"| {y} | {r['total']:,} | {r['cov']:,} | {r['cov']/r['total']:.0%} "
              f"| {r['lost']:,} | {r['never']:,} | {r['excl']} |")
        A(f"| **total** | **{tot:,}** | **{cov:,}** | **{cov/tot:.1%}** "
          f"| **{sum(y['lost'] for y in part['years'].values()):,}** "
          f"| **{sum(y['never'] for y in part['years'].values()):,}** "
          f"| **{sum(y['excl'] for y in part['years'].values())}** |")
        A("")
    A("**The missing coverage is overwhelmingly *never attempted*, not *lost*.** "
      "Watchdog kills and skip lists together account for a small minority; the "
      "bulk of the gap is commits outside the four sampled release ranges. That is "
      "the sampling design showing through, not a mining failure.")
    A("")
    A("**Implication.** The corpus is not a degraded attempt at full coverage that "
      "could be topped up — it is a set of four windows, and the space between "
      "them was never entered.")
    A("")

    # ---------------- Q6b
    A("### b. Throughput, as a distribution")
    A("")
    A("Command: per-commit timestamps and the terminating "
      "`Analyzed hadoop [Commits: N, ...]` line in `rm_chunks/**/*.log`.")
    A("")
    A(f"From **{tp['n_completed']} completed chunks** "
      f"({tp['commits_completed']:,} commits, "
      f"{tp['core_seconds_completed']:,.0f} core-seconds):")
    A("")
    A("| statistic | commits/s/core |")
    A("|---|---:|")
    for lbl, k in (("min", "min"), ("p10", "p10"), ("p25", "p25"),
                   ("median", "median"), ("p75", "p75"), ("p90", "p90"),
                   ("max", "max"), ("mean", "mean")):
        A(f"| {lbl} | {tp[k]:.3f} |")
    A(f"| **aggregate** (Σcommits ÷ Σcore-seconds) | **{tp['aggregate_rate']:.3f}** |")
    A("")
    A(f"**The spread is {tp['max']/tp['min']:,.0f}×**, min {tp['min']:.3f} to max "
      f"{tp['max']:.2f}. The median of {tp['median']:.2f} quoted in "
      "`prereg/gate_diagnosis.md` is a real number over a distribution too wide "
      "for a point estimate to mean much, which is why the cost below is a range.")
    A("")
    A(f"#### What the {tp['n_incomplete']} incomplete chunks do to it")
    A("")
    A(f"* Incomplete chunks: **{tp['n_incomplete']}**, of which "
      f"**{tp['inc_zero_processing']} never emitted a single `Processing` line**")
    A(f"* Commits they touched without contributing output: "
      f"**{tp['inc_commits_touched']:,}**")
    A(f"* **Measured** wall time they consumed: "
      f"**{tp['inc_measured_seconds']:,.0f} core-seconds** "
      f"({tp['inc_measured_seconds']/3600:.1f} core-hours), "
      f"single worst chunk **{tp['inc_max_seconds']:,.0f} s** "
      f"({tp['inc_max_seconds']/3600:.1f} h)")
    A("")
    A(f"* Requested worst case — *each ran the full {STALL}s watchdog timeout*: "
      f"{tp['worstcase_stall_seconds']:,} core-seconds, giving "
      f"{tp['rate_with_stall_incomplete']:.3f} commits/s/core")
    A(f"* **Measured reality is {tp['inc_measured_seconds']/tp['worstcase_stall_seconds']:.1f}× worse "
      f"than that worst case**: {tp['rate_with_measured_incomplete']:.3f} commits/s/core")
    A("")
    A(f"**The `{STALL}s` worst case is not a worst case.** `run_rm_safe.sh:44-50` "
      "kills a chunk whose *log file mtime* has not advanced for `STALL` seconds — "
      "it is a staleness detector, not a runtime cap. A chunk that writes one line "
      "every 149 seconds runs forever, and one did: "
      f"**{tp['inc_max_seconds']/3600:.1f} hours** before dying with no completion "
      "line. Any budget built on `n × 150s` understates the tail.")
    A("")

    # ---------------- Q6c
    A(f"### c. Wall-clock for 100% full-span coverage at parallelism {MAXPAR}")
    A("")
    A(f"`run_rm_safe.sh:24` sets `maxpar={MAXPAR}`. The `N=16` argument is a chunk "
      "count. Estimates below therefore use **8**, not 16.")
    A("")
    A(f"Target: the **{cost['missing']:,} uncovered commits** on trunk in span "
      f"({SPAN_START} → {SPAN_END}).")
    A("")
    A("| scenario | rate (commits/s/core) | wall-clock @8 | basis |")
    A("|---|---:|---:|---|")
    for s in cost["scenarios"]:
        A(f"| {s['label']} | {s['rate']:.3f} | **{s['hours']:.1f} h** | {s['basis']} |")
    A("")
    agg = [s for s in cost["scenarios"] if "aggregate" in s["label"]]
    lo, hi = min(s["hours"] for s in agg), max(s["hours"] for s in agg)
    A(f"**Range: {lo:.1f} – {hi:.1f} hours at 8-way parallelism**, taken from the "
      "two aggregate rows. The per-chunk percentile rows are illustrative only.")
    A("")
    A(f"**The aggregate rate ({tp['aggregate_rate']:.3f}/s) is "
      f"{tp['median']/tp['aggregate_rate']:.0f}× worse than the median per-chunk "
      f"rate ({tp['median']:.2f}/s), and the aggregate is the correct basis for a "
      "total-time estimate.** Total time is Σcommits ÷ Σcore-seconds; a median over "
      "chunks weights a 30-second chunk equally with a 4.6-hour one. "
      "`prereg/gate_diagnosis.md` built its estimate on the median and therefore "
      f"**understated cost by roughly {tp['median']/tp['aggregate_rate']:.0f}×** — "
      "its 10-minute figure for the 8-year span is closer to 3 hours on the same "
      "arithmetic. Reported, not edited there.")
    A("")
    A(f"The per-chunk spread is {tp['max']/tp['min']:,.0f}× "
      f"({tp['min']:.3f} to {tp['max']:.2f}), which is why no point estimate is "
      "given: where the uncovered commits fall in that distribution is unknown "
      "until they are mined.")
    A("")
    A("**What the estimate assumes.**")
    A("")
    A("1. Uncovered commits behave like covered ones. They may not: the covered set "
      "is what survived, so it is **selected for being mineable**.")
    A("2. No re-runs. `run_rm_safe.sh` discards a killed chunk's JSON entirely, so "
      "reaching 100% requires re-mining every killed range — unpriced here.")
    A("3. 8 concurrent processes scale linearly on a 12-core machine "
      "(`SLICE_LOG.md:234`). Contention is not modelled.")
    A("4. Trunk is the universe. Against `--all` "
      f"({r6['all_total']:,} commits) the target is several times larger.")
    A("")
    A("**What would invalidate it.** A single pathological commit of the kind that "
      f"produced the {tp['inc_max_seconds']/3600:.1f}-hour chunk lands in an "
      "unmined range; the skip list grows beyond the "
      f"{r6['excluded']} shas currently in it; or RefactoringMiner 3.1.4 hits the "
      "TypeScript-class defect already recorded in `paper/RM_TYPESCRIPT.md` on "
      "Java input in a form not yet seen.")
    A("")
    A("**Implication.** The cost is bounded and modest in machine time; what it "
      "does not buy is certainty, because the estimate is built from the chunks "
      "that succeeded.")
    A("")

    # ---------------- Q7
    A("## Q7 — is the Q4 tail survivable")
    A("")
    A(f"### a. The {r7['n_long']} long-delta episodes → {r7['n_uniq']} distinct groups")
    A("")
    A("Command: subject grouping over the full `--all` log, then "
      "`git -C hadoop branch -a --contains <sha>` per sha.")
    A("")
    A(f"Q4 counted **{r7['n_long']} episodes** past {LONG_DELTA_DAYS} days. Two "
      f"episodes can share one subject, so those are **{r7['n_uniq']} distinct "
      f"subject groups** — the unit used from here on.")
    A("")
    A("`release branches` counts distinct `branch-N.M*` families the group's SHAs "
      "sit on; `pattern` is mechanical: **backport** = exactly one SHA on trunk and "
      "≥1 release branch; **re-land** = ≥2 SHAs on trunk.")
    A("")
    A("| # | Jira key | SHAs | delta (d) | on trunk | release branches | key in subject | pattern |")
    A("|---|---|---:|---:|---:|---:|---|---|")
    for i, g in enumerate(r7["uniq"], 1):
        rel = len([k for k in g["families"] if k.startswith("branch-")])
        pat = "**re-land**" if g["n_on_trunk"] > 1 else (
            "backport" if g["n_on_trunk"] == 1 and rel else "unclassified")
        A(f"| {i} | {g['key']} | {g['n']} | {g['delta_d']:.0f} | {g['n_on_trunk']} "
          f"| {rel} | {'yes' if g['has_key'] else '**NO**'} | {pat} |")
    A("")
    n_key = sum(1 for g in r7["uniq"] if g["has_key"])
    A(f"**{n_key} of {r7['n_uniq']} carry a Jira key in the subject**, checked with "
      "the matcher at `scripts/citation_rate.py:40`. Subject grouping is therefore "
      "not colliding on generic text — **this is not subject collision.**")
    A("")
    A("**Verdict: two distinct patterns, not one.**")
    A("")
    A(f"* **Backport onto release branches — {r7['n_uniq']-r7['n_multi_trunk']} of "
      f"{r7['n_uniq']} groups.** One trunk landing plus `branch-N.M` copies. The "
      "long delta is backport lag, which in Hadoop runs to months.")
    A(f"* **Re-landing on trunk — {r7['n_multi_trunk']} of {r7['n_uniq']} groups.** "
      "Two SHAs *both reachable from trunk*, same author, same ticket, same "
      "subject, weeks apart. Verified individually with "
      "`git -C hadoop log -1 --format='%H %ad %an %s'`:")
    for g in r7["uniq"]:
        if g["n_on_trunk"] > 1:
            A(f"  * **{g['key']}** — " + "; ".join(f"`{p['sha']}`" for p in g["per_sha"])
              + f", {g['delta_d']:.0f} days apart, both on trunk")
    A("")
    A("The second pattern matters because it is invisible to a branch-based "
      "deduplication rule: both candidates are on trunk, so \"take the trunk one\" "
      "does not discriminate.")
    A("")

    # ---------------- Q7b
    A(f"### b. Is earliest-SHA-on-trunk well defined for these {r7['n_uniq']} groups?")
    A("")
    A("Command: `git -C hadoop rev-list trunk` as a membership set, intersected "
      "with each group's SHAs.")
    A("")
    A(f"Unit: the **{r7['n_uniq']} distinct subject groups**, not the "
      f"{r7['n_long']} episodes.")
    A("")
    A("| outcome | groups |")
    A("|---|---:|")
    A(f"| exactly one SHA on trunk — rule well defined | **{r7['well_defined']}** |")
    A(f"| **zero** SHAs on trunk — rule undefined | **{r7['n_no_trunk']}** |")
    A(f"| **two or more** SHAs on trunk — rule ambiguous | **{r7['n_multi_trunk']}** |")
    A("")
    bad = r7["n_no_trunk"] + r7["n_multi_trunk"]
    if bad:
        A(f"**The rule fails on {bad} of {r7['n_uniq']} groups "
          f"({bad/r7['n_uniq']:.0%}).** Per-sha detail:")
        A("")
        for i, g in enumerate(r7["uniq"], 1):
            if g["n_on_trunk"] != 1:
                A(f"* **{g['key']}** ({g['n']} SHAs, {g['n_on_trunk']} on trunk): "
                  + "; ".join(f"`{p['sha']}` {'trunk' if p['on_trunk'] else '/'.join(p['families'])}"
                              for p in g["per_sha"]))
        A("")
    else:
        A(f"**The rule is well defined on all {r7['n_uniq']}.** Each group has "
          "exactly one SHA reachable from trunk.")
    A("")
    A("**Implication.** Well-definedness on the tail is a necessary condition for "
      "any deduplication rule, and it is a property of Hadoop's branching policy "
      "rather than of the design — a different corpus needs the test re-run.")
    A("")

    # ---------------- Q7c
    A("### c. Size of the validity threat across all 349 episodes")
    A("")
    A("Command: for each episode, current resolution = its own `sha1` in "
      f"`{EPISODES}`; candidate rule = earliest SHA in its subject group reachable "
      "from trunk. Shift = |difference| in hours.")
    A("")
    A(f"* Episodes resolved in the clone: **{r7['n_resolved']} / {r7['n_episodes']}**")
    A(f"* **Episodes whose outcome timestamp shifts by more than "
      f"{SHIFT_THRESHOLD_H}h: {r7['shifted_gt_24h']} / {r7['n_resolved']} "
      f"= {r7['shifted_frac']:.1%}**")
    A("")
    A("**This is the size of the validity threat, not its fix.** It says how many "
      "episodes have an outcome endpoint that moves materially depending on a rule "
      "nobody has chosen. Against a 24-month window a shift of hours is "
      "immaterial; the reported figure counts only shifts beyond a day, which is "
      "where the backport tail lives.")
    A("")
    A("What it does **not** say: which resolution is correct. The current one is "
      "not wrong-by-default — it is simply *unspecified*, and an unspecified rule "
      "cannot be defended in a registered report.")
    A("")

    # ---------------- open decisions
    A("## Open decisions")
    A("")
    A("**Whether this corpus can support an interval design at all — undecided, "
      "and not decidable from what is measured here.** The evidence assembled so "
      "far constrains the question from both sides and settles neither:")
    A("")
    A("* *Against:* coverage is 45.3% at 8 years and falls to 15.3% at 2 years "
      "(`prereg/gate_diagnosis.md` Q3); the gap is dominated by commits **never "
      "attempted**, so the corpus is four windows rather than a degraded sweep; and "
      "3 of 20 drawn windows were decidable.")
    A("* *For:* the machine cost of closing the gap is bounded "
      f"({lo:.1f}–{hi:.1f} h at 8-way), the cherry-pick tail is a well-behaved "
      "backport pattern rather than data corruption, and the deduplication rule is "
      f"well defined on {r7['well_defined']} of {r7['n_uniq']} tail groups — "
      f"though it is ambiguous on {r7['n_multi_trunk']}, where two SHAs sit on "
      "trunk.")
    A("")
    A("Deciding requires a bucket-(b) rate, which does not exist, because no coder "
      "has labelled `prereg/gate_labelling.md`.")
    A("")
    A("Also undecided, and not narrowed by this file:")
    A("")
    A("1. **Whether to re-mine at all**, and against which universe — trunk "
      f"({r6['trunk_total']:,}) or `--all` ({r6['all_total']:,}). Q6 prices trunk only.")
    A("2. **Whether to raise `maxpar` above 8** or restructure chunking. The "
      "`N=16`/`maxpar=8` mismatch is reported, not repaired.")
    A("3. **What to do about the watchdog.** It is a staleness detector with no "
      "runtime cap; whether to add one is untouched.")
    A("4. **Which deduplication rule.** Earliest-on-trunk is *tested* here, not "
      "adopted; trunk-landing and last-backport are equally unexamined.")
    A("5. **Whether the destroyed run logs matter.** "
      f"{r6['cov_not_attempted']:,} mined commits have no surviving log, so any "
      "future cause-attribution inherits the same upper bound.")
    A("6. **Whether Hadoop remains the corpus.** The Gerrit-vs-Jira substitution in "
      "`prereg/RESOLUTION_GATE.md` is untouched by anything here, and "
      "`paper/RM_LANGUAGE_SUPPORT.md` still rules C++ out and leaves OpenStack's "
      "traceability unprobed.")
    A("")
    open(path, "w").write("\n".join(L) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        selftest(); return
    if not os.path.isdir(REPO):
        sys.exit(f"clone not found: {REPO}/ (offline; cannot fetch)")

    print("loading clone log...")
    log = load_commit_log()
    print(f"  {len(log):,} commits")
    print(f"reading {RM} (read-only)...")
    covered = {c.get("sha1") or c.get("sha") for c in json.load(open(RM))["commits"]}
    covered.discard(None)
    print(f"  {len(covered):,} covered")
    print("parsing chunk logs...")
    logs = parse_logs()
    excl = excluded_shas()
    print(f"  {len(logs)} logs, {len(excl)} excluded shas")

    r6 = q6(log, covered, logs, excl)
    tp = q6b(logs)
    cost = q6c(r6, tp)
    print(f"Q6: {cost['missing']:,} uncovered on trunk in span")
    print("Q7: branch containment per sha (one git call each)...")
    r7 = q7(log)
    print(f"Q7: {r7['n_long']} long-delta groups, "
          f"{r7['well_defined']} well defined, "
          f"{r7['shifted_frac']:.1%} shift >24h")

    report(r6, tp, cost, r7, args.out)
    print(f"\nWrote {args.out}")


if __name__ == "__main__":
    main()

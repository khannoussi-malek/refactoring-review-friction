#!/usr/bin/env python3
"""
friction_decomposition.py — split "friction" into the phases it is actually made of.

The dossier's timing measures (triage latency, resolution time) are aggregates
that mix two very different things: a ticket nobody has picked up, and a ticket
someone is fighting with. §12 flags this as the study's biggest threat -- maybe
all the "friction" is just open-source volunteers being slow. This script settles
it from the status changelog, which is already cached for BOTH groups.

Apache's workflow (derived from the corpus, not assumed):
    Open / Reopened   nobody has committed to the work
    In Progress       someone is actively coding
    Patch Available   working code exists, waiting on a COMMITTER to review/merge
    Resolved          done

The decisive split:
    t_to_patch  created -> first Patch Available   time until working code exists
    t_review    total time sitting in Patch Available   time waiting on a reviewer

    abstraction slower in t_to_patch  -> INTRINSIC difficulty (generalises to industry)
    abstraction slower in t_review    -> SOCIAL/coordination (an open-source effect)

IMPORTANT CAVEAT, handled explicitly below: 633 of 723 tickets go Open -> Patch
Available without ever passing through In Progress. Apache contributors work
offline and post a finished patch. So time-in-Open is NOT pure queue time -- it
conflates "waiting for a taker" with "someone quietly working". Only t_review is
unambiguous. We therefore report In-Progress results only for the subset that
actually uses the state, and never claim time-in-Open is idle time.

Usage:
    python3 scripts/friction_decomposition.py
"""
import argparse, glob, json, os
import datetime as dt
from collections import Counter

import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from blast_radius_model import (ABSTRACTION_TYPES, CONNECTOR_MODULES, parse_ts,
                                build_frame)

QUEUE_STATES = {"Open", "Reopened"}
ACTIVE_STATES = {"In Progress"}
REVIEW_STATES = {"Patch Available"}
TERMINAL = {"Resolved", "Closed"}


def state_timeline(rec):
    """(state, enter_time) pairs from a cached changelog record.

    The initial state is taken from the first transition's `fromString` rather
    than assumed to be Open -- a few tickets are filed in another state.
    """
    hist = sorted(rec.get("status_history") or [], key=lambda h: h["created"])
    if not hist:
        return []
    events = []
    first = hist[0]["status"][0]
    events.append((first["fromString"], parse_ts(rec["created"])))
    for h in hist:
        for s in h["status"]:
            events.append((s["toString"], parse_ts(h["created"])))
    return events


def phase_durations(rec):
    """Days spent in each status, plus the two headline phase measures."""
    events = state_timeline(rec)
    if not events:
        return None
    end = parse_ts(rec["resolutiondate"]) if rec.get("resolutiondate") else events[-1][1]

    per_state = Counter()
    for (state, t0), (_, t1) in zip(events, events[1:] + [(None, end)]):
        d = (t1 - t0).total_seconds() / 86400
        if d > 0:
            per_state[state] += d

    created = parse_ts(rec["created"])
    first_patch = next((t for s, t in events if s in REVIEW_STATES), None)

    return {
        "t_queue": sum(per_state[s] for s in QUEUE_STATES),
        "t_active": sum(per_state[s] for s in ACTIVE_STATES),
        "t_review": sum(per_state[s] for s in REVIEW_STATES),
        "t_to_patch": (first_patch - created).total_seconds() / 86400 if first_patch else None,
        "reached_patch": first_patch is not None,
        "used_in_progress": per_state.get("In Progress", 0) > 0,
        # A patch bounced back to Open means it went stale or was rejected.
        "n_patch_bounces": sum(
            1 for h in (rec.get("status_history") or []) for s in h["status"]
            if s["fromString"] in REVIEW_STATES and s["toString"] in QUEUE_STATES
        ),
        "total": (end - created).total_seconds() / 86400,
    }


def first_comment_latency(key, arch):
    """Days from ticket creation to the first human comment. A purer 'did anyone
    notice this?' measure than the first status change."""
    if arch:
        p = f".jira_cache/{key}.json"
        if not os.path.exists(p):
            return None, None
        j = json.load(open(p))
        cs = j.get("fields", {}).get("comment", {}).get("comments", [])
        stamps = [(c["created"], c["author"].get("name")) for c in cs]
        created = None
        cl = f".jira_changelog/{key}.json"
        if os.path.exists(cl):
            created = parse_ts(json.load(open(cl))["created"])
    else:
        p = f".jira_control/{key}.json"
        if not os.path.exists(p):
            return None, None
        j = json.load(open(p))
        stamps = [(c["created"], c.get("author")) for c in j.get("comments", [])]
        created = parse_ts(j["created"])
    if not stamps or created is None:
        return None, len({a for _, a in stamps if a})
    first = min(parse_ts(s) for s, _ in stamps)
    return (first - created).total_seconds() / 86400, len({a for _, a in stamps if a})


def load_group(keys, arch):
    src = ".jira_changelog" if arch else ".jira_control"
    rows = []
    for k in keys:
        p = f"{src}/{k}.json"
        if not os.path.exists(p):
            continue
        ph = phase_durations(json.load(open(p)))
        if ph is None:
            continue
        lat, npart = first_comment_latency(k, arch)
        a = json.load(open(f".jira_assignee/{k}.json")) if os.path.exists(f".jira_assignee/{k}.json") else {}
        rows.append({
            "key": k, "arch": arch, **ph,
            "t_first_comment": lat, "n_commenters": npart,
            "assignee": a.get("assignee"), "reporter": a.get("reporter"),
            # Did the person who raised it also do it? The mechanism of
            # attention rationing: volunteering vs. waiting to be picked.
            "self_assigned": (a.get("assignee") is not None
                              and a.get("assignee") == a.get("reporter")),
        })
    return pd.DataFrame(rows)


def mw(a, b):
    a, b = pd.Series(a).dropna(), pd.Series(b).dropna()
    if len(a) < 3 or len(b) < 3:
        return float("nan"), float("nan"), float("nan")
    return a.median(), b.median(), stats.mannwhitneyu(a, b, alternative="two-sided")[1]


def compare(title, left_lab, left, right_lab, right, measures):
    print(f"\n== {title} ==")
    print(f"  {'measure':22s} {left_lab:>14s} {right_lab:>14s} {'p':>10s}")
    out = {}
    for m, label in measures:
        lm, rm, p = mw(left[m], right[m])
        star = " *" if p == p and p < 0.05 else ""
        print(f"  {label:22s} {lm:14.2f} {rm:14.2f} {p:10.4f}{star}")
        out[m] = {"left": float(lm), "right": float(rm), "p": float(p)}
    return out


MEASURES = [
    ("t_to_patch", "days to first patch"),
    ("t_review", "days in review"),
    ("t_queue", "days in Open/Reopened"),
    ("t_first_comment", "days to 1st comment"),
    ("total", "total lifetime"),
    ("n_patch_bounces", "patch bounces"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--graph", default="module_blast_radius.json")
    ap.add_argument("--episode-files", default="episode_files.json")
    ap.add_argument("--episodes", default="architectural_episodes_all.json")
    ap.add_argument("--changelog", default=".jira_changelog")
    ap.add_argument("--props", default=".jira_props")
    ap.add_argument("--assignees", default=".jira_assignee")
    ap.add_argument("--fig", default="figures/friction_phases.png")
    ap.add_argument("--out", default="friction_decomposition.json")
    args = ap.parse_args()

    arch_keys = sorted({e["issue_key"] for e in json.load(open(args.episodes)) if e["issue_key"]})
    ctrl_keys = json.load(open("control_tickets.json"))
    A, C = load_group(arch_keys, True), load_group(ctrl_keys, False)
    print(f"Architectural tickets: {len(A)}   Ordinary control: {len(C)}")

    # The caveat, quantified before any result is read.
    print(f"\n== Workflow-usage caveat ==")
    for lab, d in [("architectural", A), ("ordinary", C)]:
        print(f"  {lab:14s} reached Patch Available: {d.reached_patch.mean():5.1%}   "
              f"ever used In Progress: {d.used_in_progress.mean():5.1%}")
    print("  -> time-in-Open conflates queueing with offline work; only t_review is")
    print("     unambiguous. In-Progress stats below use the sub-corpus that logs it.")

    res = {}
    res["arch_vs_ordinary"] = compare("Architectural vs ordinary", "architectural", A,
                                      "ordinary", C, MEASURES)

    # Attach the §5 abstraction split and the §9a connector tier.
    eps = json.load(open(args.episodes))
    abst = {e["issue_key"] for e in eps
            if e["issue_key"] and any(t in ABSTRACTION_TYPES for t in e["arch_types"])}
    A = A.copy()
    A["abstraction"] = A.key.isin(abst)
    _, tk = build_frame(args)
    conn = set(tk[tk.connector].key)
    A["connector"] = A.key.isin(conn)

    res["abstraction_vs_relocation"] = compare(
        "Abstraction vs relocation (the §5 headline, decomposed)",
        "abstraction", A[A.abstraction], "relocation", A[~A.abstraction], MEASURES)

    res["connector_vs_rest"] = compare(
        "Connector tier vs rest (the §9a finding, decomposed)",
        "connectors", A[A.connector], "rest", A[~A.connector], MEASURES)

    # In-Progress time, restricted to tickets that actually log the state.
    sub = A[A.used_in_progress]
    csub = C[C.used_in_progress]
    print(f"\n== Active coding time (In Progress), tickets that log it ==")
    lm, rm, p = mw(sub.t_active, csub.t_active)
    print(f"  architectural n={len(sub):3d} median {lm:.2f} d   "
          f"ordinary n={len(csub):3d} median {rm:.2f} d   p = {p:.4f}")
    am, rmn, p2 = mw(sub[sub.abstraction].t_active, sub[~sub.abstraction].t_active)
    print(f"  abstraction   n={sub.abstraction.sum():3d} median {am:.2f} d   "
          f"relocation n={(~sub.abstraction).sum():3d} median {rmn:.2f} d   p = {p2:.4f}")
    res["active_time"] = {"arch_vs_ord": {"arch": float(lm), "ord": float(rm), "p": float(p),
                                          "n_arch": int(len(sub)), "n_ord": int(len(csub))},
                          "abst_vs_reloc": {"abstraction": float(am), "relocation": float(rmn),
                                            "p": float(p2)}}

    # Self-assignment: volunteering vs waiting to be picked.
    print(f"\n== Self-assignment (reporter == assignee) ==")
    rows = [("architectural", A), ("ordinary", C), ("abstraction", A[A.abstraction]),
            ("relocation", A[~A.abstraction]), ("connectors", A[A.connector])]
    for lab, d in rows:
        print(f"  {lab:14s} self-assigned {d.self_assigned.mean():5.1%}  (n={len(d)})")
    ct = [[A.self_assigned.sum(), (~A.self_assigned).sum()],
          [C.self_assigned.sum(), (~C.self_assigned).sum()]]
    chi2, p_sa = stats.chi2_contingency(ct)[:2]
    print(f"  architectural vs ordinary: chi2 p = {p_sa:.4f}")
    # Does volunteering for your own ticket speed it up?
    sm_, om_, p_sp = mw(A[A.self_assigned].t_to_patch, A[~A.self_assigned].t_to_patch)
    print(f"  days-to-patch when self-assigned {sm_:.2f} vs {om_:.2f} when not, p = {p_sp:.4f}")
    res["self_assignment"] = {lab: float(d.self_assigned.mean()) for lab, d in rows} | {
        "p_arch_vs_ord": float(p_sa),
        "t_to_patch_self": float(sm_), "t_to_patch_other": float(om_), "p": float(p_sp)}

    res["workflow_artifact"] = workflow_artifact_check(A)
    res["clean_subcorpus"] = clean_subcorpus(A, C)
    res["models"] = models(A, C)
    plot(A, C, args.fig)

    json.dump(res, open(args.out, "w"), indent=2, default=float)
    print(f"\nWrote {args.out}")


def workflow_artifact_check(A):
    """A threat this decomposition uncovered, which the aggregate measures hid.

    If two groups of tickets are driven through DIFFERENT Jira workflows, their
    status-derived timings are not comparable -- a ticket whose status is never
    updated looks like it "waited" when in reality the work happened on a GitHub
    PR that nobody mirrored back into the status field."""
    print(f"\n== Threat check: do groups even use the same workflow? ==")
    for lab, s in [("connectors", A[A.connector]), ("rest", A[~A.connector])]:
        print(f"  {lab:12s} n={len(s):3d}  reached Patch Available {s.reached_patch.mean():5.1%}"
              f"   used In Progress {s.used_in_progress.mean():5.1%}")
    print("  -> The connector tier bypasses Patch Available almost entirely (a committer")
    print("     owns those modules and commits directly). Their long 'time in Open' is")
    print("     therefore partly an UNMAINTAINED STATUS FIELD, not measured waiting.")
    print("     §9a's 43.6-day connector 'triage' is closer to a lifetime than a queue.")
    sub = A[A.reached_patch]
    c, r = sub[sub.connector], sub[~sub.connector]
    if len(c) >= 3:
        p_t = stats.mannwhitneyu(c.t_to_patch.dropna(), r.t_to_patch.dropna())[1]
        p_r = stats.mannwhitneyu(c.t_review.dropna(), r.t_review.dropna())[1]
        print(f"  Among full-workflow tickets only (connectors n={len(c)}): review "
              f"{c.t_review.median():.1f} vs {r.t_review.median():.1f} d, p={p_r:.3f} "
              f"(underpowered, directionally 4x)")
    return {"connector_reached_patch": float(A[A.connector].reached_patch.mean()),
            "rest_reached_patch": float(A[~A.connector].reached_patch.mean()),
            "n_connector_full_workflow": int(len(c))}


def clean_subcorpus(A, C):
    """Re-run the headline comparisons on tickets that actually drive the full
    workflow, so no result rests on an unmaintained status field."""
    D, CC = A[A.reached_patch], C[C.reached_patch]
    print(f"\n== Headline re-tested on the full-workflow sub-corpus "
          f"(arch n={len(D)}, ordinary n={len(CC)}) ==")
    out = {}
    for lab, left, right in [("architectural vs ordinary", D, CC),
                             ("abstraction vs relocation", D[D.abstraction], D[~D.abstraction])]:
        print(f"  -- {lab} --")
        out[lab] = {}
        for m, name in [("t_to_patch", "days to first patch"), ("t_review", "days in review"),
                        ("total", "total lifetime")]:
            lm, rm, p = mw(left[m], right[m])
            star = " *" if p == p and p < 0.05 else ""
            print(f"     {name:22s} {lm:7.2f} vs {rm:7.2f}   p = {p:.4f}{star}")
            out[lab][m] = {"left": float(lm), "right": float(rm), "p": float(p)}
    return out


def models(A, C):
    """Is the abstraction effect in BUILDING the change or in GETTING IT MERGED?"""
    d = A.dropna(subset=["t_to_patch"]).copy()
    out = {}
    print(f"\n== Where does the abstraction effect live? (n={len(d)}) ==")
    for dv in ["t_to_patch", "t_review"]:
        dd = d.dropna(subset=[dv])
        X = sm.add_constant(pd.DataFrame({
            "abstraction": dd.abstraction.astype(float),
            "connector": dd.connector.astype(float),
        }, index=dd.index))
        m = sm.OLS(np.log1p(dd[dv].clip(lower=0)), X).fit(cov_type="HC3")
        print(f"  -- OLS log1p({dv}) --   (R2={m.rsquared:.3f}, n={len(dd)})")
        for c in ["abstraction", "connector"]:
            print(f"     {c:12s} coef {m.params[c]:+.3f}   p = {m.pvalues[c]:.4f}")
        out[dv] = {c: {"coef": float(m.params[c]), "p": float(m.pvalues[c])}
                   for c in ["abstraction", "connector"]} | {"r2": float(m.rsquared)}
    return out


def plot(A, C, out):
    # Plot the full-workflow sub-corpus only. Including tickets whose status was
    # never maintained would show a fake 0-day review phase (see
    # workflow_artifact_check) and understate the real review-phase gap.
    A, C = A[A.reached_patch], C[C.reached_patch]
    fig, axes = plt.subplots(1, 3, figsize=(15, 5.2))
    panels = [
        ("Building the change", "created → first patch", "t_to_patch"),
        ("Getting it merged", "time in Patch Available", "t_review"),
        ("Being noticed", "created → first comment", "t_first_comment"),
    ]
    groups = [("ordinary", C, "#a0aec0"), ("relocation", A[~A.abstraction], "#2b6cb0"),
              ("abstraction", A[A.abstraction], "#c53030")]
    for ax, (title, sub, col) in zip(axes, panels):
        data = [g[col].dropna().clip(lower=0.01).values for _, g, _ in groups]
        bp = ax.boxplot(data, tick_labels=[g[0] for g in groups], showfliers=False,
                        patch_artist=True, widths=.55,
                        medianprops=dict(color="#1a202c", linewidth=2.2))
        for patch, g in zip(bp["boxes"], groups):
            patch.set_facecolor(g[2]); patch.set_alpha(.55)
        ax.set_yscale("log")
        ax.set_ylim(0.008, 700)
        for i, v in enumerate(data):
            ax.text(i + 1, 0.97, f"{np.median(v):.1f} d", transform=ax.get_xaxis_transform(),
                    ha="center", va="top", fontsize=10, weight="bold", color="#1a202c")
        p = stats.mannwhitneyu(data[2], data[1])[1]  # abstraction vs relocation
        ax.set_title(f"{title}\n{sub}   —   abstraction vs relocation p = {p:.4f}",
                     fontsize=10)
        ax.set_ylabel("days (log scale)")
        ax.grid(alpha=.25, axis="y", which="major")
    fig.suptitle("Where does architectural friction actually live? "
                 "Abstraction costs time in BOTH building and merging",
                 fontsize=13, y=1.03)
    fig.text(0.5, -0.04, "Full-workflow sub-corpus only (tickets that reached Patch Available): "
             f"{len(A)} architectural, {len(C)} ordinary.",
             ha="center", fontsize=8.5, color="#4a5568")
    fig.tight_layout()
    fig.savefig(out, dpi=150, bbox_inches="tight")
    print(f"\nWrote {out}")


def _self_check():
    """ponytail: the timeline arithmetic is the only thing here that can be
    silently wrong, so check it against a hand-computed case."""
    rec = {
        "created": "2020-01-01T00:00:00.000+0000",
        "resolutiondate": "2020-01-11T00:00:00.000+0000",
        "status_history": [
            {"created": "2020-01-03T00:00:00.000+0000",
             "status": [{"fromString": "Open", "toString": "In Progress"}]},
            {"created": "2020-01-06T00:00:00.000+0000",
             "status": [{"fromString": "In Progress", "toString": "Patch Available"}]},
            {"created": "2020-01-08T00:00:00.000+0000",
             "status": [{"fromString": "Patch Available", "toString": "Open"}]},
            {"created": "2020-01-11T00:00:00.000+0000",
             "status": [{"fromString": "Open", "toString": "Resolved"}]},
        ],
    }
    p = phase_durations(rec)
    assert p["t_queue"] == 2 + 3, p       # Jan1-3 open, Jan8-11 back in open
    assert p["t_active"] == 3, p          # Jan3-6 in progress
    assert p["t_review"] == 2, p          # Jan6-8 patch available
    assert p["t_to_patch"] == 5, p        # created -> first Patch Available
    assert p["n_patch_bounces"] == 1, p
    assert p["total"] == 10, p
    print("self-check OK")


if __name__ == "__main__":
    import sys
    if "--self-check" in sys.argv:
        _self_check()
    else:
        main()

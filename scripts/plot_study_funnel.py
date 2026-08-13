#!/usr/bin/env python3
"""
plot_study_funnel.py -- figures/eligibility_funnel.png

The study's OTHER funnel. figures/study_funnel.png is the Hadoop *mining* funnel
(8,919 commits -> 3,949 with refactoring -> 51,861 refactorings -> 349
architectural episodes) and is correct for what it shows. It has never shown
corpus eligibility or hypothesis attrition, which is what the methods paper needs.
This script emits that second figure and leaves the first alone.

Panel A -- eligibility: 38 projects probed, 12 clear the pre-registered 0.80
commit-side bar, all 12 Hadoop-ecosystem, with the measured drop reasons.
Read from paper/traceability_probe.json, so it cannot drift.

Panel B -- attrition: the six hypotheses that did not hold, each with its named
cause. These live in README.md §4 as prose and in PROJECT_STATE.md §2 as decision
rows; there is no JSON for them, so they are transcribed below with the commit
that killed each one. Every number is quoted from README.md §4 verbatim.

Deterministic: no clock, no randomness, fixed figure size and dpi.

R1: reads a coverage artifact only. No outcome data, no timing, no held-out
project is measured here.

Usage:
    python3 scripts/plot_study_funnel.py
"""
import json
import pathlib

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
PROBE = ROOT / "paper" / "traceability_probe.json"
OUT = ROOT / "figures" / "eligibility_funnel.png"

# README.md §4 -- "What did not hold". Transcribed, not computed: these are prose
# results with no generating JSON. (hypothesis, result, named cause, commit)
KILLED = [
    ("Structural review discussion\npredicts slower resolution",
     "HR 0.69 (p=0.003) → HR 1.10 (p=0.51)",
     "discussion-volume confound", "b8d1476"),
    ("Blast radius — depended-upon\nmodules invite hesitation",
     "p=0.33 with tier controlled",
     "the connector tier, not centrality", "6d1ed8d"),
    ("Maintainer concentration replaces\nthe hand-drawn tier",
     "collapses once module size enters",
     "collinear with module size, rho = −0.86", "93056ae"),
    ("Abstraction is harder\nthan relocation",
     "×1.54 [0.97, 2.43], p=0.068, n=319",
     "split defined post hoc", "4b8c3af"),
    ("Architectural refactoring missed a\ndecade of process improvement",
     "holds to 2019 (+0.192, p=0.021); post-2020 p=0.44",
     "control arm collapses 394 → 145 → 101", "4b8c3af"),
    ("A portable tier rule generalises",
     "0 of 3 replicate (p=0.210, 1.000, 0.310)",
     "vendor share selects large modules, not thin adapters", "48caf14"),
]

INK = "#1a1a1a"
GREY = "#c7ced6"
BLUE = "#4a90e2"
DEEP = "#1f5fbf"
RED = "#b5443a"


def load_eligibility():
    probe = json.loads(PROBE.read_text())
    projects = probe["projects"]
    passing = [r for r in projects if r["passes_bar"]]
    dropped = [r for r in projects if not r["passes_bar"]]

    reasons = {}
    for r in dropped:
        reasons[r["drop_reason"]] = reasons.get(r["drop_reason"], 0) + 1
    # deterministic order: most common first, then alphabetical
    ordered = sorted(reasons.items(), key=lambda kv: (-kv[1], kv[0]))

    if len(projects) != probe["n_probed"]:
        raise ValueError("n_probed disagrees with the number of records")
    return probe, passing, dropped, ordered


def panel_a(ax, probe, passing, dropped, reasons):
    n_probed = probe["n_probed"]
    bar = probe["bar"]
    stages = [
        (f"Apache projects probed", n_probed, GREY),
        (f"clear the pre-registered\n{bar:.2f} commit-side bar", len(passing), BLUE),
        ("Hadoop-ecosystem", len(passing), DEEP),
    ]
    ys = range(len(stages))
    ax.barh(list(ys), [s[1] for s in stages],
            color=[s[2] for s in stages], height=0.62, zorder=3)
    for y, (label, n, _) in zip(ys, stages):
        ax.text(n + 0.7, y, f"{n}", va="center", ha="left",
                fontsize=15, fontweight="bold", color=INK, zorder=4)
    ax.set_yticks(list(ys))
    ax.set_yticklabels([s[0] for s in stages], fontsize=10.5)
    ax.invert_yaxis()
    ax.set_xlim(0, n_probed * 1.16)
    ax.set_xlabel("projects", fontsize=10)
    ax.set_title(
        f"{len(passing)} of {n_probed} projects can support an issue-linked study\n"
        f"and every one of them is from a single ecosystem",
        fontsize=12.5, fontweight="bold", color=INK, pad=12)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.grid(axis="x", color="#eef1f4", zorder=0)
    ax.set_axisbelow(True)

    lines = [f"{n} {reason}" for reason, n in reasons]
    ax.text(0.985, 0.06,
            f"{len(dropped)} dropped, by measured reason:\n" + "\n".join(lines),
            transform=ax.transAxes, ha="right", va="bottom", fontsize=8.6,
            color="#4a5462", linespacing=1.5,
            bbox=dict(boxstyle="round,pad=0.55", fc="#f7f9fb", ec="#dde3e9"))


def panel_b(ax):
    ax.axis("off")
    ax.set_title(
        "Six operationalisations of the original question, all closed\n"
        "with a named cause — the sampling frame became the finding",
        fontsize=12.5, fontweight="bold", color=INK, pad=12)

    n = len(KILLED)
    for i, (hyp, result, cause, sha) in enumerate(KILLED):
        y = 1.0 - (i + 0.5) / n
        ax.text(0.0, y, hyp, fontsize=9.2, va="center", ha="left",
                color=INK, linespacing=1.35)
        ax.text(0.455, y, result, fontsize=9.0, va="center", ha="left",
                color=RED, family="DejaVu Sans")
        ax.text(0.455, y - 0.055, cause, fontsize=8.0, va="center", ha="left",
                color="#5b6472", style="italic")
        # The killing commit is deliberately NOT drawn. A right-aligned sha column
        # collides with the longest result and cause strings at any font size that
        # stays legible, and the provenance belongs in the decision log anyway --
        # PROJECT_STATE.md §2 carries one row per hypothesis with its commit.
        if i < n - 1:
            ax.axhline(1.0 - (i + 1) / n, color="#eef1f4", lw=0.9)

    ax.text(0.0, -0.045,
            "Numbers verbatim from README.md §4. "
            "Killing commits: PROJECT_STATE.md §2.",
            fontsize=7.8, color="#8d96a3", va="top", ha="left")


def main():
    probe, passing, dropped, reasons = load_eligibility()

    fig, axes = plt.subplots(1, 2, figsize=(15.2, 5.0),
                             gridspec_kw={"width_ratios": [1.0, 1.32]})
    panel_a(axes[0], probe, passing, dropped, reasons)
    panel_b(axes[1])
    fig.subplots_adjust(left=0.135, right=0.975, top=0.80, bottom=0.13,
                        wspace=0.30)
    fig.savefig(OUT, dpi=150)
    plt.close(fig)
    print(f"wrote {OUT.relative_to(ROOT)}")
    print(f"  {probe['n_probed']} probed, {len(passing)} eligible, "
          f"{len(dropped)} dropped: " +
          ", ".join(f"{n} {r}" for r, n in reasons))


if __name__ == "__main__":
    main()

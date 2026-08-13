#!/usr/bin/env python3
"""
plot_two_channel.py — Jira keys vs GitHub issue references, all 38 projects.

The traceability bar is drawn on ONE channel: what fraction of commits cite a
Jira key. That framing hides the fact that projects below the bar are not
undisciplined -- most of them reference issues heavily, just in the other
system. This plots both channels at once so the bar's real meaning is visible:
it selects for *which tracker* a project writes into, not for whether it links
commits to issues at all.

Regenerable entirely from paper/traceability_probe.json.

Usage:
    python3 scripts/plot_two_channel.py --out figures/two_channel.png
"""
import argparse, json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BAR = 0.80


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", default="paper/traceability_probe.json")
    ap.add_argument("--out", default="figures/two_channel.png")
    args = ap.parse_args()

    rows = json.load(open(args.probe))["projects"]
    fig, ax = plt.subplots(figsize=(11, 8.5))

    for r in rows:
        x = r["rate_multi"] * 100
        y = r["rate_github_issue"] * 100
        keep = r["passes_bar"]
        ax.scatter(x, y, s=64 if keep else 40,
                   c="#2b6cb0" if keep else "#c53030",
                   marker="o" if keep else "x",
                   zorder=3, linewidths=1.8,
                   edgecolors="white" if keep else None)
        # Nudge labels off the marker; a few dense spots get manual offsets.
        dx, dy = 1.2, 1.2
        if r["project"] in ("skywalking", "shardingsphere"):
            dy = -3.0
        if r["project"] in ("knox", "drill"):
            dy = -3.2
        ax.annotate(r["project"], (x, y), fontsize=7.6, xytext=(dx, dy),
                    textcoords="offset points",
                    color="#1a365d" if keep else "#742a2a")

    ax.axvline(BAR * 100, color="#2f855a", linestyle="--", linewidth=1.8, zorder=2)
    ax.text(BAR * 100 + 0.8, 97, f"traceability bar = {BAR:.2f}", rotation=90,
            va="top", fontsize=9, color="#2f855a")
    # Everything right of the line is the usable corpus.
    ax.axvspan(BAR * 100, 103, color="#2f855a", alpha=0.06, zorder=1)

    ax.plot([0, 100], [0, 100], color="#a0aec0", linewidth=1, linestyle=":", zorder=1)
    ax.text(52, 55, "equal use of both trackers", rotation=45, fontsize=8,
            color="#718096", ha="center", va="center")

    n_pass = sum(1 for r in rows if r["passes_bar"])
    ax.set_xlabel("Commits citing a Jira key (%)", fontsize=11)
    ax.set_ylabel("Commits citing a GitHub issue (#NNN or GH-NNN) (%)", fontsize=11)
    ax.set_title("The bar selects a tracker, not a discipline\n"
                 f"{len(rows)} Apache Maven projects; {n_pass} pass the {BAR:.2f} "
                 "Jira-traceability bar", fontsize=12.5)
    ax.set_xlim(-3, 103)
    ax.set_ylim(-3, 103)
    ax.grid(alpha=0.25)

    handles = [
        plt.Line2D([], [], marker="o", linestyle="", color="#2b6cb0",
                   markersize=8, label=f"passes bar (n={n_pass})"),
        plt.Line2D([], [], marker="x", linestyle="", color="#c53030",
                   markersize=8, label=f"dropped (n={len(rows)-n_pass})"),
    ]
    ax.legend(handles=handles, fontsize=9, loc="upper right")

    fig.text(0.5, 0.005,
             "Points high and left reference issues heavily — in GitHub, not Jira. "
             "Ozone (top right) runs both, with Jira as system of record.",
             ha="center", fontsize=8.6, color="#4a5568")
    fig.tight_layout()
    fig.savefig(args.out, dpi=150, bbox_inches="tight")
    print(f"Wrote {args.out}")

    hi_gh = [r for r in rows if not r["passes_bar"] and r["rate_github_issue"] > 0.5]
    print(f"dropped projects citing GitHub issues in >50% of commits: {len(hi_gh)}")
    for r in sorted(hi_gh, key=lambda r: -r["rate_github_issue"]):
        print(f"   {r['project']:26s} jira {r['rate_multi']*100:5.1f}%  "
              f"github {r['rate_github_issue']*100:5.1f}%")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
llm_rater_pilot.py — second-rater pilot on the F2 codebook, and what it can and
cannot establish.

`README.md` §8 records that inter-rater agreement cannot be computed by one
person, and that the codebook sits behind that. This pilot uses a large language
model as an independent second rater over the 40-comment set in
`codebook_labeling.md`, applying `codebook.md` verbatim.

WHAT THIS SCRIPT DOES NOT DO. It does not call a model. The model's labels are an
input, committed in `paper/llm_rater_labels.json`, exactly as
`paper/matcher_labels.json` commits the labels of the manual matcher check. What
this computes is the arithmetic on top of them, so the arithmetic is auditable
even though the rating is not repeatable.

THE BLOCKER THIS SCRIPT MEASURES. Cohen's kappa needs PAIRED labels. The human
pass did not keep any: columns A and B in `codebook_labeling.md` are empty for
all 40 rows, and `codebook_results.md` records only the two 3-cell margins
(flagged 5/5/10, unflagged 1/1/18). Kappa is therefore not computable from what
exists, and no amount of second-rating recovers it.

What IS computable from margins alone are the BOUNDS kappa must lie within,
because the expected-agreement term depends only on the margins:

    Pe      = sum_k p1_k * p2_k                       (fixed by the margins)
    Po_max  = sum_k min(p1_k, p2_k)                   (most agreeable pairing)
    Po_min  = max(0, max_k (p1_k + p2_k - 1))         (least agreeable pairing)

Po_min is the largest diagonal mass any transport plan is forced to carry: row k
holds p1_k and the columns other than k hold 1 - p2_k, so p1_k + p2_k - 1 cannot
be pushed off the diagonal. Both endpoints are attainable, so the interval is
tight.

Usage:
    python3 scripts/llm_rater_pilot.py --labels paper/llm_rater_labels.json
"""
import argparse, json
from collections import Counter

CATS = ["S", "I", "C"]

# codebook_results.md, committed at de657c3. The human pass recorded margins per
# bucket and nothing per comment.
HUMAN_MARGINS = {
    "flagged":  {"S": 5, "I": 5, "C": 10},
    "unflagged": {"S": 1, "I": 1, "C": 18},
}


def margins(labels):
    c = Counter(labels)
    return {k: c.get(k, 0) for k in CATS}


def kappa_bounds(m1, m2):
    n = sum(m1.values())
    assert n == sum(m2.values()), "margins must cover the same n"
    p1 = {k: m1[k] / n for k in CATS}
    p2 = {k: m2[k] / n for k in CATS}
    pe = sum(p1[k] * p2[k] for k in CATS)
    po_max = sum(min(p1[k], p2[k]) for k in CATS)
    po_min = max(0.0, max(p1[k] + p2[k] - 1 for k in CATS))
    k_of = lambda po: (po - pe) / (1 - pe) if pe < 1 else None
    return {"n": n, "pe": pe, "po_max": po_max, "po_min": po_min,
            "kappa_max": k_of(po_max), "kappa_min": k_of(po_min)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--labels", default="paper/llm_rater_labels.json")
    ap.add_argument("--out", default="paper/llm_rater_pilot.json")
    args = ap.parse_args()

    rows = json.load(open(args.labels))["labels"]
    assert len(rows) == 40, f"expected 40 comments, got {len(rows)}"
    flagged = [r for r in rows if r["n"] <= 20]
    unflagged = [r for r in rows if r["n"] > 20]

    out = {"source_labels": args.labels,
           "human_margins": HUMAN_MARGINS,
           "kappa_computable": False,
           "why": "codebook_labeling.md columns A and B are empty for all 40 "
                  "rows; codebook_results.md records margins only. Cohen's "
                  "kappa needs paired labels.",
           "buckets": {}}

    for name, subset in (("flagged", flagged), ("unflagged", unflagged)):
        llm = margins([r["label"] for r in subset])
        hum = HUMAN_MARGINS[name]
        b = {"llm_margins": llm, "human_margins": hum,
             "bounds": kappa_bounds(hum, llm)}
        out["buckets"][name] = b
        print(f"\n{name} (n={len(subset)})")
        print(f"  human : " + "  ".join(f"{k}={hum[k]:2d}" for k in CATS))
        print(f"  llm   : " + "  ".join(f"{k}={llm[k]:2d}" for k in CATS))
        bd = b["bounds"]
        print(f"  Pe={bd['pe']:.4f}  Po in [{bd['po_min']:.4f}, {bd['po_max']:.4f}]"
              f"  =>  kappa in [{bd['kappa_min']:+.3f}, {bd['kappa_max']:+.3f}]")

    pooled_h = {k: HUMAN_MARGINS["flagged"][k] + HUMAN_MARGINS["unflagged"][k]
                for k in CATS}
    pooled_l = margins([r["label"] for r in rows])
    out["pooled"] = {"llm_margins": pooled_l, "human_margins": pooled_h,
                     "bounds": kappa_bounds(pooled_h, pooled_l)}
    bd = out["pooled"]["bounds"]
    print(f"\npooled (n=40)")
    print(f"  human : " + "  ".join(f"{k}={pooled_h[k]:2d}" for k in CATS))
    print(f"  llm   : " + "  ".join(f"{k}={pooled_l[k]:2d}" for k in CATS))
    print(f"  Pe={bd['pe']:.4f}  Po in [{bd['po_min']:.4f}, {bd['po_max']:.4f}]"
          f"  =>  kappa in [{bd['kappa_min']:+.3f}, {bd['kappa_max']:+.3f}]")

    # The instrument result the codebook exists to produce.
    f = out["buckets"]["flagged"]
    u = out["buckets"]["unflagged"]
    out["keyword_rule"] = {
        "precision_human": HUMAN_MARGINS["flagged"]["S"] / 20,
        "precision_llm": f["llm_margins"]["S"] / 20,
        "recall_human": (HUMAN_MARGINS["flagged"]["S"] /
                         (HUMAN_MARGINS["flagged"]["S"] +
                          HUMAN_MARGINS["unflagged"]["S"])),
        "recall_llm": (f["llm_margins"]["S"] /
                       (f["llm_margins"]["S"] + u["llm_margins"]["S"])
                       if (f["llm_margins"]["S"] + u["llm_margins"]["S"]) else None),
    }
    kr = out["keyword_rule"]
    print(f"\nkeyword rule, as measured by each rater:")
    print(f"  precision : human {kr['precision_human']:.0%}  llm {kr['precision_llm']:.0%}")
    print(f"  recall    : human {kr['recall_human']:.0%}  llm {kr['recall_llm']:.0%}")

    json.dump(out, open(args.out, "w"), indent=1)
    print(f"\nWrote {args.out}")


if __name__ == "__main__":
    main()

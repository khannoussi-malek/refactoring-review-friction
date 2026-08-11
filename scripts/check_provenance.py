#!/usr/bin/env python3
"""
check_provenance.py -- resolve every number in the manuscript to something that
computed it, and grade how strong that resolution is.

WHY THIS WAS REWRITTEN (2026-08-05). The previous version tested
`if token in numbers.md` -- a raw substring search against a hand-written prose
file. It never opened a script, never checked a commit hash, and never looked at
an artifact, so it could be satisfied by typing a number into `numbers.md`. The
independent audit (`audit/NUMBERS.md` §7) showed it passing three tokens by
coincidence:

    0.86  <- the manuscript's "rho = -0.86", matched against `0.86232`,
             an unrelated proportion, and having no provenance row at all
    930   <- "930 commits on other branches", matched against the commit
             hash `93056ae`
    5.5   <- a section heading `## 5.5`, matched against `15.5%` / `55.5%`

Its headline, "175 sourced, 0 unsourced", was therefore not a provenance result.
A checker that cannot fail is worse than no checker, because the paper cited it
as evidence of rigour.

WHAT THIS VERSION DOES. Three graded tiers, and a token is reported at the
highest tier it reaches:

  ARTIFACT  The value appears in a committed machine-readable artifact (a
            JSON file under the repository root or paper/), matched
            numerically rather than textually: the artifact is walked, every
            numeric leaf is rendered at the manuscript token's own precision,
            and a hit means some computed value really does round to it. This
            is the only tier that establishes a number was computed.

  DOCUMENTED  The value appears in `paper/numbers.md` as a STANDALONE token --
            not as a substring of a longer number -- inside a section whose text
            names a script path that exists on disk and a commit hash that
            resolves in this repository. Weaker than ARTIFACT: it establishes a
            traceable claim of provenance, not the provenance itself.

  EXTERNAL  The value is attributed to a cited work rather than computed
            here -- it appears as a standalone token in `paper/PRIOR_WORK.md`,
            or in a `numbers.md` section that names a DOI or arXiv identifier.
            Its provenance is the cited paper, and the check for it is
            `audit/CITATIONS.md`, not this script.

  UNSOURCED  None of the above. Reported, and the script exits 1.

Exit 1 on any UNSOURCED strict token, so this can gate a submission.

Usage:
    python3 scripts/check_provenance.py            # write the report
    python3 scripts/check_provenance.py --quiet    # exit code only
"""
import argparse
import collections
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
MANUSCRIPT = ROOT / "paper" / "manuscript"
NUMBERS = ROOT / "paper" / "numbers.md"
PRIOR = ROOT / "paper" / "PRIOR_WORK.md"
OUT = MANUSCRIPT / "PROVENANCE_CHECK.md"
SKIP_FILES = {"PROVENANCE_CHECK.md", "PAPER.md", "UNSOURCED.md", "README.md"}

TOKEN = re.compile(r"\d[\d,]*(?:\.\d+)?%?")
DATEISH = re.compile(r"\d{4}-\d{2}(?:-\d{2})?")
YEAR = re.compile(r"^(19|20)\d{2}$")
SECTION = re.compile(r"^#{2,4}\s+(\d+(?:\.\d+)*)", re.M)

# Tokens that look numeric but are not measurements. Section numbers are
# derived from the manuscript's own headings rather than hand-listed, because
# hand-listing is what let `5.5` through.
NOT_MEASUREMENTS = {
    # DOI / arXiv / dataset identifiers
    "104005", "1804.02433", "2404.01950", "2501.15387", "2605.16133",
    "15719919", "21846139", "1882291.1882308", "2025113.2025120", "1882308", "2025120",
    # upstream issue, PR and branch identifiers, and one commit hash in prose
    "1124", "998", "1471779", "256", "5179907",
    # detector version 3.1.4 tokenises as "3.1"; licence versions CC BY 4.0
    # and CFF 1.2.0 tokenise as "4.0" and "1.2"
    "3.1", "4.0", "1.2", "2.0",
    # page ranges of cited works
    "97", "106", "121", "130", "259", "268",
}

ARTIFACT_GLOBS = ["*.json", "paper/*.json", "replication/*.json",
                  "predictions/*.json", "deposit/MANIFEST-v1.json"]
# Artifacts too large to walk on every run, and which carry no headline number.
ARTIFACT_SKIP = re.compile(r"refminer|module_commit_log|ticket_first_commit|"
                           r"ticket_change_size|pr_timeline|prs_|episode_files|"
                           r"MANIFEST-v1|matcher_sample|gate_")


def section_numbers():
    out = set()
    for f in MANUSCRIPT.glob("*.md"):
        for m in SECTION.finditer(f.read_text()):
            out.add(m.group(1))
    return out


def classify(tok, sections):
    """-> 'strict' | 'weak' | None (drop)."""
    if tok in NOT_MEASUREMENTS or tok in sections:
        return None
    if YEAR.match(tok):
        return "weak"
    digits = tok.strip("%").replace(",", "").replace(".", "")
    if len(digits) < 2:
        return None
    distinctive = ("," in tok or "." in tok or "%" in tok or len(digits) >= 3)
    return "strict" if distinctive else "weak"


# ----------------------------------------------------------------- tier ARTIFACT
def numeric_leaves(obj, out):
    if isinstance(obj, dict):
        for v in obj.values():
            numeric_leaves(v, out)
    elif isinstance(obj, list):
        for v in obj:
            numeric_leaves(v, out)
    elif isinstance(obj, bool):
        pass
    elif isinstance(obj, (int, float)):
        out.append(obj)


def artifact_values():
    """{rendered string -> set of artifact paths}, at several precisions."""
    idx = collections.defaultdict(set)
    seen = set()
    for g in ARTIFACT_GLOBS:
        for p in ROOT.glob(g):
            rel = str(p.relative_to(ROOT))
            if rel in seen or ARTIFACT_SKIP.search(rel):
                continue
            seen.add(rel)
            try:
                if p.stat().st_size > 40_000_000:
                    continue
                data = json.load(open(p))
            except Exception:
                continue
            leaves = []
            numeric_leaves(data, leaves)
            for v in leaves:
                for s in render(v):
                    idx[s].add(rel)
    return idx


def render(v):
    """Every way a manuscript might legitimately print this value."""
    out = set()
    if isinstance(v, int):
        out.add(str(v))
        out.add(f"{v:,}")
        return out
    for d in (0, 1, 2, 3, 4):
        out.add(f"{v:.{d}f}")
        out.add(f"{v:.{d}f}%")
        out.add(f"{v * 100:.{d}f}")
        out.add(f"{v * 100:.{d}f}%")
        try:
            out.add(f"{v:,.{d}f}")
            out.add(f"{v * 100:,.{d}f}")
        except ValueError:
            pass
    if float(v).is_integer():
        out.add(str(int(v)))
        out.add(f"{int(v):,}")
    return out


# --------------------------------------------------------------- tier DOCUMENTED
def numbers_sections():
    text = NUMBERS.read_text()
    parts = re.split(r"^#{2,3} +(.*)$", text, flags=re.M)
    out = [("preamble", parts[0])]
    for i in range(1, len(parts), 2):
        label = parts[i].strip()
        m = re.match(r"([0-9]+[a-z]?)\.\s*(.*)", label)
        short = f"§{m.group(1)}" if m else label.split("—")[0].strip()[:38]
        out.append((short, parts[i + 1]))
    return out


def standalone(tok, body):
    """Token present, not as a substring of a longer number."""
    return re.search(r"(?<![\d.,])" + re.escape(tok) + r"(?![\d,]*\d)", body) is not None


CITES = re.compile(r"doi:|arXiv|10\.\d{4}/|SEOSS|Rath|Dabic|Vieira|GHS|"
                   r"Bachmann|Iammarino|Esfandiari|PROMISE|ICSE|Zenodo",
                   re.I)


def section_backing(body, cache):
    """(scripts that exist, commit hashes that resolve) named in this section."""
    scripts = [s for s in set(re.findall(r"`(scripts/[\w/.-]+\.(?:py|sh))`", body))
               if (ROOT / s).exists()]
    hashes = []
    for h in set(re.findall(r"`([0-9a-f]{7,10})`", body)):
        if h not in cache:
            r = subprocess.run(["git", "-C", str(ROOT), "cat-file", "-t", h],
                               capture_output=True, text=True)
            cache[h] = r.stdout.strip() == "commit"
        if cache[h]:
            hashes.append(h)
    return scripts, hashes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()

    sections = section_numbers()
    sec = numbers_sections()
    art = artifact_values()
    hcache = {}

    strict, weak = collections.defaultdict(set), collections.defaultdict(set)
    for f in sorted(MANUSCRIPT.glob("*.md")):
        if f.name in SKIP_FILES:
            continue
        text = DATEISH.sub(" ", f.read_text())
        for raw in TOKEN.findall(text):
            tok = raw.rstrip(".,")
            k = classify(tok, sections)
            if k == "strict":
                strict[tok].add(f.name)
            elif k == "weak":
                weak[tok].add(f.name)

    tiers = {}
    for tok, files in strict.items():
        hits = art.get(tok) or art.get(tok.rstrip("%"))
        docs, ext = [], []
        for label, body in sec:
            if not standalone(tok, body):
                continue
            s, h = section_backing(body, hcache)
            if s or h:
                docs.append((label, s[0] if s else "—", h[0] if h else "—"))
            elif CITES.search(body):
                ext.append((label, "numbers.md"))
        if hits and docs:
            tiers[tok] = ("ARTIFACT", files,
                          [f"`{x}`" for x in sorted(hits)[:2]] +
                          [f"{docs[0][0]} → `{docs[0][1]}`"])
            continue
        if hits and not docs:
            # A committed value rounds to this token, but nothing in numbers.md
            # claims it as a quantity. That is exactly the -0.86 / 930 case the
            # audit found: a numeric coincidence standing in for provenance.
            tiers[tok] = ("ARTIFACT_NO_ROW", files,
                          [f"`{x}`" for x in sorted(hits)[:2]])
            continue
        if docs:
            tiers[tok] = ("DOCUMENTED", files, docs[:3])
            continue
        if standalone(tok, PRIOR.read_text()):
            tiers[tok] = ("EXTERNAL", files, [("paper/PRIOR_WORK.md",
                                               "attributed to a cited work")])
        elif ext:
            tiers[tok] = ("EXTERNAL", files, ext[:3])
        else:
            tiers[tok] = ("UNSOURCED", files, [])

    counts = collections.Counter(v[0] for v in tiers.values())
    L = []
    add = L.append
    add("# Provenance check — every number in the manuscript")
    add("")
    add("<!-- GENERATED by scripts/check_provenance.py. Do not edit by hand. -->")
    add("")
    add(f"**{counts['ARTIFACT']} ARTIFACT · {counts['DOCUMENTED']} DOCUMENTED · "
        f"{counts['EXTERNAL']} EXTERNAL · **{counts['ARTIFACT_NO_ROW']} "
        f"ARTIFACT-NO-ROW · {counts['UNSOURCED']} UNSOURCED** — of "
        f"{len(tiers)} distinctive numeric tokens.")
    add("")
    add("The three tiers are not interchangeable and the distinction is the "
        "point of this file.")
    add("")
    add("* **ARTIFACT** — the value is present in a committed machine-readable "
        "artifact, matched *numerically*: the JSON is walked, each numeric leaf "
        "is rendered at the token's own precision, and a hit means a computed "
        "value really does round to what the manuscript prints. This is the only "
        "tier that establishes the number was computed.")
    add("* **DOCUMENTED** — the value appears in `paper/numbers.md` as a "
        "standalone token, in a section that names a script existing on disk and "
        "a commit hash resolving in this repository. It establishes a traceable "
        "*claim* of provenance, not the provenance itself. Prose-only figures "
        "from pipelines whose outputs were not committed land here.")
    add("* **EXTERNAL** — attributed to a cited work rather than computed "
        "here. Its provenance is that paper, and the check for it is "
        "`audit/CITATIONS.md`, which verified every reference against the "
        "source text.")
    add("* **ARTIFACT-NO-ROW** — a committed value rounds to the token, but no "
        "`numbers.md` row claims it as a quantity. **This is a numeric "
        "coincidence standing in for provenance** and is treated as a failure: "
        "it is exactly what let `rho = -0.86` match an unrelated `0.86232` and "
        "`930` match a leaf in another artifact.")
    add("* **UNSOURCED** — none of the above. The script exits 1.")
    add("")
    add("**What ARTIFACT does not establish.** A numeric match shows that some "
        "committed computed value rounds to the printed token at the printed "
        "precision. It cannot show the two are the *same quantity* — no "
        "numeric check can. Quantity identity is what the `numbers.md` row and "
        "`audit/` are for, which is why ARTIFACT requires a row and "
        "ARTIFACT-NO-ROW fails.")
    add("")
    add("Rewritten 2026-08-05. The previous version was a substring test against "
        "a hand-written file and passed three tokens by coincidence; see this "
        "script's docstring and `audit/NUMBERS.md` §7.")
    add("")

    for tier in ("UNSOURCED", "ARTIFACT_NO_ROW", "DOCUMENTED", "EXTERNAL",
                 "ARTIFACT"):
        rows = sorted((t, v) for t, v in tiers.items() if v[0] == tier)
        add(f"## {tier} — {len(rows)}")
        add("")
        if not rows:
            add("_none_")
            add("")
            continue
        add("| number | appears in | resolved to |")
        add("|---|---|---|")
        for tok, (_, files, ev) in rows:
            if tier in ("ARTIFACT", "ARTIFACT_NO_ROW"):
                eu = ", ".join(str(x) for x in ev)
            elif tier == "DOCUMENTED":
                eu = "; ".join(f"{lab} → `{s}` `{h}`" for lab, s, h in ev)
            elif tier == "EXTERNAL":
                eu = "; ".join(f"{lab} — {w}" for lab, w in ev)
            else:
                eu = "**nothing**"
            add(f"| `{tok}` | {', '.join(sorted(files))} | {eu} |")
        add("")

    add(f"## Short integers and years — {len(weak)} tokens, listed not verified")
    add("")
    add("Literal matching proves nothing for these. Each is carried by a claim "
        "whose distinctive numbers are graded above.")
    add("")
    add("| number | appears in |")
    add("|---|---|")
    for tok in sorted(weak, key=lambda t: (len(t), t)):
        add(f"| `{tok}` | {', '.join(sorted(weak[tok]))} |")
    add("")
    add("## Deliberate exclusions")
    add("")
    add("Section numbers are derived from the manuscript's own headings, not "
        "hand-listed — hand-listing is what let `5.5` through the previous "
        "version. Identifiers excluded explicitly:")
    add("")
    add("```")
    add(", ".join(sorted(NOT_MEASUREMENTS)))
    add("```")
    add("")
    add("Regenerate: `python3 scripts/check_provenance.py`")

    OUT.write_text("\n".join(L) + "\n")
    if not a.quiet:
        print(f"wrote {OUT.relative_to(ROOT)}")
        print(f"  ARTIFACT   {counts['ARTIFACT']}")
        print(f"  DOCUMENTED {counts['DOCUMENTED']}")
        print(f"  EXTERNAL   {counts['EXTERNAL']}")
        print(f"  ARTIFACT_NO_ROW {counts['ARTIFACT_NO_ROW']}")
        print(f"  UNSOURCED  {counts['UNSOURCED']}")
        for tok, (t, files, _) in sorted(tiers.items()):
            if t == "UNSOURCED":
                print(f"    UNSOURCED {tok}  ({', '.join(sorted(files))})")
        for tok, (t_, files, _) in sorted(tiers.items()):
            if t_ == "ARTIFACT_NO_ROW":
                print(f"    ARTIFACT_NO_ROW {tok}  ({', '.join(sorted(files))})")
    drift = cross_target_numbers()
    if not a.quiet:
        print(f"  TARGET_DRIFT {len(drift)}")
        for d in drift:
            print(f"    {d}")
    sys.exit(1 if (counts["UNSOURCED"] or counts["ARTIFACT_NO_ROW"] or drift)
             else 0)


NUM = re.compile(r"(?<![\w.])\d[\d,]*(?:\.\d+)?%?")


def cross_target_numbers():
    """Fail if a number in the short paper disagrees with the long one.

    Both targets are generated from the same section files and the short one is
    a strict subset, so every number it prints must also appear in the preprint.
    A number that appears only in the short paper means the two versions have
    started to diverge, which is the failure this project is a paper about.
    Missing builds are skipped rather than guessed at.

    Returns a list of problems; empty means the two agree.
    """
    short = ROOT / "paper" / "msr2027" / "main.tex"
    long_ = ROOT / "paper" / "preprint" / "preprint.tex"
    if not (short.exists() and long_.exists()):
        return []

    def nums(path):
        text = path.read_text(encoding="utf-8")
        # Venue boilerplate is not a claim: CCS concept ids, the ccsdesc
        # significance weights and the conference name and dates are fixed by
        # the template, carry no evidence, and have no counterpart to drift
        # from in the preprint.
        text = re.sub(r"\\begin\{CCSXML\}.*?\\end\{CCSXML\}", "", text,
                      flags=re.S)
        text = re.sub(r"\\ccsdesc\[?\d*\]?\{[^}]*\}", "", text)
        text = re.sub(r"\\acmConference\[[^\]]*\](\{[^}]*\}){3}", "", text)
        # Tabular column widths are computed from the column COUNT, so they
        # necessarily differ once a target drops columns. They are typesetting,
        # not claims, and leaving them in made the check cry wolf.
        text = re.sub(r"p\{\\dimexpr[^}]*\}", "", text)
        text = re.sub(r"\\(?:setlength|kern|hspace|vspace)\s*\{[^}]*\}", "", text)
        return {m.group(0) for m in NUM.finditer(text)}

    drift = sorted(nums(short) - nums(long_))
    return [f"number in the MSR paper that the preprint does not carry: {d}"
            for d in drift]


if __name__ == "__main__":
    main()

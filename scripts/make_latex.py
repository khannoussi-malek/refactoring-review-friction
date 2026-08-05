#!/usr/bin/env python3
"""
make_latex.py — render the manuscript as LaTeX for an arXiv preprint.

The manuscript is authored as Markdown section files and assembled by
`scripts/assemble_manuscript.py`. This renders the same sources to LaTeX so the
Markdown stays the single source of truth and the preprint is regenerated rather
than maintained in parallel. Editing the .tex by hand defeats the point; edit the
section and re-run.

WHAT IT HANDLES, because it only has to handle what the manuscript uses:
headings to three levels, bold, italic, inline code, fenced code, block quotes,
bullet and numbered lists, pipe tables, horizontal rules, links, footnote-free
prose, and the Unicode the sections are written in.

WHAT IT DOES NOT DO, stated so nobody assumes otherwise: it does not resolve
cross-references (the sections write "§4.3" as literal text, and that is what
comes out), it does not number tables automatically beyond the three it is told
about, and it does not do bibliography management -- citations are prose, as they
are in the Markdown. A submission-ready version needs a .bib and \\cite commands,
which is a deliberate manual step listed in deposit/ARXIV_CHECKLIST.md.

Tables are emitted as longtable so they break across pages; Table 3 is eleven
columns and is additionally set in landscape.

Usage:
    python3 scripts/make_latex.py --out paper/preprint/preprint.tex
    cd paper/preprint && pdflatex preprint.tex && pdflatex preprint.tex
"""
import argparse, os, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "paper" / "manuscript"
ORDER = ["abstract.md", "intro.md", "related.md", "method.md", "results.md",
         "taxonomy.md", "threats.md", "discussion.md",
         "acknowledgements.md"]
TABLES = [("paper/table1_eligibility.md", "Table 1", "tab:eligibility", False),
          ("paper/table2_visibility.md", "Table 2", "tab:visibility", False),
          ("paper/table3_ticket_side.md", "Table 3", "tab:ticketside", True)]

# Unicode the sections use, mapped to LaTeX that compiles under pdflatex.
UNI = {
    "—": "---", "–": "--", "×": r"$\times$", "≤": r"$\leq$", "≥": r"$\geq$",
    "→": r"$\rightarrow$", "←": r"$\leftarrow$", "⟶": r"$\longrightarrow$",
    "§": r"\S", "≈": r"$\approx$", "≠": r"$\neq$", "∈": r"$\in$",
    "∃": r"$\exists$", "∅": r"$\emptyset$", "∩": r"$\cap$", "∪": r"$\cup$",
    "·": r"$\cdot$", "±": r"$\pm$", "−": "-", "‑": "-",
    "ρ": r"$\rho$", "κ": r"$\kappa$", "τ": r"$\tau$", "Δ": r"$\Delta$",
    "α": r"$\alpha$", "β": r"$\beta$", "σ": r"$\sigma$", "µ": r"$\mu$",
    "“": "``", "”": "''", "‘": "`", "’": "'", "…": r"\ldots{}",
    "⁻": r"$^{-}$", "⁶": r"$^{6}$", "†": r"$\dagger$", "‡": r"$\ddagger$",
    "ü": r'\"u', "ä": r'\"a', "ö": r'\"o', "é": r"\'e", "è": r"\`e",
    "ˆ": "", "\u00a0": "~", "\u2009": r"\,", "✅": "", "⚠": r"\textbf{!}",
    "❌": "", "⏳": "", "≡": r"$\equiv$",
}

ESC = {"\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$",
       "#": r"\#", "_": r"\_", "{": r"\{", "}": r"\}",
       "~": r"\textasciitilde{}", "^": r"\textasciicircum{}"}


def esc(s):
    out = []
    for ch in s:
        if ch in ESC:
            out.append(ESC[ch])
        elif ch in UNI:
            out.append(UNI[ch])
        elif ord(ch) > 127:
            out.append("?")          # nothing should reach here; see --strict
        else:
            out.append(ch)
    return "".join(out)


def inline(s):
    """Markdown inline markup -> LaTeX. Code spans are escaped, not interpreted."""
    parts = re.split(r"(`[^`]*`)", s)
    done = []
    for i, p in enumerate(parts):
        if i % 2 == 1:
            done.append(r"\texttt{" + esc(p[1:-1]) + "}")
            continue
        # links first, so their URLs are not mangled by the escaper
        p = re.sub(r"\[([^\]]+)\]\(([^)]+)\)",
                   lambda m: "\x00LINK" + m.group(1) + "\x01" + m.group(2) + "\x02", p)
        p = esc(p)
        p = re.sub(r"\*\*(.+?)\*\*", r"\\textbf{\1}", p)
        p = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"\\emph{\1}", p)
        p = re.sub(r"\x00LINK(.*?)\x01(.*?)\x02",
                   lambda m: r"\href{" + m.group(2).replace("%", r"\%")
                             + "}{" + m.group(1) + "}", p)
        done.append(p)
    return "".join(done)


def parse_table(lines):
    rows = []
    for ln in lines:
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if all(set(c) <= set("-: ") for c in cells) and cells:
            continue                       # the alignment row
        rows.append(cells)
    return rows


def emit_table(rows, landscape=False, caption=None, label=None):
    if not rows:
        return []
    ncol = max(len(r) for r in rows)
    rows = [r + [""] * (ncol - len(r)) for r in rows]
    # Left-align everything: the content is mixed prose and numbers, and p-columns
    # keep wide tables from overrunning the page.
    width = f"{0.92 / ncol:.3f}\\textwidth"
    spec = "".join(f">{{\\raggedright\\arraybackslash}}p{{{width}}}" for _ in range(ncol))
    out = []
    if landscape:
        out.append(r"\begin{landscape}")
    out.append(r"\footnotesize")
    out.append(r"\begin{longtable}{" + spec + "}")
    if caption:
        out.append(r"\caption{" + inline(caption) + "}"
                   + (r"\label{" + label + "}" if label else "") + r"\\")
    head = " & ".join(r"\textbf{" + inline(c) + "}" for c in rows[0]) + r" \\"
    out += [r"\hline", head, r"\hline", r"\endfirsthead",
            r"\hline", head, r"\hline", r"\endhead"]
    for r in rows[1:]:
        out.append(" & ".join(inline(c) for c in r) + r" \\")
    out += [r"\hline", r"\end{longtable}", r"\normalsize"]
    if landscape:
        out.append(r"\end{landscape}")
    return out


def convert(md, drop_h1=False):
    lines = md.split("\n")
    out, i = [], 0
    list_stack = []

    def close_lists(to=0):
        while len(list_stack) > to:
            out.append(r"\end{" + list_stack.pop() + "}")

    while i < len(lines):
        ln = lines[i]
        s = ln.strip()

        if s.startswith("<!--"):
            while i < len(lines) and "-->" not in lines[i]:
                i += 1
            i += 1
            continue
        if s.startswith("```"):
            i += 1
            buf = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                buf.append(lines[i])
                i += 1
            i += 1
            close_lists()
            out += [r"\begin{verbatim}"] + buf + [r"\end{verbatim}"]
            continue
        if re.match(r"^\|.*\|\s*$", s):
            buf = []
            while i < len(lines) and re.match(r"^\|.*\|\s*$", lines[i].strip()):
                buf.append(lines[i])
                i += 1
            close_lists()
            out += emit_table(parse_table(buf))
            continue
        if re.match(r"^(-{3,}|\*{3,}|_{3,})$", s):
            close_lists()
            i += 1
            continue
        m = re.match(r"^(#{1,4})\s+(.*)$", s)
        if m:
            close_lists()
            lvl, txt = len(m.group(1)), m.group(2)
            txt = re.sub(r"^\d+(\.\d+)*\.?\s+", "", txt)   # strip manual numbering
            if lvl == 1 and drop_h1:
                i += 1
                continue
            cmd = {1: "section", 2: "section", 3: "subsection", 4: "subsubsection"}[lvl]
            out.append("\\" + cmd + "{" + inline(txt) + "}")
            i += 1
            continue
        if s.startswith(">"):
            buf = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                buf.append(lines[i].strip().lstrip(">").strip())
                i += 1
            close_lists()
            out += [r"\begin{quote}", inline(" ".join(buf)), r"\end{quote}"]
            continue
        m = re.match(r"^(\s*)([*+-]|\d+[.)])\s+(.*)$", ln)
        if m:
            indent, marker, txt = m.group(1), m.group(2), m.group(3)
            kind = "enumerate" if re.match(r"\d", marker) else "itemize"
            depth = 1 + len(indent) // 3
            while len(list_stack) > depth:
                out.append(r"\end{" + list_stack.pop() + "}")
            if len(list_stack) < depth:
                out.append(r"\begin{" + kind + "}")
                list_stack.append(kind)
            elif list_stack and list_stack[-1] != kind:
                out.append(r"\end{" + list_stack.pop() + "}")
                out.append(r"\begin{" + kind + "}")
                list_stack.append(kind)
            out.append(r"\item " + inline(txt))
            i += 1
            continue
        if not s:
            if list_stack and i + 1 < len(lines) and not re.match(
                    r"^(\s*)([*+-]|\d+[.)])\s+", lines[i + 1]):
                close_lists()
            out.append("")
            i += 1
            continue
        # continuation of a list item, or a paragraph
        if list_stack:
            out.append(inline(s))
        else:
            out.append(inline(s))
        i += 1
    close_lists()
    return "\n".join(out)


PREAMBLE = r"""\documentclass[11pt,a4paper]{article}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage[margin=2.4cm]{geometry}
\usepackage{array}
\usepackage{longtable}
\usepackage{pdflscape}
\usepackage[expansion=false]{microtype}
\usepackage[hidelinks]{hyperref}
\usepackage{parskip}
\setlength{\emergencystretch}{3em}
\sloppy

\title{Traceability and estimate coverage as corpus-eligibility constraints:\\
a probe of 38 Apache projects}
\author{Malek Khannoussi\\\small independent researcher\\\small\texttt{khannoussimalek@gmail.com}}
\date{\today}

\begin{document}
\maketitle
"""

FRONTMATTER = r"""
\section*{Tables}

This paper carries three tables and one figure. They are the paper; the prose is
the argument around them.

\begin{itemize}
\item \textbf{Table~\ref{tab:eligibility}} --- corpus eligibility across the 38
probed projects, both traceability channels, with commits per ticket, the
arithmetic ceiling of Section~3.1.4 and the share of it reached.
\item \textbf{Table~\ref{tab:visibility}} --- three-channel visibility of
architectural change across two ecosystems. Every cell is a different quantity
with its own denominator and no statistic is computed across them.
\item \textbf{Table~\ref{tab:ticketside}} --- the ticket realisation rate across
all 38 probed projects, with the note column recording every reason a row should
not be read at face value.
\item \textbf{Figure} \texttt{figures/eligibility\_funnel.png} --- 38 to 12 to one
ecosystem, plus the six hypotheses that did not hold. Not embedded in this
preprint; see the replication package.
\end{itemize}

\vspace{1em}\hrule\vspace{1em}
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="paper/preprint/preprint.tex")
    ap.add_argument("--strict", action="store_true",
                    help="fail on any character with no mapping")
    args = ap.parse_args()

    body = [PREAMBLE, FRONTMATTER]

    abstract_md = (SRC / "abstract.md").read_text()
    abstract_md = re.sub(r"^#\s+Abstract\s*$", "", abstract_md, flags=re.M)
    body += [r"\begin{abstract}", convert(abstract_md, drop_h1=True),
             r"\end{abstract}"]

    for name in ORDER[1:]:
        body.append(convert((SRC / name).read_text()))

    body.append(r"\clearpage")
    body.append(r"\section*{Tables}")
    for path, cap, label, land in TABLES:
        md = (ROOT / path).read_text()
        tbl_lines, caption_lines, in_tbl = [], [], False
        for ln in md.split("\n"):
            if re.match(r"^\|.*\|\s*$", ln.strip()):
                tbl_lines.append(ln)
                in_tbl = True
            elif in_tbl and not ln.strip():
                in_tbl = False
            elif not in_tbl:
                caption_lines.append(ln)
        rows = parse_table(tbl_lines)
        body.append(convert("\n".join(caption_lines)))
        body += emit_table(rows, landscape=land,
                           caption=f"{cap}. See the caption text above.",
                           label=label)

    body.append(r"\end{document}")
    text = "\n\n".join(body)

    if args.strict:
        bad = sorted({c for c in text if ord(c) > 127})
        if bad:
            raise SystemExit(f"unmapped characters: {bad}")

    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text)
    print(f"Wrote {args.out}  ({len(text.split()):,} tokens, "
          f"{len(text.splitlines()):,} lines)")
    left = sorted({c for c in text if ord(c) > 127})
    print("non-ASCII remaining:", left if left else "none")


if __name__ == "__main__":
    main()

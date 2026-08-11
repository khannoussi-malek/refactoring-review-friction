#!/usr/bin/env python3
"""
make_latex.py — render the manuscript as LaTeX for an arXiv preprint.

The manuscript is authored as Markdown section files and assembled by
`scripts/assemble_manuscript.py`. This renders the same sources to LaTeX so the
Markdown stays the single source of truth and the preprint is regenerated rather
than maintained in parallel. Editing the .tex by hand defeats the point; edit the
section and re-run.

WHY IT PARSES BY BLOCK AND NOT BY LINE
--------------------------------------
The previous version applied inline markup line by line. Markdown emphasis wraps
freely across a newline, so `**a\\nb**` never matched its own regex and 165
literal asterisks reached the PDF. Paragraphs are therefore joined into one
logical string *before* any inline substitution runs. Code spans are replaced by
sentinels rather than split on, so `**bold with `code` inside**` also survives.
`--selfcheck` fails the build if a markdown marker gets through.

SECTION NUMBERING
-----------------
The sources number their own headings (`## 3.1 ...`) and the prose cites those
numbers as literal text. Levels map h1/h2/h3/h4 to section/subsection/
subsubsection/paragraph, which reproduces the authored numbering exactly, and
`--selfcheck` verifies that claim rather than assuming it. The old map sent h1
and h2 both to \\section, which flattened the hierarchy and ran the document to
56 numbered sections.

TABLE NUMBERING
---------------
longtable steps the table counter for every environment, captioned or not, so
eight uncaptioned body tables pushed Table 1 to "Table 9". Uncaptioned tables
step it back.

WHAT IT DOES NOT DO, stated so nobody assumes otherwise: it does not resolve
cross-references (the sections write "§4.3" as literal text, and that is what
comes out), and it does not do bibliography management -- citations are prose, as
they are in the Markdown. A submission-ready version needs a .bib and \\cite
commands, which is a deliberate manual step listed in deposit/ARXIV_CHECKLIST.md.

Usage:
    python3 scripts/make_latex.py --out paper/preprint/preprint.tex --selfcheck
    cd paper/preprint && pdflatex preprint.tex && pdflatex preprint.tex
"""
import argparse
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "paper" / "manuscript"
ORDER = ["abstract.md", "intro.md", "related.md", "method.md", "results.md",
         "taxonomy.md", "threats.md", "discussion.md", "acknowledgements.md"]
# The fourth field is how many data tables in the file belong to the caption.
# table1 splits its data across "Eligible (12)" and "Dropped (26)", which are two
# halves of one table and must share one number. Every table beyond that count is
# provenance rather than data -- table2's "Sources" list -- and is set without a
# caption so it does not consume a float number the prose then cannot match.
TABLES = [("paper/table1_eligibility.md", "tab:eligibility",
           "Corpus eligibility across the 38 probed projects, both traceability "
           "channels, with commits per ticket, the arithmetic ceiling of "
           "Section 3.1.4 and the share of it reached. All quantities are the "
           "live measurement: TRR_live, ceiling_live, fill_live (Section 3.1.3).",
           2),
          ("paper/table2_visibility.md", "tab:visibility",
           "Three-channel visibility of architectural change across two "
           "ecosystems. Every cell is a different quantity with its own "
           "denominator and no statistic is computed across them.",
           1),
          ("paper/table3_ticket_side.md", "tab:ticketside",
           "The ticket realisation rate across all 38 probed projects, with the "
           "note column recording every reason a row should not be read at face "
           "value. All quantities are the frozen measurement: TRR_frozen, "
           "ceiling_frozen, fill_frozen (Section 3.1.3).",
           1)]
FIGURE = ("figures/eligibility_funnel.png", "fig:funnel",
          "Corpus attrition: 38 probed projects to 12 eligible to a single "
          "ecosystem, with the six operationalisations that were tested and "
          "closed.")

# Unicode the sections use, mapped to LaTeX that compiles under pdflatex.
UNI = {
    "—": "---", "–": "--", "×": r"$\times$", "≤": r"$\leq$", "≥": r"$\geq$",
    "→": r"$\rightarrow$", "←": r"$\leftarrow$", "⟶": r"$\longrightarrow$",
    "§": r"\S\kern0.13em ", "≈": r"$\approx$", "≠": r"$\neq$", "∈": r"$\in$",
    "∃": r"$\exists$", "∅": r"$\emptyset$", "∩": r"$\cap$", "∪": r"$\cup$",
    "·": r"$\cdot$", "±": r"$\pm$", "−": "-", "‑": "-",
    "ρ": r"$\rho$", "κ": r"$\kappa$", "τ": r"$\tau$", "Δ": r"$\Delta$",
    "α": r"$\alpha$", "β": r"$\beta$", "σ": r"$\sigma$", "µ": r"$\mu$",
    "“": "``", "”": "''", "‘": "`", "’": "'", "…": r"\ldots{}",
    "⁻": r"$^{-}$", "⁶": r"$^{6}$", "†": r"\textdagger{}", "‡": r"\textdaggerdbl{}",
    "ü": r'\"u', "ä": r'\"a', "ö": r'\"o', "é": r"\'e", "è": r"\`e",
    "ˆ": "", "\u00a0": "~", "\u2009": r"\,", "✅": r"\checkmark",
    "⚠": r"\textbf{!}", "❌": "--", "⏳": r"$\ldots$", "≡": r"$\equiv$",
}

ESC = {"\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$",
       "#": r"\#", "_": r"\_", "{": r"\{", "}": r"\}",
       "~": r"\textasciitilde{}", "^": r"\textasciicircum{}"}

# Sentinels for spans that must not be touched by the escaper or the emphasis
# regexes. \x00..\x04 cannot occur in the sources.
CODE_A, CODE_B = "\x00", "\x01"
LINK_A, LINK_B, LINK_C = "\x02", "\x03", "\x04"
MATH_A, MATH_B = "\x05", "\x06"
RAW_A, RAW_B = "\x07", "\x08"

# --------------------------------------------------------------------------
# citations and cross-references
# --------------------------------------------------------------------------

# The sources mark a citation as [@key], which reads as a citation in the
# Markdown and becomes \cite{key} here. Keys must exist in
# paper/preprint/refs.bib; --selfcheck fails the build on one that does not.
CITE = re.compile(r"\[@([A-Za-z0-9_:.-]+)\]")

# Float labels, keyed by the number the prose writes. The prose says "Table 1"
# and has said so since before any of these were floats, so the mapping is from
# the authored number to the label rather than the other way round.
FLOAT_LABELS = {"Table 1": "tab:eligibility", "Table 2": "tab:visibility",
                "Table 3": "tab:ticketside", "Figure 1": "fig:funnel"}

# Section numbers seen while parsing the headings. A reference to a number that
# was never authored is left as literal text and reported rather than pointed at
# a label that does not exist.
SECTION_NUMBERS = set()
# Floats a target does not carry. The prose still needs to make its claim, so a
# reference to one is rendered as a pointer into the replication package rather
# than a \ref with no \label, which prints "??". Populated per target in main().
ABSENT_FLOATS = {}
# What to call a table that moved to the replication package. The wording has to
# read as a noun phrase in mid-sentence, because that is where the prose puts it
# ("Table 3 computes ..." becomes "the 38-project table computes ...").
ARTIFACT_TABLE = {
    "Table 2": "the three-channel table in the artifact",
    "Table 3": "the artifact's 38-project table",
}
# set once in main(); emit_table needs it and threading it through every
# emit() call site would touch a dozen signatures for one boolean
DOCCLASS = ['article']
# Classes whose body is two-column. longtable cannot typeset there, and the
# table appendix drops to one column for these. acmart's sigconf belongs here
# just as much as IEEEtran does; omitting it is what broke the ACM build.
TWO_COLUMN = {"ieee", "acm"}
UNRESOLVED_REFS = []
EXTERNAL_REFS = []
CITED_KEYS = set()


def bib_keys(path):
    """Keys defined in the .bib, so a \\cite to a missing entry fails the build
    rather than printing a silent [?]."""
    if not path.exists():
        return set()
    return set(re.findall(r"@\w+\s*\{\s*([^,\s]+)\s*,",
                          path.read_text(encoding="utf-8")))

# --------------------------------------------------------------------------
# maths
# --------------------------------------------------------------------------

# Symbols inside a formula mean the operator, not the text glyph: within math
# mode LaTeX sets its own spacing around a relation, which is what makes an
# expression read as an expression.
MATH_UNI = {
    "≤": r"\leq ", "≥": r"\geq ", "≈": r"\approx ", "≠": r"\neq ",
    "∈": r"\in ", "∃": r"\exists ", "∅": r"\emptyset ", "∩": r"\cap ",
    "∪": r"\cup ", "·": r"\cdot ", "×": r"\times ", "→": r"\to ",
    "⟶": r"\longrightarrow ", "≡": r"\equiv ", "−": "-", "±": r"\pm ",
    "ρ": r"\rho ", "κ": r"\kappa ", "τ": r"\tau ", "σ": r"\sigma ",
    "α": r"\alpha ", "β": r"\beta ", "µ": r"\mu ", "Δ": r"\Delta ",
    "…": r"\ldots ", " ": " ", " ": r"\,",
}
GREEK_WORD = {"rho": r"\rho", "kappa": r"\kappa", "sigma": r"\sigma",
              "tau": r"\tau", "alpha": r"\alpha", "beta": r"\beta"}
RELATIONS = "=≤≥<>≡∈"


def to_math(s):
    """Formula text -> the body of a math expression.

    Multi-letter names are set upright, because CSR and Tickets are names and
    not products of variables; single letters stay italic, because c, k and p
    are variables.
    """
    s = s.strip().strip("*").strip()
    for k, v in MATH_UNI.items():
        s = s.replace(k, v)
    for word, cmd in GREEK_WORD.items():
        # a lambda, not a template: "\rho" in a replacement string is read as
        # the escape \r and raises "bad escape"
        s = re.sub(rf"(?<![A-Za-z\\]){word}(?![A-Za-z])",
                   lambda m, c=cmd: c + " ", s)
    # cardinality of a set comes first, so its bars are not read as a plain pair
    s = re.sub(r"\|\{(.*?)\}\|",
               lambda m: r"\bigl\lvert\{" + m.group(1) + r"\}\bigr\rvert", s)
    s = re.sub(r"\|([^|]+)\|", lambda m: r"\lvert " + m.group(1) + r"\rvert ", s)
    def upright(m):
        word = m.group(1)
        after = s[m.end():m.end() + 1]
        before = s[m.start() - 1:m.start()] if m.start() else ""
        body = r"\mathrm{" + word + "}"
        # A name applied to an argument -- Tickets(p, T) -- needs no space. A
        # bare predicate does: math mode eats the source space, so "k realised"
        # set as "krealised" until this put the space back explicitly.
        if after != "(" and before == " " and s[m.start() - 2:m.start() - 1].isalnum():
            return r"\;" + body
        return body

    s = re.sub(r"(?<![\\A-Za-z])([A-Za-z]{2,})", upright, s)
    return re.sub(r"\s+", " ", s).strip()


def split_top(s, seps):
    """Split on separators that are not nested inside a bracket or a brace.
    The set-builder in Definition 2 contains two membership signs, and treating
    those as top-level relations is what stopped it being set as a fraction
    while its twin in Definition 1 was."""
    out, buf, depth = [], "", 0
    i = 0
    while i < len(s):
        ch = s[i]
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
        if depth == 0:
            hit = next((sep for sep in seps if s.startswith(sep, i)), None)
            if hit:
                out += [buf, hit]
                buf = ""
                i += len(hit)
                continue
        buf += ch
        i += 1
    return out + [buf]


def display_math(s):
    r"""One formula -> a display equation. Each operand between two top-level
    relations is set as a \frac when it is a single quotient, so a ratio of two
    set cardinalities reads as one."""
    parts = split_top(s.strip().strip("*").strip(), list(RELATIONS))
    out = []
    for i, part in enumerate(parts):
        if i % 2:
            out.append(MATH_UNI.get(part, part).strip())
            continue
        halves = split_top(part, [" / "])
        if len(halves) == 3:
            out.append(r"\frac{" + to_math(halves[0]) + "}{"
                       + to_math(halves[2]) + "}")
        else:
            out.append(to_math(part))
    return r"\[" + " ".join(x for x in out if x) + r"\]"


def is_formula(s):
    """A quoted line that is an expression rather than a sentence. Kept tight:
    it must be short, carry a relation, and be dense in operators."""
    body = s.strip().strip("*").strip()
    if not body or len(body) > 140 or "\n" in body:
        return False
    if not any(r in body for r in RELATIONS):
        return False
    ops = sum(1 for c in body if c in "≤≥≈≠∈∃∅∩∪·×→⟶≡|{}/")
    return ops >= 2 and ops / len(body) > 0.04


# Inline statistics: value-preserving rewrites that put an expression into math
# mode. Every one of them only re-wraps characters; --selfcheck re-reads the
# digits out of the result and fails if any of them moved.
NUM = r"[-+−]?\d+(?:\.\d+)?"
INLINE_MATH = [
    (re.compile(rf"\|rho\|\s*([≤≥<>=])\s*({NUM})"),
     lambda m: f"|rho| {m.group(1)} {m.group(2)}"),
    (re.compile(rf"\b(rho|kappa|p|n|r)\s*([=<>≈≤≥])\s*({NUM})"),
     lambda m: f"{m.group(1)} {m.group(2)} {m.group(3)}"),
    (re.compile(rf"\[\s*({NUM})\s*,\s*({NUM})\s*\]"),
     lambda m: f"[{m.group(1)}, {m.group(2)}]"),
    (re.compile(rf"({NUM})×"), lambda m: f"{m.group(1)}×"),
    (re.compile(r"\|rho\|"), lambda m: "|rho|"),
    (re.compile(r"(?<![\w.])[−+]\d+(?:\.\d+)?(?![\w.])"), lambda m: m.group(0)),
    (re.compile(r"(?<![A-Za-z\\])(rho|kappa)(?![A-Za-z])"), lambda m: m.group(1)),
    # subscripted symbols the definitions use: H_p, K_p, C_p. In prose these
    # were setting as "H\_p" with a visible underscore while the same symbol in
    # the displayed equation set as a subscript. Code spans are already stashed,
    # so a snake_case identifier cannot reach this rule.
    # the named estimators of 3.1.3, which are lowercase and so miss the rule
    # below; without this ceiling_live set as "ceiling\_live" in the same
    # sentence where TRR_live set as a subscript
    (re.compile(r"(?<![A-Za-z0-9_\\])(ceiling|fill)_(live|frozen)(?![A-Za-z0-9_])"),
     lambda m: f"{m.group(1)}_{{{m.group(2)}}}"),
    # Matches exactly the six the sources use -- C_p H_p K_p N_p TRR_frozen
    # TRR_live -- and nothing else; checked against all nine section files.
    (re.compile(r"(?<![A-Za-z0-9_\\])([A-Z]{1,4})_([a-z]{1,8})(?![A-Za-z0-9_])"),
     lambda m: f"{m.group(1)}_{{{m.group(2)}}}"),
]


# --------------------------------------------------------------------------
# inline markup
# --------------------------------------------------------------------------

def esc(s, unmapped=None):
    out = []
    for ch in s:
        if ch in ESC:
            out.append(ESC[ch])
        elif ch in UNI:
            out.append(UNI[ch])
        elif ord(ch) > 127:
            if unmapped is not None:
                unmapped.add(ch)
            out.append("?")
        else:
            out.append(ch)
    return "".join(out)


def smart_quotes(s):
    """Straight " renders as two right-quotes in LaTeX. Pair them by position:
    a quote that opens follows start-of-string, whitespace or an opening
    bracket."""
    out, i = [], 0
    while i < len(s):
        if s[i] == '"':
            prev = out[-1] if out else " "
            out.append("“" if prev in " \t([{-–—/*_`" else "”")
        else:
            out.append(s[i])
        i += 1
    return "".join(out)


def _runs(s):
    """Every maximal run of asterisks, with whether it may open or close an
    emphasis span. Following CommonMark: a run may open if the character after
    it is not whitespace, and may close if the character before it is not."""
    runs, i = [], 0
    while i < len(s):
        if s[i] != "*":
            i += 1
            continue
        j = i
        while j < len(s) and s[j] == "*":
            j += 1
        before = s[i - 1] if i else " "
        after = s[j] if j < len(s) else " "
        runs.append({"start": i, "end": j, "left": j - i,
                     "open": not after.isspace(),
                     "close": not before.isspace()})
        i = j
    return runs


def emphasis(s):
    """Markdown emphasis -> LaTeX, by delimiter matching rather than by regex.

    Regex passes cannot parse the sources' own idiom

        **Bachmann et al. (FSE'10), *The Missing Links*** ---

    where a single run of three asterisks closes an italic and a bold at once;
    a non-greedy `\\*\\*(.+?)\\*\\*` eats `**A, *B**` and strands the last one.
    They also cannot parse `****six** ... **`, a doubled marker in taxonomy.md.
    Matching runs against a stack handles both, so neither the idiom nor the
    typo needs the manuscript edited.
    """
    runs = _runs(s)
    if not runs:
        return s
    opens, pairs, stack = [], [], []
    for r in runs:
        while r["close"] and r["left"] and stack:
            o = stack[-1]
            if not o["left"]:
                stack.pop()
                continue
            use = 2 if (o["left"] >= 2 and r["left"] >= 2) else 1
            pairs.append((o["end"] - o["left"], use, r["start"] + (r["end"]
                          - r["start"] - r["left"]), use))
            o["left"] -= use
            r["left"] -= use
            if not o["left"]:
                stack.pop()
        if r["open"] and r["left"]:
            stack.append(r)
    if not pairs:
        return s

    drop = set()
    pre, post = {}, {}
    for o_at, o_len, c_at, c_len in pairs:
        cmd = r"\textbf{" if o_len == 2 else r"\emph{"
        drop.update(range(o_at, o_at + o_len))
        drop.update(range(c_at, c_at + c_len))
        pre.setdefault(o_at + o_len, []).insert(0, cmd)
        post.setdefault(c_at, []).append("}")

    out = []
    for i, ch in enumerate(s):
        out += post.get(i, [])
        out += pre.get(i, [])
        if i not in drop:
            out.append(ch)
    out += post.get(len(s), [])
    out += pre.get(len(s), [])
    return "".join(out)


def inline(s, unmapped=None):
    """Markdown inline markup -> LaTeX.

    Order matters: code spans and links become sentinels first so neither the
    escaper nor the emphasis regexes can see inside them, then the whole string
    is escaped, then emphasis runs across the *entire* string -- which is why
    the caller must hand over a joined paragraph and not a single line.
    """
    codes, links = [], []

    def stash_code(m):
        codes.append(m.group(1))
        return f"{CODE_A}{len(codes) - 1}{CODE_B}"

    def stash_link(m):
        links.append((m.group(1), m.group(2)))
        return f"{LINK_A}{len(links) - 1}{LINK_B}"

    maths = []

    def stash_math(m):
        src, out = m.group(0), to_math(m.group(0))
        # setting a number in maths must never change the number
        assert digits(src) == digits(out), f"mathify altered {src!r} -> {out!r}"
        maths.append(out)
        return f"{MATH_A}{len(maths) - 1}{MATH_B}"

    raws = []

    def stash_raw(latex):
        raws.append(latex)
        return f"{RAW_A}{len(raws) - 1}{RAW_B}"

    s = re.sub(r"`([^`]*)`", stash_code, s)

    # citations before links, because [@key] would otherwise look like link text
    def do_cite(m):
        CITED_KEYS.add(m.group(1))
        return stash_raw(r"\cite{" + m.group(1) + "}")

    s = CITE.sub(do_cite, s)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", stash_link, s)

    # cross-references. The prose hardcodes "§4.3" and "Table 1"; those become
    # real \ref so they renumber and so a reader can click them.
    def do_section(m):
        num = m.group(2)
        # A section pointer that follows a .md filename belongs to a repository
        # memo, not to this paper. Those files use Arabic numbering, so turning
        # "paper/numbers.md §5" into a \ref would print "§V" and send a reader
        # looking for a section that does not exist. Left as literal text, and
        # left that way permanently -- this is the guard, not a one-off edit.
        before = s[:m.start()]
        prev = re.search(f"{CODE_A}(\\d+){CODE_B}\\s*$", before)
        if prev and codes[int(prev.group(1))].strip().endswith(".md"):
            EXTERNAL_REFS.append(codes[int(prev.group(1))].strip() + " " + m.group(0))
            return m.group(0)
        if num.rstrip(".") not in SECTION_NUMBERS:
            UNRESOLVED_REFS.append(m.group(0))
            return m.group(0)
        lead = r"\S\kern0.13em " if m.group(1) == "§" else "Section~"
        return stash_raw(lead + r"\ref{sec:" + num.rstrip(".") + "}")

    s = re.sub(r"(§|Section~|Section )\s?(\d+(?:\.\d+)*)", do_section, s)

    def do_float(m):
        if m.group(0) in ABSENT_FLOATS:
            return stash_raw(ABSENT_FLOATS[m.group(0)])
        label = FLOAT_LABELS.get(m.group(0))
        if not label:
            UNRESOLVED_REFS.append(m.group(0))
            return m.group(0)
        kind = m.group(0).split()[0]
        return stash_raw(kind + "~" + r"\ref{" + label + "}")

    def do_float_pair(m):
        kind, a, b = m.group(1), m.group(2), m.group(3)
        sing = kind[:-1]                       # Tables -> Table
        ka, kb = f"{sing} {a}", f"{sing} {b}"
        if ka in ABSENT_FLOATS or kb in ABSENT_FLOATS:
            # one of the pair is not in this target: emit each side on its own
            side = lambda k: (ABSENT_FLOATS[k] if k in ABSENT_FLOATS
                              else sing + "~" + r"\ref{" + FLOAT_LABELS[k] + "}")
            return stash_raw(side(ka) + " and " + side(kb))
        la, lb = FLOAT_LABELS.get(ka), FLOAT_LABELS.get(kb)
        if not (la and lb):
            UNRESOLVED_REFS.append(m.group(0))
            return m.group(0)
        return stash_raw(kind + "~" + r"\ref{" + la + r"} and~\ref{" + lb + "}")

    def do_section_pair(m):
        a, b = m.group(2), m.group(3)
        if a not in SECTION_NUMBERS or b not in SECTION_NUMBERS:
            UNRESOLVED_REFS.append(m.group(0))
            return m.group(0)
        lead = r"\S\kern0.13em " if m.group(1) == "§§" else "Sections~"
        return stash_raw(lead + r"\ref{sec:" + a + r"} and~\ref{sec:" + b + "}")

    # plurals first: "Tables 1 and 3" would otherwise be caught by the singular
    # rule as "Table" is not matched but "1 and 3" leaves two bare numbers
    s = re.sub(r"(Tables|Figures) (\d+) and (\d+)", do_float_pair, s)
    s = re.sub(r"(Sections) (\d+(?:\.\d+)*) and (\d+(?:\.\d+)*)", do_section_pair, s)
    s = re.sub(r"(?:Table|Figure) \d+", do_float, s)
    for rx, _ in INLINE_MATH:
        s = rx.sub(stash_math, s)
    s = smart_quotes(s)
    s = esc(s, unmapped)
    s = emphasis(s)
    s = re.sub(f"{MATH_A}(\\d+){MATH_B}",
               lambda m: "$" + maths[int(m.group(1))] + "$", s)

    # Links are restored after escaping, so their label has to be escaped here
    # or a character like the # in "tsantalis/RefactoringMiner#1124" reaches
    # LaTeX raw and aborts the run.
    def unstash_link(m):
        label, url = links[int(m.group(1))]
        for ch in ("%", "#"):
            url = url.replace(ch, "\\" + ch)
        return r"\href{" + url + "}{" + esc(label, unmapped) + "}"

    s = re.sub(f"{LINK_A}(\\d+){LINK_B}", unstash_link, s)
    s = re.sub(f"{CODE_A}(\\d+){CODE_B}",
               lambda m: code_span(codes[int(m.group(1))], unmapped), s)
    s = re.sub(f"{RAW_A}(\\d+){RAW_B}", lambda m: raws[int(m.group(1))], s)
    return s


def code_span(text, unmapped=None):
    """\\texttt has no hyphenation, so a long path like
    paper/manuscript/threats.md overruns the margin. Allow a break after the
    separators a reader already parses the token by."""
    body = esc(text, unmapped)
    return r"\texttt{" + re.sub(r"([/_.\-])", r"\1\\allowbreak{}", body) + "}"


# --------------------------------------------------------------------------
# block parsing
# --------------------------------------------------------------------------

HEADING = re.compile(r"^(#{1,6})\s+(.*)$")
BULLET = re.compile(r"^(\s*)([*+-])\s+(.*)$")
NUMBER = re.compile(r"^(\s*)(\d+[.)])\s+(.*)$")
ROW = re.compile(r"^\|.*\|\s*$")
RULE = re.compile(r"^(-{3,}|\*{3,}|_{3,})$")


def parse(lines):
    """Markdown lines -> a list of blocks. Blocks are the unit inline markup is
    applied to, which is what lets emphasis span a line break."""
    blocks, i, n = [], 0, len(lines)
    while i < n:
        raw, s = lines[i], lines[i].strip()

        if not s:
            i += 1
            continue

        if s.startswith("<!--"):
            while i < n and "-->" not in lines[i]:
                i += 1
            i += 1
            continue

        if s.startswith("```"):
            i += 1
            buf = []
            while i < n and not lines[i].strip().startswith("```"):
                buf.append(lines[i])
                i += 1
            blocks.append(("code", buf))
            i += 1
            continue

        m = HEADING.match(s)
        if m:
            blocks.append(("head", (len(m.group(1)), m.group(2))))
            i += 1
            continue

        if RULE.match(s):
            blocks.append(("rule", None))
            i += 1
            continue

        if ROW.match(s):
            buf = []
            while i < n and ROW.match(lines[i].strip()):
                buf.append(lines[i])
                i += 1
            blocks.append(("table", table_rows(buf)))
            continue

        if s.startswith(">"):
            # A quoted formula whose outermost symbols are cardinality bars
            # -- |{ k in Tickets(p, T) : k realised }| <= CSR(p) . |C_p| --
            # starts and ends with "|", so the pipe-table rule claimed it and
            # shredded the bound into three table cells in BOTH builds. Test
            # for a formula before letting the table rule near it.
            solo = re.sub(r"^\s*>\s?", "", raw).strip()
            if is_formula(solo) and (i + 1 >= n or not lines[i + 1].strip().startswith(">")):
                blocks.append(("quote", [("para", solo)]))
                i += 1
                continue
            buf = []
            while i < n and (lines[i].strip().startswith(">") or
                             (lines[i].strip() and buf and
                              not _starts_block(lines[i]))):
                buf.append(re.sub(r"^\s*>\s?", "", lines[i]))
                i += 1
            blocks.append(("quote", parse(buf)))
            continue

        m = BULLET.match(raw) or NUMBER.match(raw)
        if m:
            i, items, kind = read_list(lines, i)
            blocks.append((kind, items))
            continue

        # paragraph: every following line until a blank or a new block starts
        buf = [s]
        i += 1
        while i < n and lines[i].strip() and not _starts_block(lines[i]):
            buf.append(lines[i].strip())
            i += 1
        blocks.append(("para", " ".join(buf)))
    return blocks


def _starts_block(line):
    s = line.strip()
    return bool(HEADING.match(s) or ROW.match(s) or RULE.match(s)
                or s.startswith(("```", ">"))
                or BULLET.match(line) or NUMBER.match(line))


def read_list(lines, i):
    """Read one list. An item absorbs its wrapped continuation lines, so
    emphasis spanning them is joined before inline() sees it."""
    n = len(lines)
    first = BULLET.match(lines[i]) or NUMBER.match(lines[i])
    kind = "olist" if NUMBER.match(lines[i]) else "ulist"
    base = len(first.group(1))
    items = []
    while i < n:
        line = lines[i]
        m = BULLET.match(line) or NUMBER.match(line)
        if m and len(m.group(1)) <= base:
            if NUMBER.match(line) and kind == "ulist":
                break
            if BULLET.match(line) and kind == "olist":
                break
            buf = [m.group(3).strip()]
            i += 1
            # continuation lines and nested content belong to this item
            sub = []
            while i < n:
                nxt = lines[i]
                if not nxt.strip():
                    # A blank line ends the item only if what follows belongs to
                    # nobody. A deeper list marker continues it -- and so does an
                    # indented continuation paragraph, which is the case that used
                    # to escape: it closed the list, emitted itself at top level,
                    # and the following items opened a SECOND enumerate, so
                    # "Four further things" rendered 1, 2, 1, 2.
                    nx = lines[i + 1] if i + 1 < n else ""
                    m3 = BULLET.match(nx) or NUMBER.match(nx)
                    deeper_list = bool(m3) and len(m3.group(1)) > base
                    indented_para = bool(nx.strip()) and not m3 \
                        and (len(nx) - len(nx.lstrip())) > base
                    if deeper_list or indented_para:
                        sub.append("")
                        i += 1
                        continue
                    break
                m2 = BULLET.match(nxt) or NUMBER.match(nxt)
                if m2 and len(m2.group(1)) <= base:
                    break
                if m2 or _starts_block(nxt):
                    sub.append(nxt)
                    i += 1
                    continue
                (sub if sub else buf).append(nxt.strip())
                i += 1
            items.append((" ".join(buf), parse(sub) if any(x.strip() for x in sub) else []))
            continue
        if not line.strip():
            i += 1
            if i < n and (BULLET.match(lines[i]) or NUMBER.match(lines[i])):
                continue
            break
        break
    return i, items, kind


def table_rows(lines):
    rows = []
    for ln in lines:
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if cells and all(set(c) <= set("-: ") for c in cells):
            continue                       # the alignment row
        rows.append(cells)
    return rows


# --------------------------------------------------------------------------
# emission
# --------------------------------------------------------------------------

LEVEL = {1: "section", 2: "subsection", 3: "subsubsection", 4: "paragraph",
         5: "paragraph", 6: "paragraph"}
NUMBERED = re.compile(r"^(\d+(?:\.\d+)*)\.?\s+(.*)$")


def col_widths(rows, ncol, total=1.0):
    """Allocate column width in proportion to the longest cell, clamped so a
    narrow index column keeps a usable minimum and one essay column cannot eat
    the page. Equal widths put an 80-character note beside a 2-character rank."""
    longest = [max((len(r[c]) if c < len(r) else 0) for r in rows) or 1
               for c in range(ncol)]
    # square-root damping: proportional allocation alone gives the note column
    # nearly everything, which starves the numbers it exists to annotate
    weight = [w ** 0.5 for w in longest]
    scale = total / sum(weight)
    out = []
    for w, raw in zip(weight, longest):
        frac = w * scale
        out.append(min(max(frac, 0.035), 0.42))
    over = sum(out) / total
    return [w / over for w in out]


def breakable(s):
    """A p-column can only wrap at a space. "commits/ticket" has none, so it
    overhangs into the next column instead of wrapping. Offer a break after the
    separators inside any long unbroken token."""
    def fix(m):
        # never inside a control sequence: a break in \kern0.13em splits the
        # dimension and pdflatex stops with "illegal unit of measure". Code
        # spans already get their own breaks from code_span().
        if "\\" in m.group(0):
            return m.group(0)
        return re.sub(r"([/_.\-])", r"\1\\allowbreak{}", m.group(0))
    return re.sub(r"\S{10,}", fix, s)


RAGGED = []


def drop_columns(rows, drop):
    """Remove columns by header text.

    The IEEE build sets the eligibility table in landscape, where thirteen
    columns fit. sigconf is narrower and portrait, and the same thirteen
    columns rendered clipped: words vanished mid-caption and header cells ran
    into data. Shrinking the type would not have fixed it, so the short version
    carries fewer columns instead. Matching is on the header cell so the
    manifest names what a reader sees, not a column index that shifts.
    """
    if not rows or not drop:
        return rows
    def norm(c): return re.sub(r"[*`\s]+", " ", c).strip().lower()
    header = [norm(c) for c in rows[0]]
    keep = [i for i, h in enumerate(header) if h not in {norm(d) for d in drop}]
    missing = {norm(d) for d in drop} - set(header)
    if missing:
        raise SystemExit("targets.json drops a column that does not exist: "
                         + ", ".join(sorted(missing)))
    return [[r[i] for i in keep if i < len(r)] for r in rows]


def emit_table(rows, caption=None, label=None, unmapped=None,
               continued=False, caption_raw=None, no_landscape=False):
    if not rows:
        return []
    ncol = max(len(r) for r in rows)
    for r in rows[1:]:
        if len(r) != len(rows[0]):
            RAGGED.append((caption or "an inline table", len(rows[0]), len(r)))
    rows = [r + [""] * (ncol - len(r)) for r in rows]
    widths = col_widths(rows, ncol)
    # Each p-column also carries 2\tabcolsep of gutter, so a budget expressed
    # as a plain fraction of \linewidth overruns by ncol*2*tabcolsep -- 78pt on
    # the 13-column table. Subtracting it per column makes the row width come
    # out at exactly \linewidth.
    spec = "".join(r">{\raggedright\arraybackslash}p{\dimexpr "
                   f"{w:.4f}" + r"\linewidth-2\tabcolsep\relax}"
                   for w in widths)
    # A per-table landscape block starts and ends its own page, which put the
    # dagger legend -- a plain paragraph following the rows -- on the page AFTER
    # the table it explains, and stranded the "Tables" heading on a page of its
    # own. The appendix therefore opens one landscape per table FILE and passes
    # no_landscape here, so heading, rows and legend stay in one flow.
    landscape = ncol >= 8 and not no_landscape
    size = r"\scriptsize" if ncol >= 8 else r"\footnotesize"

    # In a two-column body longtable simply refuses ("longtable not in 1-column
    # mode"). The body tables are all 3 to 7 rows, so they fit a float; table*
    # spans both columns, which the widest of them needs. The three big tables
    # go to the appendix, which drops to one column so longtable works there.
    # A captioned table narrow enough to set as a float belongs in the body as a
    # table*, not in a one-column appendix behind a \clearpage. Table 1 at seven
    # columns cost a whole page that way, of which it filled a sixth.
    floated = DOCCLASS[0] in TWO_COLUMN and ncol < 8 and (
        (not caption and not caption_raw) or (caption and not continued))

    out = []
    if floated:
        cap = ([r"\caption{" + inline(caption, unmapped) + "}"
                + (r"\label{" + label + "}" if label else "")] if caption else [])
        out += [r"\begin{table*}[htbp]", r"\centering"] + cap + [
                r"\begingroup" + size + r"\setlength{\tabcolsep}{3pt}",
                r"\begin{tabular}{" + spec + "}", r"\toprule",
                " & ".join(r"\textbf{" + breakable(inline(c, unmapped)) + "}"
                           for c in rows[0]) + r" \\", r"\midrule"]
        for r in rows[1:]:
            out.append(" & ".join(breakable(inline(c, unmapped)) for c in r) + r" \\")
        out += [r"\bottomrule", r"\end{tabular}", r"\endgroup",
                r"\end{table*}"]
        return out

    if landscape:
        out.append(r"\begin{landscape}")
    out.append(r"\begingroup" + size + r"\setlength{\tabcolsep}{3pt}")
    out.append(r"\begin{longtable}{" + spec + "}")
    if caption_raw:
        # \caption* prints the text without consuming a number, which is how the
        # second half of a split table keeps its parent's. A numbered \caption
        # here printed the NEXT number and only then was the counter wound back,
        # so Table 1's continuation appeared as "Table 2". caption_raw is emitted
        # verbatim because it carries a \ref the escaper would mangle.
        out.append(r"\caption*{" + caption_raw + r"}\\")
    elif caption:
        out.append(r"\caption{" + inline(caption, unmapped) + "}"
                   + (r"\label{" + label + "}" if label else "") + r"\\")
    head = " & ".join(r"\textbf{" + breakable(inline(c, unmapped)) + "}"
                      for c in rows[0]) + r" \\"
    out += [r"\toprule", head, r"\midrule", r"\endfirsthead"]
    if caption:
        out.append(r"\caption[]{\emph{(continued)}}\\")
    out += [r"\toprule", head, r"\midrule", r"\endhead",
            r"\bottomrule", r"\endlastfoot"]
    for r in rows[1:]:
        out.append(" & ".join(breakable(inline(c, unmapped)) for c in r) + r" \\")
    out.append(r"\end{longtable}")
    if not (caption and not continued):
        # longtable steps the table counter for every environment, captioned or
        # not. Anything that is not a numbered float winds it back.
        out.append(r"\addtocounter{table}{-1}")
    out.append(r"\endgroup")
    if landscape:
        out.append(r"\end{landscape}")
    return out


ONLY_OPEN = re.compile(r"<!--\s*only:\s*([\w,\s-]+?)\s*-->")
ONLY_CLOSE = re.compile(r"<!--\s*/only\s*-->")


def select_spans(lines, target, where=""):
    """Keep only the spans this target is entitled to.

    Section-level exclusion in targets.json cannot express a difference of a
    paragraph, and the two papers genuinely differ below section granularity:
    the short one is single-ecosystem and carries its own abstract. The
    alternative is a second copy of the prose, which is the drift this project
    exists to describe, so the two variants sit adjacent in one file instead:

        <!-- only: preprint -->
        ...text only the long version gets...
        <!-- /only -->

    An unbalanced marker silently swallows the rest of a file, so it raises.
    """
    out, allowed, depth = [], None, 0
    for i, ln in enumerate(lines, 1):
        m = ONLY_OPEN.search(ln)
        if m:
            if depth:
                raise SystemExit(f"{where}:{i}: nested <!-- only: --> is not supported")
            allowed = {x.strip() for x in m.group(1).split(",") if x.strip()}
            depth = 1
            continue
        if ONLY_CLOSE.search(ln):
            if not depth:
                raise SystemExit(f"{where}:{i}: <!-- /only --> with no opening marker")
            allowed, depth = None, 0
            continue
        if depth and target not in allowed:
            continue
        out.append(ln)
    if depth:
        raise SystemExit(f"{where}: unclosed <!-- only: --> marker")
    return out


def read_section(name, target):
    """One place where a source file is read, so span selection cannot be
    forgotten at one of the call sites."""
    path = SRC / name if not isinstance(name, pathlib.Path) else name
    return select_spans(path.read_text(encoding="utf-8").split("\n"),
                        target, where=path.name)


def load_targets():
    """Per-target section manifest. Absent file means every target takes every
    section, so the generator still runs in a checkout that predates it."""
    path = SRC / "targets.json"
    if not path.exists():
        return {}
    return {k: v for k, v in json.loads(path.read_text(encoding="utf-8")).items()
            if not k.startswith("_")}


def target_for(cls, targets):
    for name, spec in targets.items():
        if cls in spec.get("applies_to", []):
            return name, spec
    return None, {"exclude": [], "figure": True, "front_matter": True}


def drop_excluded(blocks, excluded):
    """Remove each excluded section and everything under it.

    A section ends at the next heading of the same or a shallower level, so
    excluding 6.3 also removes a 6.3.1 nested beneath it without that number
    having to be listed. Returns the kept blocks and the numbers actually seen,
    which lets the caller fail on a manifest entry that matches nothing rather
    than silently keeping a section it was told to cut."""
    if not excluded:
        return list(blocks), set()
    kept, hit, cutting_at = [], set(), None
    for kind, payload in blocks:
        if kind == "head":
            lvl, txt = payload
            m = NUMBERED.match(txt)
            number = m.group(1) if m else None
            if cutting_at is not None and lvl <= cutting_at:
                cutting_at = None          # this heading closes the cut
            if cutting_at is None and number in excluded:
                cutting_at, _ = lvl, hit.add(number)
                continue
        if cutting_at is None:
            kept.append((kind, payload))
    return kept, hit


def emit(blocks, starred=False, headings=None, unmapped=None, depth=0):
    out = []
    for kind, payload in blocks:
        if kind == "para":
            out += [inline(payload, unmapped), ""]
        elif kind == "head":
            lvl, txt = payload
            m = NUMBERED.match(txt)
            number, title = (m.group(1), m.group(2)) if m else (None, txt)
            cmd = LEVEL[min(lvl, 6)]
            star = "*" if starred else ""
            body = inline(title, unmapped)
            if headings is not None and not starred:
                headings.append((cmd, number, title))
            out.append("\\" + cmd + star + "{" + body + "}")
            # label keyed by the number the prose already cites, so "§4.3"
            # resolves without the sources having to learn a key scheme
            if number and not starred:
                out.append(r"\label{sec:" + number + "}")
            if starred and cmd in ("section", "subsection"):
                out.append(r"\addcontentsline{toc}{" + cmd + "}{" + body + "}")
            out.append("")
        elif kind == "code":
            out += [r"\begin{quote}\footnotesize\begin{verbatim}"] \
                + payload + [r"\end{verbatim}\end{quote}", ""]
        elif kind == "table":
            out += emit_table(payload, unmapped=unmapped) + [""]
        elif kind == "rule":
            out += [r"\medskip\hrule\medskip", ""]
        elif kind == "quote":
            # a quoted line that is an expression is a display equation the
            # sources had no way to mark up; setting it as indented bold text
            # is what made the method section read as prose about symbols
            if (len(payload) == 1 and payload[0][0] == "para"
                    and is_formula(payload[0][1])):
                out += [display_math(payload[0][1]), ""]
                continue
            out += [r"\begin{quote}"] \
                + emit(payload, starred, headings, unmapped, depth + 1) \
                + [r"\end{quote}", ""]
        elif kind in ("ulist", "olist"):
            env = "itemize" if kind == "ulist" else "enumerate"
            out.append(r"\begin{" + env + "}")
            for text, sub in payload:
                out.append(r"\item " + inline(text, unmapped))
                if sub:
                    out += emit(sub, starred, headings, unmapped, depth + 1)
            out += [r"\end{" + env + "}", ""]
    return out


def convert(md, starred=False, headings=None, unmapped=None):
    return "\n".join(emit(parse(md.split("\n")), starred, headings, unmapped))


def convert_blocks(blocks, starred=False, headings=None, unmapped=None):
    return "\n".join(emit(blocks, starred, headings, unmapped))


# --------------------------------------------------------------------------
# document
# --------------------------------------------------------------------------

TITLE = ("Traceability and estimate coverage as corpus-eligibility "
         "constraints: a probe of 38 Apache projects")
AUTHOR = "Malek Khannoussi"

# The build date is fixed, not \\today. A paper built on pinned shas and a
# SHA-256 manifest that re-dates itself on every compile is contradicting its own
# claim to be reproducible.
BUILD_DATE = "5 August 2026"

# MSR asks that a submission not share a title with anything already public, and
# the preprint and its repository are public under the title below. The
# submission therefore carries its own, which also states the claim the short
# paper leads with. The preprint title is left alone so outreach already sent
# still resolves. PROJECT_STATE.md records the decision.
TITLE = {
    "default": "Traceability and estimate coverage as corpus-eligibility "
               "constraints: a probe of 38 Apache projects",
    "acm": "An arithmetic ceiling on issue--commit linkage, and what it means "
           "for corpus selection",
}

COMMON = r"""
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{array}
\usepackage{booktabs}
\usepackage{longtable}
\usepackage{pdflscape}
\usepackage{graphicx}
%% resolve the figure whether pdflatex runs from paper/preprint (repo layout) or
%% from a flat directory with the image beside the .tex (arXiv submission)
\graphicspath{{../../}{./}}
\usepackage{microtype}

%% Links are coloured rather than hidden. An internal cross-reference a reader
%% cannot see is one they will not click; the tones are dark enough to print as
%% near-black on paper.
\usepackage[colorlinks=true,
            linkcolor={[rgb]{0.10,0.20,0.50}},
            citecolor={[rgb]{0.00,0.35,0.25}},
            urlcolor={[rgb]{0.35,0.10,0.35}},
            pdftitle={Traceability and estimate coverage as corpus-eligibility constraints: a probe of 38 Apache projects},
            pdfauthor={Malek Khannoussi},
            pdfsubject={Empirical software engineering; mining software repositories},
            pdfkeywords={traceability, corpus eligibility, refactoring, issue linkage, mining software repositories},
            pdfcreator={scripts/make\_latex.py}]{hyperref}

\widowpenalty=10000
\clubpenalty=10000
\setlength{\emergencystretch}{2em}
"""

ARTICLE = r"""%% arXiv defaults to latex+dvips unless the source says otherwise
\pdfoutput=1
\documentclass[11pt,a4paper]{article}

%% Latin Modern in place of bare T1 Computer Modern. Without it pdflatex falls
%% back to 600dpi bitmap EC fonts: the page renders rough on screen and the text
%% layer loses ligatures, so "different" extracts as "dierent" and the PDF is
%% not searchable for those words.
\usepackage{lmodern}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage[english]{babel}
\usepackage[margin=2.5cm,bottom=2.8cm]{geometry}
\usepackage[font=small,labelfont=bf,skip=6pt]{caption}
\usepackage{parskip}
""" + COMMON + r"""
\title{\bfseries Traceability and estimate coverage as corpus-eligibility
constraints:\\[2pt] a probe of 38 Apache projects}
\author{Malek Khannoussi\\[2pt]
\normalsize Independent Researcher\\
\normalsize Tunisia\\
\normalsize\texttt{khannoussimalek@gmail.com}}
\date{BUILDDATE}

\begin{document}
\maketitle
\thispagestyle{empty}
"""

IEEE = r"""\pdfoutput=1
\documentclass[conference]{IEEEtran}
\IEEEoverridecommandlockouts

%% IEEEtran asks for Courier (pcr) for \texttt, which a basic TeX Live does not
%% ship; without this the run dies with "Metric (TFM) file not found". Latin
%% Modern Mono is metrically sane and is already used by the article build.
\usepackage{lmodern}
\renewcommand{\ttdefault}{lmtt}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
""" + COMMON + r"""
\title{Traceability and estimate coverage as corpus-eligibility constraints:\\
a probe of 38 Apache projects}

\author{\IEEEauthorblockN{Malek Khannoussi}
\IEEEauthorblockA{Independent Researcher\\
Tunisia\\
khannoussimalek@gmail.com}}

\date{BUILDDATE}

\begin{document}
\maketitle
"""

KEYWORDS = r"""
\begin{IEEEkeywords}
traceability, corpus eligibility, refactoring, issue linkage, mining software
repositories
\end{IEEEkeywords}
"""

# --------------------------------------------------------------------------
# ACM target -- MSR 2027 submission
# --------------------------------------------------------------------------
# acmart already loads amsmath, amssymb, booktabs, graphicx, microtype, caption
# and hyperref. Re-loading them is at best a duplicate and at worst an option
# clash, so this preamble adds only what acmart leaves out. It must also NOT
# reuse COMMON: COMMON's hyperref call hard-codes pdfauthor and pdftitle, which
# would put the author's name in the metadata of a double-anonymous submission.
# `pdfinfo` is the check, and it is part of the verification list.
ACM = r"""\documentclass[sigconf,review,anonymous]{acmart}

%% acmart does not load these three.
\usepackage{array}
\usepackage{longtable}
\usepackage{pdflscape}
\graphicspath{{../../}{./}}

%% No author, title or creator metadata keys are set here. acmart drives
%% hyperref itself, and anything set in this preamble reaches the PDF metadata,
%% where it would survive every source-level anonymisation check.

%% A submission carries no DOI, ISBN or price.
\settopmatter{printacmref=false}
\renewcommand\footnotetextcopyrightpermission[1]{}
\acmConference[MSR 2027]{22nd International Conference on Mining Software
Repositories}{April 26--27, 2027}{Dublin, Ireland}

\widowpenalty=10000
\clubpenalty=10000
\setlength{\emergencystretch}{2em}

\title{TITLETEXT}

%% The anonymous option suppresses this block; it is kept minimal regardless so
%% there is nothing to leak if the option is ever dropped by accident.
\author{Anonymous Author(s)}

\begin{document}
"""

# acmart wants the CCS block and the keywords between the abstract and
# \maketitle, which is why the ACM path emits \maketitle itself rather than
# taking it from the preamble the way IEEE and article do.
ACM_TOPMATTER = r"""
\begin{CCSXML}
<ccs2012>
<concept>
<concept_id>10011007.10011074.10011099</concept_id>
<concept_desc>Software and its engineering~Software verification and
validation</concept_desc>
<concept_significance>500</concept_significance>
</concept>
<concept>
<concept_id>10011007.10011074.10011134</concept_id>
<concept_desc>Software and its engineering~Software evolution</concept_desc>
<concept_significance>300</concept_significance>
</concept>
</ccs2012>
\end{CCSXML}

\ccsdesc[500]{Software and its engineering~Software verification and validation}
\ccsdesc[300]{Software and its engineering~Software evolution}

\keywords{traceability, corpus eligibility, issue linkage, sampling frames,
mining software repositories}

\maketitle
"""


def preamble(cls):
    """The document class is a parameter because the venues in this area are
    split: arXiv takes the single-column article, IEEE conferences take the
    two-column IEEEtran, and ACM venues take acmart."""
    src = {"ieee": IEEE, "acm": ACM}.get(cls, ARTICLE)
    return (src.replace("BUILDDATE", BUILD_DATE)
               .replace("TITLETEXT", TITLE[cls if cls in TITLE else "default"]))


def frontmatter(figure_ok):
    """The reader's map of the paper. It follows the abstract rather than
    preceding it -- the old order put a list of tables between the title and the
    abstract."""
    # if the image is absent the bullet is dropped rather than replaced by a
    # build diagnostic -- "not found at build time" is not a sentence a reader
    # of the paper should ever see
    fig = (r"\item \textbf{Figure~\ref{fig:funnel}} --- 38 to 12 to one "
           r"ecosystem, plus the six hypotheses that did not hold."
           if figure_ok else "")
    return r"""
\bigskip
\noindent\textbf{What to read first.} This paper carries three tables and one
figure. They are the paper; the prose is the argument around them.

\begin{itemize}\setlength{\itemsep}{2pt}
\item \textbf{Table~\ref{tab:eligibility}} --- corpus eligibility across the 38
probed projects, both traceability channels, with commits per ticket, the
arithmetic ceiling of Section~\ref{sec:3.1.4} and the share of it reached.
\item \textbf{Table~\ref{tab:visibility}} --- three-channel visibility of
architectural change across two ecosystems. Every cell is a different quantity
with its own denominator and no statistic is computed across them.
\item \textbf{Table~\ref{tab:ticketside}} --- the ticket realisation rate across
all 38 probed projects, with the note column recording every reason a row should
not be read at face value.
""" + fig + r"""
\end{itemize}

\medskip\hrule
"""


def emit_figure(unmapped):
    path = ROOT / FIGURE[0]
    if not path.exists():
        return []
    cap = (r"\caption{" + inline(FIGURE[2], unmapped) + r"}\label{"
           + FIGURE[1] + "}")
    if DOCCLASS[0] in TWO_COLUMN:
        # figure* spans both columns, which is 18cm against the article build's
        # 16cm. Rotating it as well would fight the two-column output routine
        # for no gain, and did: it left an 828pt overfull box.
        return ["", r"\begin{figure*}[t]", r"\centering",
                r"\includegraphics[width=\textwidth]{" + FIGURE[0] + "}",
                cap, r"\end{figure*}", ""]
    # The image is 2280x750 -- a 3:1 strip whose panel labels are unreadable at
    # 16cm. A landscape page gives ~24cm of measure, half again as wide.
    return ["", r"\begin{landscape}", r"\begin{figure}[p]", r"\centering",
            r"\includegraphics[width=\linewidth]{" + FIGURE[0] + "}",
            cap, r"\end{figure}", r"\end{landscape}", ""]


def bibliography(cls="article"):
    """IEEEtran numeric style for the arXiv and IEEE builds, so [1], [2] means
    the same thing in both.

    acmart ships its own style and does NOT ship IEEEtran.bst. Emitting
    IEEEtran here made bibtex abort with "I couldn't open style file
    IEEEtran.bst", which leaves a zero-byte .bbl -- so every \\cite rendered as
    "[?]" and the reference list was absent from the PDF entirely, while
    pdflatex still produced a plausible-looking document."""
    style = "ACM-Reference-Format" if cls == "acm" else "IEEEtran"
    return ["", r"\bibliographystyle{" + style + "}", r"\bibliography{refs}", ""]


def table_appendix(unmapped, cls="article", keep=None, tgt=None, drop_cols=None,
                   tspec_parts=None, force_appendix=None):
    """Each table file carries its own headings, its data table and a prose
    caption. The headings are starred so the appendix cannot renumber the
    paper's sections, and the first data table in each file takes the caption
    and the label the front matter points at."""
    # Two-column bodies cannot hold these tables. longtable is incompatible
    # with twocolumn, and Table 3 is 38 rows over 11 columns, which no
    # single-page float can take. The appendix therefore drops to one column so
    # longtable works and landscape gives the measure. No row or column is lost,
    # which is the constraint that decides this: the ceiling and fill columns
    # are the paper's mechanism.
    # Both ieee and acm(sigconf) set two columns, and longtable refuses to
    # typeset there ("longtable not in 1-column mode"). Keying this to "ieee"
    # alone sent nine such errors into the ACM build, which still produced a
    # PDF, so the damage was only visible in the log.
    # The one-column appendix exists only because longtable cannot typeset in
    # two columns. If every table this target keeps fits a float, the appendix
    # costs a forced page break and buys nothing.
    # Width must be judged AFTER the manifest drops columns, or a table cut down
    # to seven columns still drags in the one-column appendix it no longer needs.
    def _kept_tables():
        for path, label, _c, n_data in TABLES:
            if keep is not None and label not in keep:
                continue
            seen = 0
            for k, pl in parse(read_section(ROOT / path, tgt)):
                if k != "table":
                    continue
                seen += 1
                lim = (tspec_parts or {}).get(label)
                if lim is not None and seen > lim:
                    break
                yield (drop_columns(pl, (drop_cols or {}).get(label))
                       if seen == 1 else pl)
    # Measured, not assumed: for the MSR target the one-column appendix came out
    # at 12 pages and the same table set as body floats at 13, because a wide
    # float displaces more text than the page break costs. The manifest records
    # the choice so it is not re-litigated from intuition.
    needs_onecol = (force_appendix if force_appendix is not None
                    else any(max(len(r) for r in pl) >= 8 for pl in _kept_tables()))
    out = [r"\clearpage"] if needs_onecol else []
    if cls in TWO_COLUMN and needs_onecol:
        out.append(r"\onecolumn")
    header = [r"\section*{Tables}",
              r"\addcontentsline{toc}{section}{Tables}", ""]
    for path, label, caption, n_data in TABLES:
        # A target that names its tables gets only those; the rest move to the
        # replication package and are cited there, not deleted.
        if keep is not None and label not in keep:
            continue
        blocks = parse(read_section(ROOT / path, tgt))
        # One landscape per FILE, not per table. Opening it around the whole
        # file keeps the heading, both halves of a split table and the legend
        # in a single flow, so the legend cannot orphan onto the next page.
        parts = (tspec_parts or {}).get(label)
        wide = any(k == "table" and max(len(r) for r in p) >= 8
                   for k, p in blocks)
        body = []
        if wide:
            body.append(r"\begin{landscape}")
        if header:
            body += header
            header = []
        seen, dropped_h1, head_start = 0, False, None
        for kind, payload in blocks:
            # the file's own h1 repeats the caption verbatim; one title is enough
            # "Caption" and "Sources" are structural markers in the source
            # file, not headings of the paper. They were printing as body text
            # above each caption block.
            if kind == "head" and payload[1].strip() in ("Caption", "Sources"):
                continue
            if kind == "head" and payload[0] == 1 and not dropped_h1:
                dropped_h1 = True
                continue
            if kind == "table":
                seen += 1
                hs, head_start = head_start, None

                if seen == 1:
                    body += emit_table(
                        drop_columns(payload, (drop_cols or {}).get(label)),
                        caption=caption, label=label,
                        unmapped=unmapped, no_landscape=wide)
                elif parts is not None and seen > parts:
                    # a heading emitted just above introduced only this table
                    if hs is not None:
                        del body[hs:]
                    # This target takes only the first `parts` data tables of
                    # the file. Everything after them, including the headings
                    # that introduce them, belongs to the artifact.
                    break
                elif seen <= n_data:
                    # second half of the same table: same number, no new float
                    body += emit_table(
                        payload, continued=True, unmapped=unmapped,
                        no_landscape=wide,
                        caption_raw=r"\textbf{Table~\ref{" + label
                        + r"}}, \emph{continued.}")
                else:
                    # provenance, not data: no caption and no number at all
                    body += emit_table(payload, unmapped=unmapped,
                                       no_landscape=wide)
            else:
                if kind == "head" and head_start is None:
                    head_start = len(body)
                body += emit([(kind, payload)], starred=True, unmapped=unmapped)
        if wide:
            body.append(r"\end{landscape}")
        out += body
        out.append("")
    if cls in TWO_COLUMN and needs_onecol:
        out.append(r"\twocolumn")
    return out


# --------------------------------------------------------------------------
# self-check
# --------------------------------------------------------------------------

LEAKS = [
    # any surviving asterisk is a leak: LaTeX has no use for a bare one here,
    # and an unpaired marker is exactly what the old line-by-line pass produced
    ("literal emphasis marker", re.compile(r"\*")),
    ("literal markdown link", re.compile(r"\[[^\]]+\]\([^)]+\)")),
    ("unconverted heading", re.compile(r"(?m)^#{1,6}\s")),
    ("unconverted table row", re.compile(r"(?m)^\|")),
    ("stray sentinel", re.compile(r"[\x00-\x04]")),
]

DEPTH = {"section": 1, "subsection": 2, "subsubsection": 3, "paragraph": 4}


def check_numbering(headings):
    """The prose cites section numbers as literal text, so LaTeX's automatic
    numbering has to reproduce the numbers the sources authored. Simulate the
    counters and report any heading where it does not."""
    counters, bad = [0, 0, 0, 0], []
    for cmd, number, title in headings:
        d = DEPTH[cmd]
        if d > 3:
            continue
        counters[d - 1] += 1
        for k in range(d, 4):
            counters[k] = 0
        got = ".".join(str(c) for c in counters[:d])
        if number and got != number:
            bad.append((number, got, title))
    return bad


STARRED = re.compile(r"\\(?:sub){0,2}section\*|\\paragraph\*|\\caption\*"
                     r"|\\(?:begin|end)\{(?:table|figure)\*\}")


def digits(s):
    """Every digit run in order. mathify only re-wraps characters, so this
    sequence must be identical before and after -- a value that moved is a
    value the typesetter changed, which is the one thing it may never do."""
    return re.findall(r"\d+(?:\.\d+)?", s)


def selfcheck(text, headings, unmapped=None, ragged=None, renumbers=False):
    problems = []
    # Every cross-reference is a \ref keyed on the authored number, so a target
    # that cuts sections renumbers correctly by construction. What it must not
    # do is point at something that is no longer there.
    #
    # This check was written for sec: only, and passed a build carrying twenty
    # broken tab: references that printed as "??". A check narrower than its
    # own success message is worse than no check, so it now covers every
    # reference command and every prefix, and demo() breaks each one.
    labels = set(re.findall(r"\\label\{([^}]+)\}", text))
    used = set(re.findall(r"\\(?:ref|eqref|autoref|Cref|cref)\{([^}]+)\}", text))
    dangling = sorted(used - labels)
    if dangling:
        problems.append("reference with no matching label, would print '??': "
                        + ", ".join(dangling))
    # a character with no mapping is silently printed as "?", so the build has
    # to fail on it rather than only mention it
    if unmapped:
        problems.append("characters with no LaTeX mapping, printed as '?': "
                        + " ".join(sorted(unmapped)))
    for where, head, row in ragged or []:
        problems.append(f"ragged table row in {where}: header has {head} cells, "
                        f"row has {row} -- cells would be silently padded")
    # a starred sectioning command is the one legitimate asterisk in the output
    scan = STARRED.sub("", text)
    for name, rx in LEAKS:
        hits = rx.findall(scan)
        if hits:
            problems.append(f"{name}: {len(hits)} occurrence(s), first {hits[0]!r}")
    # Drift between the authored number and the printed one is a defect only
    # when every section is present; when the manifest cuts sections the
    # renumbering is the point, and the dangling-\ref check above is what
    # guards correctness instead.
    if not renumbers:
        for authored, got, title in check_numbering(headings):
            problems.append(f"section number drift: source says {authored}, "
                            f"LaTeX will print {got} -- {title!r}")
    for env in ("longtable", "itemize", "enumerate", "quote", "verbatim",
                "figure", "landscape"):
        o = len(re.findall(r"\\begin\{" + env + r"\}", text))
        c = len(re.findall(r"\\end\{" + env + r"\}", text))
        if o != c:
            problems.append(f"unbalanced {env}: {o} begin, {c} end")
    return problems


def demo():
    """Smallest check that fails if emphasis matching breaks. The third case is
    the sources' bold-ending-in-italic idiom and the fourth is the doubled
    marker in taxonomy.md; both used to strand an asterisk in the PDF."""
    cases = [
        ("**a**", r"\textbf{a}"),
        ("*a*", r"\emph{a}"),
        ("**A, *B*** rest", r"\textbf{A, \emph{B}} rest"),
        ("****six** of the keys**", r"\textbf{\textbf{six} of the keys}"),
        ("plain text", "plain text"),
        ("2 * 3 * 4", "2 * 3 * 4"),           # spaced asterisks are not markup
    ]
    for src, want in cases:
        got = emphasis(src)
        assert got == want, f"emphasis({src!r}) -> {got!r}, want {want!r}"

    # a paragraph is joined before inline() runs, so emphasis spans the newline
    joined = convert("**bold\nacross a line** and `co-de`")
    assert "**" not in joined, joined
    assert r"\textbf{bold across a line}" in joined, joined

    # h2 must not become a section, or the paper renumbers to 56
    heads = []
    convert("# 1. Intro\n\n# 2. Related\n\n# 3. Method\n\n## 3.1 Rates\n\n"
            "### 3.1.1 Tickets\n\n## 3.2 Corpus\n", headings=heads)
    assert [h[0] for h in heads[2:]] == ["section", "subsection",
                                         "subsubsection", "subsection"], heads
    assert not check_numbering(heads), check_numbering(heads)

    # the old h1/h2 -> section map is what ran the document to 56 sections
    flat = [("section", n, t) for _, n, t in heads]
    assert check_numbering(flat), "flattening h2 to section must be detected"

    # an indented continuation paragraph must stay INSIDE its item. It used to
    # close the list, so a four-item list with a continuation after item 2
    # rendered as two lists numbered 1, 2, 1, 2.
    lst = convert("1. one\n2. two\n\n   still two, indented\n3. three\n4. four\n")
    assert lst.count(r"\begin{enumerate}") == 1, lst
    assert lst.count(r"\item") == 4, lst
    assert "still two, indented" in lst, lst
    assert lst.index("still two, indented") < lst.index(r"\item three"), lst

    # The ACM path: acmart, all three options, and no author identity anywhere
    # in the preamble. pdfauthor in particular would survive into the metadata
    # of a double-anonymous submission.
    acm = preamble("acm")
    assert r"\documentclass[sigconf,review,anonymous]{acmart}" in acm, acm[:200]
    for leak in ("Khannoussi", "Tunisia", "khannoussimalek", "pdfauthor"):
        assert leak not in acm, f"ACM preamble leaks {leak!r}"
    assert r"\begin{CCSXML}" in ACM_TOPMATTER and r"\keywords{" in ACM_TOPMATTER
    assert TITLE["acm"] != TITLE["default"], "submission must not reuse the preprint title"

    # The dangling-reference check must catch EVERY prefix and EVERY reference
    # command. It previously covered sec: alone and reported success over
    # twenty broken tab: references. Break each one and require a complaint.
    ok = r"\label{sec:1}\label{tab:x}\label{fig:y}\label{eq:z}" \
         r"\ref{sec:1}\ref{tab:x}\ref{fig:y}\eqref{eq:z}"
    assert not selfcheck(ok, [], renumbers=True), selfcheck(ok, [], renumbers=True)
    for broken, why in [(r"\ref{tab:gone}", "tab"), (r"\ref{fig:gone}", "fig"),
                        (r"\eqref{eq:gone}", "eq"), (r"\ref{sec:gone}", "sec"),
                        (r"\autoref{tab:gone}", "autoref")]:
        found = selfcheck(ok + broken, [], renumbers=True)
        assert any("no matching label" in p for p in found), \
            f"dangling {why} reference not detected: {found}"

    # Per-target spans: each target sees its own text and nobody sees both.
    src = ["shared", "<!-- only: preprint -->", "long", "<!-- /only -->",
           "<!-- only: msr2027 -->", "short", "<!-- /only -->", "tail"]
    assert select_spans(src, "preprint") == ["shared", "long", "tail"]
    assert select_spans(src, "msr2027") == ["shared", "short", "tail"]
    for bad in (["<!-- only: x -->", "a"], ["<!-- /only -->"]):
        try:
            select_spans(bad, "x"); raise AssertionError("unbalanced marker accepted")
        except SystemExit:
            pass

    # Excluding a section takes its subsections with it, and stops at the next
    # heading of the same level.
    doc = ("# 6. Threats\n\n## 6.2 Keep me\n\nkeep A\n\n## 6.3 Cut me\n\n"
           "cut B\n\n### 6.3.1 Cut me too\n\ncut C\n\n## 6.4 Keep me also\n\nkeep D\n")
    kept, hit = drop_excluded(parse(doc.split("\n")), {"6.3"})
    flat = convert_blocks(kept)
    assert hit == {"6.3"}, hit
    assert "keep A" in flat and "keep D" in flat, flat
    for gone in ("cut B", "cut C", "6.3.1"):
        assert gone not in flat, f"{gone!r} survived the cut"
    print("demo: ok")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="paper/preprint/preprint.tex")
    ap.add_argument("--selfcheck", action="store_true",
                    help="fail the build on leaked markdown or number drift")
    ap.add_argument("--test", action="store_true", help="run demo() and exit")
    ap.add_argument("--class", "--template", dest="cls", default="article",
                    choices=["article", "ieee", "acm"],
                    help="article = single-column arXiv preprint; "
                         "ieee = two-column IEEEtran conference layout; "
                         "acm = acmart sigconf, review + anonymous (MSR)")
    args = ap.parse_args()

    if args.test:
        demo()
        return

    unmapped, headings = set(), []
    figure_ok = (ROOT / FIGURE[0]).exists()

    DOCCLASS[0] = args.cls
    tname, tspec = target_for(args.cls, load_targets())

    # A table this target does not print is still a real artifact, and the
    # prose still needs to point somewhere. Name the artifact rather than
    # emitting a reference with no label.
    ABSENT_FLOATS.clear()
    keep_tabs = tspec.get("tables")
    if keep_tabs is not None:
        for prose, label in FLOAT_LABELS.items():
            if label.startswith("tab:") and label not in keep_tabs:
                ABSENT_FLOATS[prose] = ARTIFACT_TABLE.get(prose, "the artifact")

    # Collect the section numbers this target actually KEEPS, before converting
    # anything, so a reference in section 2 to a section defined in section 7
    # still resolves. Sections the manifest cuts are deliberately left out: a
    # reference into a cut section must be reported as unresolved rather than
    # emitted as a \ref with no \label, which prints "??" in the PDF.
    SECTION_NUMBERS.clear()
    UNRESOLVED_REFS.clear()
    CITED_KEYS.clear()
    for name in ORDER[1:]:
        blocks, _ = drop_excluded(
            parse(read_section(name, tname)),
            set(tspec.get("exclude", [])))
        for kind, payload in blocks:
            if kind == "head":
                n = NUMBERED.match(payload[1])
                if n:
                    SECTION_NUMBERS.add(n.group(1))
    body = [preamble(args.cls)]

    abstract_md = re.sub(r"^#\s+Abstract\s*$", "",
                         "\n".join(read_section("abstract.md", tname)), flags=re.M)
    body += [r"\begin{abstract}", convert(abstract_md, unmapped=unmapped),
             r"\end{abstract}"]
    if args.cls == "ieee":
        body.append(KEYWORDS)
    if args.cls == "acm":
        # acmart wants the CCS block and the keywords between the abstract and
        # \maketitle. The reader's map is dropped for this target: it costs most
        # of a column and ten pages is a desk-reject criterion, not a guideline.
        body.append(ACM_TOPMATTER)
    else:
        # No \clearpage after the reader's map: the map overruns page 1 by a few
        # lines, and forcing a break there left those lines alone on a
        # 324-character page. Letting Section 1 follow on the same page costs
        # nothing and the rule under the map still separates them.
        body += [frontmatter(figure_ok)]

    excluded = set(tspec.get("exclude", []))
    seen_excluded = set()
    for i, name in enumerate(ORDER[1:]):
        blocks = parse(read_section(name, tname))
        blocks, hit = drop_excluded(blocks, excluded)
        seen_excluded |= hit
        body.append("\n".join(emit(blocks, headings=headings, unmapped=unmapped)))
        if name == "results.md" and tspec.get("figure", True):
            body += emit_figure(unmapped)

    # A manifest entry that matches no heading is a silent cut that never
    # happened. Fail loudly rather than ship the section it was meant to remove.
    missing = excluded - seen_excluded
    if missing:
        sys.exit(f"targets.json: no section matches {sorted(missing)} "
                 f"(target {tname!r}); the text was NOT cut")

    body += table_appendix(unmapped, args.cls, keep=tspec.get("tables"), tgt=tname,
                           drop_cols=tspec.get("drop_columns"),
                           tspec_parts=tspec.get("table_parts"),
                           force_appendix=tspec.get("table_appendix"))
    body += bibliography(args.cls)
    body.append(r"\end{document}")
    text = "\n\n".join(body)

    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")

    print(f"Wrote {args.out}  [{args.cls}]  ({len(text.splitlines()):,} lines, "
          f"{len(headings)} numbered headings, {len(CITED_KEYS)} cited works)")
    if EXTERNAL_REFS:
        from collections import Counter
        print("external memo pointers kept as literal text:",
              dict(Counter(EXTERNAL_REFS)))
    if UNRESOLVED_REFS:
        from collections import Counter
        print("REFERENCES LEFT AS LITERAL TEXT (no such label):",
              dict(Counter(UNRESOLVED_REFS)))
    if unmapped:
        print("UNMAPPED CHARACTERS (rendered as '?'):", sorted(unmapped))
    if not figure_ok:
        print(f"NOTE: {FIGURE[0]} not found; figure omitted")

    problems = selfcheck(text, headings, unmapped, RAGGED,
                         renumbers=bool(tspec.get("exclude")))
    missing = CITED_KEYS - bib_keys(ROOT / 'paper' / 'preprint' / 'refs.bib')
    if missing:
        problems.append('cited but not in refs.bib: ' + ', '.join(sorted(missing)))
    if problems:
        print("\nSELF-CHECK FAILURES:")
        for p in problems:
            print("  -", p)
        if args.selfcheck:
            sys.exit(1)
    else:
        print("Self-check: no leaked markdown, no section-number drift, "
              "environments balanced.")


if __name__ == "__main__":
    main()

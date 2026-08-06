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
# set once in main(); emit_table needs it and threading it through every
# emit() call site would touch a dozen signatures for one boolean
DOCCLASS = ['article']
UNRESOLVED_REFS = []
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
    s = re.sub(r"(?<![\\A-Za-z])([A-Za-z]{2,})",
               lambda m: r"\mathrm{" + m.group(1) + "}", s)
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
        if num.rstrip(".") not in SECTION_NUMBERS:
            UNRESOLVED_REFS.append(m.group(0))
            return m.group(0)
        lead = r"\S\kern0.13em " if m.group(1) == "§" else "Section~"
        return stash_raw(lead + r"\ref{sec:" + num.rstrip(".") + "}")

    s = re.sub(r"(§|Section~|Section )\s?(\d+(?:\.\d+)*)", do_section, s)

    def do_float(m):
        label = FLOAT_LABELS.get(m.group(0))
        if not label:
            UNRESOLVED_REFS.append(m.group(0))
            return m.group(0)
        kind = m.group(0).split()[0]
        return stash_raw(kind + "~" + r"\ref{" + label + "}")

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
                    if i + 1 < n and (BULLET.match(lines[i + 1])
                                      or NUMBER.match(lines[i + 1])) \
                            and len((BULLET.match(lines[i + 1])
                                     or NUMBER.match(lines[i + 1])).group(1)) > base:
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


def emit_table(rows, caption=None, label=None, unmapped=None,
               continued=False, caption_raw=None):
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
    landscape = ncol >= 8
    size = r"\scriptsize" if ncol >= 8 else r"\footnotesize"

    # In a two-column body longtable simply refuses ("longtable not in 1-column
    # mode"). The body tables are all 3 to 7 rows, so they fit a float; table*
    # spans both columns, which the widest of them needs. The three big tables
    # go to the appendix, which drops to one column so longtable works there.
    floated = DOCCLASS[0] == "ieee" and not caption and not caption_raw

    out = []
    if floated:
        out += [r"\begin{table*}[htbp]", r"\centering",
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


def preamble(cls):
    """The document class is a parameter because the venues in this area are
    split: arXiv takes the single-column article, IEEE conferences take the
    two-column IEEEtran, and ACM venues take acmart, which slots in here the
    same way."""
    src = IEEE if cls == "ieee" else ARTICLE
    return src.replace("BUILDDATE", BUILD_DATE)


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
arithmetic ceiling of Section~3.1.4 and the share of it reached.
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
    if DOCCLASS[0] == "ieee":
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


def bibliography():
    """IEEEtran numeric style in both builds, so [1], [2] means the same thing
    whichever class is used."""
    return ["", r"\bibliographystyle{IEEEtran}", r"\bibliography{refs}", ""]


def table_appendix(unmapped, cls="article"):
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
    out = [r"\clearpage"]
    if cls == "ieee":
        out.append(r"\onecolumn")
    out += [r"\section*{Tables}",
            r"\addcontentsline{toc}{section}{Tables}", ""]
    for path, label, caption, n_data in TABLES:
        blocks = parse((ROOT / path).read_text(encoding="utf-8").split("\n"))
        seen, dropped_h1 = 0, False
        for kind, payload in blocks:
            # the file's own h1 repeats the caption verbatim; one title is enough
            if kind == "head" and payload[0] == 1 and not dropped_h1:
                dropped_h1 = True
                continue
            if kind == "table":
                seen += 1
                if seen == 1:
                    out += emit_table(payload, caption=caption, label=label,
                                      unmapped=unmapped)
                elif seen <= n_data:
                    # second half of the same table: same number, no new float
                    out += emit_table(
                        payload, continued=True, unmapped=unmapped,
                        caption_raw=r"\textbf{Table~\ref{" + label
                        + r"}}, \emph{continued.}")
                else:
                    # provenance, not data: no caption and no number at all
                    out += emit_table(payload, unmapped=unmapped)
            else:
                out += emit([(kind, payload)], starred=True, unmapped=unmapped)
        out.append("")
    if cls == "ieee":
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


def selfcheck(text, headings, unmapped=None, ragged=None):
    problems = []
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
    print("demo: ok")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="paper/preprint/preprint.tex")
    ap.add_argument("--selfcheck", action="store_true",
                    help="fail the build on leaked markdown or number drift")
    ap.add_argument("--test", action="store_true", help="run demo() and exit")
    ap.add_argument("--class", dest="cls", default="article",
                    choices=["article", "ieee"],
                    help="article = single-column arXiv preprint; "
                         "ieee = two-column IEEEtran conference layout")
    args = ap.parse_args()

    if args.test:
        demo()
        return

    unmapped, headings = set(), []
    figure_ok = (ROOT / FIGURE[0]).exists()

    # Collect every authored section number BEFORE converting anything, so a
    # reference in section 2 to a section defined in section 7 still resolves.
    SECTION_NUMBERS.clear()
    UNRESOLVED_REFS.clear()
    CITED_KEYS.clear()
    for name in ORDER[1:]:
        for line in (SRC / name).read_text(encoding="utf-8").split("\n"):
            m = HEADING.match(line.strip())
            if m:
                n = NUMBERED.match(m.group(2))
                if n:
                    SECTION_NUMBERS.add(n.group(1))

    DOCCLASS[0] = args.cls
    body = [preamble(args.cls)]

    abstract_md = re.sub(r"^#\s+Abstract\s*$", "",
                         (SRC / "abstract.md").read_text(encoding="utf-8"), flags=re.M)
    body += [r"\begin{abstract}", convert(abstract_md, unmapped=unmapped),
             r"\end{abstract}"]
    if args.cls == "ieee":
        body.append(KEYWORDS)
    body += [frontmatter(figure_ok), r"\clearpage"]

    for i, name in enumerate(ORDER[1:]):
        body.append(convert((SRC / name).read_text(encoding="utf-8"), headings=headings,
                            unmapped=unmapped))
        if name == "results.md":
            body += emit_figure(unmapped)

    body += table_appendix(unmapped, args.cls)
    body += bibliography()
    body.append(r"\end{document}")
    text = "\n\n".join(body)

    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")

    print(f"Wrote {args.out}  [{args.cls}]  ({len(text.splitlines()):,} lines, "
          f"{len(headings)} numbered headings, {len(CITED_KEYS)} cited works)")
    if UNRESOLVED_REFS:
        from collections import Counter
        print("REFERENCES LEFT AS LITERAL TEXT (no such label):",
              dict(Counter(UNRESOLVED_REFS)))
    if unmapped:
        print("UNMAPPED CHARACTERS (rendered as '?'):", sorted(unmapped))
    if not figure_ok:
        print(f"NOTE: {FIGURE[0]} not found; figure omitted")

    problems = selfcheck(text, headings, unmapped, RAGGED)
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

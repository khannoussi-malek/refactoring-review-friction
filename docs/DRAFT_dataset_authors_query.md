# DRAFT — query to the Public Jira Dataset authors

**Status: DRAFT. NOT SENT.** Do not send without the author's review.

Written 2026-08-05. Subject matter: `README.md` §9(a), `paper/numbers.md` §5
("Validation note — the project count, and why 1,822 is not usable") and §10e.

## Recipients

**Walid Maalej is no longer at Hamburg.** He moved to the Hasso Plattner
Institute; the address on the 2022 paper is stale. Verified from HPI's own site
(https://hpi.de/en/research/research-groups/software-engineering-and-ai/, page
last changed 28/05/2026): **Prof. Dr. Walid Maalej, Head of Software Engineering
and AI**, W3 Professor and Chair at the joint Digital Engineering Faculty of HPI
and the University of Potsdam, in post since 1 February. The only address HPI
publishes for him is **`office-maalej@hpi.de`**, which is the group office mailbox
— the same address listed for the office assistant, Anne Klonower
(+49 331-5509-4900). There is no personal address on the page.

Montgomery's and Lüders's addresses are from the title page of arXiv:2201.08368,
*An Alternative Issue Tracking Dataset of Public Jira Repositories*, MSR 2022
(doi:10.1145/3524842.3528486) — read from the paper itself, not from a search
summary.

| role | name | address | verified |
|---|---|---|---|
| **To** | Lloyd Montgomery | `lloyd.montgomery@uni-hamburg.de` | paper title page, 2022 |
| **Cc** | Clara Marie Lüders | `clara.marie.lueders@uni-hamburg.de` | paper title page, 2022 |
| **Cc** | Walid Maalej | **`office-maalej@hpi.de`** | **HPI site, 2026** |

**To the first author, the others copied.** A question about how the dataset was
built goes to the person who built it; co-authors belong on the copy line, not
addressed equally.

**Two checks before sending, and only one of them is closed.**

1. **Maalej: closed.** The HPI address is current and institutionally published.
   Note it is an *office* mailbox, so a technical query will reach him via an
   assistant. That is the route HPI offers.
2. **Montgomery and Lüders: open.** Their addresses are four years old and I
   could **not** confirm either from a current institutional page — the Hamburg
   group page I fetched no longer lists any of the three, which is consistent with
   Maalej's chair having moved. Google Scholar still shows Montgomery with a
   verified `uni-hamburg.de` address, but a Scholar profile is not an
   institutional source and I am not treating it as one. **Check both before
   sending**; a bounced primary recipient wastes the request.

Also worth considering: whether a comment on the Zenodo record would be the better
channel, since the answer is useful to other users of the dataset.

**To:** lloyd.montgomery@uni-hamburg.de

**Cc:** clara.marie.lueders@uni-hamburg.de; office-maalej@hpi.de

**Subject:** The Public Jira Dataset — a project count I could not reproduce

---

Dear Dr Montgomery,

I have been using the Public Jira Dataset (Zenodo 15719919) as a base-rate source
and cannot reproduce the published project count. I expect I am missing a
processing step rather than that anything is wrong, so I would rather ask than
guess. I have copied your co-authors.

Streaming the mongodump archive, I parse 2,686,282 issues against the 2.7 million
published. On that pass, counting distinct project **keys** in each issue's final
state gives **1,276** projects. Implementing the count as your notebook defines
it — the union of project **names** in the final state and in the changelog —
gives **2,506**. The published figure is **1,822**.

The one measurement I have that bears on the gap: across those issues, 326
project ids carry more than one distinct name and none carries more than one key.
Removing the surplus names brings the name-based union to roughly 2,180, so
renaming appears to explain part of the difference and not all of it.

**Is there a normalisation or deduplication step between these two figures that I
have not reproduced?** That is my only question. If the published count comes
from a different pass or a filter on the project set, I would cite whichever
definition you consider canonical.

I am happy to send the parsing script and the per-project counts if that would be
useful.

Thank you for depositing the dataset — it is the only source I found that lets a
single-project observation be checked against a base rate across sixteen
organisations, and streaming the archive rather than restoring it made it usable
on a laptop.

With best wishes,

Malek Khannoussi
khannoussimalek@gmail.com
https://github.com/khannoussi-malek/refactoring-review-friction

---

## Notes for the author — not part of the email

**Word count: 273.** Under the 300 asked for. Verified by counting the body between the salutation and the signature.

**A judgment call you should check.** The brief asked the email to carry two
findings: the project count, and the spring-batch result (0% every year since
2020; the published 4,046 does not reproduce). **I included only the first.**

The reason: **4,046 is our figure, not theirs.** It comes from
`paper/eligibility_failure_modes.md` and counts `BATCH-` keys in spring-batch's
*git commit messages*, which is a measurement this study made against a clone —
nothing in the Public Jira Dataset produces it. Writing to the dataset's authors
that we could not reproduce our own number would confuse the request, and the
brief also asked for "one question, plainly asked".

If you want the spring-batch material to reach them, the honest framing is a
separate observation rather than a failure to reproduce, along these lines — and
it is genuinely useful to them, because BATCH is a project in the Spring Jira
they distribute:

> Separately, and only as an observation about a project in the Spring Jira:
> spring-batch's commits cite `BATCH-` keys in 45.6% of 7,035 commits overall,
> but in none of the most recent 1,000 and at 0% in every year from 2020. Anyone
> using the dataset for issue–commit linkage on that project would get very
> different answers depending on where their commit window stops.

Adding it takes the email to roughly 350 words.

**Every number in the email is sourced.** 2,686,282 / 1,276 / 2,506 / 1,822 and
the 326-ids result are `scripts/jira_estimates.py` (`eee902f`) with the
id↔name and id↔key measurements at `0f116aa` and `5179907`, recorded at
`paper/numbers.md` §5 and §10d. The "roughly 2,180" is stated as an approximation
in the repository (*consistent with rename inflation, unverified*) and is phrased
that way here. **Do not tighten it before sending.**

**If a reply establishes the canonical definition**, the correction is additive:
add a dated note to `paper/numbers.md` §5 rather than editing the three-figure
table, and update `README.md` §9(a) to record that the question was answered and
by whom.

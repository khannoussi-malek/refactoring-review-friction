# Which Bachmann figure §2.4 is using

**Report only.** This file does not decide whether the ticket realisation rate is
or is not the quantity Bachmann et al. measured. That question sits behind the
gate at `paper/REVISION_LOG.md`, and `paper/BACHMANN_DETERMINATION.md` does not
exist. Nothing here rewrites the distinctness argument or touches a
`[DETERMINATION PENDING]` marker.

Written 2026-08-05. Source: Bachmann, Bird, Rahman, Devanbu & Bernstein, *The
Missing Links: Bugs and Bug-fix Commits*, FSE'10, worked from the full text.

Quotations are reproduced exactly as the source sets them, ligatures and curly
quotes included.

---

## The two figures, both verified

### (a) The commit-side figure, which is what §2.4 quotes

Found verbatim, page 6, §6.1 "Bugs Incognito":

> "This means, that only 47.6% of bug ﬁx related commits ( 32+7 82 ) are
> documented in the bug tracking database."

The paper prints its own arithmetic in the sentence. The denominator is **82 bug
fix related commits**, established two sentences earlier on the same page:

> "As shown in Table 2, we have 82 bug ﬁx related com- mits in our evaluation
> dataset. 32 of them (bug report) are directly related to the bug tracking
> database. 7 other commits contain a bug-ﬁx, but are not the initial bug ﬁx
> commit rather than a merge of versions which contain bug ﬁxes indirectly (bug
> report (merge))."

So (32 + 7) / 82 = 47.56%. **Denominator: commits.** Verified.

### (b) The ticket-side figure, which §2.4 does not mention

Not printed as a percentage anywhere in the paper. It is a subtraction across two
rows of Table 1, page 3, "Apache Datasets: Details", Original Dataset column,
found verbatim:

> "#Fixed bug reports 4 559 (23.20%) 23 (22.33%)
> #Linked bug reports 256 (10.63%) 10 (9.71%)"

559 fixed, 256 linked, so 303 unlinked, and 303 / 559 = **54.20%** of fixed bug
reports carry no link. I recomputed this rather than taking it from
`paper/PRIOR_ART_EVIDENCE.md`. **Denominator: fixed bug reports.** Verified.

The stray "4" before 559 is the footnote marker, and the footnote defines the
denominator:

> "4We deﬁne “ﬁxed” bug reports as bug reports that have at least one associated
> ﬁxing activity (which means a status change to “ﬁxed”) within the considered
> time period."

Two facts worth recording because they bound how the figure may be used. The
string "54%" appears nowhere in Bachmann, and neither does "46%"; both were
searched across the full text. And the Table 1 column is a single project, the
Apache HTTP web server, over 2004-06-18 to 2008-04-25.

---

## What §2.4 says today

`paper/manuscript/related.md`, lines 132 to 133, verbatim:

> from commit messages. Against that ground truth they found that **only 47.6% of
> bug-fix-related commits are documented in the bug tracking database**. Their

That is figure (a). The paper's quotation of it is accurate, and the audit trail
in `audit/CITATIONS.md` already covers it. **§2.4 does not mention figure (b) at
all.**

---

## Which figure is the like-for-like comparator

Reasoning from denominators only, and stopping there.

| | numerator | denominator | direction |
|---|---|---|---|
| Bachmann (a), quoted in §2.4 | bug-fix commits carrying a link | **82 bug-fix commits** | commit-side |
| Bachmann (b), not quoted | fixed bug reports with no link | **559 fixed bug reports** | ticket-side |
| CSR, `method.md` Definition 1 | commits citing a key | **commits reachable from H_p** | commit-side |
| TRR, `method.md` Definition 2 | tickets ever cited | **tickets in the tracker at T** | ticket-side |

TRR's denominator is tickets. Of the two Bachmann figures, only (b) has a
denominator counted in issues rather than in commits. **(b) is therefore the
comparator that shares TRR's direction; (a) shares CSR's.**

That is a statement about which quantities are commensurable, and it is as far as
this file goes. Whether TRR and (b) are the same quantity depends on more than
direction: (b) restricts to bugs and to fixed bugs, TRR admits every issue type
and every resolution (`method.md` §3.1.1). Those differences are section A of
`paper/DETERMINATION_WORKSHEET.md` and they are the author's to weigh.

---

## What §2.4 would need to say

Described, not drafted. Writing the replacement prose would be making the
determination.

1. **Name the direction of the figure it already quotes.** As it stands, 47.6% is
   introduced without saying its denominator is commits, so a reader comparing it
   to TRR is comparing across the asymmetry without being told.
2. **Report figure (b) alongside it**, with its denominator, its derivation, and
   the fact that Bachmann never prints it as a percentage. A reader who checks the
   source will not find "54.20%" and needs to be told it is a subtraction.
3. **State the residual differences in scope** between (b) and TRR: bugs against
   all issue types, fixed against all resolutions, one project against 38.
4. **Then make whatever comparison the determination licenses.** Steps 1 to 3 are
   reporting and can be done under either branch of the worksheet. Step 4 cannot.

Points 1 to 3 do not presuppose an answer. Point 4 is the gate.

---

## What could not be established

* Whether the original omission was deliberate. The commit-side figure is the one
  Bachmann prints in prose, and the ticket-side one has to be derived, so quoting
  (a) is what reading the paper normally produces. Nothing in the repository
  records a decision either way.
* Whether Bachmann's 559 fixed bug reports include issue types that Jira would
  not call bugs. Their tracker is Bugzilla and the paper does not enumerate types.
  This is open question 2 in `paper/PRIOR_ART_EVIDENCE.md` and would need their
  replication package.
* Whether the 47.6% and the 54.20% are consistent with each other on the same
  data. They come from different tables over different periods, the evaluation
  sample against the original dataset, and the paper does not relate them.

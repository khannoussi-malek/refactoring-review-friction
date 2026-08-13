# arXiv endorsement requests

Two drafts. Send one, wait, then send the other if the first goes unanswered.
Sending both at once risks two people spending effort on the same click.

Before sending, get your endorsement code from arXiv: start the submission, and
when it asks for an endorser it gives you a six-character code and a URL. The
code is what makes this one click for them instead of a research task. Paste it
where each draft says `[CODE]`.

Neither draft mentions positions, supervision, funding or relocation, and
neither should acquire such a mention later. An endorsement request that carries
a second ask is a different email and gets a worse response rate.

---

## (a) Nikolaos Tsantalis

Best first approach: there is an existing technical interaction to point at, and
it is one where you gave rather than asked.

**Subject:** `arXiv endorsement for cs.SE (RefactoringMiner issue #1124)`

```
Dear Professor Tsantalis,

I filed issue #1124 on RefactoringMiner last July, the one about 160
interface-to-class false positives in a single commit. They traced back to
TypeScript type aliases having no representation in the class model.

I have a paper ready for arXiv that uses RefactoringMiner as its detector. I am
an independent researcher submitting from a personal address, and since January
that means I need a person to endorse me for cs.SE.

It is "Traceability and estimate coverage as corpus-eligibility constraints: a
probe of 38 Apache projects". Twelve of 38 Apache projects clear a
pre-registered issue-commit traceability bar, and most of the divergence between
commit-side and ticket-side linkage rates turns out to be arithmetic rather than
project discipline.

Endorsing confirms only that the topic fits cs.SE. It is not a judgment on the
work and carries no responsibility for it. One click, code [CODE], at
https://arxiv.org/auth/endorse

Malek Khannoussi
```

---

## (b) Michael Rath, or Patrick Mäder

Send to one, not both. Rath is the better first choice: SEOSS 33 lists him
first and the reproduction below is of a figure from that dataset.

**Subject:** `arXiv endorsement for cs.SE (SEOSS 33 reproduction)`

```
Dear Dr Rath,

I validated a traceability probe against SEOSS 33, and you may want the result
regardless of the rest of this email. Restricting my scan to the earliest 12,419
Flink commits, the change-set count you publish, gives 41.9841% against your
41.98%. The 24-point gap I first saw was scope, not disagreement.

That check is Section 4.4 of a paper I want to post to arXiv. I am an
independent researcher submitting from a personal address, so I need a person to
endorse me for cs.SE.

It is "Traceability and estimate coverage as corpus-eligibility constraints: a
probe of 38 Apache projects". Twelve of 38 Apache projects clear a
pre-registered linkage bar, and the gap between commit-side and ticket-side
rates is mostly arithmetic, set by commits per ticket.

Endorsing confirms only that the topic fits cs.SE. One click, code [CODE], at
https://arxiv.org/auth/endorse

Malek Khannoussi
```

---

## If both go unanswered

Reasonable next candidates, in order, each with an existing hook in the paper:

1. **Lloyd Montgomery, Clara Lüders or Walid Maalej**, who deposited the Public
   Jira Dataset. Every frozen ticket denominator in the paper comes from it.
2. **Christian Bird**, whose ESEC/FSE'09 bias result the paper cites as the
   reason missing links matter at all.
3. Any cs.SE author who has posted to arXiv in the last five years. The
   endorsement system does not require a topical connection, only an eligible
   endorser, so the connection is a courtesy rather than a requirement.

Do not send more than two requests in the same week. arXiv treats a burst of
requests as a signal worth looking at, and it is easily avoided.

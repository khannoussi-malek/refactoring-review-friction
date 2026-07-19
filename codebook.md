# F2 codebook (draft) — "does the review discussion cite *structure*?"

The week-1 miner (`scripts/pr_review_signal.py`) flags F2 when a review comment contains
any structural keyword (`interface`, `extract`, `refactor`, `too big`, …). That is **too
loose** — it fires on trivial or off-topic uses of those words. This codebook is the
manual rule that a real RQ1 measurement replaces the keyword count with.

All examples below are **verbatim hadoop PR-review comments** pulled from the traced
episodes (via githubbot's Jira relay). They are the ground truth to label against.

---

## The unit of coding
One **review comment** on the episode's PR (as relayed into Jira). Label each comment;
an *episode* is F2-positive if **≥1** of its comments is labelled **STRUCTURAL**.

## Labels (mutually exclusive; pick the strongest that applies)

### 1. STRUCTURAL  ✅ (this is the F2 signal)
The comment **argues about the code's shape** — how responsibilities are divided across
classes/interfaces/packages/modules: proposing or contesting an extract/move/split, a
new interface/abstraction, coupling, layering, or where something *should live*.

Real positives (HADOOP-18679, the BulkDelete-API / Extract-Interface episode):
- > "my solution would have **pulled out `createStore()` into a method** and overrode it,
  >  or **added `S3AInternals.setStore()`** call." — proposes an extract + interface change.
- > "+ some **interface `getVersionForDeleteOperations() -> String`** to put on s3/abfs file
  >  status, the way we do for `getEtag()`, so you can **extract version info without
  >  playing class-cast games**." — argues for an interface to remove a structural smell.

### 2. INCIDENTAL  ❌ (keyword present, but not a structural argument)
A structural *word* appears, but the comment is not arguing about code shape — it's a
factual note, a trivial cleanup, or the word means something else.

Real false-positives the keyword detector caught:
- > "have **refactored** the import order, and **refactored** `log.error` to `log.debug`."
  (HADOOP-19102) — "refactored" used for import ordering / log level. Not architectural.
- > "12 **too big** …" (HADOOP-19221) — "too big" is about a *thread count* in a test run,
  not a class. Pure keyword collision.
- > "implements the Supplier **interface**, which invokes …" — states a fact about an API,
  proposes no structural change.

### 3. STYLE / CORRECTNESS  ❌ (review discussion, but not about structure)
Genuine review, but about behaviour, tests, naming, bugs, or approval — the axis RQ1 must
*not* count as structural (per the worksheet: if these can't be told apart, that's an
RQ2 human-factors finding).
- > "I like this; a lot cleaner. +1 pending a couple of minor comments." (HADOOP-19120) — approval.
- > "please rebase and fix the typo." — housekeeping.
- CI/Yetus reports — excluded before coding (the miner already drops these as `ci`).

---

## Decision rule (apply in order)
1. Is it a bot CI/Yetus report? → drop (not coded).
2. Does it **propose or debate a change to how code is divided** (extract/move/split/
   interface/abstraction/coupling/where-it-lives)? → **STRUCTURAL**.
3. Does a structural *word* appear only as a fact, a trivial edit, or a different meaning
   (thread counts, import order, log levels)? → **INCIDENTAL**.
4. Otherwise it's review about behaviour/tests/naming/approval → **STYLE / CORRECTNESS**.

## Boundary calls (write the tricky ones here as you code)
- **HADOOP-19098** tripped F2 on a *single* keyword — re-read it under this rule before
  trusting it; it is the borderline case that shows why keyword>0 is insufficient.
- "modify the tests **due to the new interface**" (HADOOP-18679) — the interface change is
  real but this specific comment is about *test fallout*. Code it STYLE/CORRECTNESS unless
  it also argues the interface's shape.

## How this feeds the pipeline
Replace `f2_structural_review = struct_hits > 0` in `pr_review_signal.py` with a labelled
judgment once ~30–50 comments are coded and inter-rater agreement (κ) is acceptable. Until
then, treat the miner's `struct_hits` as a **recall-first prefilter**: it surfaces
candidate comments cheaply; the codebook decides which are truly STRUCTURAL.

## Next
- Code ~30–50 comments across the wide-run episodes (two raters), compute κ.
- Freeze the rule, wire it into the miner, re-run for the real F2 rate.

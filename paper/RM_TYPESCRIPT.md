# RefactoringMiner mislabels TypeScript type aliases — stub

Separate future paper. Recorded so it is not lost; **not developed further**.

- **Defect.** `Change Type Declaration Kind`, **160** instances in one
  `BearStudio/start-ui-web` commit, all `interface → class`; 3rd most frequent type in that corpus.
- **Counterexample.** `src/features/account/types.ts` is `export type Account = User` — a plain type
  alias, neither interface nor class. `UMLClass` has no type-alias representation, so it defaults to class.
- **Corroboration.** The codebase uses function components exclusively and contains essentially no classes.
- **Detector.** RefactoringMiner 3.1.4; TypeScript support complete 2026-05-24, two months old at
  measurement, no independent validation in the literature.
- **Upstream.** [tsantalis/RefactoringMiner#1124](https://github.com/tsantalis/RefactoringMiner/issues/1124),
  filed 2026-07-25. Verified 2026-07-30: open, and about this defect.

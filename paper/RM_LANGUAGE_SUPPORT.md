# Which source languages does RefactoringMiner 3.1.4, as built here, support?

Read-only inspection of the local build. No network, no RefactoringMiner run over
any repository. Verified 2026-08-01.

**Answer: Java yes. TypeScript yes. Python yes. C/C++ no — parser plumbing is
present and linked, but C and C++ have no entry in the language enum the
detector dispatches on, and upstream claims neither detection nor AST diff.**

This decides corpus viability for the violation-symptom design: **OpenStack is
Python and is therefore detectable; Qt is C++ and is not.**

## Verdict

| language | refactoring detection in this build | evidence |
|---|---|---|
| **Java** | **yes** | `JavaFileProcessor`, `Constants.JAVA`, `PathFileUtils.isJavaFile`, JDT (`org.eclipse.jdt.core-3.45.0.jar`, `ecj-3.45.0.jar`); upstream ✅/✅; two benchmarks |
| **TypeScript** | **yes** | `TypeScriptFileProcessor`, `Constants.TYPESCRIPT`, `isTypeScriptFile`, swc4j parser + native `libswc4j-macos-arm64.v.2.1.0.dylib`; upstream ✅/✅; **no benchmark** |
| **Python** | **yes** | `PythonFileProcessor`, `Constants.PYTHON`, `isPythonFile`, ANTLR `extension/base/lang/python/PythonParser` (213 classes) + `PythonTreeSitterNgTreeGenerator`; upstream ✅/✅; benchmark present |
| **C** | **no** | `PathFileUtils.isCFile` exists; **no `Constants.C`**, no `CFileProcessor`; absent from the upstream table entirely |
| **C++** | **no** | `CppFileProcessor` + `CppPreprocessor` exist and link Eclipse CDT; **no `Constants.CPP`**; upstream marks detection and AST diff **blank** |

Also present but out of scope here: Kotlin (`KotlinFileProcessor`, `Constants.KOTLIN`,
upstream ✅/✅, benchmark present), JavaScript (`isJavaScriptFile`, swc4j
`Swc4jMediaType.JavaScript`, upstream ✅/✅, no `Constants` entry of its own),
C# (`extension/base/lang/csharp`, 284 classes; absent from the upstream table).

## The command output

No-argument invocation:

```
$ ./RefactoringMiner/bin/RefactoringMiner
Exception in thread "main" java.lang.IllegalArgumentException: Type `RefactoringMiner -h` to show usage.
	at org.refactoringminer.RefactoringMiner.argumentException(RefactoringMiner.java:412)
	at org.refactoringminer.RefactoringMiner.main(RefactoringMiner.java:27)
```

Usage:

```
$ ./RefactoringMiner/bin/RefactoringMiner -h
-h											Show options
-a <git-repo-folder> <branch> -json <path-to-json-file>					Detect all refactorings at <branch> for <git-repo-folder>. If <branch> is not specified, commits from all branches are analyzed.
-bc <git-repo-folder> <start-commit-sha1> <end-commit-sha1> -json <path-to-json-file>	Detect refactorings between <start-commit-sha1> and <end-commit-sha1> for project <git-repo-folder>
-bt <git-repo-folder> <start-tag> <end-tag> -json <path-to-json-file>			Detect refactorings between <start-tag> and <end-tag> for project <git-repo-folder>
-c <git-repo-folder> <commit-sha1> -json <path-to-json-file>				Detect refactorings at specified commit <commit-sha1> for project <git-repo-folder>
-c <git-repo-folder> <commit-sha1> --parent-index <n> -json <path-to-json-file>	Detect refactorings against merge parent <n> for the specified commit
-gc <git-URL> <commit-sha1> <timeout> -json <path-to-json-file>				Detect refactorings at specified commit <commit-sha1> for project <git-URL> within the given <timeout> in seconds. All required information is obtained directly from GitHub using the OAuth token in github-oauth.properties
-gc <git-URL> <commit-sha1> <timeout> --parent-index <n> -json <path-to-json-file>	Detect refactorings against merge parent <n> for the specified GitHub commit
-gp <git-URL> <pull-request> <timeout> -json <path-to-json-file>			Detect refactorings at specified pull request <pull-request> for project <git-URL> within the given <timeout> in seconds for each commit in the pull request. All required information is obtained directly from GitHub using the OAuth token in github-oauth.properties
```

**The CLI names no language and takes no language flag.** Nine option lines, all
about commit ranges and sources. Language is selected internally from the file
extension, so `-h` cannot answer this question and the jars had to be read.

## Why the language enum is the deciding evidence, not the bundled parsers

`org/refactoringminer/util/PathFileUtils` declares seven predicates —
`isJavaFile`, `isPythonFile`, `isKotlinFile`, `isTypeScriptFile`,
**`isCFile`**, **`isCppFile`**, `isJavaScriptFile` — plus `isSupportedFile`,
`isLangSupportedFile` and `getLang`. The presence of `isCppFile` is what makes a
parser-jar count misleading.

`getLang` returns `gr/uom/java/xmi/Constants`, and that enum has exactly four
language members:

```
JAVA   PYTHON   KOTLIN   TYPESCRIPT
```

There is **no `C` and no `CPP` member for `getLang` to return.** The extension
literals compiled into `PathFileUtils` are `.java`, `.tsx`, `.cpp`, `.hpp` —
so C++ files are *recognised* and *parseable* and are not *dispatched to a
language model*.

The parser layer for C++ is genuinely wired, which is why this needs saying
explicitly rather than inferring from the jar list: `gr/uom/java/xmi/CppFileProcessor`
and `gr/uom/java/xmi/CppPreprocessor` exist, and the build references live CDT
API types — `org/eclipse/cdt/core/parser/FileContent`,
`org/eclipse/cdt/core/parser/ScannerInfo`,
`org/eclipse/cdt/core/parser/IncludeFileContentProvider`, and the
`org/eclipse/cdt/core/dom/ast/*` tree (`ASTVisitor`, `IASTCompositeTypeSpecifier`,
`IASTDeclSpecifier`, …), backed by `eclipse-cdt-core-9.2.100.202507101054+1.jar`
(5.9 MB). **A bundled parser is not a detector.**

## Upstream's own statement, at the commit this build came from

`RefactoringMiner-src/README.md:10-18`, at HEAD `45d0705ce7` (2026-07-17):

| Language | Refactoring detection | AST diff generation | Roadmap |
|---|---|---|---|
| Java | ✅ | ✅ | |
| Python | ✅ | ✅ | `[x]` Support comments; `[x]` Support version 3.14 |
| Kotlin | ✅ | ✅ | `[ ]` Validate precision/recall |
| TypeScript | ✅ | ✅ | `[x]` swc4j Parser; `[ ]` Create benchmark |
| JavaScript | ✅ | ✅ | `[x]` swc4j Parser; `[ ]` Validate precision/recall |
| **C++** | *(blank)* | *(blank)* | `[x]` Eclipse CDT Parser |

**C is not a row in that table at all.** C++ is the only row with both capability
columns empty, and its single ticked roadmap item is the parser — matching the
jar evidence exactly.

## Build provenance — this table describes this binary

- `scripts/setup.sh:13-20` clones upstream `--depth 1` and runs `./gradlew distZip`.
- `RefactoringMiner-src/build.gradle:12-14` pins `version = '3.1.4'` absent a `buildVersion` property.
- `RefactoringMiner-src/build/distributions/RefactoringMiner-3.1.4.zip` (170,013,221 bytes) is dated **2026-07-19 00:53**; `RefactoringMiner/lib/RefactoringMiner-3.1.4.jar` is dated **2026-07-19 00:52**, and `RefactoringMiner/` `2026-07-19 00:53`.
- Source HEAD: `45d0705ce763bb7debf26a712a55055d94d642cc`, *"Undo, as it breaks Parameterize test in commit"*, 2026-07-17 16:55:37 -0400.

So the README table above is the README of the tree that produced this jar, not
a current upstream page.

## Bundled tree-sitter grammars are GumTree diff generators, not detectors

`RefactoringMiner/lib/` ships 16 `tree-sitter-*.jar` grammars — c, c-sharp,
cmake, cpp, go, haskell, java, javascript, kotlin, ocaml, php, **python**, r,
ruby, rust, swift, tsx, typescript. `gen.treesitter-ng-4.0.0-beta8.jar` registers
one `*TreeSitterNgTreeGenerator` per grammar via
`META-INF/services/com.github.gumtreediff.gen.TreeGenerator`.

**Counting these would give a false answer of ~16 languages.** They feed GumTree's
AST-diff layer. Only `PythonTreeSitterNgTreeGenerator` is referenced from a
`FileProcessor` (`gr/uom/java/xmi/PythonFileProcessor`); the C, C++, Go, Rust,
Swift, PHP, Ruby, OCaml, R and Haskell generators are registered and unused by
the refactoring detector.

## Accuracy evidence is thinner than the ✅ column

`RefactoringMiner-src/documentation/accuracy.md` contains four benchmark
sections: **Java Benchmark 1**, **Java Benchmark 2**, **Python Benchmark**,
**Kotlin Benchmark**. There is **no TypeScript, JavaScript or C++ benchmark**,
consistent with upstream's own unchecked `[ ] Create benchmark` for TypeScript.
`paper/RM_TYPESCRIPT.md` already records one TypeScript defect found in this repo
(160 false `interface → class` detections, upstream issue #1124), so the
TypeScript ✅ is a support claim, not a validated-accuracy claim.

Python's benchmark exists but was **not re-run or independently checked here**;
its precision and recall on OpenStack-scale Python are NOT COMPUTABLE from local
data, because no Python corpus is on disk and R4 forbids fetching one.

## Consequence for corpus choice

- **OpenStack (Python)** — detectable in principle by this build. Support is
  claimed and benchmarked upstream; accuracy on that corpus is unmeasured here.
- **Qt Base / Qt Creator (C++)** — **not detectable by this build.** The
  refactoring-detected leg of the violation-symptom design cannot be operated on
  a C++ corpus with RefactoringMiner 3.1.4 as built. This is a hard blocker, not
  a tuning problem.
- **Hadoop (Java)** — fully supported, benchmarked twice upstream, and the corpus
  already mined in this repo. It is why the feasibility gate runs on Hadoop.

Nothing above was measured by running the detector. It is a capability reading of
a binary, and the C++ verdict rests on upstream's own blank cells plus the
missing enum member, not on an attempted C++ run.

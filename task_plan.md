# Task Plan: Publication evidence redevelopment

## Goal
Turn the evidence-honest ZipMould mechanism study into a submission-ready paper: complete the frozen confirmatory experiment from a clean tagged release, analyze and archive its evidence, write the manuscript, and verify the reproducibility package.

## Current Phase
Phase 15

## Phases

### Phase 1: Inventory and requirements
- [x] Inventory manuscripts, presentations, code, data, results, and documentation
- [x] Identify the scientific claims and intended contribution
- [x] Record the publication-readiness criteria used for the audit
- **Status:** complete

### Phase 2: Scientific and reproducibility audit
- [x] Evaluate methods, controls, statistics, and claim-to-evidence alignment
- [x] Test whether the computational artifacts build and reproduce reported outputs
- [x] Check manuscript completeness and internal consistency
- **Status:** complete

### Phase 3: Venue and novelty calibration
- [x] Compare the work with current related literature
- [x] Identify plausible venue classes and their evidentiary expectations
- **Status:** complete

### Phase 4: Synthesis and recommendations
- [x] Give a defensible publishability verdict
- [x] Separate submission blockers from valuable later extensions
- [x] Provide a prioritized development plan
- **Status:** complete

### Phase 5: Completion audit and delivery
- [x] Verify each conclusion against authoritative repository or external evidence
- [x] Prepare a self-contained assessment with file/source references
- **Status:** complete

### Phase 6: Freeze the paper claim and confirm benchmark design
- [x] Write the claim, primary question, estimand, and outcome-contingent interpretation
- [x] Define test-lock semantics and leakage controls
- [x] Define generated instance families and non-solver validity criteria
- **Status:** complete

### Phase 7: Implement deterministic instance generation
- [x] Add generator, canonical serialization, certificates, and structural metrics
- [x] Add train/dev generation and sealed-test commitment workflow
- [x] Add unit tests for determinism, validity, and lock verification
- **Status:** complete

### Phase 8: Calibrate difficulty without opening test
- [x] Generate train/dev candidate instances
- [x] Benchmark only the feedback-frozen constructor during distribution selection
- [x] Select informative family/size strata without observing a treatment effect
- **Status:** complete

### Phase 9: Seal the confirmatory test set
- [x] Generate an opaque secret test seed outside tracked artifacts
- [x] Commit seed and canonical-corpus hashes without exposing instances
- [x] Verify deterministic regeneration and leakage guards without writing or benchmarking test
- **Status:** complete

### Phase 10: Verification and handoff
- [x] Run unit, lint, type, generator, and lock-integrity checks
- [x] Audit every claim/lock requirement against current artifacts
- [x] Document use, forbidden pre-analysis actions, and final study decision rule
- **Status:** complete

### Phase 11: Freeze the confirmatory experiment pipeline
- [x] Define the immutable seed schedule, configuration, manifest, hardware capture, and output schema
- [x] Implement the full-versus-frozen runner and predeclared stratified cluster-bootstrap analysis
- [x] Add scientific regression tests and a one-command dry-run verification path
- **Status:** complete

### Phase 12: Create and execute the clean confirmatory release
- [x] Verify all checks and lock commitments from a clean commit
- [x] Commit and tag the exact confirmatory code/configuration before opening test
- [x] Unlock once, run all 150 puzzles x 30 seeds x 2 paired conditions, and archive raw outputs
- **Status:** complete

### Phase 13: Analyze and package confirmatory evidence
- [x] Produce the frozen primary estimate, interval, outcome classification, and stratum summaries
- [x] Generate publication tables/figures and an immutable run manifest with checksums
- [x] Independently validate result completeness, pairing, solution paths, and report regeneration
- **Status:** complete

### Phase 14: Write the journal manuscript
- [x] Build a defensible related-work corpus and bibliography from primary sources
- [x] Draft the complete paper around the frozen claim and actual confirmatory outcome
- [x] Add limitations, threats, data/code availability, figures, tables, and appendices
- **Status:** complete

### Phase 15: Submission-readiness audit
- [x] Build the manuscript and run code, data, citation, figure, and claim consistency checks
- [ ] Verify a clean-clone reproduction workflow and archive/release instructions
- [ ] Audit every publication requirement and enumerate only genuinely external submission tasks
- **Status:** in_progress

## Key Questions
1. Is there a coherent, novel, falsifiable contribution supported by the artifacts?
2. Can an independent reviewer reproduce the central results?
3. What minimum work is required before a credible small-journal submission?
4. Which venue class fits the actual contribution without overstating it?
5. What claim remains true whether feedback wins, ties, or loses on the new test?
6. How can a test corpus be fixed and verifiable without making it available to tuning code?
7. Which procedural families remove the current heuristic ceiling without selecting test puzzles on solver outcomes?

## Decisions Made
| Decision | Rationale |
|----------|-----------|
| Assess publication readiness, not merely artifact polish | A paper can look complete while lacking evidence, novelty, or reproducibility. |
| Preserve existing modified presentation files | They are user-owned changes and part of the evidence under review. |
| Verdict: major redevelopment, not minor revision | The same-config feedback-free diagnostic matches full-method success, and the manuscript/reproducibility package is incomplete. |
| New paper framing must be outcome-invariant | The paper should study when feedback helps, not promise superiority before the sealed test is opened. |
| Test set will be committed by secret-seed hash and canonical-corpus hash | This fixes the instances while keeping the seed/data outside normal training and dev paths until unlock. |

## Errors Encountered
| Error | Attempt | Resolution |
|-------|---------|------------|
| Python `-c` received literal `\\n` sequences and raised `SyntaxError` during Parquet comparison | 1 | Replace the multi-line loop with separate single-expression reads; do not repeat the same quoting form. |
| Firecrawl output file was not present at the first check while the CLI finished asynchronously | 1 | Verified the CLI session and rechecked output creation before reading. |
| An `apply_patch` context did not match the current `findings.md` ordering | 1 | Re-read the current files and applied a narrower patch against exact context. |
| `ruff check .` reported two C401 findings in `tests/test_solver_state.py` | 1 | During the later authorized implementation pass, replaced the generator expressions with set comprehensions; full Ruff now passes. |
| A post-analysis `uv run` check could not create a lock file in the read-only user cache | 1 | Use the existing project virtualenv interpreter directly for the pure read-only Parquet comparison. |
| A combined patch targeted the Stage 4 test-results row in the wrong planning file | 1 | Split the update between `findings.md` and the actual test table in `progress.md`. |
| Initial challenge checks: pytest collected imported `test_seed_commitment`; Ruff found 25 style issues; Pyright found 10 typing errors | 1 | Rename the helper so pytest does not collect it, replace adjacent `zip` calls with `pairwise`, add typed JSON conversion helpers/constants, and tighten test casts. |
| `uv run` again could not create a temporary cache lock during public-corpus inspection | 1 | Use the existing `.venv/bin/python` directly for read-only/generated-data diagnostics. |
| Initial calibration script passed Ruff but had 7 Pyright errors around Polars/JSON/joblib return types | 1 | Validate scalar/list inputs explicitly and cast the third-party joblib result at the boundary. |
| A combined calibration typing patch missed the exact context near target-bound extraction | 1 | Applied the independent data-boundary changes first, re-read the remaining block, then patched the target bounds separately. |
| Explicit-strata validation pushed the single schema loader over Ruff's branch/statement thresholds | 1 | Keep the validation together as one schema boundary and document a narrow complexity exemption on that function. |
| The public-certificate regression test introduced one Ruff magic-number finding and three Pyright errors at the JSON boundary | 1 | Added a named corpus-size constant and explicit typed conversion of certificate rows; targeted tests, Ruff, and Pyright then passed. |
| Final calibration hash check first targeted `report.json`, but the runner names split-specific reports | 1 | Located and verified `calibration64-selected/dev_report.json`; its SHA-256 matches the documented `aa427108...7fe2` anchor. |
| An `rg` completion search parsed the leading-dash pattern as an option | 1 | Re-ran with the `--` option terminator and confirmed only the final audit checkbox remained. |
| Initial architecture inspection targeted nonexistent `experiments/common.py` | 1 | Use the self-contained Stage 4 dispatcher and the actual solver/IO modules as references for the new Challenge v1 pipeline. |
| First confirmatory static checks found eight Ruff findings and 13 strict-Pyright errors | 1 | Replace untyped TOML scalar conversions with checked helpers, name frozen constants, simplify comprehensions/return annotations, and remove the stale lint suppression before rerunning. |
| First public smoke run failed because loky could not unpickle `lru_cache` wrappers from a `python -m` `__main__` module | 1 | Remove module-level cache wrappers from serialized worker functions, verify multiprocessing, then optimize with explicitly picklable batch workers if needed. |
| First regression-test lint run found import ordering and one magic-number assertion | 1 | Apply Ruff's mechanical import organization and replace the literal with a named expected-solution count. |
| Combined checkpoint/test patch missed the import context after Ruff reorganized it | 1 | Re-read both exact regions and apply the release-resume guard and tag-gate test against current text. |
| First full preflight found one stale `SolverConfig` import after hash validation moved into the protocol | 1 | Remove the unused import; tests and lock verification already passed, then rerun full lint/type checks. |
| `make paper-verify` could not acquire the shared uv cache lock while three other uv checks ran concurrently | 1 | Keep parallelization for independent checks but rerun the Make target sequentially after the other uv processes exit. |
| Sequential `make paper-verify` hit the same read-only uv cache-lock failure | 2 | Stop retrying uv through Make; make scientific targets invoke the already-synced project `.venv/bin/python`, while dependency installation remains `uv sync`. |
| First annotated-tag command could not write `.git` inside the filesystem sandbox | 1 | Requested the required scoped escalation and created `challenge-v1-confirmatory-v1` successfully before unlock. |
| Initial figure generator passed execution/types but Ruff found four long lines and one disallowed print | 1 | Wrap SVG/table construction calls and keep the generator silent on success before regenerating figures. |
| First line-wrap repair left an unterminated f-string at a LaTeX row terminator | 1 | Replace fragile terminal backslash escaping with a single raw `_LATEX_ROW_END` constant reused by every generated row. |
| Local image viewer could not process SVG directly, and `rsvg-convert` is unavailable | 1 | Use the installed ImageMagick `magick` command to render temporary PNG previews, leaving SVG as the publication artifact. |
| A broad `sed` read of the Springer chapter exceeded the useful output/context window | 1 | Switched to targeted `rg` patterns and narrow line ranges; exact authors, venue, volume, pages, year, and DOI were recovered without another broad dump. |
| Initial method inspection assumed flat `src/zipmould/solver.py` and `_kernel.py` paths | 1 | Located the actual package files with `rg --files` and read `solver/api.py`, `solver/_kernel.py`, `solver/_heuristics.py`, and `solver/state.py`. |
| Initial benchmark-spec inspection assumed `spec.toml` | 1 | Located and read the authoritative `benchmark/challenge/v1/spec.json`. |
| An overbroad recursive mechanism search included minified frontend assets and thousands of metric matches | 1 | Restricted subsequent reads to exact source files and narrow line ranges. |
| TeX and Inkscape executables are absent from the environment | 1 | Check for an already-installed alternative document renderer; otherwise keep portable LaTeX source and make the missing engine an explicit external build prerequisite. |
| First Typst compile rejected the multi-letter math identifier `pos` and warned that Libertinus Mono was unavailable | 1 | Render the operator as math text and use the installed Nimbus Mono PS face for code. |
| Second Typst compile treated `softplus` as an undefined math symbol | 1 | Typeset the implementation function name explicitly as math text. |
| Third Typst compile treated mnemonic heuristic subscripts as undefined multi-letter symbols | 1 | Typeset `man`, `warn`, `art`, and `par` as textual subscripts. |
| A placeholder-marker scan included `paper/README.md` before that file existed | 1 | Created the paper-package README and reran checks against the complete package. |
| First manuscript-checker lint found hard-coded result constants and a Unicode-minus warning | 1 | Derive all display tokens from the archived JSON and construct the typographic minus by Unicode name. |
| Directory-wide Pyright could not resolve Polars for the already-validated figure script | 1 | Keep the existing explicit figure-script validation and type-check the new standard-library manuscript checker independently. |
| Calibration evidence was first read from a stale scratch-style path | 1 | Located and verified the tracked authoritative `benchmark/challenge/v1/calibration.report.json` (229/500, all five strata informative). |
| A combined Make/README patch missed the exact evidence-README wording | 1 | Split the build-target changes from the narrow evidence-documentation replacement and apply against current text. |
| Direct Pyright execution was detached from the uv-managed environment and emitted 512 false missing-import errors | 1 | Run the repository check through `uv run pyright`; it reports 0 errors and the expected 11 third-party typing warnings. |
| `bun run test` invoked Bun's shell `test` because the frontend script is named `test:unit` | 1 | Run `bun run test:unit --run`; all 13 files and 65 tests pass. |
| A direct pytest process started concurrently with other full audits stopped progressing after 20 tests | 1 | Terminated the stalled audit process and reran sequentially through `uv run pytest -vv`; all 46 tests passed in 0.61 seconds. |
| Local `git clone --local` could not hardlink Git objects across the workspace and `/tmp` filesystems | 1 | Created a fresh temporary target and cloned with `--no-local`, which copied objects successfully. |
| Clean-clone `uv sync --offline` could not write its cache lock inside the sandbox | 1 | Used the approved scoped unsandboxed `rtk uv sync --offline`; the lockfile environment installed entirely from the local cache. |
| First clean-clone `make paper` lacked the ignored runtime `sealed/` test paths required by the frozen analyzer | 1 | Add an integrity-checked, non-overwriting restoration step from the versioned post-analysis test release before reanalysis. |

## Notes
- External web content belongs in findings.md, not this file.
- The user explicitly authorized development work and changes to gitignored experiment artifacts for Phases 6–15.
- The user reports the prior seed backup/commit/freeze prerequisites are done; current-state checks remain authoritative before test unlock.

# Progress Log

## Session: 2026-07-16

### Phase 1: Inventory and requirements
- **Status:** complete
- **Started:** 2026-07-16
- Actions taken:
  - Read repository-level RTK instructions and the scientific planning workflow.
  - Confirmed pre-existing user modifications in `presentations/zipmould.md` and `presentations/zipmould.pdf`.
  - Defined a publication-readiness audit covering science, reproducibility, manuscript quality, novelty, and venue fit.
  - Inventoried the repository and began extracting the claim structure from the README and presentation.
  - Confirmed that no journal manuscript or bibliography artifact is currently present.
  - Extracted the algorithm mapping, hypotheses, baselines, and claimed statistical protocol from the presentation.
  - Reviewed current Stage 4 summary, primary report, and extended report.
  - Identified the non-significant comparison with the strongest baseline and the absence of results from the presentation.
  - Audited the Stage 4 manifest, analysis implementation, tracked output set, and metrics code.
  - Found mismatches between the claimed FDR/4x4 protocol and the executed three-baseline analysis, plus missing versioned current raw results.
  - Audited Stage 1 and Stage 2 manifests, analyses, dev gate, winner report, and tracked artifact coverage.
  - Found that the design-factor hypotheses are not directly tested and that the tuned winner tie-break uses timing from untuned Stage 1 configurations.
  - Reviewed packaging, build targets, benchmark parsing/splitting, corpus metadata, licensing, and recent history.
  - Identified missing dataset provenance/licensing and the absence of an end-to-end experiment reproduction command.
  - Reviewed the candidate kernel, baseline implementations, tuned/default configurations, and experiment dispatchers.
  - Found unequal compute and tuning budgets, incomparable iteration semantics, and an ACO baseline vulnerable to pheromone/softmax saturation.
  - Quantified current/superseded run provenance and timing from the local raw Parquet tables.
  - Established that 70.4% of winner trials solve on the first population, before pheromone learning can contribute.
  - Ran a same-config, feedback-frozen post-hoc diagnostic across all 37 test puzzles x 30 seeds; it also solved 1,110/1,110 trials.
  - Reclassified the current evidence as support for the tuned construction heuristic, not for an SMA-specific performance contribution.
  - Began current related-work calibration; broad search confirms substantial prior improved/hybrid SMA and graph-optimization literature.
  - Narrowed the novelty question to the precise ZipMould edge-memory mechanism; discrete/routing and graph-oriented slime-mould precedents already exist.
  - Completed targeted searches for prior SMA vehicle-routing applications and slime-mould/ACO hybrids; source verification is in progress.
  - Verified primary/indexed discrete-routing and slime-mould/ACO precedents relevant to the novelty claim.
  - Collected current official venue criteria for a software-paper route and a broad algorithms-journal route; detailed fit assessment is next.
  - Determined that JOSS is not an immediate substitute for the algorithm paper and that broad algorithm-journal scope does not lower the core evidence threshold.
  - Confirmed that binary SMA and extensive hybrid/improved-SMA literature must be included in novelty positioning.
  - Verified binary-SMA precedents on official Elsevier and Springer pages.
  - Attempted to resolve a full binary-SMA DOI; the search index continued to truncate that Springer identifier, so it will not be used as a precise final citation.
- Files created/modified:
  - `task_plan.md` (created)
  - `findings.md` (created)
  - `progress.md` (created)

### Phase 2: Scientific and reproducibility audit
- **Status:** complete
- Actions taken:
  - Audited experiment design, analysis code, result provenance, baselines, budgets, and claim-to-evidence alignment.
  - Ran a same-config feedback-free diagnostic that matched the winner's perfect test success.
  - Began external novelty and venue calibration in parallel with reproducibility checks.
  - Ran Python verification: 35 tests pass; Pyright has 0 errors/9 warnings; Ruff finds two minor C401 issues.
  - Ran frontend unit verification: 13 test files and 65 tests pass.
  - Regenerated Stage 4 primary/extended reports and aggregate in an isolated temporary directory from the local raw table; JSON hashes match and aggregate tables are equal.
  - Verified a further method/narrative mismatch: the “positive” code still includes negative-rank deposits and differs only by clipping pheromone at zero.

### Phase 3: Venue and novelty calibration
- **Status:** complete
- Actions taken:
  - Verified discrete/binary SMA, CVRP, graph-optimization, and slime-mould/ACO precedents.
  - Checked current broad algorithm-journal scope and JOSS eligibility criteria.

### Phase 4: Synthesis and recommendations
- **Status:** complete
- Actions taken:
  - Reached a not-submission-ready verdict with a plausible path to a modest journal after major redevelopment.
  - Separated seven required workstreams from optional visualizer/presentation polish.
  - Defined viable mechanism-paper, honest empirical/negative-result, and later software-paper framings.

### Phase 5: Completion audit and delivery
- **Status:** complete
  - Audited each user requirement against repository, runtime, result, literature, and venue evidence.
  - Confirmed the final answer must distinguish “promising foundation” from “submission-ready paper” and classify the remaining work as major rather than cosmetic.
  - Prepared the evidence-linked final verdict and prioritized development sequence.

## Test Results
| Test | Input | Expected | Actual | Status |
|------|-------|----------|--------|--------|
| Python tests | `uv run pytest` | Suite passes | 35 passed | Pass |
| Python lint | `uv run ruff check .` | No findings | 2 minor C401 findings | Fail |
| Python types | `uv run pyright` | No errors | 0 errors, 9 warnings | Pass |
| Frontend unit tests | `bun run test:unit --run` | Suite passes | 13 files, 65 tests passed | Pass |
| Stage 4 report regeneration | Local current `results.parquet` in isolated temp dir | Match current derived artifacts | JSON SHA-256 hashes identical; aggregate equal, 148 rows | Pass with provenance caveat |
| Independent solution validity | Tuned winner, all 37 test puzzles, seed 0 | Every reported path satisfies all puzzle constraints | 37/37 valid | Pass |

## Error Log
| Timestamp | Error | Attempt | Resolution |
|-----------|-------|---------|------------|
| 2026-07-16 | Literal `\\n` in `python -c` caused `SyntaxError` | 1 | Use separate single-line Parquet summary expressions. |
| 2026-07-16 | Firecrawl output not yet present on immediate check | 1 | Waited for asynchronous completion and verified the resulting JSON. |
| 2026-07-16 | Patch context mismatch while logging verification findings | 1 | Re-read the files and applied a narrower exact-context patch. |
| 2026-07-16 | Ruff reports two C401 findings in a solver-state test | 1 | Logged for readiness assessment; no source modification authorized. |
| 2026-07-16 | `uv run` cache lock failed during isolated aggregate comparison | 1 | Retry with `.venv/bin/python`, avoiding uv cache access. |
| 2026-07-16 | Combined patch looked for a progress-table row in `findings.md` | 1 | Split the updates and applied each against the correct file. |
| 2026-07-16 | Initial challenge test/lint/type run failed (pytest helper collection; 25 Ruff findings; 10 Pyright errors) | 1 | Apply targeted naming, iteration, constant, and JSON typing fixes before rerunning. |
| 2026-07-16 | Final calibration hash check used the nonexistent generic name `report.json` | 1 | Check the runner's split-specific `dev_report.json`; the documented SHA-256 matches. |
| 2026-07-16 | `rg` treated the leading-dash unchecked-box pattern as an option | 1 | Add the `--` option terminator and rerun the completion search. |

## 5-Question Reboot Check
| Question | Answer |
|----------|--------|
| Where am I? | Phase 5 complete; ready for delivery |
| Where am I going? | Final evidence-linked handoff |
| What's the goal? | Determine whether the artifacts support a journal paper and what development remains |
| What have I learned? | See findings.md |
| What have I done? | Completed inventory, scientific/reproducibility audit, novelty/venue calibration, synthesis, and completion audit |

## Session: 2026-07-16 — Evidence redevelopment

### Phase 6: Freeze the paper claim and confirm benchmark design
- **Status:** complete
- Actions taken:
  - Adopted an outcome-invariant mechanism-study framing rather than a superiority claim.
  - Drafted the primary comparison and puzzle-clustered solve-probability estimand.
  - Chose a secret-seed plus canonical-corpus commitment model for the sealed test.
  - Added the v1 spec/README, generator core, sealing CLI, gitignore boundaries, and initial tests.
  - Initial challenge checks exposed pytest helper-name collection plus 25 Ruff and 10 Pyright findings; targeted fixes are in progress.
  - Finished the public v1 candidate spec, leakage policy, and outcome-invariant claim.
  - Repaired the initial validation issues: 5 challenge tests pass, targeted Ruff is clean, and targeted Pyright has zero errors.
- Files created/modified:
  - `task_plan.md`
  - `findings.md`
  - `progress.md`

### Phase 7: Implement deterministic instance generation
- **Status:** complete
- Actions taken:
  - Implemented stable RNG, randomized Hamiltonian certificates, waypoint selection, wall families, metrics, canonical hashing, seed commitments, public generation, sealed verification, and guarded unlock.
  - Added determinism, solver-format compatibility, wall/certificate, and lock-tamper tests.
  - Generated 192 public train and 64 public dev instances; the canonical public corpus hash is `9792ca1b...e2b7ab6`.
  - A follow-up `uv run` inspection hit the known read-only cache-lock issue; use the project virtualenv directly for diagnostics.
  - Calibration runner lint passed; Pyright identified seven third-party/data-boundary typing issues to fix before execution.
  - The first frozen dev calibration solved 84/320 trials (0.2625 overall), meeting the aggregate target but revealing eight 0%/100% strata.
  - Added a tracked 53-walker x 64-iteration calibration configuration to probe a more informative construction budget without consulting a treatment effect.
  - The 64-iteration probe identified five dev-informative strata (rates 0.25–0.80); froze those strata at 200/100/150 train/dev/test counts.
  - Regenerated the final public corpus deterministically: 200 train, 100 dev, canonical corpus hash `229e6dca...c803e44`.
  - Final frozen-only calibration solved 229/500 (0.458) and all five strata met the 0.15–0.85 target.
  - Created `paper/CLAIM.md` with the outcome-invariant contribution, primary estimand, interpretation thresholds, explicit non-claims, and test commitments.

### Phase 8: Calibrate difficulty without opening test
- **Status:** complete
- Actions taken:
  - Used only feedback-frozen dev outcomes to choose the 3,392-path budget and five informative family/size strata.
  - Generated the final 200-train/100-dev public corpus with canonical SHA-256 `229e6dca5b52cec2594fcbc5d8ddf6ca0ae1883c6eef21e9f9e735c74c803e44`.
  - Confirmed the final frozen-only dev rate is 229/500 (0.458), with all stratum rates in the frozen 0.15–0.85 target.
  - Recorded the full calibration history and integrity anchors in `benchmark/challenge/v1/CALIBRATION.md`.

### Phase 9: Seal the confirmatory test set
- **Status:** complete
- Actions taken:
  - Created a mode-0600, gitignored 256-bit test seed without printing its contents.
  - Committed the spec, seed, 150-puzzle canonical corpus, and certificate hashes in `test.lock.json`.
  - Regenerated and verified the sealed corpus in memory; verification reported `test_material_written=false`.
  - Confirmed the guarded unlock refuses to run without its final-analysis acknowledgement and that no `sealed/` output directory exists.

### Phase 10: Verification and handoff
- **Status:** complete
- Actions taken:
  - Added an independent regression check for all 300 public planted certificates, including coverage, uniqueness, endpoints, waypoint order, adjacency, walls, and solver feasibility.
  - Ran the full Python suite: 41 tests pass.
  - Ran repository-wide Ruff: all checks pass after repairing the two pre-existing C401 test findings.
  - Ran repository-wide Pyright: 0 errors and 10 third-party typing warnings.
  - Re-verified the test commitment against the private seed without writing test material.
  - Corrected the calibration runner's default to the tracked 64-iteration Challenge v1 configuration and retained the exact selection-time report as a tracked artifact.
  - Audited the claim, spec, public manifest, calibration report, test lock, ignore rules, secret permissions, and absence of unsealed test material against one another.

## Final Evidence-Redevelopment Checks
| Check | Actual | Status |
|------|--------|--------|
| Python tests | 41 passed | Pass |
| Python lint | All checks passed | Pass |
| Python types | 0 errors, 10 third-party warnings | Pass |
| Public certificate validation | 300/300 puzzles validated | Pass |
| Public corpus identity | Canonical SHA-256 `229e6dca...c803e44` | Pass |
| Sealed test integrity | 150 puzzles; canonical SHA-256 `3ee36892...b0b0fa4`; no material written | Pass |
| Leakage boundaries | Secret mode 0600; secret/scratch/sealed paths gitignored; sealed output absent | Pass |

## Session: 2026-07-16 — Confirmatory study and manuscript

### Phase 11: Freeze the confirmatory experiment pipeline
- **Status:** in_progress
- Actions taken:
  - Re-read the scientific planning workflow and restored the complete audit context.
  - Verified the worktree is clean at commit `8b1a8d1` and contains the benchmark release.
  - Found no tag at `HEAD` and no Challenge v1 confirmatory runner or predeclared analysis implementation; the sealed test therefore remains unopened.
  - Expanded the plan through confirmatory execution, evidence packaging, manuscript drafting, and submission audit.
  - Audited the legacy Stage 4 dispatcher and solver API; confirmed the solver already supports a same-config paired `freeze_pheromone` intervention and records the provenance fields needed by the new runner.
  - Determined that confirmatory output must stay under the pre-existing ignored scratch boundary during execution so per-run Git provenance remains clean.
  - Fixed the intervention semantics: paired initial seeds with no claim of synchronized post-intervention RNG streams, because stochastic feedback updates themselves consume randomness.
  - Added the frozen final config, typed protocol, release verifier, public smoke/final checkpointed runner, solution validator, and predeclared primary analysis.
  - Release verification confirms config hash `208b2ef3dac411a69b3a9a339262796a`, the expected 150-puzzle lock, and that the current implementation tree is correctly dirty/untagged before release.
  - Initial targeted static checks exposed eight style findings and 13 strict typing errors at TOML/third-party data boundaries; targeted repairs are in progress before any smoke run.
  - Reached clean targeted Ruff and zero targeted Pyright errors (one joblib typing warning remains).
  - The first public smoke dispatch failed before accessing test or executing trials because loky cannot deserialize module-level `lru_cache` wrappers when the runner is launched with `python -m`; the worker boundary will be made explicitly picklable.
  - Removed the unpicklable cache wrappers; the public-only 8-job smoke grid now completes with both conditions, zero failures, and `test_material_accessed=false`.
  - Added four regression tests covering protocol drift, frozen RNG/decision behavior, stratified bootstrap behavior, complete paired-grid validation, and independent validation of every archived solved path in a synthetic analysis run; all four pass.
  - Added the exact release-tag gate and checkpoint provenance validator; the confirmatory regression file now contains five passing tests.
  - Full preflight reached 46 passing tests and a verified unopened 150-puzzle lock; lint/type checks found only one stale analysis import, now removed.
  - Full Ruff is clean, Pyright has zero errors (11 dependency/joblib warnings), and `git diff --check` passes; the Make preflight alone collided with concurrent uv cache locking and will be rerun sequentially.
  - Sequential Make reproduced the uv cache restriction, so scientific Make targets now use the synchronized project virtualenv directly rather than touching the user cache.
  - Both `make paper-verify` and the 8-job public-only `make paper-smoke` now pass through the documented one-command workflow.
  - Phase 11 is complete: the intervention, release manifest, hardware capture, output/checkpoint schema, exact hashes, bootstrap, decision rule, solution validation, tag gate, tests, and human protocol are frozen before test unlock.

### Phase 12: Create and execute the clean confirmatory release
- **Status:** complete
- Actions taken:
  - Began the pre-commit release audit; no sealed test material has been written or inspected.
  - Confirmed the release diff contains only intended scientific pipeline/docs files, has no whitespace errors, keeps secret/scratch artifacts ignored, and still has no `sealed/` directory.
  - Committed the frozen pipeline as `06ef8bb` and created annotated tag `challenge-v1-confirmatory-v1`; the first sandboxed tag write failed read-only, and the approved scoped retry succeeded.
  - Reverified the clean tagged release: 46 tests pass, Ruff passes, Pyright has 0 errors/11 third-party warnings, and the sealed corpus commitment verifies without writing data.
  - Performed the single acknowledged unlock; the final release verifier matched the unlocked corpus and certificate commitments while Git remained clean.
  - Executed all 9,000 trials in 145.0 seconds with zero failed rows and raw SHA-256 `a899646e...b1976a`.
  - Ran the frozen analysis for the first time: full 2,039/4,500 (45.31%), frozen 1,981/4,500 (44.02%), Delta +1.29 percentage points, 95% CI [-0.04, +2.64] points, classification `practically equivalent`.
  - Independently revalidated every one of the 4,020 archived solution paths during analysis.
  - Independently regenerated report JSON/Markdown, puzzle effects, and all bootstrap replicates into `/tmp`; every artifact was byte-identical.
  - Created the versioned post-analysis evidence package under `paper/results/challenge-v1/`, including all raw/derived results, the manifest, post-analysis test corpus/certificates, and the revealed seed.
  - Verified every packaged byte checksum, the revealed seed against its pre-analysis commitment, and exact equality of the archived raw table/test corpus with their run-time sources.
  - Phase 12 is complete; the test was opened once and the exact complete evidence is now reproducible outside ignored local state.

### Phase 13: Analyze and package confirmatory evidence
- **Status:** complete
- Actions taken:
  - Completed the frozen primary analysis and evidence validation.
  - Began publication table/figure generation from the immutable result package.
  - Added a dependency-free vector figure/LaTeX table generator; first execution succeeded and Pyright passed, while five Ruff presentation issues are being repaired.
  - A first formatting repair broke one LaTeX row's f-string escaping; switched all generated row endings to a shared raw constant before rerunning.
  - Figure generation now passes Ruff, execution, and Pyright; generated LaTeX rows were inspected and have correct line terminators.
  - The local viewer does not accept SVG and `rsvg-convert` is absent, so visual QA will use temporary ImageMagick PNG renderings.
  - Rendered both SVGs to temporary PNGs for visual inspection; the plots are clear, but the primary figure's right-edge values were clipped, so its canvas/plot width is being corrected.
  - Widened and rerendered the primary SVG; all interval/stratum labels now fit, and both publication figures passed visual QA.
  - Generated two booktabs-ready LaTeX tables directly from the frozen JSON report.
  - Phase 13 is complete: immutable raw/derived evidence, manifest, checksums, reproducibility reveal, tables, figures, and independent regeneration checks are all present.

### Phase 14: Write the journal manuscript
- **Status:** complete
- Actions taken:
  - Began primary-source related-work verification and manuscript drafting around the actual practical-equivalence result.
  - Loaded the Firecrawl research workflow, confirmed authentication/credits, and inventoried eleven existing related-work search caches to avoid redundant web requests.
  - Added `.firecrawl/` to `.gitignore` and extracted primary-source leads from the existing discrete, graph, routing, and binary SMA caches; exact metadata still needs targeted verification because several cached URLs are truncated.
  - Completed targeted searches for the original SMA paper, binary SMA, Hamilton paths in grid graphs, and biological adaptive-network design; result metadata will be checked before citation.
  - Verified exact SIAM and Science DOI records for grid-graph Hamiltonicity and biological adaptive-network design; original/binary SMA metadata still requires page scraping because search URLs are truncated.
  - Scraped the original SMA Elsevier page, binary-SMA institutional record, PLOS ONE CVRP paper, and SIAM grid-Hamiltonian record for primary metadata extraction.
  - Extracted exact original-SMA, binary-SMA, and grid-Hamiltonian citation metadata and the precise scope distinction needed for the novelty statement.
  - Verified exact PLOS ONE metadata and scope for the prior SMA-to-CVRP application, and located a DOI-resolved SMA/ACO hybrid chapter for metadata follow-up.
  - Ran targeted metadata searches for original Ant System, Efron's bootstrap paper, Lakens' equivalence-testing primer, and the SMA/ACO chapter; the title-only SMA/ACO query returned no result, so its known DOI/publisher page will be used directly.
  - Scraped the IEEE Ant System record, DOI-resolved Efron paper, PMC equivalence primer, Springer SMA/ACO chapter, and Science Physarum network paper for exact primary metadata.
  - Verified exact ACO, bootstrap, practical-equivalence, and Physarum network citation metadata and fixed the manuscript terminology: the predeclared interval-inside-band rule is a practical-equivalence classification, not a formal TOST analysis.
  - A broad Springer-cache read produced excessive output; replaced it with targeted line extraction and recovered the exact Rong et al. (2021) authors, LNCS volume 12689, pages 322--332, and DOI.
  - Identified direct earlier Physarum graph/ACO precedents from the publisher record, so the novelty claim will be restricted to this ordered grid-Hamiltonian domain and the precise edge-feedback intervention.
  - Audited the exact constructor, heuristic, fitness, rank-deposit, decay, restart-noise, and frozen-intervention code paths so the Methods section can use equations that match the implementation rather than the earlier presentation shorthand.
  - Audited the Challenge v1 generator: planted certificate, endpoint-backbite randomization, deceptive waypoint selection, certificate-preserving wall placement, and the five dev-selected frozen strata.
  - Found no local TeX engine or Inkscape installation; alternative renderers will be checked before treating PDF compilation as an external prerequisite.
  - Found Typst 0.14.2 and drafted the complete blinded manuscript plus a standard BibTeX database; the first compile reached a narrow math-identifier/font issue now corrected.
  - Resolved three small Typst math/font issues; the 4,207-word manuscript now compiles without warnings to a tagged nine-page A4 PDF.
  - Visually inspected the title/abstract, both result figures and tables, discussion, declarations, and reference page; layout, labels, vector plots, DOI links, and pagination are legible with no clipping.
  - Added a one-command paper build, a manuscript/evidence consistency checker, package documentation, and a submission handoff that separates completed science from author- and venue-dependent tasks.
  - `make paper` now also performs an independent reanalysis from the archived raw table, revalidates all 4,020 solutions, and byte-compares both reports, the puzzle-effect table, and all 10,000 bootstrap replicates before auditing manuscript claims.
  - Phase 14 is complete: the primary-source bibliography, full manuscript, limitations/threats, reproducibility statement, figures, tables, blinded declarations, and compiled PDF are present.
  - Phase 15 has begun; the manuscript build and code/data/citation/figure/claim consistency checks pass, with full repository and clean-clone audits remaining.

### Phase 15: Submission-readiness audit
- **Status:** in_progress
- Actions taken:
  - Verified the complete one-command paper build, raw evidence checksums, byte-identical independent analysis, 4,020-path revalidation, and post-analysis lock verifier.
  - Full Ruff passes; `uv run pyright` reports 0 errors and 11 third-party typing warnings; the new manuscript checker independently reports 0 Pyright findings.
  - Sequential Python verification passes all 46 tests, and frontend verification passes all 65 unit tests across 13 files.
  - A direct Pyright call lacked the uv environment, the first frontend command used the wrong script name, and a concurrently launched direct pytest process stalled; all three were replaced by isolated canonical commands and passed without source changes.
  - Reviewed the complete release diff and confirmed that the pre-test tag remains fixed at `06ef8bb`; the next step is a post-analysis publication commit followed by clean-clone reproduction.
  - Created post-analysis publication commit `9e77e06` while leaving `challenge-v1-confirmatory-v1` fixed at `06ef8bb`.
  - A no-local `/tmp` clone verified the publication commit and every archived checksum, then installed the exact lockfile environment offline against the clone itself.
  - The first clone paper build exposed one real packaging gap: frozen analysis expects ignored runtime test files. Added a checksum-verified restoration step that refuses to overwrite differing material and runs before archived reanalysis.

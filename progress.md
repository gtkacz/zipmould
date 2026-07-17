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

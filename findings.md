# Findings & Decisions

## Requirements
- Decide whether the current artifacts could support publication, including in a small journal.
- Explain whether further development is needed and distinguish essential from optional work.
- Base the verdict on the authoritative current worktree and current external publication context.
- Decide and record the paper's honest claim before seeing a new confirmatory test result.
- Create provenance-safe new instances that avoid the current ceiling.
- Create a locked test set that is fixed and verifiable but unavailable to tuning/evaluation until deliberately unlocked.
- Complete a clean, tagged, reproducible confirmatory run and use its actual outcome to write a submission-ready mechanism-study manuscript.

## Confirmatory Pipeline Audit
- Commit `8b1a8d1` is clean and contains the challenge benchmark, but no tag currently points at `HEAD`.
- No Challenge v1 confirmatory runner or implementation of the frozen stratified cluster bootstrap exists yet, so the locked test must remain sealed while those artifacts are built and tested.
- The legacy Stage 4 dispatcher is reusable only as a structural reference: it loads the legacy corpus/split implicitly and dispatches unrelated baselines, while Challenge v1 needs an explicit sealed corpus, exactly two paired conditions, immutable seeds `0..29`, result completeness checks, and release-manifest capture.
- `solve()` already exposes the required `freeze_pheromone` flag and records configuration hash, Git SHA, dirty status, timing, fitness, solution, and iteration count. The final runner can therefore use the identical `SolverConfig` and seed with only the frozen/full flag changed.
- The project already depends on Polars and joblib, which are sufficient for the raw result table and parallel execution; no new analysis dependency is required for a deterministic NumPy bootstrap.
- Challenge output must be written under an already-ignored path before confirmatory workers start; otherwise `RunResult.git_dirty` would correctly mark the release dirty merely because the result directory is untracked. The existing `benchmark/challenge/v1/scratch/` boundary is suitable.
- The final configuration needs its own tracked `v1-confirmatory.toml`; the current file is explicitly labelled a calibration configuration even though its 53 x 64 construction budget is the frozen study budget.
- RNG pairing will mean identical puzzle, solver configuration, global seed, and run seed. It is not a common-random-number design after the intervention: full feedback executes stochastic edge updates while the frozen condition does not, so subsequent RNG consumption may diverge. This is part of the defined algorithmic intervention and must be disclosed.
- A valid raw result needs enough information for later independent checks: complete 150 x 30 x 2 pairing, condition/freeze flag, family/size stratum, config hash, Git SHA/dirty flag, solve outcome, path budget/use, iteration/time/fitness, and the returned solution path (or an equally auditable encoding).
- The pre-commit release audit shows only the intended protocol/config/runner/analysis/tests/docs/planning files as non-ignored changes. The seed and smoke output remain ignored, and `benchmark/challenge/v1/sealed/` is still absent.

## Confirmatory Result
- The exact pre-test release is commit `06ef8bbfae5de29fe6cd4ebf0175a94f04880e9b`, tagged `challenge-v1-confirmatory-v1`. Immediately before unlock it was clean, passed 46 tests and Ruff, had zero Pyright errors, and reverified the sealed lock in memory.
- The test was opened once through the acknowledged guard. The unlocked corpus and certificates matched commitments `3ee36892...b0b0fa4` and `5cbfd756...0dc293`; no generator/config/analysis changes occurred between tag, unlock, run, and analysis.
- The complete 9,000-row grid ran in 145.0 seconds on an AMD Ryzen 9 9950X3D (32 logical CPUs) with zero failed/infeasible/dirty rows. Raw result SHA-256 is `a899646ef363ad2fd295e704b35f73b22efeb08ad10ebd5dc6429e1d32b1976a`.
- Full feedback solved 2,039/4,500 trials (0.4531); frozen feedback solved 1,981/4,500 (0.4402).
- The frozen primary estimate is `Delta=0.0128889` (full minus frozen), with 95% stratified puzzle-bootstrap interval `[-0.0004444, 0.0264444]`. Because the entire interval lies within `[-0.05, +0.05]`, the predeclared classification is **practically equivalent**.
- All 4,020 solved rows retained their paths and passed independent Hamiltonian coverage, endpoint, waypoint-order, adjacency, and wall validation.
- Heterogeneity is descriptive rather than confirmatory: 57 puzzles favored full, 45 favored frozen, and 48 tied. Stratum deltas were +0.0089 (chambered/N12), +0.0300 (open/N14), -0.0167 (open/N16), +0.0278 (sparse/N12), and +0.0144 (sparse/N14).
- The honest paper result is therefore stronger as a negative mechanism finding: under the frozen budget and Challenge v1 distribution, edge feedback did not provide a practically meaningful overall improvement over the identical constraint-aware constructor with feedback frozen.
- Visual QA confirms that the primary equivalence-band/interval plot and per-puzzle heterogeneity plot communicate the predeclared result without turning descriptive stratum variation into confirmatory inference. The first primary SVG canvas clipped its right-hand numeric labels, so the final canvas was widened before manuscript use.

## Manuscript Source Audit
- Firecrawl CLI v1.15.2 is authenticated with two-way concurrency and 901 credits available. Eleven prior search caches already cover discrete/binary SMA, combinatorial SMA, routing, graph optimization, SMA/ACO hybrids, reviews, and venue scope, so new searches should target only missing primary sources rather than duplicate broad queries.
- `.firecrawl/` was initially unignored and contains research caches rather than publication artifacts; it is now excluded by `.gitignore` before the manuscript release.
- Existing search caches identify usable primary-source leads but contain truncated publisher URLs in several records. Confirmed leads include Zhang et al.'s 2023 PLOS ONE/PubMed CVRP study, an Elsevier binary SMA paper, a Springer binary SMA paper, and graph-oriented Physarum/slime-mould optimization work. Exact DOI/title/author metadata must be resolved through targeted DOI/publisher searches before entering BibTeX.
- Broad cache results are noisy and dominated by later hybrid/improved variants and ResearchGate mirrors. The manuscript should cite a compact chain of original/primary works rather than imply a systematic review: original SMA, representative binary/discrete SMA, representative combinatorial routing SMA, Physarum network optimization, SMA/ACO hybrid precedent, grid-graph Hamiltonicity, and ACO.
- Targeted publisher searches verify Itai, Papadimitriou, and Szwarcfiter's *Hamilton Paths in Grid Graphs* at SIAM DOI `10.1137/0211056` and Tero et al.'s *Rules for Biologically Inspired Adaptive Network Design* at Science DOI `10.1126/science.1177894`.
- The original SMA and binary-SMA searches reached the correct Elsevier/institutional records, but the cached search representation truncates their URLs. Their exact DOI/authors/pages will be taken from scraped primary or institutional metadata rather than guessed from the truncated strings.
- Elsevier metadata verifies Li, Chen, Wang, Heidari, and Mirjalili, *Slime mould algorithm: A new method for stochastic optimization*, Future Generation Computer Systems 111 (2020), 300–323, DOI `10.1016/j.future.2020.03.055`. The paper introduces continuous SMA with adaptive positive/negative weights; ZipMould must be described as inspired by, not a direct discrete transcription of, that method.
- Torrens University's publication record verifies Abdel-Basset, Mohamed, Chakrabortty, Ryan, and Mirjalili, *An efficient binary slime mould algorithm integrated with a novel attacking-feeding strategy for feature selection*, Computers & Industrial Engineering 153 (2021), 107078, DOI `10.1016/j.cie.2020.107078`. This directly rules out any “first binary/discrete SMA” claim.
- The SIAM record confirms the grid-graph paper's venue details: SIAM Journal on Computing 11(4), 676–686 (1982), DOI `10.1137/0211056`, by Alon Itai, Christos H. Papadimitriou, and Jayme Luiz Szwarcfiter.
- The PLOS ONE primary record verifies Zhang, Liu, and Bai, *Improved slime mould algorithm based on hybrid strategy optimization of Cauchy mutation and simulated annealing*, PLOS ONE 18(1):e0280512 (2023), DOI `10.1371/journal.pone.0280512`. It explicitly evaluates both standard/improved SMA on CVRP and describes discrete-solving ability, so “first SMA applied to a discrete routing problem” is untenable.
- The DOI-resolved hybrid precedent is Rong et al.'s *A Slime Mold Fractional-Order Ant Colony Optimization Algorithm for Travelling Salesman Problems*, in LNCS 12689 (2021), pp. 322--332, DOI `10.1007/978-3-030-78743-1_29`.

## Frozen Claim
- **Contribution claim:** ZipMould introduces and openly evaluates an edge-state, rank-weighted feedback operator for stochastic construction of ordered Hamiltonian grid paths; the contribution is the controlled mechanism study and reproducible benchmark, not an a priori assertion of superiority.
- **Primary research question:** Under a matched path-construction budget on procedurally generated hard instances, how does adding the edge-feedback operator change per-puzzle probability of solution relative to the identical tuned constructor with feedback frozen?
- **Outcome-invariant interpretation:** The paper will report where feedback helps, is neutral, or hurts. The legacy 245-puzzle corpus is explicitly a ceiling-regime result in which no incremental feedback benefit was detected.
- **Primary estimand:** Puzzle-clustered mean difference in solve probability within a fixed construction budget, full feedback minus frozen feedback, with seeds nested within puzzle.
- **Confirmatory discipline:** All model/config choices and analysis code are frozen using train/dev only; the new test seed and instances remain sealed until a deliberate final analysis release.
- The durable claim artifact is now `paper/CLAIM.md`. It fixes a 3,392-path budget, 30 seeds, puzzle-clustered solve-rate difference, stratified cluster bootstrap, and a five-percentage-point practical-effect band while making every possible outcome reportable.

## Challenge v1 Design Decisions
- The paper title/claim direction is “When does edge feedback help?” rather than “ZipMould outperforms baselines.” This remains truthful for a positive, null, or negative sealed-test effect.
- Every generated puzzle carries a planted Hamiltonian certificate. Walls are sampled only outside certificate edges, and waypoint order is derived from the certificate, so solvability does not depend on a solver result.
- Three generator families supply five calibrated `(family, size)` strata across 12x12, 14x14, and 16x16 grids. Counts are 200 train, 100 dev, and 150 sealed test, balanced at 40/20/30 puzzles per stratum.
- A custom SplitMix64 generator and hash-derived per-instance seeds make instances stable across Python processes and independent of generation order.
- The tracked lock will reveal only public distribution counts and SHA-256 commitments to the secret seed, canonical corpus, hidden certificates, and exact spec.
- Calibration is allowed to target a non-ceiling feedback-frozen dev solve rate of 0.15–0.85. Generator settings may not be chosen based on whether full feedback beats frozen feedback.
- The initial 200-iteration frozen dev probe achieved an informative overall rate (84/320 = 0.2625) but exposed eight uninformative family/size cells at exactly 0% or 100%. The benchmark will not hide those strata inside a good overall average: a 64-iteration calibration budget is being probed, and the final public spec will enumerate only dev-informative strata.
- The final selected-strata calibration uses 100 fresh dev puzzles x 5 seeds at 3,392 constructed paths. Frozen feedback solved 229/500 (0.458); all five strata lie in the predeclared 0.15–0.85 interval (0.39, 0.74, 0.23, 0.78, 0.15). No full-feedback outcomes were evaluated during selection.
- The final public train/dev corpus contains 300 puzzles and has canonical SHA-256 `229e6dca5b52cec2594fcbc5d8ddf6ca0ae1883c6eef21e9f9e735c74c803e44`. Every puzzle has been independently checked against its planted certificate and the solver feasibility precheck.
- The sealed 150-puzzle test corpus is committed at canonical SHA-256 `3ee368923fa0ae785a7591994b5e1e5fa052d2a8f98113ddf7ed3ac8bb0b0fa4`. In-memory regeneration verifies the commitment; no test material has been written and the unlock directory is absent.

## Audit Criteria
- Clear research question and scoped contribution
- Adequate engagement with related work and a defensible novelty statement
- Methods detailed enough to reproduce
- Appropriate baselines, controls, replication, uncertainty, and statistical treatment
- Results that directly support the stated claims
- Limitations and threats to validity
- Accessible code, dependency/environment metadata, data/provenance, and run instructions
- Manuscript completeness, figure/table quality, citations, and venue fit

## Research Findings
- The repository contains a solver implementation, four baseline implementations, staged experiment scripts/manifests, benchmark data and splits, current and superseded Stage 4 outputs, automated tests, a web visualizer, deployment assets, and one Portuguese Marp presentation.
- No journal manuscript source, abstract, conventional paper sections, bibliography file, or manuscript-oriented figures/tables are present in the inventory. The presentation is therefore the closest current statement of the scientific argument, not a submission-ready paper.
- The README defines the target as an ordered-waypoint Hamiltonian path on a grid with walls, and describes ZipMould as inspired by Li et al.'s continuous Slime Mould Algorithm.
- Pre-existing uncommitted changes affect `presentations/zipmould.md` and its generated PDF; these are evidence under review and must not be overwritten.
- The implementation/reproducibility surface is substantial enough to merit a full scientific audit: `src/zipmould`, `configs`, `benchmark`, `experiments/stage1`, `stage2`, `stage4`, and tests.
- The presentation states a concrete algorithmic contribution: replace continuous SMA position vectors with edge pheromone; use deterministic bounded `v_b`, linear rank-signed deposits, `v_c` decay, and a pheromone-noise zeta branch. This is substantially hybridized with ACO and differs materially from Li et al.'s update rule.
- The presentation states three hypotheses and a train/dev/test protocol, but contains no results section. Its narrative goes directly from protocol to a live demo.
- Current Stage 4 reports cover 37 held-out puzzles and 30 seeds per condition (1,110 trials each). `tuned-winner` solved all 1,110 runs; backtracking solved 1,080/1,110; heuristic-only 414/1,110; ACO 73/1,110.
- At the puzzle-level aggregation used by the report, tuned-winner solved 37/37 and backtracking 36/37. Their paired comparison is explicitly non-significant (`b=1`, `c=0`), with a bootstrap 95% interval for the solve-count difference of [0, 3]. The defensible claim is parity/a small observed edge over the strongest baseline, not statistical superiority.
- Tuned-winner beats the weaker ACO and heuristic-only baselines on puzzle-level McNemar comparisons, according to the report. Those comparisons do not isolate which ZipMould mechanism causes the gain.
- The reported efficiency comparison has 1,080 paired solved trials and negative candidate-minus-backtracking quartiles for both iterations and wall time, but interpretation requires checking the analysis code and whether iteration counts are comparable across unlike algorithms.
- The presentation calls the hypotheses/protocol “pre-registered,” but repository evidence alone does not establish a public, immutable, time-stamped preregistration. That terminology should not appear in a paper unless external evidence exists.
- Both `experiments/stage4/out_pre_endpoint_fix` and `experiments/stage4/out` exist. This suggests the held-out test was recomputed after a code correction, so the paper must disclose the correction and avoid the unqualified claim that test results were computed only once.
- The Stage 4 manifest actually compares only one tuned ZipMould configuration against three baselines. It does not run the presentation's “4 conditions x 4 baselines” test matrix, and the analysis code performs no Benjamini-Hochberg/FDR correction. The presentation's stated protocol is inconsistent with the executed Stage 4 analysis.
- The “McNemar” implementation first collapses 30 seeds to `solved_any` per puzzle, then applies a custom normal-approximation decision rule to only 37 pairs. It does not report an exact McNemar p-value or effect-size interval. Aggregating by “any seed solved” can make stochastic solvers look better as seed count increases and obscures reliability; the 30-seed rates should be analyzed directly with puzzle-aware repeated-measures methods or a clearly justified per-puzzle estimand.
- `experiments/stage4/out/results.parquet` and `aggregate.parquet` exist locally but are ignored/untracked; only three derived JSON reports in the current output directory are versioned. A clean clone therefore lacks the raw current Stage 4 result table needed to regenerate those reports.
- Analysis docstrings cite `docs/design.md` sections for the pre-specified decision rule, but that file is absent from the repository inventory. The claim of preregistration is unsupported and the analysis specification is not self-contained.
- Current Stage 4 trace artifacts are also untracked; only traces and raw Parquet outputs under the explicitly superseded `out_pre_endpoint_fix` directory are versioned.
- Stage 1 runs the four ZipMould variants plus four baselines on the dev split, but its analysis only compares each variant against each baseline. It never performs the factorial contrasts needed for hypotheses 1 (signed vs positive) and 2 (stratified vs unified), despite the presentation describing those hypotheses.
- Stage 1 also lacks any implemented FDR correction. Thus neither the claimed correction nor the two design-factor hypothesis tests are present in code.
- Stage 2 tunes all four variants on train and re-evaluates on dev. All tuned variants hit a ceiling (370/370 for both unified variants; 369/370 for both stratified variants), so the dev data provide virtually no discrimination among mechanisms.
- The selected winner (`zipmould-uni-positive`) ties `zipmould-uni-signed` on tuned dev solves and train objective. The tie is broken using median iterations from Stage 1's *default-config* runs, not median iterations of the tuned configurations. This is not a valid efficiency comparison of the actual candidate configurations.
- Only the winner is evaluated on test. Consequently the held-out results cannot support claims about signed feedback or stratification; they only evaluate the selected hybrid as a whole against baselines.
- Stage 1 result tables/traces and all four Optuna study databases exist locally but are ignored/untracked. The two committed Stage 2 JSON summaries are insufficient to independently verify tuning, dev-gate runs, or winner selection from a clean clone.
- The benchmark has 245 puzzles split 171/37/37. Stratification uses source-provided `difficulty` labels and coarse size buckets; no derivation or validation of difficulty is documented.
- `benchmark/data/raw.json` contains game-like level metadata (names, hash codes, play counts, creator fields, creation timestamps), but neither the README nor parser records the dataset source URL, acquisition procedure/date, ownership, permission, citation, or dataset license. The repository's MIT license covers the software package but does not establish redistribution rights for third-party puzzle content.
- The benchmark parser normalizes an already-present `raw.json`; it does not provide a script that acquires the corpus from its original source. This prevents provenance verification and a true data-from-source reproduction.
- The dependency environment is well pinned at the lockfile level (`uv.lock`, Python 3.13 range, bounded dependencies), but the README documents only the visualizer workflow. The Makefile exposes visualizer development tasks, not the scientific experiment pipeline. There is no top-level command or protocol for reproducing Stage 1–4 and regenerating tables.
- Difficulty-stratified random splitting of levels from one corpus is reasonable for within-corpus evaluation, but the current evidence supports only that distribution. It does not establish generalization to other Zip implementations, procedurally generated puzzles, or unseen puzzle families.
- Resource budgets are not matched across conditions. The tuned winner uses population 53 x up to 200 iterations (10,600 path constructions); ACO and heuristic-only use population 30 x 200 (6,000); backtracking is deterministic and is redundantly rerun for all 30 “seeds.” The backtracking implementation ignores its configured `iter_cap=1` and uses only a 300-second deadline.
- The extended report's cross-algorithm “iterations” comparison is not scientifically interpretable: a ZipMould/ACO iteration is a whole population of path constructions, while a backtracking iteration is one DFS loop/node-processing step. It should be removed or replaced with matched wall-clock/evaluation-budget metrics.
- Wall-time comparisons also mix a Numba-compiled population kernel, a Python-loop ACO wrapper with Numba subroutines, and pure-Python DFS. They can describe these implementations on documented hardware after warm-up, but cannot by themselves support algorithmic efficiency claims.
- The tuned ZipMould candidate received 50-trial hyperparameter optimization per variant. The ACO baseline uses fixed, undocumented choices (`rho=0.1`, `Q=1`) and no comparable tuning. Moreover, ACO deposits unnormalized raw fitness into unbounded positive pheromone while the candidate uses clipped rank weights; this can saturate the shared softmax and is not evidence against a well-configured ACO.
- The heuristic-only baseline is useful and shares the candidate's construction heuristic, but weaker ACO/random baselines do not establish state-of-the-art performance. The strongest comparator is a custom naive DFS, not a recognized exact solver or a competitive Hamiltonian-path/constraint-programming formulation.
- The selected candidate is the *positive*, unified variant. Thus its successful configuration excludes the signed negative feedback presented as the closest SMA analogue. Any paper must confront the possibility that performance comes from the ACO-style construction heuristics and tuning rather than a distinctive slime-mould mechanism.
- Every current Stage 4 row records `git_dirty=true` and commit `c5b6f7d...`, which is older than the current repository HEAD. The precise uncommitted source state used to generate the result table is therefore not reconstructible from Git. The superseded run likewise records a different older commit with `git_dirty=true`.
- Current Stage 4 wall-time medians are approximately 1.59 ms (winner), 31.5 ms (backtracking), 108.9 ms (heuristic-only), and 166.0 ms (ACO), but these are implementation timings without documented hardware or benchmark isolation. Backtracking reaches its 300-second cap on the unsolved puzzle.
- The winner solves 781/1,110 runs (70.4%) in iteration 1, before any learned pheromone can affect construction because initial `tau_0=0`. The other 329 runs may benefit from subsequent feedback. This makes a same-config, feedback-frozen ablation essential to attribute success to the proposed update rather than tuned heuristics and a larger population.
- A post-hoc diagnostic performed during this audit used the *same tuned winner configuration* (including population 53, tuned heuristic weights, and 200 iterations) but invoked the existing heuristic-only path with `alpha=0` and frozen pheromone. It also solved 1,110/1,110 test runs, with every puzzle at a 100% seed solve rate and median 1 iteration. This is not a pre-specified confirmatory result, but it demonstrates that the current success endpoint provides no evidence that pheromone feedback—or any SMA-derived update—is necessary.
- The central performance framing is therefore not currently supported. The repository establishes that a tuned stochastic heuristic constructor solves this corpus extremely well; it does not establish added value from the proposed slime-mould dynamics.
- Initial current-literature search finds an established body of improved/hybrid SMA papers and prior slime-mould graph-optimization work. A novelty claim cannot rest on “first discrete/graph adaptation” without a much tighter systematic comparison. Specific primary sources still require verification.
- Targeted literature search surfaced a 2023 PLOS ONE primary paper on an improved SMA applied beyond continuous benchmarks to a capacitated routing problem, plus references to slime-mould/ant-colony fusion and discrete graph-optimization work. This makes “SMA adapted to a combinatorial graph domain” too broad a novelty claim; the defensible novelty would need to be the precise edge-memory/rank-update construction for ordered Hamiltonian paths and must be compared against those predecessors.
- Verified primary/indexed precedents include Zhang et al. (2023), DOI `10.1371/journal.pone.0280512`, which evaluates an improved SMA on the capacitated vehicle-routing problem, and an ACM-indexed chapter titled “A Slime Mold Fractional-Order Ant Colony Optimization ...” (DOI `10.1007/978-3-030-78743-1_29`). At minimum, the paper needs to explain how ZipMould differs from existing SMA-to-routing and slime-mould/ACO hybrids.
- A broad algorithms journal is topically compatible with combinatorial optimization, but scope fit does not cure the causal-evidence and manuscript gaps. Venue breadth is not a substitute for demonstrating what the proposed mechanism adds.
- JOSS is not a shortcut for the current results paper. Its current official criteria require an obvious research application, sufficient public development history, demonstrated research use/impact, installability/testing/documentation, and explicitly say the JOSS paper must not focus on new research results. ZipMould could become a software-paper candidate only after a research-use story and stronger user documentation; the present algorithmic claim belongs in a conventional study.
- Review-oriented literature search also surfaces prior binary SMA variants and a large improvement/hybridization literature. The related-work burden is therefore broader than the six references in the presentation: continuous SMA variants, binary/discrete SMA, Physarum graph algorithms, ACO hybrids, Hamiltonian-path/constraint solvers, and puzzle-solving benchmarks all need coverage.
- Official publisher search results verify at least two binary/discrete SMA papers, including “An efficient binary slime mould algorithm ...” (Elsevier) and “A Novel Binary Slime Mould Algorithm with AU Strategy ...” (Springer). ZipMould may still be novel for ordered Hamiltonian paths and edge-level state, but it is not the first discrete SMA.
- The Python test suite passes (35 tests), and Pyright reports 0 errors/9 dependency-typing warnings. Ruff fails on two minor test-style findings, so the repository is close to clean but not fully green.
- Test coverage is strongly weighted toward the visualizer. Only one test exercises solver state construction; there are no direct tests for solver validity across puzzles, pheromone updates, baselines, feasibility/fitness, experiment dispatch, result aggregation, McNemar calculations, or winner selection. Passing tests therefore do not validate the scientific pipeline.
- Frontend unit verification also passes (13 files, 65 tests), supporting the visualizer's engineering quality.
- Given the untracked local current `results.parquet`, the Stage 4 primary and extended analyses run successfully in an isolated temporary directory. Regenerated `report.json` and `extended_report.json` are byte-identical to the repository copies, and the aggregate Parquet tables are equal (148 rows). The downstream analysis is reproducible *from the local raw table*; the missing clean-clone raw table and dirty source provenance remain the blockers.
- An independent path validator reran the tuned candidate at seed 0 on all 37 test puzzles and confirmed 37/37 solutions cover every free cell exactly once, respect adjacency/walls and waypoint order, and start/end correctly. This supports implementation correctness for that sample, though it does not replace systematic solver tests.
- The code does not implement the presentation's description of the `positive` condition as “only the upper half deposits.” `_pheromone_update` always includes negative rank weights from the lower half; `tau_signed=false` merely clips the resulting pheromone at zero instead of allowing negative pheromone. Both conditions therefore contain subtractive lower-ranked deposits, and the factor isolates pheromone sign support, not the presence/absence of negative feedback.
- The tuned winner's `z=0.3879` is applied independently to every pheromone edge on every update, replacing that edge with Gaussian noise. This is qualitatively and quantitatively different from Li et al.'s approximately 0.03 per-agent random-restart branch. The manuscript must describe it as a new edge-noise operator and validate it directly, not imply a near-transcription of SMA.
- Exact primary metadata for the core related-work set is now verified: Li et al., *Future Generation Computer Systems* 111 (2020), 300--323, DOI `10.1016/j.future.2020.03.055`; Abdel-Basset et al., *Computers & Industrial Engineering* 153 (2021), 107078, DOI `10.1016/j.cie.2020.107078`; Itai et al., *SIAM Journal on Computing* 11(4) (1982), 676--686, DOI `10.1137/0211056`; and Zhang et al., *PLOS ONE* 18(1) (2023), e0280512, DOI `10.1371/journal.pone.0280512`.
- The biological/network and inferential foundations are likewise exact: Tero et al., *Science* 327(5964) (2010), 439--442, DOI `10.1126/science.1177894`; Dorigo et al., *IEEE Transactions on Systems, Man, and Cybernetics, Part B* 26(1) (1996), 29--41, DOI `10.1109/3477.484436`; Efron, *Annals of Statistics* 7(1) (1979), 1--26, DOI `10.1214/aos/1176344552`; and Lakens, *Social Psychological and Personality Science* 8(4) (2017), 355--362, DOI `10.1177/1948550617697177`.
- The confirmatory rule should be called a predeclared practical-equivalence classification, not a formal TOST procedure: the 95% cluster-bootstrap interval is compared directly with the fixed +/-5 percentage-point band. Lakens is useful for the conceptual distinction between absence of evidence and evidence bounded within a smallest effect of interest, but does not turn this custom interval rule into TOST.
- Publisher metadata verifies Rong et al. (2021), “A Slime Mold Fractional-Order Ant Colony Optimization Algorithm for Travelling Salesman Problems,” in *Advances in Swarm Intelligence*, LNCS 12689, pp. 322--332, DOI `10.1007/978-3-030-78743-1_29`. Its explicit SMA/ACO/TSP synthesis rules out broad claims of first slime-mould/ant-style combinatorial construction.
- Rong et al.'s references identify still earlier direct graph precedents: Zhang et al. (2016), “Slime mould inspired applications on graph-optimization problems,” pp. 519--562, DOI `10.1007/978-3-319-26662-6_26`; Liang et al. (2017), Physarum-inspired ACO for community mining, pp. 737--749, DOI `10.1007/978-3-319-57454-7_57`; and Qian et al. (2013), an ant colony system based on the Physarum network, pp. 297--305, DOI `10.1007/978-3-642-38703-6_35`. A representative subset is sufficient for the manuscript, provided the novelty language stays domain- and mechanism-specific.
- Exact implementation inspection fixes the method description. At each step the constructor excludes visited cells, walls, out-of-order waypoints, and choices that disconnect the remaining unvisited subgraph. A legal edge receives logit `alpha*tau + beta*log(eta)`, where `eta` is a product of softplus-transformed Manhattan, Warnsdorff/onward-degree, residual-connectivity, and checkerboard-parity terms raised to their configured exponents; the next edge is sampled by softmax.
- Each iteration independently rebuilds 53 paths. Walkers are ranked by fitness and receive symmetric linear weights `w_r=(n-2r+1)/(n-1)`, from +1 for the best to -1 for the worst. Their traversed-edge weights are summed, then edge state is updated as `tau <- v_c*tau + v_b*deposit`, with `v_b=tanh(1-t/T)` and `v_c=1-t/T`; each edge is independently replaced by `Normal(0,tau_max/4)` with probability `z`, then clipped to `[0,tau_max]` in the frozen nonnegative configuration.
- The feedback-frozen arm skips the entire edge-state update. Because `tau_0=0`, its pheromone term stays exactly zero while every legality rule, heuristic, configuration value, population, iteration cap, puzzle, and initial seed remains unchanged. The intervention therefore isolates the implemented update as a package, including rank deposition, decay, and edge noise.
- Challenge v1 starts from a deterministic serpentine Hamiltonian certificate, applies `12*N^2` endpoint backbite moves, chooses sparse ordered waypoints whose long certificate gaps have geometrically close endpoints, and places walls only on noncertificate edges. Open, sparse-wall, and chambered-wall families therefore remain guaranteed solvable; five family/size strata were selected using only frozen-arm dev difficulty.
- No TeX engine or Inkscape executable is installed, but Typst 0.14.2 is available. The journal-neutral Typst source compiles cleanly to a visually audited nine-page PDF with native SVG figures and a standard BibTeX database; venue-template conversion remains venue-dependent.

## Technical Decisions
| Decision | Rationale |
|----------|-----------|
| Treat build success as necessary but not sufficient | Executable artifacts do not by themselves establish scientific validity or novelty. |

## Updated Publication Verdict After Confirmatory Study
- The earlier “not submission-ready” verdict below is superseded. The causal evidence gap, ceiling benchmark, missing raw data, dirty-run provenance, absent manuscript, and missing reproduction path were addressed in Phases 6--15.
- The repository now contains a defensible journal-neutral research manuscript and complete reproducibility package. The claim is a controlled negative mechanism result, not algorithmic superiority: +1.29 percentage points with 95% interval [-0.04,+2.64], classified practically equivalent inside the predeclared +/-5-point band.
- A fresh no-local clone can install the exact locked environment offline, regenerate the paper, restore only checksum-matching released test material, revalidate 4,020 paths, reproduce every derived artifact byte for byte, and remain Git-clean.
- The work is ready for author/venue adaptation. It is not literally uploadable until the authors choose a journal, supply identity and legal declarations, select data/code licenses, create a durable archive DOI, and apply the venue's current template and portal requirements.

## Initial Publication Verdict (superseded after Phases 6--15)
- **Not submission-ready as a research paper, even for a small reputable journal.** This is not mainly a writing problem: the current benchmark and ablations do not support the SMA-specific performance claim.
- **Promising paper foundation:** the implementation, corpus, experiment scaffolding, visualizer, and initial replicated runs are substantial. With major experimental redevelopment and a manuscript, a modest applied algorithms/optimization venue is plausible.
- The most defensible current result is a negative/mechanistic one: on this corpus and tuned configuration, feedback-free construction matches the full method at 100% success. A paper can either embrace that result or obtain new evidence on harder data that the feedback operator adds value.
- The adaptation may still be technically novel in its precise edge-state update for ordered Hamiltonian paths, but novelty is not yet established against binary/discrete SMA, routing applications, Physarum graph methods, and slime-mould/ACO hybrids.

## Required Development Before Submission (priority order)
1. **Choose and freeze the claim.** Either (a) a mechanism paper showing an incremental benefit from edge-level SMA feedback, or (b) an honest empirical/solver paper centered on the constraint-aware stochastic constructor and the finding that SMA feedback was unnecessary on the original corpus.
2. **Replace the ceiling evaluation.** Build or acquire harder, provenance-cleared instances; include procedural and/or external puzzle families; separate by generator/family where possible; and lock a genuinely new confirmatory test set because the existing test has been repeatedly inspected and post-hoc analyzed.
3. **Run causal, fair ablations.** At minimum compare the full candidate with the same tuned configuration under frozen pheromone, `z=0`, no rank-sign term, constant decay, true positive-only deposits, and matched unified/stratified variants. Give competitive ACO and exact/constraint baselines comparable tuning and compute budgets.
4. **Use defensible endpoints and statistics.** Pre-specify success-within-budget and time/evaluation profiles; treat puzzle as the independent cluster with seeds nested within puzzle; report effect sizes and uncertainty; use exact paired tests or hierarchical/cluster-aware analyses; correct only the planned family of secondary contrasts.
5. **Make the scientific run reconstructible.** Tag a clean commit; archive raw Stage 1–4 tables, tuning studies, manifests, configs, logs, hardware/software details, checksums, and a one-command pipeline; add core scientific regression tests. Rerun final results from that clean release.
6. **Resolve data provenance.** Document source, acquisition date/method, license/permission, transformations, exclusions, difficulty labels, and redistribution rights. Release a generator or metadata-only retrieval path if raw levels cannot legally be redistributed.
7. **Write the manuscript.** Add abstract, scoped contributions, related work, formal problem/method, actual experimental protocol, results with figures/tables, limitations/threats, data/code availability, and a conclusion that matches the evidence. Remove unsupported “pre-registered,” FDR, positive-only, and one-time-test claims unless they are made true.

## Valuable but Not Submission Blockers
- Further visualizer/deployment polish; those artifacts are already stronger than the scientific narrative requires.
- Broader UI tests and presentation design refinements.
- Additional biological metaphor, unless it yields a testable mechanism; metaphor alone will not strengthen the paper.

## Venue Calibration
- If new experiments demonstrate a mechanism effect under fair budgets, target a conventional applied algorithms, computational intelligence, or metaheuristics journal; the work fits broad combinatorial-optimization scope.
- If the feedback remains unnecessary, a smaller empirical/negative-results or application-oriented venue may still be plausible with the constructor as the contribution and transparent null result.
- A software-paper route such as JOSS is a later option only after documented research use/impact and user-facing research-software documentation; it cannot carry the new algorithm-results claim in its current form.

## Completion Audit
| User requirement | Evidence checked | Determination |
|------------------|------------------|---------------|
| Are the artifacts sufficient for a paper now? | Repository inventory; presentation structure; Stage 1–4 manifests/reports; raw-output tracking; tests; run provenance | No. No manuscript exists, the executed protocol contradicts the stated protocol, and central mechanism attribution fails the same-config ablation. |
| Could the work become publishable in a small journal? | Coherent implemented method; 245-puzzle corpus; functioning experiment pipeline; exact report regeneration; current venue scopes | Yes, conditionally, after major experimental and manuscript redevelopment. |
| Does it need further development? | Causal ablation, baseline fairness, statistics, novelty, data rights, reproducibility, and manuscript audit | Yes. Seven submission-critical workstreams are enumerated in priority order; UI/presentation polish is explicitly noncritical. |
| Is the verdict reproducible from current evidence? | 35 Python tests; 65 frontend tests; independent validation of 37/37 seed-0 solutions; identical regenerated Stage 4 JSON hashes and aggregate table | Engineering/results transformation verified, with explicit caveats that current raw outputs are untracked and final runs came from a dirty source state. |

## Issues Encountered
| Issue | Resolution |
|-------|------------|
| Current scientific narrative omits the results it promises | Use Stage 4 reports as evidence and classify a full Results section as a submission blocker. |
| Executed analysis differs from the presentation's protocol | Treat the reports/code as authoritative and require the manuscript to describe the actual analysis or rerun a corrected pre-specified analysis. |
| Derived reports are versioned without current raw results | Require archival of raw result tables plus checksums/provenance or a deterministic regeneration package. |
| Winner tie-break uses default rather than tuned run timing | Re-evaluate tied tuned configurations under the same protocol or pre-specify a scientifically meaningful tie rule. |
| Dataset provenance and redistribution status are undocumented | Add a data statement with source, license/permission, acquisition, transformations, exclusions, and an alternative release path if redistribution is not permitted. |
| Baseline compute/tuning budgets are unequal | Define a common wall-clock or solution-evaluation budget, tune competitive baselines comparably, and report hardware/warm-up details. |
| Iteration counts are incomparable across algorithms | Do not use raw iteration differences as an efficiency result; report time, evaluations/expanded nodes, and success profiles under matched budgets. |
| Published runs came from dirty, unreconstructible source states | Rerun the final locked analysis from a tagged clean commit/container and archive raw outputs with commit/config/data hashes. |
| Same-config feedback-free diagnostic ties the winner at 100% success | Redesign experiments around harder/non-ceiling instances and direct, equally tuned mechanism ablations; consider an honest negative-result or heuristic-solver framing if no effect emerges. |
| Core scientific logic lacks regression tests | Add golden/fixture tests for valid solutions, mechanism updates, baseline budget semantics, aggregation, exact statistics, and stage selection. |
| “Positive vs signed” factor is misdescribed | Rename/define it as nonnegative-vs-signed pheromone or implement a true positive-only deposit ablation; update hypotheses accordingly. |
| Firecrawl search output appeared after the first immediate file check | Poll/verify output creation before inspecting; the search subsequently completed successfully. |
| Initial generator checks failed on helper naming/style/typing | Renamed the commitment helper, adopted `pairwise`, tightened JSON casts/constants, and reached 5 passing tests, clean targeted Ruff, and zero targeted Pyright errors. |

## Resources
- Local repository: `/home/gtkacz/Codes/slime-mould`
- Primary project overview: `README.md`
- Current scientific narrative: `presentations/zipmould.md`
- Broad literature search cache: `.firecrawl/search-sma-discrete.json`
- Targeted combinatorial-SMA search cache: `.firecrawl/search-sma-combinatorial.json`
- Slime-mould graph search cache: `.firecrawl/search-slime-graph.json`
- SMA vehicle-routing search cache: `.firecrawl/search-sma-vrp.json`
- Slime-mould/ACO hybrid search cache: `.firecrawl/search-slime-aco.json`
- Exact SMFACO search cache: `.firecrawl/search-smfaco-exact.json`
- Official JOSS-criteria search cache: `.firecrawl/search-joss-criteria.json`
- Official Algorithms-scope search cache: `.firecrawl/search-algorithms-scope.json`
- SMA review search cache: `.firecrawl/search-sma-review.json`
- Binary-SMA search cache: `.firecrawl/search-binary-sma.json`
- Binary-SMA DOI search cache: `.firecrawl/search-binary-sma-doi.json`

## Visual/Browser Findings
- Current external literature confirms prior binary/discrete SMA, CVRP use, and slime-mould/ACO hybridization; ZipMould must claim narrower mechanism/domain novelty.
- Current JOSS criteria make it an unsuitable shortcut for a new-results paper and require demonstrated research impact/public development.

---
*Update after every 2 view/browser/search operations.*

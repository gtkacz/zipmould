#set document(
  title: "Does Edge Feedback Help? A Controlled Study of a Slime-Mould–Inspired Constructor for Ordered Hamiltonian Grid Paths",
  author: (
    "Gabriel Mitelman Tkacz",
    "Leandro Augusto da Silva (Supervisor)",
    "Gustavo Scalabrini Sampaio (Supervisor)",
  ),
  keywords: (
    "Hamiltonian path",
    "grid graph",
    "slime mould algorithm",
    "stochastic construction",
    "mechanism ablation",
    "practical equivalence",
  ),
)

#set page(
  paper: "a4",
  margin: (top: 19mm, bottom: 21mm, x: 21mm),
  numbering: "1",
  number-align: center,
)
#set text(font: "Libertinus Serif", size: 10.2pt, lang: "en")
#set par(justify: true, leading: 0.68em)
#set heading(numbering: "1.")
#set table(inset: 4pt, stroke: (x: none, y: 0.35pt + luma(190)))
#show table.cell.where(y: 0): set text(weight: "bold")
#show link: set text(fill: rgb("245a7a"))
#show cite: set text(fill: rgb("245a7a"))
#show raw: set text(font: "Nimbus Mono PS", size: 8.7pt)
#let orcid(id) = link("https://orcid.org/" + id)[
  #box(image("orcid.svg", height: 0.9em))
]

#align(center)[
  #text(size: 17pt, weight: "bold")[Does Edge Feedback Help?]
  #v(2pt)
  #text(size: 13pt, weight: "semibold")[A Controlled Study of a Slime-Mould–Inspired Constructor for Ordered Hamiltonian Grid Paths]
  #v(9pt)
  #text(size: 10pt)[Gabriel Mitelman Tkacz#super("1") #orcid("0009-0004-3619-4561")]
  #v(2pt)
  #text(size: 9pt)[
    Leandro Augusto da Silva#super("2") #orcid("0000-0002-8671-3102"), Gustavo Scalabrini Sampaio#super("2") #orcid("0000-0003-1150-5584")
  ]
  #v(3pt)
  #text(size: 8pt)[#super("1") School of Engineering, Mackenzie Presbyterian University, São Paulo, SP, Brazil]
  #v(1pt)
  #text(size: 8pt)[#super("2") Faculty of Computing and Informatics, Mackenzie Presbyterian University, São Paulo, SP, Brazil]
]

#v(8pt)
#block(fill: luma(246), inset: 10pt, radius: 2pt)[
  *Abstract.* Bio-inspired metaheuristics often combine a constructive search policy with a shared adaptive state, making it difficult to identify which component produces observed performance. We study this question for ZipMould, a stochastic constructor for ordered Hamiltonian paths on square grid graphs. Its constraint-aware policy combines waypoint legality, residual-connectivity pruning, onward degree, Manhattan proximity, and checkerboard parity with a nonnegative edge state updated from rank-weighted populations. We compare the complete algorithm with the identical constructor under a single intervention: the edge-state update is frozen at its zero initialization.

  To avoid the ceiling found in a legacy 245-puzzle corpus, we introduce Challenge v1, a deterministic, guaranteed-solvable benchmark with planted Hamiltonian certificates, deceptive ordered waypoints, and open, sparse-wall, and chambered instances. Generator strata were selected using only feedback-frozen train/development performance. Before opening a cryptographically committed 150-puzzle test set, we froze the configuration, 30 paired seeds per puzzle, a budget of 3,392 constructed paths per run, the analysis code, and a practical-effect band of ±5 percentage points.

  Full feedback solved 2,039 of 4,500 per-condition runs (45.31%); frozen feedback solved 1,981 of 4,500 (44.02%). The puzzle-clustered mean difference was +1.29 percentage points, with a predeclared 95% stratified puzzle-bootstrap interval of [−0.04, +2.64] points; the estimate leans toward feedback and 97% of bootstrap replicates are positive, but the interval nearly touches zero, so any benefit is small and statistically borderline. Because the complete interval lies inside the practical-effect band, the predeclared outcome is practically equivalent. We read the estimate and interval rather than the label alone: the result does not show that feedback is universally useless, nor that it is exactly inert, but that this implemented edge-feedback package produced no practically important average improvement (below the ±5-point band) under the frozen benchmark, configuration, and budget. The study contributes a mechanism-isolating design, a leakage-controlled benchmark, and a reproducible near-null result.
]

#text(size: 9pt)[*Keywords:* ordered Hamiltonian path; grid graph; slime mould algorithm; stochastic construction; mechanism ablation; practical equivalence]

= Introduction

Adaptive population metaheuristics are frequently evaluated as indivisible algorithms. A method may combine a strong constructive policy, feasibility filters, tuned domain heuristics, population sampling, and a shared memory update, yet performance is attributed to the bio-inspired update as a whole. This makes a basic causal question surprisingly hard to answer: does the adaptive state improve the probability of solving the target problem, or does the constructor already do the work?

This question matters for slime-mould–inspired optimization. Biological _Physarum_ networks adapt their transport structure in response to flow and resource conditions @tero2010network. The continuous Slime Mould Algorithm (SMA) translated related ideas into an adaptive stochastic optimizer with time-varying positive and negative weights @li2020sma. Subsequent work extended SMA to binary feature selection @abdelbasset2021binary, vehicle routing @zhang2023cvrp, graph problems @zhang2016graph, and hybrids with ant-colony search @rong2021smfaco. Consequently, the scientific value of another discrete adaptation cannot rest on the biological metaphor or on a broad claim of being the first combinatorial SMA. It must identify the implemented mechanism and test what that mechanism adds.

We examine ZipMould, a stochastic constructor for an ordered Hamiltonian grid-path problem. A population of walkers builds self-avoiding paths using hard waypoint and residual-connectivity constraints plus four local heuristics. Between iterations, paths deposit signed rank weights on edges; the resulting edge state decays, receives stochastic edge replacement, and is clipped to a nonnegative range. The central experiment disables that update while holding the constructor and its complete configuration fixed. Because the initial edge state is zero, the comparison asks specifically whether the implemented feedback package changes solve probability.

An earlier 245-puzzle corpus could not answer this question: the tuned full constructor and a same-configuration frozen diagnostic both solved all 1,110 test trials. We therefore treat that corpus as a ceiling diagnostic, not as evidence for feedback. Challenge v1 was built before the confirmatory comparison to obtain nontrivial success rates without selecting instances on a favorable treatment contrast. Its test seed and canonical corpus were cryptographically committed while hidden; code, configuration, paired seed schedule, estimand, bootstrap, and decision rule were frozen at a clean tagged commit before a single acknowledged unlock.

The paper makes three contributions:

+ It gives an implementation-faithful description of an edge-state, rank-weighted stochastic constructor for ordered Hamiltonian grid paths and isolates the complete edge-feedback update with a matched frozen-state intervention.
+ It introduces Challenge v1, a synthetic and redistribution-safe benchmark with planted solution certificates, public train/development splits, a committed held-out test split, and explicit leakage controls.
+ It reports the confirmatory result whether favorable or not. Under 150 puzzles, 30 paired seeds, and 3,392 constructed paths per run, feedback changed average solve probability by +1.29 percentage points (95% interval [−0.04, +2.64]), a small, statistically borderline positive estimate that is practically equivalent under the predeclared ±5-point band.

The claim is deliberately narrow. We do not claim state-of-the-art solver performance, formal equivalence for every instance family, or that edge feedback cannot help under other configurations or budgets. The contribution is the controlled evidence about this mechanism in the frozen study.

= Related work

== Slime-mould optimization and discrete adaptations

SMA was introduced as a continuous stochastic optimizer whose population weights and control parameters change over time @li2020sma. ZipMould is inspired by this adaptive-feedback vocabulary, but it is not a direct transcription: its state belongs to graph edges rather than agents or continuous decision coordinates, and its high-probability random operator replaces individual edge values. This distinction is important because superficial reuse of a metaphor can conceal a materially different algorithm.

Discrete SMA predates this work. Abdel-Basset et al. proposed a binary SMA for feature selection @abdelbasset2021binary. Zhang et al. applied an improved hybrid SMA to the capacitated vehicle-routing problem @zhang2023cvrp. Earlier Physarum-inspired research addressed graph-optimization problems directly @zhang2016graph. Hybrids also connect Physarum or slime-mould models with ant-colony optimization: Liang et al. used a Physarum-inspired ACO for community mining @liang2017physarumaco, while Rong et al. combined a slime-mould model, fractional-order memory, and ACO for the travelling-salesman problem @rong2021smfaco. ZipMould's potential novelty is therefore limited to its precise edge-memory construction and its use for ordered Hamiltonian grid paths, not discrete or graph-based SMA in general.

== Hamiltonian grid paths and constructive memory

Hamiltonian paths in grid graphs are computationally difficult in general; Itai, Papadimitriou, and Szwarcfiter established NP-completeness for relevant grid-graph variants @itai1982grid. The ordered-waypoint requirement studied here adds precedence constraints: designated vertices must appear in a fixed sequence along a path that visits every free vertex once. The present work evaluates a stochastic heuristic and does not propose a new complexity result or exact algorithm.

The edge-state sampling rule is also close in spirit to ant-colony optimization (ACO), where construction probabilities depend on shared pheromone and heuristic desirability. The Ant System of Dorigo, Maniezzo, and Colorni is the canonical example @dorigo1996antsystem. ZipMould differs in its constraint-specific policy, symmetric rank deposits, time-dependent update coefficients, and per-edge replacement noise. We therefore use “slime-mould–inspired” as design provenance, while recognizing ACO as a neighboring algorithmic family.

== Practical equivalence and clustered uncertainty

A non-significant difference does not establish that two methods are meaningfully alike. Equivalence analysis instead requires a smallest effect of interest and evidence that the plausible effect is contained within it @lakens2017equivalence. Our frozen rule is not a formal two-one-sided-test procedure. It is a predeclared practical-equivalence classification: a puzzle-cluster bootstrap interval is compared directly with a ±5 percentage-point band. A reader who prefers a size-controlled equivalence test can apply two one-sided tests to the same interval; we report the interval itself so that this remains possible. Bootstrap resampling follows the general nonparametric principle introduced by Efron @efron1979bootstrap, with puzzles, not individual seeds, as the independent units.

= Problem formulation

Let $G = (V, E)$ be the undirected graph induced by the free cells of an $N times N$ orthogonal grid after wall edges are removed. Let $W = (q_1, ..., q_K)$ be distinct ordered waypoints. A feasible solution is a vertex sequence

$ P = (v_1, ..., v_L), quad L = |V|, $

such that every vertex of $V$ appears exactly once, consecutive vertices share an edge in $E$, $v_1=q_1$, $v_L=q_K$, and the waypoint positions satisfy

$ "pos"_P(q_1) < "pos"_P(q_2) < ... < "pos"_P(q_K). $

Thus, the required path is Hamiltonian over the free cells and respects a total precedence order. Challenge v1 uses no blocked cells, but wall edges alter adjacency. A run is successful only if it returns a path that is revalidated against coverage, uniqueness, adjacency, wall exclusion, endpoints, and waypoint order.

= ZipMould constructor and feedback

== Constraint-aware path construction

Each iteration initializes $n$ independent walkers at $q_1$. A walker maintains its visited set and the index of the most recently reached waypoint. From its current vertex, a neighbor is legal only if it is unvisited, is connected by an open edge, and is not a future waypoint other than the next required one. The constructor additionally rejects a move if deleting the visited prefix and candidate cell disconnects any of the remaining free vertices. This residual-connectivity test is a hard pruning rule, not a soft score.

For a legal candidate edge $e$, four heuristic terms are computed:

+ *Manhattan proximity* favors geometric proximity to the next waypoint.
+ *Onward degree* uses a Warnsdorff-style preference for candidates with fewer legal onward moves.
+ *Residual connectivity* is zero for candidates that preserve a connected remainder; disconnecting candidates have already been rejected.
+ *Parity balance* weakly favors moves leaving the two checkerboard color classes within one vertex of balance.

After a softplus transform, their product is

$ eta(e) = product_j "softplus"(h_j(e))^(gamma_j), $

where $j$ indexes the four heuristics. With edge state $tau_e$, the sampling logit is

$ ell(e) = alpha tau_e + beta log eta(e), $

and the next edge is drawn from the softmax over legal candidates. Unified feedback is used in the confirmatory configuration, so one edge-state field is shared across waypoint segments.

Completed and partial paths are ranked by the fitness

$ f = L_P + beta_1 k_P + beta_2/(1+d_M) + beta_3 I_("solved"), $

where $L_P$ is visited length, $k_P$ is waypoint progress, $d_M$ is Manhattan distance to the next waypoint (the term reaches $beta_2$ after the final waypoint), and the final indicator supplies a large completion bonus. Fitness guides feedback only; the reported endpoint is validated success within a construction budget.

== Rank-weighted edge update

After constructing the population, walkers receive weights by descending fitness rank $r in {1,...,n}$:

$ w_r = (n - 2r + 1)/(n - 1). $

The best path receives +1, the worst −1, and middle ranks interpolate linearly. For edge $e$, the deposit $D_e$ is the sum of the weights of walkers whose paths traverse $e$. At zero-indexed iteration $t$ of cap $T$, the deterministic proposal is

$ tilde(tau)_e = v_c(t) tau_e + v_b(t) D_e, $

with $v_c(t)=1-t/T$ and $v_b(t)=tanh(1-t/T)$. Independently for every edge, with probability $z$ this proposal is replaced by a draw from $cal(N)(0, (tau_max/4)^2)$. The value is then clipped to $[0,tau_max]$. Lower-ranked paths therefore make subtractive deposits, but the stored state is nonnegative; this should not be described as a positive-only deposit rule.

The feedback-frozen intervention skips the entire update. Since $tau_0=0$, its edge state remains identically zero. All hard constraints, heuristic values, coefficients, path sampling, population size, stopping rules, puzzle, and initial seed remain the same. The intervention isolates the update package (rank deposition, time-dependent memory, and edge replacement noise) but does not identify those subcomponents separately.

#figure(
  table(
    columns: (2.2fr, 1fr, 2.2fr, 1fr),
    align: (left, right, left, right),
    table.header([Parameter], [Value], [Parameter], [Value]),
    [$n$ walkers], [53], [$T$ iterations], [64],
    [Path budget], [3,392], [$alpha$], [0.3178],
    [$beta$], [0.7347], [$gamma_("man")$], [0.1218],
    [$gamma_("warn")$], [3.0656], [$gamma_("art")$], [1.3901],
    [$gamma_("par")$], [0.3089], [$z$], [0.3879],
    [$tau_0$], [0], [$tau_max$], [3.1983],
    [Feedback field], [unified], [State support], [nonnegative],
  ),
  caption: [Frozen Challenge v1 configuration. Both conditions use every value shown; only execution of the edge-state update differs.],
) <tab-config>

= Challenge v1 benchmark

== Guaranteed-solvable generation

Challenge v1 contains only synthetic content. For each instance, the generator begins with a serpentine Hamiltonian path on the complete $N times N$ grid and applies $12N^2$ randomized endpoint-backbite moves. These moves alter the certificate while preserving its Hamiltonian property. Ordered waypoints are sampled along the resulting certificate. Interior waypoints preferentially maximize a ratio of certificate distance to Manhattan distance, creating long required segments whose endpoints appear geometrically close.

Walls are then sampled only from edges absent from the certificate, so the planted path always remains feasible. Three generator families control topology: open instances contain no walls; sparse instances independently remove noncertificate edges with probability 0.12; chambered instances add sparse walls and remove most noncertificate edges crossing periodic room boundaries. Certificates are stored separately and used to validate every generated puzzle.

Five family/size strata were selected: chambered 12×12, open 14×14, open 16×16, sparse 12×12, and sparse 14×14. Each stratum contributes 40 public training puzzles, 20 public development puzzles, and 30 held-out test puzzles, for 200/100/150 puzzles. Strata were retained only when feedback-frozen development success was informative. The calibration used five seeds per development puzzle and produced an overall frozen solve rate of 0.458; all selected stratum rates lay within the prespecified 0.15–0.85 target range. The full-minus-frozen contrast was never used to select generator parameters, strata, configuration, or budget. The solver's heuristic and feedback hyperparameters (@tab-config) were not tuned on Challenge v1: they were inherited from the legacy tuned winner, which had been selected where both arms saturated near a solve-rate ceiling. Only the iteration cap (hence the construction budget) was lowered from that legacy setting; the five strata were then chosen using feedback-frozen development difficulty alone. Because a saturated regime cannot discriminate configurations by feedback benefit, the confirmatory comparison estimates the effect of feedback at this transported operating point, not at one selected to make feedback maximally useful.

== Test commitment and release discipline

The test split was generated from a random 256-bit seed kept outside tracked artifacts. Before test access, the repository committed a domain-separated seed hash, canonical-corpus hash, certificate hash, exact stratum counts, and public specification hash. Verification regenerated and hashed the test corpus in memory without writing puzzle contents. Final execution required a clean commit carrying the annotated tag #raw("challenge-v1-confirmatory-v1").

After code, configuration, schedule, and analysis were frozen, the test was unlocked once with an explicit final-analysis acknowledgement. The complete corpus, seed reveal, certificates, raw trials, manifest, and derived reports were archived after analysis. This is a repository-level cryptographic commitment rather than registration with an external preregistration service.

= Confirmatory design and analysis

== Conditions, pairing, and budget

The two conditions were full feedback and feedback frozen. Each used the same configuration in @tab-config. For each of 150 puzzles, both conditions were run with seeds 0–29, producing 9,000 required rows. Population 53 and iteration cap 64 give a maximum of 3,392 constructed paths per run; this was the scientific budget. A 300-second wall-clock guard was retained only as an engineering failsafe and was never reached.

Seed pairing means that conditions begin from the same derived kernel seed for a puzzle. It does not create common random numbers after the intervention: feedback updates consume random draws in the full arm but are skipped in the frozen arm, so later random streams diverge. Pairing is preserved in descriptive outcome counts, while puzzle remains the independent analysis unit.

== Estimand, interval, and decision rule

For puzzle $p$, let $s_F(p)$ and $s_0(p)$ be the proportions of its 30 seeds solved under full and frozen feedback. The primary estimand is

$ Delta = 1/150 sum_(p=1)^150 (s_F(p) - s_0(p)). $

Uncertainty was computed with 10,000 stratified cluster-bootstrap replicates. Within each of the five frozen strata, 30 puzzles were sampled with replacement; the paired per-puzzle condition difference was retained, and the 150 sampled effects were averaged. The bootstrap used a local SplitMix64 stream with seed 20260716. The 95% endpoints were the prespecified empirical order statistics at indices $floor(0.025B)$ and $ceil(0.975B)-1$ for $B=10,000$. The bootstrap resamples puzzles and carries each selected puzzle's observed 30-seed difference, so the interval reflects between-puzzle variation, inclusive of the realized within-puzzle seed sampling noise, rather than separately resampling seeds. No formal power or precision target was predeclared; the sample size followed the calibration design of five strata, 30 test puzzles per stratum, and 30 seeds per puzzle. The achieved 95% interval half-width was 1.34 percentage points, comfortably finer than the ±5-point band, so the design proved decisive at this precision; a materially wider interval would instead have fallen under the inconclusive label.

Before test unlock, ±5 percentage points was declared the smallest practically important average effect. The outcome labels were:

+ *helpful* if the full interval was above +0.05;
+ *harmful* if the full interval was below −0.05;
+ *practically equivalent* if the full interval was inside [−0.05,+0.05]; and
+ *inconclusive* otherwise.

This rule differs from declaring equivalence after a non-significant test. It also differs from a formal TOST analysis; it is an interval-and-band classification frozen for this study. Marginal condition rates, five stratum effects, per-puzzle effect directions, and paired seed outcomes were predeclared as descriptive secondary results. Iteration counts and wall time were archived but were not confirmatory efficiency endpoints.

== Integrity checks

Analysis required the exact 150×30×2 grid, without duplicate or failed rows. Every row had to match the frozen configuration hash, tag commit, seed schedule, budget, and intervention field. All 4,020 returned solutions were independently revalidated from their archived coordinate paths. After the first analysis, a second run in a separate directory reproduced the report, puzzle-effect table, and all bootstrap replicates byte for byte.

= Results

Full feedback solved 2,039 of 4,500 trials (45.31%), compared with 1,981 of 4,500 (44.02%) for frozen feedback (@tab-primary). The primary mean full-minus-frozen difference was +0.01289, or +1.29 percentage points. Its 95% stratified puzzle-bootstrap interval was [−0.00044,+0.02644], equivalent to [−0.04,+2.64] percentage points (@fig-primary). The entire interval lies inside the predeclared ±5-point practical-effect band; the confirmatory classification is therefore *practically equivalent*. As a post-hoc description of where the interval sits, 97.1% of the 10,000 bootstrap replicates were positive (one-sided tail probability 0.029 for $Delta <= 0$), so the small positive estimate is statistically borderline rather than clearly nonzero; this characterizes the interval and does not change the predeclared classification.

#figure(
  table(
    columns: (2.3fr, 1fr, 1fr, 1.1fr),
    align: (left, right, right, right),
    table.header([Condition], [Solved], [Trials], [Solve rate]),
    [Full feedback], [2,039], [4,500], [0.453],
    [Feedback frozen], [1,981], [4,500], [0.440],
  ),
  caption: [Confirmatory marginal success counts. The primary analysis uses clustered per-puzzle differences rather than treating 4,500 trials as independent.],
) <tab-primary>

#figure(
  image("figures/challenge-primary.svg", width: 100%),
  caption: [Full-minus-frozen solve-probability effects. The overall interval is the prespecified stratified puzzle-bootstrap interval. Stratum intervals are not inferential claims; stratum point estimates are descriptive. The shaded band marks ±5 percentage points.],
) <fig-primary>

The five descriptive stratum effects ranged from −1.67 points for open 16×16 to +3.00 points for open 14×14 (@tab-strata). No stratum point estimate crossed either practical boundary. These estimates were not separately powered or multiplicity-adjusted and should not be read as evidence of family-specific benefit. Descriptively, the larger positive estimates fell in strata with mid-to-high base solve rates (open 14×14 and sparse 12×12, near 0.67 and 0.74), while the hardest strata (open 16×16 and sparse 14×14, near 0.29 and 0.16) showed a small negative and a small positive estimate; this is consistent with feedback helping modestly only where the base constructor has room to improve, but the design is not powered to support such a claim.

#figure(
  table(
    columns: (2.8fr, 0.9fr, 0.9fr, 0.9fr),
    align: (left, right, right, right),
    table.header([Stratum], [Full], [Frozen], [Difference]),
    [Chambered, 12×12], [0.379], [0.370], [+0.009],
    [Open, 14×14], [0.684], [0.654], [+0.030],
    [Open, 16×16], [0.279], [0.296], [−0.017],
    [Sparse, 12×12], [0.753], [0.726], [+0.028],
    [Sparse, 14×14], [0.170], [0.156], [+0.014],
  ),
  caption: [Predeclared descriptive results by generator stratum. Each row contains 30 puzzles, 30 seeds per puzzle, and 900 trials per condition.],
) <tab-strata>

Across the 4,500 paired puzzle-seed combinations, both arms solved 1,574, only full feedback solved 465, only frozen feedback solved 407, and neither solved 2,054. At puzzle level, full feedback had a higher seed solve rate on 57 puzzles, the arms tied on 48, and frozen feedback was higher on 45. The distribution of per-puzzle effects is heterogeneous but centered near zero (@fig-puzzles); the secondary displays do not alter the primary classification. Thirty-six of the 150 puzzles were solved identically by both arms on every seed (13 by neither arm and 23 by both), so their per-puzzle difference is necessarily zero and cannot contribute to the estimand; restricting the mean to the remaining 114 puzzles raises the point estimate to +1.70 percentage points, still well inside the practical band. This is a post-hoc descriptive sensitivity, not a redefinition of the primary estimand.

#figure(
  image("figures/challenge-puzzle-effects.svg", width: 100%),
  caption: [All 150 per-puzzle differences, sorted within stratum. Blue favors full feedback, red favors frozen feedback, and gray is a tie. This plot is descriptive.],
) <fig-puzzles>

= Discussion

The controlled result is negative in the scientifically useful sense: the implemented edge-feedback package did not produce a practically important average improvement under the frozen Challenge v1 design. The point estimate favors feedback slightly, but the full 95% interval (from a negligible disadvantage to a 2.64-point advantage) remains well inside the ±5-point band. That interval also contains zero, and the small positive lean (four of five strata, and 465 versus 407 seed wins) is therefore not statistically resolved: the finding is that any average effect is too small to matter under the predeclared band, not that feedback is exactly neutral. Describing this result only as “not significant” would miss the predeclared practical claim; describing it as universal equivalence would overstate it.

The result clarifies the legacy ceiling. On the original test corpus, the tuned full constructor solved 1,110/1,110 trials, and a post-hoc same-configuration frozen diagnostic also solved 1,110/1,110. Challenge v1 lowered both methods into an informative success regime, yet the average contrast remained small. Together, these observations suggest that the constraint-aware constructor, not its adaptive edge state, is the dominant source of performance in the studied settings.

Several mechanisms could explain the small contrast. First, hard residual-connectivity pruning is powerful: it removes moves that would make Hamiltonian completion impossible. Second, the onward-degree heuristic directly encodes a classic constructive principle, while waypoint legality and parity balance further narrow the choice set. Third, the relatively high edge-replacement probability ($z=0.3879$ independently per edge per update) can disrupt accumulated state as well as diversify it. Finally, 64 iterations may be sufficient for the constructor to sample many useful paths but too short, too long, or otherwise mismatched for stable edge learning. The present intervention intentionally does not decide among these explanations. In particular, because $z$ and $tau_max$ were fixed by legacy full-feedback tuning (where they were only weakly identified) and were never optimized for the Challenge contrast, the near-null result cannot separate an intrinsically inert feedback signal from a real but miscalibrated one that a different replacement rate, clip, or iteration cap might render useful. The ablation answers whether this configured update helps, not whether edge feedback can be made to help.

Methodologically, the study illustrates why mechanism ablations should preserve the surrounding algorithm. A separate “heuristic baseline” with a different population or budget cannot identify the effect of feedback. Freezing a zero-initialized state inside the same implementation removes a much narrower component. Likewise, a hard benchmark selected because the proposed method wins can bias the treatment contrast. Challenge v1 used only frozen-arm difficulty for calibration and concealed the confirmatory split until the analysis was immutable.

The practical-equivalence band is a scientific judgment rather than a fact supplied by the data. Five percentage points was chosen before unlock as the smallest average solve-probability gain that would justify retaining the update's machinery (signed rank deposition, temporal decay, and per-edge stochastic replacement, together with the extra hyperparameters ($alpha$, $z$, $tau_max$) and the per-iteration rank sort and whole-edge-set deposit they impose) over the simpler stateless constructor; a smaller average gain would not, in our judgment, warrant that added complexity and tuning burden for this endpoint. Readers who prefer a narrower threshold can still use the reported interval: it rules out average improvements above 2.64 points at the chosen confidence level but does not establish equivalence inside, for example, ±1 point. Reporting the estimate and interval keeps that sensitivity visible.

The outcome does not imply that shared edge memory has no research value. Heterogeneous effects and the mechanistic structure motivate new, explicitly exploratory work: separately remove rank-negative deposits, decay, and edge replacement; vary the construction budget; learn state per waypoint segment; or identify instance features that modify the effect. Such studies should use new development data and a newly locked confirmatory split. They should not repurpose the released Challenge v1 test set for another confirmatory claim.

= Limitations and threats to validity

*Synthetic instances.* Challenge v1 guarantees solvability and avoids third-party data rights, but its instances arise from one planted-certificate generator. Backbite-randomized paths, deceptive waypoint placement, and certificate-preserving walls may not represent human-authored puzzles or other Hamiltonian graph distributions.

*Limited domain and scales.* The confirmatory set covers five family/size strata and square grids of size 12, 14, or 16. Conclusions may not generalize to larger grids, blocked cells, non-grid graphs, other waypoint densities, or different wall processes.

*One configuration and budget.* The heuristic and feedback hyperparameters were inherited from the legacy tuned winner rather than re-tuned on Challenge v1, and that winner was selected where both arms saturated near a solve ceiling; only the iteration cap (hence the 3,392-path budget) and the five strata were set from feedback-frozen development difficulty. The experiment therefore estimates the effect of feedback at this transported operating point, not one chosen to make feedback maximally useful, and it neither averages over hyperparameters nor shows that either arm is optimally tuned. Re-tuning each arm on development solve rate (which does not select on the treatment contrast) could give feedback a stronger chance and is left to explicitly exploratory work. Interactions between feedback and population, iteration cap, state clipping, or noise may change the effect.

*Composite intervention.* Freezing the update simultaneously removes signed rank deposits, temporal decay, and stochastic edge replacement. The design has strong isolation at the package level but cannot attribute the result to a subcomponent. The nonnegative state also clips negative aggregate deposits; calling it “positive-only” would be inaccurate.

*Random-stream divergence.* Conditions share their initial derived seed, but feedback consumes random draws, so their streams cease to be synchronized. The comparison is between two stochastic algorithms with paired initialization, not a common-random-number estimate at every construction decision.

*Practical band and interval.* The ±5-point band was predeclared but remains domain judgment. The empirical percentile cluster bootstrap is transparent and reproducible, but other interval procedures could differ in finite samples. The classification is not a formal TOST result.

*No state-of-the-art comparison.* The mechanism question requires a matched constructor ablation, not a leaderboard. This paper therefore does not establish superiority over exact solvers, constraint programming, specialized ACO, or other tuned metaheuristics. Archived legacy baselines are contextual only and are not used for the confirmatory claim.

// = Reproducibility and data availability

// The software, benchmark specification, public train/development corpus, test commitment, frozen protocol, and analysis are included with the artifact. The pre-test release is Git commit #raw("06ef8bbfae5de29fe6cd4ebf0175a94f04880e9b") and annotated tag #raw("challenge-v1-confirmatory-v1"). The post-analysis evidence directory contains all 9,000 raw rows, 4,020 solved coordinate paths, the exact test corpus and certificates, the revealed seed, 10,000 bootstrap replicates, per-puzzle effects, environment and hardware metadata, and SHA-256 checksums.

// The raw result SHA-256 is #raw("a899646ef363ad2fd295e704b35f73b22efeb08ad10ebd5dc6429e1d32b1976a"). Execution used Python 3.13.12, NumPy 2.4.4, Numba 0.65.1, and Polars 1.40.1 on an AMD Ryzen 9 9950X3D system with 32 logical CPUs. The complete 9,000-run grid finished in 145.0 seconds with no failed rows; timing is provenance, not a comparative endpoint.

// From the repository root, #raw("make paper-verify") checks the frozen protocol, #raw("make paper-smoke") exercises both arms on public data, #raw("make paper-analyze") regenerates the analysis, and #raw("make paper-figures") regenerates publication displays. For audit from the paper package alone, #raw("paper/scripts/secondary_analysis.py") re-derives the primary interval from the archived per-puzzle effects, reproducing the frozen 10,000-replicate bootstrap byte for byte, and regenerates the post-hoc descriptive quantities (one-sided tail probability, achieved precision, saturation counts, and the informative-puzzle sensitivity) reported above. The evidence package documents seed reconstruction and byte-level verification. The public repository and archive URLs will be added to the data-availability statement upon public release.

= Conclusion

ZipMould's edge-state feedback was tested against the same stochastic constructor with the update frozen, under a sealed and reproducible Challenge v1 protocol. Full feedback improved average solve probability by 1.29 percentage points, with a 95% puzzle-bootstrap interval from −0.04 to +2.64 points. This interval lies within the predeclared ±5-point band, yielding a practically equivalent classification. The evidence therefore supports a narrow conclusion: for this implementation, benchmark, configuration, and budget, adding adaptive edge feedback produced no practically important average gain over the stateless constructor, even though the point estimate and most strata leaned weakly in its favour. Publishing that result, together with the test commitment, raw paths, and exact analysis, provides a firmer basis for future mechanism design than attributing ceiling performance to a biological metaphor.

// = Declarations

// *Ethics approval:* Not applicable; the study uses synthetic benchmark instances and no human or animal participants.

#bibliography("references.bib", style: "ieee", title: "References")

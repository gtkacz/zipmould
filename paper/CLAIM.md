# Frozen paper claim

## Working title

**Does Edge Feedback Help? A Controlled Study of a Slime-Mould–Inspired
Constructor for Ordered Hamiltonian Grid Paths**

## Honest contribution claim

ZipMould introduces an edge-state, rank-weighted feedback operator for
stochastic construction of ordered Hamiltonian grid paths and evaluates that
operator against the *identical* constraint-aware constructor with feedback
frozen. The scientific contribution is the controlled mechanism study, the
procedural benchmark, and the reproducible evidence, not an advance assertion
that the feedback operator is superior.

The original 245-puzzle corpus is reported as a ceiling regime: after tuning,
both the full and feedback-free constructors solved every run, so it provides
no evidence of incremental feedback benefit.

This framing remains true if the confirmatory effect is positive, negligible,
negative, or uncertain.

## Primary question and estimand

> Under a matched budget of 3,392 constructed paths on Challenge v1, how does
> adding edge feedback change solve probability relative to the same
> configuration and seeds with pheromone frozen?

For puzzle `p`, let `s_full(p)` and `s_frozen(p)` be the proportions of 30
predeclared seeds solved within budget. The primary estimand is:

```text
Delta = mean_p [s_full(p) - s_frozen(p)]
```

Puzzle is the independent cluster; seeds are nested repeated trials. The point
estimate and a 95% interval will be computed by a 10,000-replicate stratified
cluster bootstrap that resamples puzzles within the five frozen strata.

The smallest practically important effect is fixed at five percentage points:

- `helpful`: the full 95% interval is above `+0.05`;
- `harmful`: the full 95% interval is below `-0.05`;
- `practically equivalent`: the full interval is inside `[-0.05, +0.05]`;
- `inconclusive`: anything else.

All four outcomes are publishable outcomes of the mechanism study. Secondary
analyses may describe time/evaluation profiles and stratum heterogeneity, but
must not replace or redefine the primary estimand.

## Confirmatory controls

- Full and frozen conditions use the same solver configuration, path budget,
  puzzle, and seed.
- Generator and solver choices may use train/dev only.
- Generator strata were selected from feedback-frozen dev difficulty, never
  from a favorable full-minus-frozen effect.
- Challenge test has 150 puzzles: 30 from each frozen `(family, size)` stratum.
- Test seed and puzzle contents remain gitignored and unopened.
- The tracked lock commits to:
  - spec: `4eeeb31dc8b1ed13dbe8fd1e2fd3e04a3adeeef7bbe7040f687cd27e4db030a4`
  - seed: `96863e761391a8198d4f3f2ab7a6f7a52f1ce4d85d123d094e1cba101b10f494`
  - corpus: `3ee368923fa0ae785a7591994b5e1e5fa052d2a8f98113ddf7ed3ac8bb0b0fa4`
  - certificates: `5cbfd756cbf63c67267a156ade1b78267d2ec6135ed7be4628302e8bfb0dc293`
- Unlocking is permitted only after the final configuration, RNG comparison
  behavior, seeds, analysis code, and clean tagged commit are frozen.

## Claims this paper will not make

- that ZipMould is the first discrete SMA;
- that the edge operator is a direct transcription of continuous SMA;
- that success on the legacy corpus demonstrates feedback benefit;
- that a non-significant difference proves equivalence;
- that raw iteration counts are comparable across unrelated algorithms;
- that the current test is preregistered anywhere beyond this repository's
  cryptographic commitment and Git history.

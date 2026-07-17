# Challenge v1 confirmatory protocol

Status: **frozen before test unlock**

This document is the human-readable counterpart of
`experiments/challenge_v1/protocol.toml`. The TOML file and executable analysis
are authoritative for exact paths and machine-readable constants.

## Question and intervention

The confirmatory question is whether enabling ZipMould's edge-state feedback
changes success probability relative to the same constraint-aware stochastic
constructor with feedback frozen.

Both arms use `configs/challenge/v1-confirmatory.toml`, the same puzzle, and the
same `(global_seed, seed)` pair. The only intervention is
`freeze_pheromone=false` (full feedback) versus `true` (feedback frozen).
The seed pairing does not imply common random numbers after the intervention:
stochastic feedback updates consume randomness in the full arm and do not run
in the frozen arm. The treatment therefore compares the two algorithms as
implemented, starting from paired initial seeds.

## Confirmatory grid

- Test puzzles: 150, fixed by `benchmark/challenge/v1/test.lock.json`
- Frozen strata: 5, with 30 puzzles per stratum
- Seeds: integers `0..29`, paired within puzzle across conditions
- Conditions: `full-feedback`, `feedback-frozen`
- Runs: `150 x 30 x 2 = 9,000`
- Population: 53 constructed paths per iteration
- Iteration cap: 64
- Maximum construction budget: 3,392 paths per run
- Wall-clock guard: 300 seconds; the construction budget is the scientific
  endpoint and the guard is an engineering failsafe

Frozen integrity anchors:

- solver config hash: `208b2ef3dac411a69b3a9a339262796a`
- challenge spec SHA-256: `4eeeb31dc8b1ed13dbe8fd1e2fd3e04a3adeeef7bbe7040f687cd27e4db030a4`
- sealed corpus SHA-256: `3ee368923fa0ae785a7591994b5e1e5fa052d2a8f98113ddf7ed3ac8bb0b0fa4`
- sealed certificate SHA-256: `5cbfd756cbf63c67267a156ade1b78267d2ec6135ed7be4628302e8bfb0dc293`

Every one of the 9,000 rows is required. A worker exception, infeasible puzzle,
dirty Git state, configuration drift, duplicate/missing pair, or invalid
returned solution prevents confirmatory analysis. Interrupted execution may
resume only from rows whose release SHA, config hash, seeds, and intervention
fields match the frozen protocol.

## Primary estimand

For puzzle `p`, let `s_full(p)` and `s_frozen(p)` be the fractions of its 30
seeds solved within budget. The primary estimate is

```text
Delta = mean_p [s_full(p) - s_frozen(p)].
```

Puzzle is the independent cluster; seeds are nested repeated trials. The 95%
interval is a 10,000-replicate stratified cluster bootstrap. Each replicate
samples 30 puzzles with replacement inside each of the five strata, preserves
the paired condition difference for every selected puzzle, and averages over
all 150 sampled puzzle effects. The frozen SplitMix64 seed is `20260716`.
Interval endpoints are empirical order statistics at indices
`floor(0.025 B)` and `ceil(0.975 B)-1` in the zero-indexed sorted bootstrap
array, where `B=10,000`.

## Decision rule

The smallest practically important effect is five percentage points.

- `helpful`: the complete 95% interval is above `+0.05`;
- `harmful`: the complete interval is below `-0.05`;
- `practically equivalent`: the complete interval is inside
  `[-0.05, +0.05]`;
- `inconclusive`: every other outcome.

The classification changes the conclusion, not the paper's research question
or reportability.

## Predeclared descriptive results

The report also includes full and frozen marginal solve rates, five stratum
differences, the counts of puzzles with positive/zero/negative effects, and
paired seed outcomes (`both`, `full_only`, `frozen_only`, `neither`). These are
descriptive and do not replace the primary estimate. Iteration and wall-time
fields are archived for diagnostics but are not confirmatory efficiency
endpoints.

## Release and data handling

Final execution requires a clean commit carrying the exact tag
`challenge-v1-confirmatory-v1`. Unlocking verifies the published corpus and
certificate commitments before writing test material under the ignored
`benchmark/challenge/v1/sealed/` directory. Runtime checkpoints and raw output
are written under the ignored `scratch/` boundary so creating results cannot
dirty the tagged release. After analysis, raw results, manifests, checksums,
and derived evidence are copied into a versioned release artifact without
altering the pre-test tag.

# ZipMould Challenge v1

This benchmark is a synthetic, guaranteed-solvable corpus for the paper's
confirmatory mechanism study. It has no third-party puzzle content.

## Frozen paper question

> Under a matched path-construction budget on hard ordered-Hamiltonian grid
> instances, how does SMA-derived edge feedback change per-puzzle solve
> probability relative to the identical constructor with pheromone frozen?

The claim is deliberately outcome-invariant. The paper reports whether feedback
helps, is neutral, or hurts. The original 245-level corpus is retained as the
ceiling regime where both methods achieved 100% success after tuning.

## Instance families

Every puzzle is generated from a planted Hamiltonian path on a full square grid.
Waypoints are ordered along that certificate, and walls are added only on
non-certificate edges, so solvability is guaranteed by construction.

- `open-deceptive`: no walls; sparse consecutive waypoints are selected to make
  Euclidean/Manhattan shortcuts misleading relative to the planted path.
- `sparse-deceptive`: the same waypoint regime with a light random wall field.
- `chambered-deceptive`: room-like boundary walls with certificate crossings
  kept open, plus deceptive waypoint placement.

The five frozen strata were selected only from feedback-frozen dev difficulty:

```text
chambered-deceptive / 12x12
open-deceptive      / 14x14
open-deceptive      / 16x16
sparse-deceptive    / 12x12
sparse-deceptive    / 14x14
```

The public train/dev schedules and sealed test schedule contain respectively
40/20/30 independently seeded puzzles from each stratum (200/100/150 total).

## Leakage model

`train` and `dev` are generated from the public seeds in `spec.json`. Generator
parameters may be calibrated only from the feedback-frozen dev solve rate, using
the target interval in the spec. They must not be selected for a favorable
full-minus-frozen effect.

The test split is defined by a random 256-bit seed stored only at:

```text
benchmark/challenge/v1/.secrets/test_seed.txt
```

That path is gitignored. The tracked `test.lock.json` publishes:

- a domain-separated SHA-256 commitment to the secret seed;
- the SHA-256 hash of the canonical test corpus;
- the SHA-256 hash of the hidden planted-path certificates;
- the exact public spec hash and balanced family/size counts.

This fixes the test set without exposing its puzzle contents. Verification
regenerates and hashes the set in memory; it does not write puzzles. Unlocking
requires an explicit `--acknowledge-final-analysis` flag and creates a local
audit marker. Once unlocked or inspected, the test set must not be used to tune
the generator, solver, budgets, hypotheses, or analysis.

## Intended workflow

```bash
# Generate public train/dev data and certificates
uv run python benchmark/scripts/challenge.py generate-public

# After dev-only calibration is frozen, create the test commitments
uv run python benchmark/scripts/challenge.py seal-test

# Integrity check without writing test instances
uv run python benchmark/scripts/challenge.py verify-test-lock

# Final analysis only; do not run during development
uv run python benchmark/scripts/challenge.py unlock-test \
  --acknowledge-final-analysis
```

The final confirmatory run must use a clean tagged commit and pre-written
analysis code. Opening the test before that point invalidates its held-out
status.

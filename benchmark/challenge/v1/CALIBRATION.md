# Challenge v1 difficulty calibration

Generator calibration used only the same-config, feedback-frozen constructor.
The full-feedback condition was not evaluated during family, size, or budget
selection. This prevents selecting a test distribution because it favors the
proposed mechanism.

## Frozen probe

- Configuration: `configs/challenge/v1-calibration.toml`
- Population: 53
- Iteration cap: 64
- Maximum constructed paths per run: 3,392
- Seeds per dev puzzle: 5 (`0..4`)
- Overall target interval: `[0.15, 0.85]`
- Per-stratum target interval: `[0.15, 0.85]`
- Required informative-strata fraction: `>= 0.80`

Reproduce the final dev-only probe with:

```bash
uv run python benchmark/scripts/calibrate_challenge.py \
  --conditions frozen \
  --out-dir benchmark/challenge/v1/scratch/calibration64-selected
```

The command defaults to the tracked Challenge v1 calibration configuration.
Raw output is intentionally gitignored because timings and dirty-tree metadata
are machine/session specific. The exact selection-time summary is retained as
`calibration.report.json`; reruns should reproduce its solve outcomes, not its
machine-dependent wall-time value.

## Calibration history

1. The first 16-stratum, 200-iteration probe solved 84/320 frozen dev
   trials (`0.2625`). The overall target passed, but eight cells were at exactly
   0% or 100%, so the aggregate concealed uninformative strata.
2. Repeating the 16-stratum probe at 64 iterations solved 70/320 (`0.21875`).
   Five strata fell inside the target interval and were selected without
   evaluating full feedback.
3. A fresh 100-puzzle dev split was generated over those five strata. At five
   seeds per puzzle, the frozen constructor solved 229/500 (`0.458`). All five
   strata passed:

| Family | N | Solved / 100 | Rate |
|---|---:|---:|---:|
| chambered-deceptive | 12 | 39 | 0.39 |
| open-deceptive | 14 | 74 | 0.74 |
| open-deceptive | 16 | 23 | 0.23 |
| sparse-deceptive | 12 | 78 | 0.78 |
| sparse-deceptive | 14 | 15 | 0.15 |

The generator distribution and calibration budget are now frozen. Future
solver tuning may use train/dev, but must not change the generator spec or test
commitments.

## Integrity anchors

- Canonical spec SHA-256: `4eeeb31dc8b1ed13dbe8fd1e2fd3e04a3adeeef7bbe7040f687cd27e4db030a4`
- Canonical public corpus SHA-256: `229e6dca5b52cec2594fcbc5d8ddf6ca0ae1883c6eef21e9f9e735c74c803e44`
- Tracked calibration report SHA-256: `aa427108f6f888615c69212cafe97692cf44ae2a429eac91f80d4f3e379d7fe2`

The first two local report hashes are retained in the session audit log. Raw
calibration outputs live under the gitignored `scratch/` directory.

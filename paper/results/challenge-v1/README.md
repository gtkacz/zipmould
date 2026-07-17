# Challenge v1 confirmatory evidence release

This directory is the post-analysis evidence package for the mechanism study
frozen at Git commit `06ef8bbfae5de29fe6cd4ebf0175a94f04880e9b`, tag
`challenge-v1-confirmatory-v1`.

## Confirmatory result

| Condition | Solved | Trials | Solve rate |
|---|---:|---:|---:|
| Full feedback | 2,039 | 4,500 | 0.4531 |
| Feedback frozen | 1,981 | 4,500 | 0.4402 |

The puzzle-clustered mean difference was `+0.01289` with frozen 95%
stratified-bootstrap interval `[-0.00044, +0.02644]`. The predeclared outcome
is **practically equivalent** because the entire interval is within the
`[-0.05, +0.05]` practical-effect band.

## Contents

- `results.parquet`: all 9,000 raw rows, including all 4,020 solved paths;
- `run_manifest.json`: release, environment, hardware, timing, and file hashes;
- `report.json` / `report.md`: frozen confirmatory report;
- `puzzle_effects.parquet`: the 150 per-puzzle condition effects;
- `primary_bootstrap.parquet`: all 10,000 primary bootstrap replicates;
- `test_seed.reveal.txt`: post-analysis reveal of the seed committed before
  test unlock;
- `test/`: the exact released test corpus, certificates, metrics, split, and
  unlock audit marker;
- `checksums.sha256`: byte-level checksums for the evidence files.

The raw result table has SHA-256
`a899646ef363ad2fd295e704b35f73b22efeb08ad10ebd5dc6429e1d32b1976a`.
The test corpus's *canonical* commitment remains
`3ee368923fa0ae785a7591994b5e1e5fa052d2a8f98113ddf7ed3ac8bb0b0fa4`;
this differs from the CBOR file-byte checksum by design.

## Verification

From the repository root, verify byte integrity:

```bash
sha256sum -c paper/results/challenge-v1/checksums.sha256
```

To reconstruct the test from the pre-analysis commitment in a clean clone:

```bash
mkdir -p benchmark/challenge/v1/.secrets
cp paper/results/challenge-v1/test_seed.reveal.txt \
  benchmark/challenge/v1/.secrets/test_seed.txt
chmod 600 benchmark/challenge/v1/.secrets/test_seed.txt
uv run python benchmark/scripts/challenge.py verify-test-lock
uv run python benchmark/scripts/challenge.py unlock-test \
  --acknowledge-final-analysis
```

The verifier regenerates in memory and must report the canonical corpus hash
above before unlock. To regenerate the analysis without rerunning solvers and
compare every derived artifact byte for byte:

```bash
make paper-reproduce
```

The same independent regeneration performed at release time produced
byte-identical report, puzzle-effect, and bootstrap artifacts and revalidated
all archived solved paths.

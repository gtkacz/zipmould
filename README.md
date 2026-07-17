# ZipMould
ZipMould is a [Li](https://www.sciencedirect.com/science/article/abs/pii/S0167739X19320941)-inspired slime mould solver for Zip puzzles.

## 1. Problem Statement

A *Zip* puzzle consists of:

- An $N \times N$ grid of cells.
- A subset $\mathcal{W} \subseteq \{1, 2, \dots, N^2\}$ of cells pre-labelled with strictly-increasing positive integers $1, 2, \dots, K$ (the **waypoints**). Let $K = |\mathcal{W}|$.
- An optional set of **wall constraints**: for any cell, zero or more of its four edges may be marked impassable.

A valid solution is a sequence of cells $\pi_1, \pi_2, \dots, \pi_{N^2}$ satisfying:

1. $\pi_1$ is the cell labelled $1$ and $\pi_{N^2}$ is the cell labelled $K$.
2. Consecutive cells $\pi_t, \pi_{t+1}$ are 4-adjacent and the edge between them is not walled.
3. Every cell of the grid appears exactly once (Hamiltonian path).
4. Waypoints are visited in ascending order: if $\pi_a$ has label $k$ and $\pi_b$ has label $k+1$, then $a < b$.
5. The path neither branches nor crosses itself (implied by Hamiltonian).

## Visualizer

An interactive web visualizer lives at `src/zipmould/viz/` (FastAPI
backend) and `viz-web/` (Vue 3 frontend). To run it locally:

```bash
uv sync --extra viz
cd viz-web && bun install && bun run build
uv run zipmould viz serve
# Open http://127.0.0.1:8000
```

See `docs/superpowers/specs/2026-04-26-solver-visualizer-design.md` for
the full design.

## Research benchmark

The publication study uses the fully synthetic, guaranteed-solvable
`Challenge v1` benchmark under `benchmark/challenge/v1/`. Its public corpus has
200 train and 100 dev puzzles. A further 150-puzzle test set is fixed by
cryptographic commitments but remains sealed behind a gitignored 256-bit seed.

The frozen paper question is whether edge feedback helps the otherwise
identical constraint-aware constructor—not whether ZipMould is superior by
assumption. See:

- `paper/CLAIM.md` for the claim, primary estimand, and interpretation rules;
- `benchmark/challenge/v1/README.md` for generation and lock handling;
- `benchmark/challenge/v1/CALIBRATION.md` for the dev-only selection record.

Generate or verify public artifacts with:

```bash
uv run python benchmark/scripts/challenge.py generate-public
uv run python benchmark/scripts/challenge.py verify-test-lock
```

Do not run `unlock-test` until the final clean confirmatory release is frozen.

The frozen confirmatory workflow is documented in `paper/PROTOCOL.md`. Before
unlock, exercise both arms only on public dev data:

```bash
uv run python -m experiments.challenge_v1.run verify
uv run python -m experiments.challenge_v1.run smoke --workers 2
```

Final execution is guarded by the exact release tag and the unlocked corpus
commitments. The final-only commands are exposed through the `paper-run` and
`paper-analyze` Make targets; do not invoke them during development.

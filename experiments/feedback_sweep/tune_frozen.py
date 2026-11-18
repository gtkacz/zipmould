"""Re-tune the stateless constructor on dev, so feedback is compared with its strongest frozen rival.

The recalibrated feedback variant changed only feedback values, which the frozen
arm ignores. A fair reading of its gain needs the frozen arm's own heuristic
weights re-tuned on the same dev puzzles. Random search keeps the population and
iteration cap, hence the path budget, fixed.
"""

from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path
from typing import cast

import polars as pl
from joblib import Parallel, delayed  # pyright: ignore[reportMissingTypeStubs]

from experiments.challenge_v1.protocol import DEFAULT_PROTOCOL, load_protocol
from experiments.challenge_v1.run import validate_solution
from zipmould.config import SolverConfig
from zipmould.io.puzzles import load_corpus, load_split
from zipmould.solver.api import solve

SEARCH_SEED = 20261118
OUT = Path(__file__).parent / "out" / "tune-frozen"


def _log_uniform(rng: random.Random, low: float, high: float) -> float:
    return math.exp(rng.uniform(math.log(low), math.log(high)))


def candidates(count: int) -> list[dict[str, float]]:
    """Legacy search ranges for the weights that shape the stateless policy; the first candidate is unchanged."""
    rng = random.Random(SEARCH_SEED)  # noqa: S311 - reproducible search, not cryptographic
    sampled = [
        {
            "beta": _log_uniform(rng, 0.1, 4.0),
            "gamma_man": _log_uniform(rng, 0.1, 4.0),
            "gamma_warns": _log_uniform(rng, 0.1, 4.0),
            "gamma_par": rng.uniform(0.0, 2.0),
        }
        for _ in range(count - 1)
    ]
    return [{}, *sampled]


def _run_one(
    corpus_path: str, config_path: str, puzzle_id: str, seed: int, overrides: dict[str, float], freeze: bool
) -> bool:
    config = SolverConfig.from_toml(Path(config_path)).model_copy(update=overrides)
    puzzle = load_corpus(corpus_path)[puzzle_id]
    result = solve(puzzle, config, seed=seed, global_seed=0, freeze_pheromone=freeze)
    if result.solved:
        if result.solution is None:
            msg = f"{puzzle_id}: solved result has no solution"
            raise ValueError(msg)
        validate_solution(puzzle, result.solution)
    return result.solved


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidates", type=int, default=48)
    parser.add_argument("--seeds", type=int, default=5)
    parser.add_argument("--workers", type=int, default=-1)
    args = parser.parse_args(argv)

    protocol = load_protocol(DEFAULT_PROTOCOL)
    puzzle_ids = load_split("dev", protocol.public_splits)
    pool = candidates(args.candidates)
    jobs = [(index, pid, seed) for index in range(len(pool)) for pid in puzzle_ids for seed in range(args.seeds)]
    solved = cast(
        "list[bool]",
        Parallel(n_jobs=args.workers, backend="loky")(
            delayed(_run_one)(str(protocol.public_corpus), str(protocol.config), pid, seed, pool[index], True)
            for index, pid, seed in jobs
        ),
    )
    rows = pl.DataFrame({"candidate": [j[0] for j in jobs], "puzzle_id": [j[1] for j in jobs], "solved": solved})
    rates = rows.group_by("candidate").agg(pl.col("solved").mean().alias("solve_rate")).sort("candidate")
    ranked = sorted(
        (
            {
                "candidate": int(r["candidate"]),
                "solve_rate": float(r["solve_rate"]),
                "overrides": pool[int(r["candidate"])],
            }
            for r in rates.to_dicts()
        ),
        key=lambda item: -cast("float", item["solve_rate"]),
    )
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "search.json").write_text(json.dumps(ranked, indent=2) + "\n", encoding="utf-8")
    for item in ranked[:5]:
        print(
            f"candidate {item['candidate']:2d} solve rate {cast('float', item['solve_rate']):.3f} {item['overrides']}"
        )
    baseline = next(item for item in ranked if item["candidate"] == 0)
    print(f"unchanged weights: solve rate {cast('float', baseline['solve_rate']):.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Exploratory feedback sweep on public Challenge v1 dev puzzles.

The confirmatory study tested one transported configuration and could not tell
an inert feedback signal from a miscalibrated one. This sweep varies the
feedback knobs on dev data only and pairs every full-feedback variant with the
feedback-frozen arm at the same population and iteration cap. Results are
exploratory: dev puzzles informed stratum selection, and nothing here may be
reported as confirmatory.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import fmean
from typing import cast

import polars as pl
from joblib import Parallel, delayed  # pyright: ignore[reportMissingTypeStubs]

from experiments.challenge_v1.analyze import PuzzleEffect, percentile_interval, stratified_cluster_bootstrap
from experiments.challenge_v1.protocol import DEFAULT_PROTOCOL, load_protocol
from experiments.challenge_v1.run import validate_solution
from zipmould.config import SolverConfig
from zipmould.io.puzzles import load_corpus, load_split
from zipmould.solver.api import solve

# Best of 48 random heuristic weightings for the frozen arm on dev (tune.py, out/tune-frozen/search.json).
TUNED_WEIGHTS: dict[str, object] = {
    "beta": 2.7561635750871565,
    "gamma_man": 0.19462968620619914,
    "gamma_warns": 2.059311258120656,
    "gamma_par": 1.1202530451930357,
}
# Overrides of the frozen confirmatory configuration; `frozen` variants skip the update.
VARIANTS: dict[str, tuple[dict[str, object], bool]] = {
    "frozen": ({}, True),
    "full": ({}, False),
    "full-z0": ({"z": 0.0}, False),
    "full-z0.1": ({"z": 0.1}, False),
    "full-alpha1": ({"alpha": 1.0}, False),
    "full-z0-alpha1": ({"z": 0.0, "alpha": 1.0}, False),
    "full-z0-alpha3": ({"z": 0.0, "alpha": 3.0}, False),
    "full-signed": ({"tau_signed": True}, False),
    "full-stratified": ({"pheromone_mode": "stratified"}, False),
    "full-z0-alpha0.5": ({"z": 0.0, "alpha": 0.5}, False),
    "full-z0-alpha0.75": ({"z": 0.0, "alpha": 0.75}, False),
    "full-z0-alpha1.5": ({"z": 0.0, "alpha": 1.5}, False),
    "full-z0-alpha2": ({"z": 0.0, "alpha": 2.0}, False),
    "full-z0.1-alpha1": ({"z": 0.1, "alpha": 1.0}, False),
    "full-z0-alpha1-T128": ({"z": 0.0, "alpha": 1.0, "iter_cap": 128}, False),
    "full-z0-alpha1-T256": ({"z": 0.0, "alpha": 1.0, "iter_cap": 256}, False),
    "frozen-T128": ({"iter_cap": 128}, True),
    "full-T128": ({"iter_cap": 128}, False),
    "frozen-T256": ({"iter_cap": 256}, True),
    "full-T256": ({"iter_cap": 256}, False),
    "frozen-tuned": (TUNED_WEIGHTS, True),
    "full-tuned": (TUNED_WEIGHTS, False),
    "full-tuned-z0-alpha1": ({**TUNED_WEIGHTS, "z": 0.0, "alpha": 1.0}, False),
    # Best full-arm candidate of the equal-effort search (tune.py --arm full, out/tune-full/search.json).
    "full-joint": ({**TUNED_WEIGHTS, "alpha": 1.166577996787761, "z": 0.3622409860901429}, False),
}
# Feedback against the re-tuned stateless constructor rather than its own frozen twin.
EXTRA_COMPARISONS: tuple[tuple[str, str], ...] = (("full-z0-alpha1", "frozen-tuned"),)
BOOTSTRAP_REPLICATES = 10000
BOOTSTRAP_SEED = 20260716
CONFIDENCE_LEVEL = 0.95


def _reference(name: str) -> str:
    overrides, _ = VARIANTS[name]
    if "iter_cap" in overrides:
        return f"frozen-T{overrides['iter_cap']}"
    return "frozen-tuned" if "-tuned" in name or name == "full-joint" else "frozen"


def _run_one(corpus_path: str, config_path: str, puzzle_id: str, seed: int, variant: str) -> dict[str, object]:
    overrides, freeze = VARIANTS[variant]
    config = SolverConfig.from_toml(Path(config_path)).model_copy(update=overrides)
    puzzle = load_corpus(corpus_path)[puzzle_id]
    result = solve(puzzle, config, seed=seed, global_seed=0, condition=variant, freeze_pheromone=freeze)
    if result.solved:
        if result.solution is None:
            msg = f"{puzzle_id}: solved result has no solution"
            raise ValueError(msg)
        validate_solution(puzzle, result.solution)
    return {
        "puzzle_id": puzzle_id,
        "seed": seed,
        "variant": variant,
        "solved": result.solved,
        "iters": result.iters_used,
        "wall_ms": result.wall_clock_s * 1000.0,
    }


def _strata(metrics_path: Path) -> dict[str, tuple[str, int]]:
    payload = cast("dict[str, list[dict[str, object]]]", json.loads(metrics_path.read_text(encoding="utf-8")))
    return {str(row["puzzle_id"]): (str(row["family"]), int(cast("int", row["N"]))) for row in payload["metrics"]}


def summarize(rows: pl.DataFrame, strata: dict[str, tuple[str, int]]) -> list[dict[str, object]]:
    """Paired dev effect of each full variant against its matched frozen arm."""
    counts = rows.group_by("puzzle_id", "variant").agg(pl.col("solved").sum(), pl.len().alias("seeds"))
    solved = {(str(r["puzzle_id"]), str(r["variant"])): int(r["solved"]) for r in counts.to_dicts()}
    seeds = int(cast("int", counts["seeds"].max()))
    puzzles = sorted(rows["puzzle_id"].unique().to_list())
    summary: list[dict[str, object]] = []
    comparisons = [(name, _reference(name)) for name, (_, freeze) in VARIANTS.items() if not freeze]
    for variant, reference in [*comparisons, *EXTRA_COMPARISONS]:
        if (puzzles[0], variant) not in solved or (puzzles[0], reference) not in solved:
            continue
        effects = [
            PuzzleEffect(
                puzzle_id=pid,
                family=strata[pid][0],
                n=strata[pid][1],
                full_solved=solved[(pid, variant)],
                frozen_solved=solved[(pid, reference)],
                seeds=seeds,
            )
            for pid in puzzles
        ]
        replicates = stratified_cluster_bootstrap(effects, replicates=BOOTSTRAP_REPLICATES, seed=BOOTSTRAP_SEED)
        lower, upper = percentile_interval(replicates, CONFIDENCE_LEVEL)
        summary.append(
            {
                "variant": variant,
                "reference": reference,
                "overrides": VARIANTS[variant][0],
                "full_rate": fmean(e.full_rate for e in effects),
                "frozen_rate": fmean(e.frozen_rate for e in effects),
                "delta": fmean(e.delta for e in effects),
                "ci_lower": lower,
                "ci_upper": upper,
            }
        )
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seeds", type=int, default=30)
    parser.add_argument("--workers", type=int, default=-1)
    parser.add_argument("--variants", nargs="*", default=list(VARIANTS))
    parser.add_argument("--split", choices=("train", "dev"), default="dev")
    parser.add_argument("--out", type=Path, default=None, help="defaults to experiments/feedback_sweep/out/<split>")
    args = parser.parse_args(argv)

    protocol = load_protocol(DEFAULT_PROTOCOL)
    puzzle_ids = load_split(args.split, protocol.public_splits)
    strata = _strata(protocol.public_corpus.with_name("metrics.json"))
    args.out = args.out or Path(__file__).parent / "out" / args.split
    args.out.mkdir(parents=True, exist_ok=True)
    results_path = args.out / "results.parquet"
    existing = pl.read_parquet(results_path) if results_path.exists() else None
    done = set() if existing is None else set(existing["variant"].unique().to_list())

    jobs = [
        (str(protocol.public_corpus), str(protocol.config), pid, seed, variant)
        for variant in args.variants
        if variant not in done
        for pid in puzzle_ids
        for seed in range(args.seeds)
    ]
    new_rows = cast(
        "list[dict[str, object]]",
        Parallel(n_jobs=args.workers, backend="loky")(delayed(_run_one)(*job) for job in jobs),
    )
    frames = [frame for frame in (existing, pl.DataFrame(new_rows) if new_rows else None) if frame is not None]
    rows = pl.concat(frames).sort("variant", "puzzle_id", "seed")
    rows.write_parquet(results_path)

    summary = summarize(rows, strata)
    (args.out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    for row in summary:
        print(
            f"{row['variant']:18s} full={cast('float', row['full_rate']):.3f} "
            f"frozen={cast('float', row['frozen_rate']):.3f} "
            f"delta={cast('float', row['delta']) * 100:+.2f} pp "
            f"[{cast('float', row['ci_lower']) * 100:+.2f}, {cast('float', row['ci_upper']) * 100:+.2f}]"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

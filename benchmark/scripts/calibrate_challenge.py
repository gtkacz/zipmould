"""Dev-only difficulty calibration for ZipMould Challenge v1.

Generator parameters may be selected from the same-config feedback-frozen
condition's solve rate only.  The sealed test is deliberately inaccessible.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Literal, cast

import polars as pl
from joblib import Parallel, delayed  # pyright: ignore[reportMissingTypeStubs]

from zipmould.challenge import load_challenge_spec
from zipmould.config import SolverConfig
from zipmould.io.puzzles import load_corpus, load_split
from zipmould.solver.api import solve

REPO_ROOT = Path(__file__).resolve().parents[2]
CHALLENGE_ROOT = REPO_ROOT / "benchmark" / "challenge" / "v1"
DEFAULT_SPEC = CHALLENGE_ROOT / "spec.json"
DEFAULT_CORPUS = CHALLENGE_ROOT / "public" / "puzzles.cbor"
DEFAULT_SPLITS = CHALLENGE_ROOT / "public" / "splits.json"
DEFAULT_METRICS = CHALLENGE_ROOT / "public" / "metrics.json"
DEFAULT_CONFIG = REPO_ROOT / "configs" / "challenge" / "v1-calibration.toml"
DEFAULT_OUT = CHALLENGE_ROOT / "scratch" / "calibration"

Condition = Literal["feedback-frozen", "full-feedback"]


def _load_metrics(path: Path) -> dict[str, dict[str, int | float | str]]:
    payload: object = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        msg = f"metrics payload at {path} must be an object"
        raise ValueError(msg)
    rows = cast("dict[str, object]", payload).get("metrics")
    if not isinstance(rows, list):
        msg = f"metrics payload at {path} must contain a list"
        raise ValueError(msg)
    out: dict[str, dict[str, int | float | str]] = {}
    for raw_row in cast("list[object]", rows):
        if not isinstance(raw_row, dict):
            msg = "each metrics row must be an object"
            raise ValueError(msg)
        row = cast("dict[str, int | float | str]", raw_row)
        out[str(row["puzzle_id"])] = row
    return out


def _run_one(
    puzzle_id: str,
    seed: int,
    condition: Condition,
    corpus_path: str,
    config_path: str,
    family: str,
    n: int,
) -> dict[str, object]:
    puzzle = load_corpus(corpus_path)[puzzle_id]
    config = SolverConfig.from_toml(Path(config_path))
    frozen = condition == "feedback-frozen"
    result = solve(
        puzzle,
        config,
        seed=seed,
        global_seed=0,
        condition=condition,
        freeze_pheromone=frozen,
    )
    return {
        "puzzle_id": puzzle_id,
        "family": family,
        "N": n,
        "seed": seed,
        "condition": condition,
        "solved": result.solved,
        "iters": result.iters_used,
        "wall_ms": result.wall_clock_s * 1000.0,
        "best_fitness_normalised": result.best_fitness_normalised,
        "config_hash": result.config_hash,
        "git_sha": result.git_sha,
        "git_dirty": result.git_dirty,
    }


def _report(
    df: pl.DataFrame,
    target_min: float,
    target_max: float,
    target_stratum_min: float,
    target_stratum_max: float,
    required_informative_fraction: float,
) -> dict[str, object]:
    by_condition = (
        df.group_by("condition")
        .agg(
            n=pl.len(),
            solved=pl.col("solved").sum(),
            solve_rate=pl.col("solved").mean(),
            median_iters=pl.col("iters").median(),
            median_wall_ms=pl.col("wall_ms").median(),
        )
        .sort("condition")
        .to_dicts()
    )
    by_family_size = (
        df.group_by(["condition", "family", "N"])
        .agg(
            n=pl.len(),
            solved=pl.col("solved").sum(),
            solve_rate=pl.col("solved").mean(),
            median_iters=pl.col("iters").median(),
        )
        .sort(["condition", "family", "N"])
        .to_dicts()
    )
    frozen = df.filter(pl.col("condition") == "feedback-frozen")
    frozen_mean: object = frozen["solved"].mean() if not frozen.is_empty() else None
    frozen_rate = float(frozen_mean) if isinstance(frozen_mean, int | float) else None
    frozen_strata = [row for row in by_family_size if row["condition"] == "feedback-frozen"]
    informative_strata = [
        row
        for row in frozen_strata
        if target_stratum_min <= float(cast("int | float", row["solve_rate"])) <= target_stratum_max
    ]
    informative_fraction = float(len(informative_strata)) / float(len(frozen_strata)) if frozen_strata else 0.0
    overall_target_met = frozen_rate is not None and target_min <= frozen_rate <= target_max
    target_met = overall_target_met and informative_fraction >= required_informative_fraction
    return {
        "selection_guard": "generator difficulty may use feedback-frozen rates only; never full-minus-frozen effect",
        "target_feedback_frozen_solve_rate": [target_min, target_max],
        "feedback_frozen_solve_rate": frozen_rate,
        "target_feedback_frozen_stratum_solve_rate": [target_stratum_min, target_stratum_max],
        "informative_strata": len(informative_strata),
        "total_strata": len(frozen_strata),
        "informative_strata_fraction": informative_fraction,
        "required_informative_strata_fraction": required_informative_fraction,
        "difficulty_target_met": target_met,
        "by_condition": by_condition,
        "by_family_size": by_family_size,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, default=DEFAULT_SPEC)
    parser.add_argument("--corpus", type=Path, default=DEFAULT_CORPUS)
    parser.add_argument("--splits", type=Path, default=DEFAULT_SPLITS)
    parser.add_argument("--metrics", type=Path, default=DEFAULT_METRICS)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--split", choices=("train", "dev"), default="dev")
    parser.add_argument("--conditions", choices=("frozen", "both"), default="frozen")
    parser.add_argument("--workers", type=int, default=-1)
    args = parser.parse_args()

    spec = load_challenge_spec(args.spec)
    split_name = str(args.split)
    ids = load_split(split_name, args.splits)
    public_manifest = json.loads(args.splits.read_text(encoding="utf-8"))
    if public_manifest.get("test") != [] or not public_manifest.get("sealed_test"):
        msg = "calibration requires a public manifest with an empty sealed test split"
        raise ValueError(msg)
    metrics = _load_metrics(args.metrics)
    raw_seeds = spec.calibration["seeds"]
    if not isinstance(raw_seeds, list):
        msg = "calibration seeds must be a list of integers"
        raise ValueError(msg)
    raw_seed_items = cast("list[object]", raw_seeds)
    if not all(isinstance(seed, int) for seed in raw_seed_items):
        msg = "calibration seeds must be a list of integers"
        raise ValueError(msg)
    seeds = list(cast("list[int]", raw_seed_items))
    conditions: tuple[Condition, ...] = (
        ("feedback-frozen", "full-feedback") if args.conditions == "both" else ("feedback-frozen",)
    )
    jobs = [
        (
            puzzle_id,
            seed,
            condition,
            str(args.corpus),
            str(args.config),
            str(metrics[puzzle_id]["family"]),
            int(metrics[puzzle_id]["N"]),
        )
        for condition in conditions
        for puzzle_id in ids
        for seed in seeds
    ]
    rows = cast(
        "list[dict[str, object]]",
        Parallel(n_jobs=args.workers, backend="loky", verbose=0)(
            delayed(_run_one)(*job) for job in jobs
        ),
    )
    df = pl.DataFrame(rows)
    calibration = spec.calibration
    numeric_keys = (
        "target_dev_solve_rate_min",
        "target_dev_solve_rate_max",
        "target_stratum_solve_rate_min",
        "target_stratum_solve_rate_max",
        "required_informative_strata_fraction",
    )
    numeric: dict[str, float] = {}
    for key in numeric_keys:
        value = calibration[key]
        if not isinstance(value, int | float):
            msg = f"calibration {key} must be numeric"
            raise ValueError(msg)
        numeric[key] = float(value)
    report = _report(
        df,
        target_min=numeric["target_dev_solve_rate_min"],
        target_max=numeric["target_dev_solve_rate_max"],
        target_stratum_min=numeric["target_stratum_solve_rate_min"],
        target_stratum_max=numeric["target_stratum_solve_rate_max"],
        required_informative_fraction=numeric["required_informative_strata_fraction"],
    )
    args.out_dir.mkdir(parents=True, exist_ok=True)
    df.write_parquet(args.out_dir / f"{split_name}_results.parquet")
    (args.out_dir / f"{split_name}_report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

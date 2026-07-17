"""Frozen primary analysis for the Challenge v1 confirmatory experiment."""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from pathlib import Path
from statistics import fmean
from typing import Literal, cast

import polars as pl

from experiments.challenge_v1.protocol import DEFAULT_PROTOCOL, ConfirmatoryProtocol, file_sha256, load_protocol
from experiments.challenge_v1.run import validate_solution
from zipmould.io.puzzles import load_corpus, load_split

Outcome = Literal["helpful", "harmful", "practically equivalent", "inconclusive"]


class BootstrapRng:
    """SplitMix64 stream local to the frozen analysis implementation."""

    __slots__ = ("_state",)

    _MASK = (1 << 64) - 1

    def __init__(self, seed: int) -> None:
        self._state = seed & self._MASK

    def next_u64(self) -> int:
        self._state = (self._state + 0x9E3779B97F4A7C15) & self._MASK
        value = self._state
        value = ((value ^ (value >> 30)) * 0xBF58476D1CE4E5B9) & self._MASK
        value = ((value ^ (value >> 27)) * 0x94D049BB133111EB) & self._MASK
        return (value ^ (value >> 31)) & self._MASK

    def randbelow(self, upper: int) -> int:
        if upper <= 0:
            msg = "bootstrap sample size must be positive"
            raise ValueError(msg)
        limit = (1 << 64) - ((1 << 64) % upper)
        while True:
            value = self.next_u64()
            if value < limit:
                return value % upper


@dataclass(frozen=True, slots=True)
class PuzzleEffect:
    puzzle_id: str
    family: str
    n: int
    full_solved: int
    frozen_solved: int
    seeds: int

    @property
    def full_rate(self) -> float:
        return float(self.full_solved) / float(self.seeds)

    @property
    def frozen_rate(self) -> float:
        return float(self.frozen_solved) / float(self.seeds)

    @property
    def delta(self) -> float:
        return self.full_rate - self.frozen_rate

    @property
    def stratum(self) -> str:
        return f"{self.family}/N{self.n}"


def stratified_cluster_bootstrap(
    effects: list[PuzzleEffect],
    *,
    replicates: int,
    seed: int,
) -> list[float]:
    """Resample puzzle effects with replacement within each frozen stratum."""
    by_stratum: dict[str, list[float]] = {}
    for effect in sorted(effects, key=lambda item: item.puzzle_id):
        by_stratum.setdefault(effect.stratum, []).append(effect.delta)
    if not by_stratum or any(not values for values in by_stratum.values()):
        msg = "bootstrap requires at least one puzzle in every represented stratum"
        raise ValueError(msg)
    rng = BootstrapRng(seed)
    estimates: list[float] = []
    total = sum(len(values) for values in by_stratum.values())
    for _ in range(replicates):
        sampled_sum = 0.0
        for stratum in sorted(by_stratum):
            values = by_stratum[stratum]
            sampled_sum += sum(values[rng.randbelow(len(values))] for _ in values)
        estimates.append(sampled_sum / float(total))
    return estimates


def percentile_interval(values: list[float], confidence_level: float) -> tuple[float, float]:
    """Return the frozen empirical order-statistic percentile interval."""
    if not values or not 0.0 < confidence_level < 1.0:
        msg = "percentile interval requires values and confidence in (0, 1)"
        raise ValueError(msg)
    ordered = sorted(values)
    tail = (1.0 - confidence_level) / 2.0
    lower_index = min(int(math.floor(tail * len(ordered))), len(ordered) - 1)
    upper_index = min(int(math.ceil((1.0 - tail) * len(ordered))) - 1, len(ordered) - 1)
    return (ordered[lower_index], ordered[upper_index])


def classify_effect(lower: float, upper: float, practical_effect: float) -> Outcome:
    """Apply the outcome-invariant decision rule frozen before test unlock."""
    if lower > practical_effect:
        return "helpful"
    if upper < -practical_effect:
        return "harmful"
    if lower >= -practical_effect and upper <= practical_effect:
        return "practically equivalent"
    return "inconclusive"


def _rows(path: Path) -> list[dict[str, object]]:
    return cast("list[dict[str, object]]", pl.read_parquet(path).to_dicts())


def _validate_grid(
    protocol: ConfirmatoryProtocol,
    rows: list[dict[str, object]],
) -> tuple[list[str], str]:
    puzzle_ids = load_split("test", protocol.sealed_splits)
    conditions = protocol.condition_map()
    expected = {
        (puzzle_id, seed, condition)
        for puzzle_id in puzzle_ids
        for seed in protocol.seeds
        for condition in conditions
    }
    actual_keys = [
        (str(row["puzzle_id"]), int(cast("int", row["seed"])), str(row["condition"])) for row in rows
    ]
    if len(actual_keys) != len(set(actual_keys)):
        msg = "results contain duplicate puzzle/seed/condition rows"
        raise ValueError(msg)
    if set(actual_keys) != expected:
        missing = len(expected - set(actual_keys))
        extra = len(set(actual_keys) - expected)
        msg = f"results do not match frozen grid: {missing} missing, {extra} extra"
        raise ValueError(msg)
    expected_hash = protocol.expected_config_hash
    git_shas: set[str] = set()
    for row in rows:
        condition = str(row["condition"])
        if bool(row["freeze_pheromone"]) != conditions[condition]:
            msg = f"{condition}: freeze flag does not match protocol"
            raise ValueError(msg)
        if str(row["config_hash"]) != expected_hash:
            msg = "result config hash drifted from confirmatory configuration"
            raise ValueError(msg)
        if int(cast("int", row["global_seed"])) != protocol.global_seed:
            msg = "result global seed drifted from confirmatory protocol"
            raise ValueError(msg)
        if int(cast("int", row["path_budget"])) != protocol.constructed_path_budget:
            msg = "result path budget drifted from confirmatory protocol"
            raise ValueError(msg)
        if bool(row["failed"]) or bool(row["infeasible"]) or bool(row["git_dirty"]):
            msg = "results contain a failed, infeasible, or dirty-tree run"
            raise ValueError(msg)
        git_shas.add(str(row["git_sha"]))
    if len(git_shas) != 1:
        msg = "results contain multiple Git revisions"
        raise ValueError(msg)
    return puzzle_ids, next(iter(git_shas))


def _validate_solutions(protocol: ConfirmatoryProtocol, rows: list[dict[str, object]]) -> int:
    corpus = load_corpus(protocol.sealed_corpus)
    validated = 0
    for row in rows:
        raw_solution = row["solution_json"]
        if bool(row["solved"]):
            if not isinstance(raw_solution, str):
                msg = f"{row['puzzle_id']}: solved row lacks an archived solution"
                raise ValueError(msg)
            decoded: object = json.loads(raw_solution)
            if not isinstance(decoded, list):
                msg = "archived solution must be a coordinate list"
                raise ValueError(msg)
            solution = tuple((int(point[0]), int(point[1])) for point in cast("list[list[int]]", decoded))
            validate_solution(corpus[str(row["puzzle_id"])], solution)
            validated += 1
        elif raw_solution is not None:
            msg = f"{row['puzzle_id']}: unsolved row unexpectedly archives a solution"
            raise ValueError(msg)
    return validated


def _puzzle_effects(protocol: ConfirmatoryProtocol, rows: list[dict[str, object]]) -> list[PuzzleEffect]:
    grouped: dict[str, dict[str, object]] = {}
    for row in rows:
        puzzle_id = str(row["puzzle_id"])
        entry = grouped.setdefault(
            puzzle_id,
            {
                "family": str(row["family"]),
                "N": int(cast("int", row["N"])),
                "full-feedback": 0,
                "feedback-frozen": 0,
                "full_n": 0,
                "frozen_n": 0,
            },
        )
        condition = str(row["condition"])
        count_key = "full_n" if condition == "full-feedback" else "frozen_n"
        entry[count_key] = int(cast("int", entry[count_key])) + 1
        entry[condition] = int(cast("int", entry[condition])) + int(bool(row["solved"]))
    effects: list[PuzzleEffect] = []
    expected_seeds = len(protocol.seeds)
    for puzzle_id, entry in grouped.items():
        if entry["full_n"] != expected_seeds or entry["frozen_n"] != expected_seeds:
            msg = f"{puzzle_id}: condition seed counts are incomplete"
            raise ValueError(msg)
        effects.append(
            PuzzleEffect(
                puzzle_id=puzzle_id,
                family=str(entry["family"]),
                n=int(cast("int", entry["N"])),
                full_solved=int(cast("int", entry["full-feedback"])),
                frozen_solved=int(cast("int", entry["feedback-frozen"])),
                seeds=expected_seeds,
            )
        )
    return sorted(effects, key=lambda item: item.puzzle_id)


def _by_stratum(effects: list[PuzzleEffect]) -> list[dict[str, object]]:
    groups: dict[str, list[PuzzleEffect]] = {}
    for effect in effects:
        groups.setdefault(effect.stratum, []).append(effect)
    return [
        {
            "stratum": stratum,
            "puzzles": len(items),
            "trials_per_condition": sum(item.seeds for item in items),
            "full_solved": sum(item.full_solved for item in items),
            "frozen_solved": sum(item.frozen_solved for item in items),
            "full_solve_rate": fmean(item.full_rate for item in items),
            "frozen_solve_rate": fmean(item.frozen_rate for item in items),
            "delta": fmean(item.delta for item in items),
        }
        for stratum, items in sorted(groups.items())
    ]


def _paired_seed_counts(rows: list[dict[str, object]]) -> dict[str, int]:
    pairs: dict[tuple[str, int], dict[str, bool]] = {}
    for row in rows:
        key = (str(row["puzzle_id"]), int(cast("int", row["seed"])))
        pairs.setdefault(key, {})[str(row["condition"])] = bool(row["solved"])
    counts = {"both": 0, "full_only": 0, "frozen_only": 0, "neither": 0}
    for outcomes in pairs.values():
        full = outcomes["full-feedback"]
        frozen = outcomes["feedback-frozen"]
        label = "both" if full and frozen else "full_only" if full else "frozen_only" if frozen else "neither"
        counts[label] += 1
    return counts


def _effect_rows(effects: list[PuzzleEffect]) -> list[dict[str, object]]:
    return [
        {
            "puzzle_id": item.puzzle_id,
            "family": item.family,
            "N": item.n,
            "stratum": item.stratum,
            "seeds": item.seeds,
            "full_solved": item.full_solved,
            "frozen_solved": item.frozen_solved,
            "full_solve_rate": item.full_rate,
            "frozen_solve_rate": item.frozen_rate,
            "delta": item.delta,
        }
        for item in effects
    ]


def _markdown(report: dict[str, object]) -> str:
    primary = cast("dict[str, object]", report["primary"])
    strata = cast("list[dict[str, object]]", report["by_stratum"])
    lines = [
        "# Challenge v1 confirmatory result",
        "",
        f"**Decision:** {primary['classification']}",
        "",
        (
            f"Full minus frozen solve probability: `{float(cast('float', primary['estimate'])):.4f}` "
            f"(95% stratified puzzle-bootstrap interval "
            f"`[{float(cast('float', primary['ci_lower'])):.4f}, "
            f"{float(cast('float', primary['ci_upper'])):.4f}]`)."
        ),
        "",
        "| Stratum | Full | Frozen | Difference |",
        "|---|---:|---:|---:|",
    ]
    lines.extend(
        (
            f"| {row['stratum']} | {float(cast('float', row['full_solve_rate'])):.3f} | "
            f"{float(cast('float', row['frozen_solve_rate'])):.3f} | "
            f"{float(cast('float', row['delta'])):+.3f} |"
        )
        for row in strata
    )
    return "\n".join(lines) + "\n"


def analyze(protocol: ConfirmatoryProtocol, *, results_path: Path, output_dir: Path) -> dict[str, object]:
    """Validate the complete raw grid and produce the frozen report."""
    rows = _rows(results_path)
    puzzle_ids, git_sha = _validate_grid(protocol, rows)
    validated_solutions = _validate_solutions(protocol, rows)
    effects = _puzzle_effects(protocol, rows)
    if len(effects) != len(puzzle_ids):
        msg = "puzzle effect table is incomplete"
        raise ValueError(msg)
    bootstraps = stratified_cluster_bootstrap(
        effects,
        replicates=protocol.bootstrap_replicates,
        seed=protocol.bootstrap_seed,
    )
    lower, upper = percentile_interval(bootstraps, protocol.confidence_level)
    estimate = fmean(effect.delta for effect in effects)
    classification = classify_effect(lower, upper, protocol.practical_effect)
    full_solved = sum(effect.full_solved for effect in effects)
    frozen_solved = sum(effect.frozen_solved for effect in effects)
    total_per_condition = len(effects) * len(protocol.seeds)
    effect_counts = {
        "positive": sum(effect.delta > 0.0 for effect in effects),
        "zero": sum(effect.delta == 0.0 for effect in effects),
        "negative": sum(effect.delta < 0.0 for effect in effects),
    }
    by_stratum = _by_stratum(effects)
    report: dict[str, object] = {
        "study_id": protocol.study_id,
        "analysis_status": "confirmatory",
        "git_sha": git_sha,
        "raw_results_sha256": file_sha256(results_path),
        "config_hash": protocol.expected_config_hash,
        "puzzles": len(effects),
        "seeds_per_puzzle": len(protocol.seeds),
        "trials_per_condition": total_per_condition,
        "validated_solutions": validated_solutions,
        "full_feedback": {"solved": full_solved, "solve_rate": full_solved / total_per_condition},
        "feedback_frozen": {"solved": frozen_solved, "solve_rate": frozen_solved / total_per_condition},
        "primary": {
            "estimand": protocol.primary_estimand,
            "estimate": estimate,
            "confidence_level": protocol.confidence_level,
            "ci_lower": lower,
            "ci_upper": upper,
            "bootstrap_replicates": protocol.bootstrap_replicates,
            "bootstrap_seed": protocol.bootstrap_seed,
            "bootstrap_unit": protocol.bootstrap_unit,
            "interval_method": "empirical_order_statistic_percentile",
            "practical_effect": protocol.practical_effect,
            "classification": classification,
        },
        "puzzle_effect_direction": effect_counts,
        "paired_seed_outcomes": _paired_seed_counts(rows),
        "by_stratum": by_stratum,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    pl.DataFrame(_effect_rows(effects)).write_parquet(output_dir / "puzzle_effects.parquet", compression="zstd")
    pl.DataFrame(
        {"replicate": list(range(protocol.bootstrap_replicates)), "delta": bootstraps}
    ).write_parquet(output_dir / "primary_bootstrap.parquet", compression="zstd")
    (output_dir / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (output_dir / "report.md").write_text(_markdown(report), encoding="utf-8")
    return report


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", type=Path, default=DEFAULT_PROTOCOL)
    parser.add_argument("--results", type=Path)
    parser.add_argument("--out-dir", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    protocol = load_protocol(Path(args.protocol).resolve())
    results_path = Path(args.results).resolve() if args.results else protocol.output_dir / "results.parquet"
    output_dir = Path(args.out_dir).resolve() if args.out_dir else protocol.output_dir / "analysis"
    report = analyze(protocol, results_path=results_path, output_dir=output_dir)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

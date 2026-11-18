"""Regenerate the primary interval and post-hoc descriptive secondaries.

This script is deliberately self-contained: it reproduces the frozen primary
bootstrap interval from the archived per-puzzle effects alone, so the central
inferential number can be audited from the paper package without importing the
main repository's analysis module. It then computes the descriptive quantities
reported in the manuscript's Results and Discussion (achieved interval
precision, observed saturation, the outcome-selected subset calculation,
and the stratum base-rate/effect pattern).

None of these quantities replace or redefine the predeclared primary estimand;
they characterise where the frozen interval sits and are labelled post hoc in
the manuscript.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from statistics import NormalDist
from typing import cast

import numpy as np
import polars as pl

PAPER = Path(__file__).resolve().parents[1]
RESULTS = PAPER / "results" / "challenge-v1"
GENERATED = PAPER / "generated"

# Fixed by the frozen protocol; duplicated here so the interval is regenerable
# from the paper package alone rather than by importing the experiment code.
BOOTSTRAP_REPLICATES = 10000
BOOTSTRAP_SEED = 20260716
CONFIDENCE_LEVEL = 0.95
PRACTICAL_EFFECT = 0.05
SEEDS_PER_PUZZLE = 30
TOLERANCE = 1e-12
POPULATION = 53
PROFILE_ITERATIONS = (8, 16, 32, 48, 64)
SIGN_FLIP_REPLICATES = 20000


class BootstrapRng:
    """SplitMix64 stream mirroring the frozen analysis implementation."""

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
        # Rejection sampling removes modulo bias; matches the frozen analysis.
        limit = (1 << 64) - ((1 << 64) % upper)
        while True:
            value = self.next_u64()
            if value < limit:
                return value % upper


def stratified_cluster_bootstrap(
    deltas_by_puzzle: list[tuple[str, str, float]],
    *,
    replicates: int,
    seed: int,
) -> list[float]:
    """Resample puzzle effects with replacement within each frozen stratum.

    The iteration order (puzzles sorted by id, strata sorted by name) matches
    the frozen analysis so the replicate stream is reproduced exactly.
    """
    by_stratum: dict[str, list[float]] = {}
    for _puzzle_id, stratum, delta in sorted(deltas_by_puzzle, key=lambda item: item[0]):
        by_stratum.setdefault(stratum, []).append(delta)
    rng = BootstrapRng(seed)
    total = sum(len(values) for values in by_stratum.values())
    estimates: list[float] = []
    for _ in range(replicates):
        sampled_sum = 0.0
        for stratum in sorted(by_stratum):
            values = by_stratum[stratum]
            sampled_sum += sum(values[rng.randbelow(len(values))] for _ in values)
        estimates.append(sampled_sum / float(total))
    return estimates


def percentile_interval(values: list[float], confidence_level: float) -> tuple[float, float]:
    ordered = sorted(values)
    tail = (1.0 - confidence_level) / 2.0
    lower_index = min(int(math.floor(tail * len(ordered))), len(ordered) - 1)
    upper_index = min(int(math.ceil((1.0 - tail) * len(ordered))) - 1, len(ordered) - 1)
    return (ordered[lower_index], ordered[upper_index])


def _paired_seed_outcomes(results: pl.DataFrame, puzzle_ids: list[str]) -> tuple[np.ndarray, np.ndarray]:
    """Iteration of first solve per (puzzle, seed) for each arm; unsolved runs never solve."""
    unsolved = np.iinfo(np.int64).max
    wide = (
        results.with_columns(pl.when(pl.col("solved")).then(pl.col("iters")).otherwise(unsolved).alias("solved_at"))
        .pivot(on="condition", index=["puzzle_id", "seed"], values="solved_at")
        .sort("puzzle_id", "seed")
    )
    shape = (len(puzzle_ids), SEEDS_PER_PUZZLE)
    if wide["puzzle_id"].unique(maintain_order=True).to_list() != puzzle_ids:
        raise SystemExit("raw rows and per-puzzle effects disagree on the puzzle set")
    return (
        wide["full-feedback"].to_numpy().reshape(shape),
        wide["feedback-frozen"].to_numpy().reshape(shape),
    )


def budget_profile(
    full_at: np.ndarray, frozen_at: np.ndarray, puzzle_ids: list[str], strata: list[str]
) -> list[dict[str, object]]:
    """Solve probability by construction budget, truncating each archived run.

    A truncated run is not a run with a smaller iteration cap: the feedback
    schedule depends on the cap, so this describes the frozen design only.
    """
    profile: list[dict[str, object]] = []
    for iterations in PROFILE_ITERATIONS:
        deltas = ((full_at <= iterations).mean(axis=1) - (frozen_at <= iterations).mean(axis=1)).tolist()
        replicates = stratified_cluster_bootstrap(
            list(zip(puzzle_ids, strata, deltas, strict=True)), replicates=BOOTSTRAP_REPLICATES, seed=BOOTSTRAP_SEED
        )
        lower, upper = percentile_interval(replicates, CONFIDENCE_LEVEL)
        profile.append(
            {
                "iterations": iterations,
                "paths": iterations * POPULATION,
                "full_rate": float((full_at <= iterations).mean()),
                "frozen_rate": float((frozen_at <= iterations).mean()),
                "delta": float(np.mean(deltas)),
                "ci_lower": lower,
                "ci_upper": upper,
            }
        )
    return profile


def effect_dispersion(full_solved: np.ndarray, frozen_solved: np.ndarray) -> dict[str, object]:
    """Compare the spread of per-puzzle effects with seed-level noise alone.

    Under the sharp null that feedback changes no run, the two arms of a seed
    pair are exchangeable, so swapping them at random gives the spread that
    sampling noise produces without any puzzle-specific effect.
    """
    differences = full_solved.astype(np.float64) - frozen_solved.astype(np.float64)
    observed = float(differences.mean(axis=1).std(ddof=1))
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    null = np.empty(SIGN_FLIP_REPLICATES)
    for index in range(SIGN_FLIP_REPLICATES):
        signs = rng.choice((-1.0, 1.0), size=differences.shape)
        null[index] = (differences * signs).mean(axis=1).std(ddof=1)
    return {
        "observed_sd": observed,
        "null_sd_mean": float(null.mean()),
        "p_value": float((null >= observed).mean()),
        "replicates": SIGN_FLIP_REPLICATES,
    }


def interval_sensitivity(deltas: list[float], strata: list[str], replicates: list[float]) -> dict[str, list[float]]:
    """Other common 95% intervals for the same estimate, to show the classification does not hinge on the procedure."""
    values = np.asarray(deltas)
    labels = np.asarray(strata)
    groups = [values[labels == stratum] for stratum in sorted(set(strata))]
    weights = [len(group) / len(values) for group in groups]
    standard_error = math.sqrt(
        sum(w * w * group.var(ddof=1) / len(group) for w, group in zip(weights, groups, strict=True))
    )
    estimate = float(values.mean())
    normal = NormalDist()
    z = normal.inv_cdf(1.0 - (1.0 - CONFIDENCE_LEVEL) / 2.0)
    boot = np.asarray(replicates)
    tail = (1.0 - CONFIDENCE_LEVEL) / 2.0
    bias = normal.inv_cdf(float((boot < estimate).mean()))
    jackknife = np.array([np.delete(values, index).mean() for index in range(len(values))])
    spread = jackknife.mean() - jackknife
    acceleration = float((spread**3).sum() / (6.0 * (spread**2).sum() ** 1.5))

    def bca_level(level: float) -> float:
        shifted = bias + normal.inv_cdf(level)
        return normal.cdf(bias + shifted / (1.0 - acceleration * shifted))

    return {
        "stratified_normal": [estimate - z * standard_error, estimate + z * standard_error],
        "basic_bootstrap": [
            2.0 * estimate - float(np.quantile(boot, 1.0 - tail)),
            2.0 * estimate - float(np.quantile(boot, tail)),
        ],
        "bca_bootstrap": [float(np.quantile(boot, bca_level(tail))), float(np.quantile(boot, bca_level(1.0 - tail)))],
    }


def main() -> int:
    report = json.loads((RESULTS / "report.json").read_text(encoding="utf-8"))
    primary = cast("dict[str, object]", report["primary"])
    effects = pl.read_parquet(RESULTS / "puzzle_effects.parquet")

    deltas_by_puzzle = [
        (str(row["puzzle_id"]), str(row["stratum"]), float(cast("float", row["delta"]))) for row in effects.to_dicts()
    ]
    replicates = stratified_cluster_bootstrap(deltas_by_puzzle, replicates=BOOTSTRAP_REPLICATES, seed=BOOTSTRAP_SEED)
    lower, upper = percentile_interval(replicates, CONFIDENCE_LEVEL)

    # Self-containment proof: the interval regenerated here must equal the frozen one.
    ci_lower = float(cast("float", primary["ci_lower"]))
    ci_upper = float(cast("float", primary["ci_upper"]))
    if abs(lower - ci_lower) > TOLERANCE or abs(upper - ci_upper) > TOLERANCE:
        msg = f"regenerated interval [{lower}, {upper}] does not match frozen " f"[{ci_lower}, {ci_upper}]"
        raise SystemExit(msg)

    archived = pl.read_parquet(RESULTS / "primary_bootstrap.parquet")["delta"].to_list()
    if len(archived) != len(replicates) or any(
        abs(a - b) > TOLERANCE for a, b in zip(sorted(archived), sorted(replicates), strict=True)
    ):
        raise SystemExit("regenerated replicates do not match the archived bootstrap")

    estimate = float(cast("float", primary["estimate"]))
    half_width = (ci_upper - ci_lower) / 2.0

    full = effects["full_solved"].to_list()
    frozen = effects["frozen_solved"].to_list()
    floor_puzzles = sum(1 for f, z in zip(full, frozen, strict=True) if f == 0 and z == 0)
    ceiling_puzzles = sum(
        1 for f, z in zip(full, frozen, strict=True) if f == SEEDS_PER_PUZZLE and z == SEEDS_PER_PUZZLE
    )
    saturated = floor_puzzles + ceiling_puzzles
    nonsaturated = effects.height - saturated
    delta_sum = float(effects["delta"].sum())
    nonsaturated_estimate = delta_sum / nonsaturated if nonsaturated else float("nan")

    strata = (
        effects.with_columns(((pl.col("full_solve_rate") + pl.col("frozen_solve_rate")) / 2.0).alias("base_rate"))
        .group_by("stratum")
        .agg(pl.col("base_rate").mean(), pl.col("delta").mean())
        .sort("base_rate")
    )

    puzzle_ids = effects["puzzle_id"].to_list()
    full_at, frozen_at = _paired_seed_outcomes(pl.read_parquet(RESULTS / "results.parquet"), puzzle_ids)
    profile = budget_profile(full_at, frozen_at, puzzle_ids, effects["stratum"].to_list())
    if (profile[-1]["ci_lower"], profile[-1]["ci_upper"]) != (lower, upper):
        raise SystemExit("full-budget profile does not reproduce the frozen interval")
    dispersion = effect_dispersion(full_at <= PROFILE_ITERATIONS[-1], frozen_at <= PROFILE_ITERATIONS[-1])
    # The update first runs after iteration 1, so both arms share every first-iteration outcome.
    sensitivity = interval_sensitivity(
        [delta for _, _, delta in deltas_by_puzzle], [stratum for _, stratum, _ in deltas_by_puzzle], replicates
    )
    first_iteration_solves = {
        "full": int((full_at == 1).sum()),
        "frozen": int((frozen_at == 1).sum()),
        "both": int(((full_at == 1) & (frozen_at == 1)).sum()),
    }

    summary: dict[str, object] = {
        "regenerated_interval": [lower, upper],
        "matches_frozen_interval": True,
        "matches_archived_replicates": True,
        "estimate": estimate,
        "interval_half_width": half_width,
        "practical_effect": PRACTICAL_EFFECT,
        "floor_puzzles": floor_puzzles,
        "ceiling_puzzles": ceiling_puzzles,
        "saturated_puzzles": saturated,
        "nonsaturated_puzzles": nonsaturated,
        "estimate_over_nonsaturated_puzzles": nonsaturated_estimate,
        "subset_interpretation": (
            "Outcome-selected descriptive subset; changes target population; no equivalence inference."
        ),
        "stratum_base_rate_vs_delta": strata.to_dicts(),
        "budget_profile": profile,
        "effect_dispersion": dispersion,
        "first_iteration_solves": first_iteration_solves,
        "interval_sensitivity": sensitivity,
    }
    GENERATED.mkdir(parents=True, exist_ok=True)
    (GENERATED / "secondary_analysis.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    print(f"regenerated interval matches frozen report: [{lower:+.5f}, {upper:+.5f}]")
    print(f"estimate: {estimate * 100:+.2f} pp")
    print(f"achieved 95% interval half-width: {half_width * 100:.2f} pp (band {PRACTICAL_EFFECT * 100:.0f} pp)")
    print(
        f"saturated puzzles: {saturated} (floor {floor_puzzles}, ceiling {ceiling_puzzles}); "
        f"nonsaturated: {nonsaturated}"
    )
    print(
        f"estimate over nonsaturated puzzles only: {nonsaturated_estimate * 100:+.2f} pp "
        f"(vs {estimate * 100:+.2f} pp over all {effects.height})"
    )
    for row in strata.to_dicts():
        print(
            f"  {row['stratum']!s:26s} base={float(cast('float', row['base_rate'])) * 100:5.1f}%  "
            f"delta={float(cast('float', row['delta'])) * 100:+.2f} pp"
        )
    for row in profile:
        print(
            f"  budget {cast('int', row['paths']):5d} paths: delta={cast('float', row['delta']) * 100:+.2f} pp "
            f"[{cast('float', row['ci_lower']) * 100:+.2f}, {cast('float', row['ci_upper']) * 100:+.2f}]"
        )
    print(
        f"per-puzzle effect SD {cast('float', dispersion['observed_sd']) * 100:.2f} pp vs "
        f"{cast('float', dispersion['null_sd_mean']) * 100:.2f} pp from seed noise alone "
        f"(p={cast('float', dispersion['p_value']):.3f})"
    )
    for name, (low, high) in sensitivity.items():
        print(f"  {name:18s} [{low * 100:+.2f}, {high * 100:+.2f}] pp")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

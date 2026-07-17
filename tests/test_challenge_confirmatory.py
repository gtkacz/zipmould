"""Regression tests for the frozen Challenge v1 experiment and analysis."""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path
from typing import cast

import experiments.challenge_v1.run as confirmatory_run
import polars as pl
import pytest
from experiments.challenge_v1.analyze import (
    BootstrapRng,
    PuzzleEffect,
    analyze,
    classify_effect,
    percentile_interval,
    stratified_cluster_bootstrap,
)
from experiments.challenge_v1.protocol import (
    DEFAULT_PROTOCOL,
    EXPECTED_CONDITIONS,
    EXPECTED_SEEDS,
    load_protocol,
    validate_protocol,
)

from zipmould.config import SolverConfig

_EXPECTED_PATH_BUDGET = 3_392
_BOOTSTRAP_TEST_REPLICATES = 100
_EXPECTED_VALIDATED_SOLUTIONS = 4


def test_protocol_freezes_conditions_seeds_and_budget() -> None:
    protocol = load_protocol(DEFAULT_PROTOCOL)
    config = SolverConfig.from_toml(protocol.config)
    assert protocol.condition_map() == EXPECTED_CONDITIONS
    assert protocol.seeds == EXPECTED_SEEDS
    assert config.config_hash() == protocol.expected_config_hash
    assert config.population * config.iter_cap == _EXPECTED_PATH_BUDGET
    assert protocol.constructed_path_budget == _EXPECTED_PATH_BUDGET

    with pytest.raises(ValueError, match="seeds must be exactly"):
        validate_protocol(replace(protocol, seeds=tuple(range(29))))


def test_final_release_gate_requires_exact_tag(monkeypatch: pytest.MonkeyPatch) -> None:
    protocol = load_protocol(DEFAULT_PROTOCOL)

    def untagged(*args: str) -> str:
        if args == ("rev-parse", "HEAD"):
            return "deadbeef"
        return ""

    monkeypatch.setattr(confirmatory_run, "_git_output", untagged)
    with pytest.raises(ValueError, match="requires tag"):
        confirmatory_run.verify_release(protocol, require_tag=True, require_sealed=False)

    def tagged(*args: str) -> str:
        if args == ("rev-parse", "HEAD"):
            return "deadbeef"
        if args == ("tag", "--points-at", "HEAD"):
            return protocol.required_tag
        return ""

    monkeypatch.setattr(confirmatory_run, "_git_output", tagged)
    verified = confirmatory_run.verify_release(protocol, require_tag=True, require_sealed=False)
    assert verified["git_sha"] == "deadbeef"
    assert verified["git_dirty"] is False


def test_bootstrap_rng_and_decision_rule_are_frozen() -> None:
    rng = BootstrapRng(123456789)
    assert [rng.next_u64() for _ in range(4)] == [
        2466975172287755897,
        8832083440362974766,
        3534771765162737125,
        9592110948284743397,
    ]
    assert classify_effect(0.051, 0.2, 0.05) == "helpful"
    assert classify_effect(-0.2, -0.051, 0.05) == "harmful"
    assert classify_effect(-0.05, 0.05, 0.05) == "practically equivalent"
    assert classify_effect(-0.01, 0.08, 0.05) == "inconclusive"


def test_stratified_bootstrap_preserves_constant_effect() -> None:
    effects = [
        PuzzleEffect("a", "open", 12, 3, 0, 3),
        PuzzleEffect("b", "open", 12, 3, 0, 3),
        PuzzleEffect("c", "sparse", 14, 3, 0, 3),
        PuzzleEffect("d", "sparse", 14, 3, 0, 3),
    ]
    estimates = stratified_cluster_bootstrap(
        effects,
        replicates=_BOOTSTRAP_TEST_REPLICATES,
        seed=7,
    )
    assert estimates == [1.0] * _BOOTSTRAP_TEST_REPLICATES
    assert percentile_interval(estimates, 0.95) == (1.0, 1.0)


def _public_certificates() -> dict[str, str]:
    path = Path("benchmark/challenge/v1/public/certificates.json")
    payload = cast("dict[str, object]", json.loads(path.read_text(encoding="utf-8")))
    rows = cast("list[dict[str, object]]", payload["certificates"])
    return {
        str(row["puzzle_id"]): json.dumps(row["solution"], separators=(",", ":"))
        for row in rows
    }


def _public_metrics() -> dict[str, tuple[str, int]]:
    path = Path("benchmark/challenge/v1/public/metrics.json")
    payload = cast("dict[str, object]", json.loads(path.read_text(encoding="utf-8")))
    rows = cast("list[dict[str, object]]", payload["metrics"])
    return {str(row["puzzle_id"]): (str(row["family"]), int(cast("int", row["N"]))) for row in rows}


def test_analysis_validates_complete_paired_grid_and_solutions(tmp_path: Path) -> None:
    protocol = load_protocol(DEFAULT_PROTOCOL)
    public_splits = cast(
        "dict[str, object]",
        json.loads(Path("benchmark/challenge/v1/public/splits.json").read_text(encoding="utf-8")),
    )
    puzzle_ids = cast("list[str]", public_splits["dev"])[:2]
    split_path = tmp_path / "splits.json"
    split_path.write_text(json.dumps({"train": [], "dev": [], "test": puzzle_ids}), encoding="utf-8")
    tiny = replace(
        protocol,
        seeds=(0, 1),
        sealed_corpus=protocol.public_corpus,
        sealed_splits=split_path,
        bootstrap_replicates=_BOOTSTRAP_TEST_REPLICATES,
        bootstrap_seed=3,
    )
    certificates = _public_certificates()
    metrics = _public_metrics()
    config_hash = SolverConfig.from_toml(tiny.config).config_hash()
    rows: list[dict[str, object]] = []
    for puzzle_id in puzzle_ids:
        family, n = metrics[puzzle_id]
        for seed in tiny.seeds:
            for condition, frozen in tiny.condition_map().items():
                solved = not frozen
                rows.append(
                    {
                        "puzzle_id": puzzle_id,
                        "family": family,
                        "N": n,
                        "seed": seed,
                        "global_seed": tiny.global_seed,
                        "condition": condition,
                        "freeze_pheromone": frozen,
                        "config_hash": config_hash,
                        "path_budget": tiny.constructed_path_budget,
                        "solved": solved,
                        "infeasible": False,
                        "feasibility_reason": None,
                        "best_fitness": 1.0 if solved else 0.0,
                        "best_fitness_normalised": 1.0 if solved else 0.0,
                        "iters": 1,
                        "wall_ms": 1.0,
                        "solution_json": certificates[puzzle_id] if solved else None,
                        "failed": False,
                        "failure_reason": None,
                        "git_sha": "deadbeef",
                        "git_dirty": False,
                        "versions_json": "{}",
                    }
                )
    results_path = tmp_path / "results.parquet"
    pl.DataFrame(rows).write_parquet(results_path)
    output = tmp_path / "analysis"
    report = analyze(tiny, results_path=results_path, output_dir=output)
    primary = cast("dict[str, object]", report["primary"])
    assert primary["estimate"] == 1.0
    assert primary["ci_lower"] == 1.0
    assert primary["ci_upper"] == 1.0
    assert primary["classification"] == "helpful"
    assert report["validated_solutions"] == _EXPECTED_VALIDATED_SOLUTIONS
    assert (output / "report.json").exists()
    assert (output / "puzzle_effects.parquet").exists()
    assert (output / "primary_bootstrap.parquet").exists()

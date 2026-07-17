"""Verify, smoke-test, and execute the frozen Challenge v1 experiment."""

from __future__ import annotations

import argparse
import json
import os
import platform
import subprocess  # nosec B404
import traceback
from collections.abc import Sequence
from datetime import UTC, datetime
from itertools import pairwise
from pathlib import Path
from typing import cast

import cbor2
import polars as pl
from joblib import Parallel, delayed  # pyright: ignore[reportMissingTypeStubs]

from experiments.challenge_v1.protocol import (
    DEFAULT_PROTOCOL,
    REPO_ROOT,
    ConfirmatoryProtocol,
    file_sha256,
    load_protocol,
)
from zipmould.challenge import canonical_json_bytes, sha256_hex
from zipmould.config import SolverConfig
from zipmould.io.puzzles import load_corpus, load_split
from zipmould.puzzle import Coord, Puzzle
from zipmould.solver.api import RunResult, solve

_BATCH_SIZE = 150
_SMOKE_PUZZLES = 2
_SMOKE_SEEDS = (0, 1)


def _git_output(*args: str) -> str:
    completed = subprocess.run(  # noqa: S603  # nosec B603 B607
        ["git", *args],  # noqa: S607
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def _read_json(path: Path) -> dict[str, object]:
    value: object = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        msg = f"expected JSON object at {path}"
        raise ValueError(msg)
    return {str(key): item for key, item in cast("dict[object, object]", value).items()}


def _canonical_cbor_sha256(path: Path) -> str:
    with path.open("rb") as handle:
        payload: object = cbor2.load(handle)
    return sha256_hex(canonical_json_bytes(payload))


def _canonical_json_sha256(path: Path) -> str:
    payload: object = json.loads(path.read_text(encoding="utf-8"))
    return sha256_hex(canonical_json_bytes(payload))


def _cpu_model() -> str:
    cpuinfo = Path("/proc/cpuinfo")
    if cpuinfo.exists():
        for line in cpuinfo.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.lower().startswith("model name") and ":" in line:
                return line.split(":", 1)[1].strip()
    return platform.processor() or "unknown"


def verify_release(protocol: ConfirmatoryProtocol, *, require_tag: bool, require_sealed: bool) -> dict[str, object]:
    """Verify release and lock invariants without running a solver."""
    sha = _git_output("rev-parse", "HEAD")
    dirty = bool(_git_output("status", "--porcelain"))
    tags = tuple(filter(None, _git_output("tag", "--points-at", "HEAD").splitlines()))
    if require_tag and dirty:
        msg = "confirmatory execution requires a clean worktree"
        raise ValueError(msg)
    if require_tag and protocol.required_tag not in tags:
        msg = f"confirmatory execution requires tag {protocol.required_tag!r} at HEAD"
        raise ValueError(msg)

    lock = _read_json(protocol.test_lock)
    checks: dict[str, object] = {
        "study_id": protocol.study_id,
        "git_sha": sha,
        "git_dirty": dirty,
        "head_tags": list(tags),
        "required_tag": protocol.required_tag,
        "config_hash": protocol.expected_config_hash,
        "test_count": lock["test_count"],
        "test_corpus_sha256": lock["corpus_sha256"],
        "sealed_material_required": require_sealed,
    }
    if require_sealed:
        required = (
            protocol.sealed_corpus,
            protocol.sealed_splits,
            protocol.sealed_corpus.with_name("certificates.json"),
            protocol.sealed_corpus.with_name("metrics.json"),
            protocol.sealed_corpus.with_name("OPENED.json"),
        )
        missing = [str(path) for path in required if not path.exists()]
        if missing:
            msg = f"sealed test is not fully unlocked: {', '.join(missing)}"
            raise FileNotFoundError(msg)
        if _canonical_cbor_sha256(protocol.sealed_corpus) != lock["corpus_sha256"]:
            msg = "unlocked test corpus does not match its commitment"
            raise ValueError(msg)
        if _canonical_json_sha256(protocol.sealed_corpus.with_name("certificates.json")) != lock["certificate_sha256"]:
            msg = "unlocked test certificates do not match their commitment"
            raise ValueError(msg)
        test_ids = load_split("test", protocol.sealed_splits)
        if len(test_ids) != int(cast("int", lock["test_count"])) or len(set(test_ids)) != len(test_ids):
            msg = "unlocked test split is incomplete or contains duplicate ids"
            raise ValueError(msg)
        corpus = load_corpus(protocol.sealed_corpus)
        if set(test_ids) != set(corpus):
            msg = "unlocked corpus and test split ids differ"
            raise ValueError(msg)
        checks["sealed_material_verified"] = True
    return checks


def _load_worker_corpus(path: str) -> dict[str, Puzzle]:
    return load_corpus(path)


def _load_worker_config(path: str) -> SolverConfig:
    return SolverConfig.from_toml(Path(path))


def validate_solution(puzzle: Puzzle, solution: Sequence[Coord]) -> None:
    """Reject a claimed solution that violates any puzzle constraint."""
    path = tuple(solution)
    if len(path) != puzzle.L() or len(set(path)) != puzzle.L() or set(path) != set(puzzle.free_cells()):
        msg = f"{puzzle.id}: returned path is not Hamiltonian over the free cells"
        raise ValueError(msg)
    if path[0] != puzzle.waypoints[0] or path[-1] != puzzle.waypoints[-1]:
        msg = f"{puzzle.id}: returned endpoints do not match first/last waypoints"
        raise ValueError(msg)
    position = {cell: index for index, cell in enumerate(path)}
    if [position[waypoint] for waypoint in puzzle.waypoints] != sorted(position[w] for w in puzzle.waypoints):
        msg = f"{puzzle.id}: returned path visits waypoints out of order"
        raise ValueError(msg)
    for before, after in pairwise(path):
        if abs(before[0] - after[0]) + abs(before[1] - after[1]) != 1:
            msg = f"{puzzle.id}: returned path contains a non-adjacent move"
            raise ValueError(msg)
        if tuple(sorted((before, after))) in puzzle.walls:
            msg = f"{puzzle.id}: returned path crosses a wall"
            raise ValueError(msg)


def _result_row(
    result: RunResult,
    *,
    puzzle: Puzzle,
    family: str,
    n: int,
    seed: int,
    global_seed: int,
    condition: str,
    freeze_pheromone: bool,
    path_budget: int,
) -> dict[str, object]:
    if result.solved:
        if result.solution is None:
            msg = f"{puzzle.id}: solved result has no solution"
            raise ValueError(msg)
        validate_solution(puzzle, result.solution)
    solution_json = (
        json.dumps([[row, column] for row, column in result.solution], separators=(",", ":"))
        if result.solution is not None
        else None
    )
    return {
        "puzzle_id": puzzle.id,
        "family": family,
        "N": n,
        "seed": seed,
        "global_seed": global_seed,
        "condition": condition,
        "freeze_pheromone": freeze_pheromone,
        "config_hash": result.config_hash,
        "path_budget": path_budget,
        "solved": result.solved,
        "infeasible": result.infeasible,
        "feasibility_reason": result.feasibility_reason,
        "best_fitness": result.best_fitness,
        "best_fitness_normalised": result.best_fitness_normalised,
        "iters": result.iters_used,
        "wall_ms": result.wall_clock_s * 1000.0,
        "solution_json": solution_json,
        "failed": False,
        "failure_reason": None,
        "git_sha": result.git_sha,
        "git_dirty": result.git_dirty,
        "versions_json": json.dumps(dict(result.versions), sort_keys=True, separators=(",", ":")),
    }


def _failed_row(
    *,
    puzzle_id: str,
    family: str,
    n: int,
    seed: int,
    global_seed: int,
    condition: str,
    freeze_pheromone: bool,
    config_hash: str,
    path_budget: int,
    reason: str,
) -> dict[str, object]:
    return {
        "puzzle_id": puzzle_id,
        "family": family,
        "N": n,
        "seed": seed,
        "global_seed": global_seed,
        "condition": condition,
        "freeze_pheromone": freeze_pheromone,
        "config_hash": config_hash,
        "path_budget": path_budget,
        "solved": False,
        "infeasible": False,
        "feasibility_reason": None,
        "best_fitness": 0.0,
        "best_fitness_normalised": 0.0,
        "iters": 0,
        "wall_ms": 0.0,
        "solution_json": None,
        "failed": True,
        "failure_reason": reason,
        "git_sha": "",
        "git_dirty": False,
        "versions_json": "{}",
    }


def _run_one(
    *,
    corpus_path: str,
    config_path: str,
    puzzle_id: str,
    family: str,
    n: int,
    seed: int,
    global_seed: int,
    condition: str,
    freeze_pheromone: bool,
    path_budget: int,
) -> dict[str, object]:
    config = _load_worker_config(config_path)
    try:
        puzzle = _load_worker_corpus(corpus_path)[puzzle_id]
        result = solve(
            puzzle,
            config,
            seed=seed,
            global_seed=global_seed,
            condition=condition,
            freeze_pheromone=freeze_pheromone,
        )
        return _result_row(
            result,
            puzzle=puzzle,
            family=family,
            n=n,
            seed=seed,
            global_seed=global_seed,
            condition=condition,
            freeze_pheromone=freeze_pheromone,
            path_budget=path_budget,
        )
    except Exception as exc:
        return _failed_row(
            puzzle_id=puzzle_id,
            family=family,
            n=n,
            seed=seed,
            global_seed=global_seed,
            condition=condition,
            freeze_pheromone=freeze_pheromone,
            config_hash=config.config_hash(),
            path_budget=path_budget,
            reason=f"{type(exc).__name__}: {exc}\n{traceback.format_exc()}",
        )


def _metrics_by_id(path: Path) -> dict[str, tuple[str, int]]:
    payload = _read_json(path)
    raw_metrics = payload.get("metrics")
    if not isinstance(raw_metrics, list):
        msg = f"metrics payload at {path} has no metrics list"
        raise ValueError(msg)
    output: dict[str, tuple[str, int]] = {}
    for item in cast("list[object]", raw_metrics):
        row = _read_object(item, "metrics row")
        output[str(row["puzzle_id"])] = (str(row["family"]), int(cast("int", row["N"])))
    return output


def _read_object(value: object, label: str) -> dict[str, object]:
    if not isinstance(value, dict):
        msg = f"{label} must be an object"
        raise ValueError(msg)
    return {str(key): item for key, item in cast("dict[object, object]", value).items()}


def _jobs(
    protocol: ConfirmatoryProtocol,
    *,
    corpus_path: Path,
    puzzle_ids: Sequence[str],
    seeds: Sequence[int],
) -> list[dict[str, object]]:
    metrics = _metrics_by_id(corpus_path.with_name("metrics.json"))
    return [
        {
            "corpus_path": str(corpus_path),
            "config_path": str(protocol.config),
            "puzzle_id": puzzle_id,
            "family": metrics[puzzle_id][0],
            "n": metrics[puzzle_id][1],
            "seed": seed,
            "global_seed": protocol.global_seed,
            "condition": condition.name,
            "freeze_pheromone": condition.freeze_pheromone,
            "path_budget": protocol.constructed_path_budget,
        }
        for puzzle_id in puzzle_ids
        for seed in seeds
        for condition in protocol.conditions
    ]


def _key(row: dict[str, object]) -> tuple[str, int, str]:
    return (str(row["puzzle_id"]), int(cast("int", row["seed"])), str(row["condition"]))


def _run_jobs(jobs: Sequence[dict[str, object]], workers: int) -> list[dict[str, object]]:
    return cast(
        "list[dict[str, object]]",
        Parallel(n_jobs=workers, backend="loky", verbose=0)(delayed(_run_one)(**job) for job in jobs),
    )


def _write_rows(rows: Sequence[dict[str, object]], path: Path) -> None:
    ordered = sorted(rows, key=_key)
    pl.DataFrame(ordered).write_parquet(path, compression="zstd", statistics=True)


def run_smoke(protocol: ConfirmatoryProtocol, *, workers: int) -> dict[str, object]:
    """Exercise both arms on a tiny public-dev subset without touching test."""
    puzzle_ids = load_split("dev", protocol.public_splits)[:_SMOKE_PUZZLES]
    jobs = _jobs(protocol, corpus_path=protocol.public_corpus, puzzle_ids=puzzle_ids, seeds=_SMOKE_SEEDS)
    rows = _run_jobs(jobs, workers)
    failures = [row for row in rows if bool(row["failed"])]
    output = protocol.output_dir.parent / "confirmatory-smoke"
    output.mkdir(parents=True, exist_ok=True)
    _write_rows(rows, output / "results.parquet")
    summary: dict[str, object] = {
        "mode": "public-dev-smoke",
        "test_material_accessed": False,
        "jobs": len(rows),
        "failures": len(failures),
        "conditions": sorted({str(row["condition"]) for row in rows}),
        "puzzles": puzzle_ids,
        "seeds": list(_SMOKE_SEEDS),
    }
    (output / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if failures:
        msg = f"confirmatory smoke test had {len(failures)} failed jobs"
        raise RuntimeError(msg)
    return summary


def _checkpoint_rows(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        return []
    return cast("list[dict[str, object]]", pl.read_parquet(path).to_dicts())


def _validate_checkpoint(
    protocol: ConfirmatoryProtocol,
    rows: Sequence[dict[str, object]],
    release: dict[str, object],
) -> None:
    expected_config = protocol.expected_config_hash
    expected_conditions = protocol.condition_map()
    for row in rows:
        condition = str(row["condition"])
        if condition not in expected_conditions or bool(row["freeze_pheromone"]) != expected_conditions[condition]:
            msg = "checkpoint condition does not match the frozen intervention"
            raise ValueError(msg)
        if (
            str(row["config_hash"]) != expected_config
            or int(cast("int", row["path_budget"])) != protocol.constructed_path_budget
        ):
            msg = "checkpoint configuration or path budget drifted"
            raise ValueError(msg)
        if int(cast("int", row["global_seed"])) != protocol.global_seed:
            msg = "checkpoint global seed drifted"
            raise ValueError(msg)
        if str(row["git_sha"]) != release["git_sha"] or bool(row["git_dirty"]):
            msg = "checkpoint was not produced from the clean tagged release"
            raise ValueError(msg)
        if bool(row["failed"]) or bool(row["infeasible"]):
            msg = "checkpoint contains a failed or infeasible run"
            raise ValueError(msg)


def run_confirmatory(
    protocol: ConfirmatoryProtocol,
    protocol_path: Path,
    *,
    workers: int,
    batch_size: int,
) -> dict[str, object]:
    """Run or resume the exact sealed grid and preserve a checkpoint per batch."""
    release = verify_release(protocol, require_tag=True, require_sealed=True)
    output = protocol.output_dir
    output.mkdir(parents=True, exist_ok=True)
    results_path = output / "results.parquet"
    manifest_path = output / "run_manifest.json"
    if results_path.exists() or manifest_path.exists():
        msg = f"final confirmatory output already exists under {output}; refusing to rerun"
        raise FileExistsError(msg)

    started = datetime.now(UTC)
    puzzle_ids = load_split("test", protocol.sealed_splits)
    jobs = _jobs(protocol, corpus_path=protocol.sealed_corpus, puzzle_ids=puzzle_ids, seeds=protocol.seeds)
    checkpoint_path = output / "checkpoint.parquet"
    existing = _checkpoint_rows(checkpoint_path)
    _validate_checkpoint(protocol, existing, release)
    existing_by_key = {_key(row): row for row in existing}
    if len(existing_by_key) != len(existing):
        msg = "checkpoint contains duplicate puzzle/seed/condition rows"
        raise ValueError(msg)
    pending = [
        job
        for job in jobs
        if (str(job["puzzle_id"]), int(cast("int", job["seed"])), str(job["condition"]))
        not in existing_by_key
    ]

    all_rows = list(existing)
    for offset in range(0, len(pending), batch_size):
        batch = pending[offset : offset + batch_size]
        all_rows.extend(_run_jobs(batch, workers))
        _write_rows(all_rows, checkpoint_path)
        completed = len(all_rows)
        print(json.dumps({"completed": completed, "total": len(jobs)}, sort_keys=True))

    if len(all_rows) != len(jobs):
        msg = f"confirmatory grid incomplete: expected {len(jobs)}, got {len(all_rows)}"
        raise RuntimeError(msg)
    failures = [row for row in all_rows if bool(row["failed"])]
    _write_rows(all_rows, results_path)
    completed = datetime.now(UTC)
    manifest = {
        **release,
        "protocol_path": str(protocol_path.relative_to(REPO_ROOT)),
        "protocol_sha256": file_sha256(protocol_path),
        "config_path": str(protocol.config.relative_to(REPO_ROOT)),
        "config_file_sha256": file_sha256(protocol.config),
        "results_path": str(results_path.relative_to(REPO_ROOT)),
        "results_file_sha256": file_sha256(results_path),
        "workers": workers,
        "batch_size": batch_size,
        "started_utc": started.isoformat(),
        "completed_utc": completed.isoformat(),
        "elapsed_seconds": (completed - started).total_seconds(),
        "platform": platform.platform(),
        "cpu_model": _cpu_model(),
        "logical_cpus": os.cpu_count(),
        "rows": len(all_rows),
        "failed_rows": len(failures),
        "solved_rows": sum(bool(row["solved"]) for row in all_rows),
        "versions": json.loads(str(all_rows[0]["versions_json"])),
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if failures:
        msg = f"confirmatory execution completed with {len(failures)} failed rows; do not analyze"
        raise RuntimeError(msg)
    return manifest


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", type=Path, default=DEFAULT_PROTOCOL)
    subparsers = parser.add_subparsers(dest="command", required=True)
    verify = subparsers.add_parser("verify")
    verify.add_argument("--final", action="store_true", help="require the release tag and unlocked committed corpus")
    smoke = subparsers.add_parser("smoke")
    smoke.add_argument("--workers", type=int, default=2)
    run = subparsers.add_parser("run")
    run.add_argument("--workers", type=int, default=-1)
    run.add_argument("--batch-size", type=int, default=_BATCH_SIZE)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    protocol_path = Path(args.protocol).resolve()
    protocol = load_protocol(protocol_path)
    command = str(args.command)
    if command == "verify":
        payload = verify_release(protocol, require_tag=bool(args.final), require_sealed=bool(args.final))
    elif command == "smoke":
        payload = run_smoke(protocol, workers=int(args.workers))
    elif command == "run":
        batch_size = int(args.batch_size)
        if batch_size <= 0:
            msg = "batch size must be positive"
            raise ValueError(msg)
        payload = run_confirmatory(protocol, protocol_path, workers=int(args.workers), batch_size=batch_size)
    else:  # pragma: no cover - argparse enforces commands
        msg = f"unknown command {command!r}"
        raise ValueError(msg)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

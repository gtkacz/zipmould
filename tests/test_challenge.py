"""Determinism, validity, and lock-integrity tests for Challenge v1."""

from __future__ import annotations

import json
from itertools import pairwise
from pathlib import Path
from typing import cast

import cbor2
import pytest

from zipmould.challenge import (
    ChallengeSpec,
    FamilySpec,
    StableRng,
    build_test_lock,
    corpus_payload,
    generate_puzzle,
    generate_split,
    load_challenge_spec,
    sealed_seed_commitment,
    verify_test_lock,
)
from zipmould.feasibility import precheck
from zipmould.puzzle import load_puzzles_cbor

_GRID_SIZE = 6
_CELL_COUNT = _GRID_SIZE * _GRID_SIZE
_PUBLIC_PUZZLE_COUNT = 300


def _tiny_spec() -> ChallengeSpec:
    family = FamilySpec(
        name="tiny-deceptive",
        wall_rate=0.2,
        waypoint_fraction=0.2,
        min_waypoints=4,
        max_waypoints=8,
        waypoint_mode="deceptive",
        partition_period=0,
        partition_wall_rate=0.0,
    )
    return ChallengeSpec(
        format_version=1,
        generator_version="zipmould-challenge-v1",
        sizes=(_GRID_SIZE,),
        counts={"train": 1, "dev": 1, "test": 1},
        public_seeds={"train": "train", "dev": "dev"},
        backbite_steps_per_cell=4,
        families=(family,),
        strata=((family.name, _GRID_SIZE),),
        calibration={},
        confirmatory={},
    )


def test_stable_rng_has_frozen_sequence() -> None:
    rng = StableRng(123456789)
    assert [rng.next_u64() for _ in range(4)] == [
        2466975172287755897,
        8832083440362974766,
        3534771765162737125,
        9592110948284743397,
    ]


def test_generate_puzzle_is_deterministic_and_certificate_is_loadable(tmp_path: Path) -> None:
    spec = _tiny_spec()
    family = spec.families[0]
    first = generate_puzzle(
        split="train",
        family=family,
        n=_GRID_SIZE,
        ordinal=0,
        master_seed="deterministic",
        backbite_steps_per_cell=4,
    )
    second = generate_puzzle(
        split="train",
        family=family,
        n=_GRID_SIZE,
        ordinal=0,
        master_seed="deterministic",
        backbite_steps_per_cell=4,
    )
    assert first == second
    assert len(first.solution) == _CELL_COUNT
    assert len(set(first.solution)) == _CELL_COUNT

    path = tmp_path / "puzzles.cbor"
    with path.open("wb") as handle:
        cbor2.dump(corpus_payload([first]), handle, canonical=True)
    loaded = load_puzzles_cbor(path)
    puzzle = loaded[str(first.puzzle["id"])]
    assert puzzle.N == _GRID_SIZE
    assert len(cast("list[object]", first.puzzle["waypoints"])) == puzzle.K


def test_walls_never_cross_the_planted_certificate() -> None:
    generated = generate_split(_tiny_spec(), "dev", "wall-check")
    item = generated[0]
    raw_walls = cast("list[list[list[int]]]", item.puzzle["walls"])
    walls = {
        tuple(sorted(((int(a[0]), int(a[1])), (int(b[0]), int(b[1])))))
        for a, b in raw_walls
    }
    certificate_edges = {
        tuple(sorted((a, b)))
        for a, b in pairwise(item.solution)
    }
    assert walls.isdisjoint(certificate_edges)


def test_test_lock_detects_secret_or_payload_tampering() -> None:
    spec = _tiny_spec()
    secret = "ab" * 32
    lock = build_test_lock(spec, secret)
    verified = verify_test_lock(spec, secret, lock)
    assert len(verified) == 1
    assert lock["seed_commitment_sha256"] == sealed_seed_commitment(secret)

    with pytest.raises(ValueError, match="seed_commitment_sha256"):
        verify_test_lock(spec, "cd" * 32, lock)

    tampered = dict(lock)
    tampered["corpus_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="corpus_sha256"):
        verify_test_lock(spec, secret, tampered)


def test_repository_spec_is_balanced_and_seals_test() -> None:
    spec = load_challenge_spec("benchmark/challenge/v1/spec.json")
    strata = len(spec.strata)
    assert spec.counts["train"] % strata == 0
    assert spec.counts["dev"] % strata == 0
    assert spec.counts["test"] % strata == 0
    assert spec.counts == {"train": 200, "dev": 100, "test": 150}
    assert spec.strata == (
        ("chambered-deceptive", 12),
        ("open-deceptive", 14),
        ("open-deceptive", 16),
        ("sparse-deceptive", 12),
        ("sparse-deceptive", 14),
    )


def test_public_corpus_matches_all_independent_certificates() -> None:
    root = Path("benchmark/challenge/v1/public")
    corpus = load_puzzles_cbor(root / "puzzles.cbor")
    certificate_payload = cast(
        "dict[str, object]",
        json.loads((root / "certificates.json").read_text(encoding="utf-8")),
    )
    raw_certificates = certificate_payload["certificates"]
    certificates: dict[str, tuple[tuple[int, int], ...]] = {}
    for row in cast("list[dict[str, object]]", raw_certificates):
        raw_solution = cast("list[list[int]]", row["solution"])
        certificates[str(row["puzzle_id"])] = tuple(
            (int(cell[0]), int(cell[1])) for cell in raw_solution
        )
    assert len(corpus) == _PUBLIC_PUZZLE_COUNT
    assert set(corpus) == set(certificates)

    for puzzle_id, puzzle in corpus.items():
        solution = certificates[puzzle_id]
        assert len(solution) == puzzle.L()
        assert len(set(solution)) == puzzle.L()
        assert set(solution) == set(puzzle.free_cells())
        assert solution[0] == puzzle.waypoints[0]
        assert solution[-1] == puzzle.waypoints[-1]
        positions = {cell: index for index, cell in enumerate(solution)}
        waypoint_positions = [positions[waypoint] for waypoint in puzzle.waypoints]
        assert waypoint_positions == sorted(waypoint_positions)
        assert all(
            abs(a[0] - b[0]) + abs(a[1] - b[1]) == 1 and tuple(sorted((a, b))) not in puzzle.walls
            for a, b in pairwise(solution)
        )
        assert precheck(puzzle).feasible

"""Typed loading and invariant checks for the frozen Challenge v1 protocol."""

from __future__ import annotations

import hashlib
import json
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import cast

from zipmould.challenge import challenge_spec_sha256, load_challenge_spec
from zipmould.config import SolverConfig

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PROTOCOL = Path(__file__).with_name("protocol.toml")
EXPECTED_CONDITIONS = {"full-feedback": False, "feedback-frozen": True}
EXPECTED_SEEDS = tuple(range(30))
EXPECTED_BOOTSTRAP_REPLICATES = 10_000
EXPECTED_CONFIDENCE_LEVEL = 0.95
EXPECTED_PRACTICAL_EFFECT = 0.05
EXPECTED_TEST_COUNT = 150


@dataclass(frozen=True, slots=True)
class ConditionSpec:
    """One arm of the paired mechanism intervention."""

    name: str
    freeze_pheromone: bool


@dataclass(frozen=True, slots=True)
class ConfirmatoryProtocol:
    """Immutable fields that determine the confirmatory experiment."""

    protocol_version: int
    study_id: str
    benchmark_spec: Path
    test_lock: Path
    public_corpus: Path
    public_splits: Path
    sealed_corpus: Path
    sealed_splits: Path
    config: Path
    expected_config_hash: str
    expected_spec_sha256: str
    expected_test_corpus_sha256: str
    expected_test_certificate_sha256: str
    output_dir: Path
    required_tag: str
    global_seed: int
    seeds: tuple[int, ...]
    constructed_path_budget: int
    bootstrap_replicates: int
    bootstrap_seed: int
    confidence_level: float
    practical_effect: float
    primary_estimand: str
    bootstrap_unit: str
    rng_coupling: str
    conditions: tuple[ConditionSpec, ...]

    def condition_map(self) -> dict[str, bool]:
        return {condition.name: condition.freeze_pheromone for condition in self.conditions}


def _repo_path(value: object) -> Path:
    path = Path(str(value))
    return path if path.is_absolute() else REPO_ROOT / path


def _as_dict(value: object, label: str) -> dict[str, object]:
    if not isinstance(value, dict):
        msg = f"{label} must be a table"
        raise ValueError(msg)
    return {str(key): item for key, item in cast("dict[object, object]", value).items()}


def _as_int_list(value: object, label: str) -> tuple[int, ...]:
    if not isinstance(value, list):
        msg = f"{label} must be a list of integers"
        raise ValueError(msg)
    items = cast("list[object]", value)
    if not all(isinstance(item, int) and not isinstance(item, bool) for item in items):
        msg = f"{label} must be a list of integers"
        raise ValueError(msg)
    return tuple(cast("list[int]", items))


def _as_int(value: object, label: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        msg = f"{label} must be an integer"
        raise ValueError(msg)
    return value


def _as_float(value: object, label: str) -> float:
    if not isinstance(value, int | float) or isinstance(value, bool):
        msg = f"{label} must be numeric"
        raise ValueError(msg)
    return float(value)


def _as_bool(value: object, label: str) -> bool:
    if not isinstance(value, bool):
        msg = f"{label} must be boolean"
        raise ValueError(msg)
    return value


def load_protocol(path: Path = DEFAULT_PROTOCOL) -> ConfirmatoryProtocol:
    """Load the protocol and reject any drift from its confirmatory invariants."""
    with path.open("rb") as handle:
        raw = _as_dict(tomllib.load(handle), "protocol")
    raw_conditions = raw.get("conditions")
    if not isinstance(raw_conditions, list):
        msg = "conditions must be an array of tables"
        raise ValueError(msg)
    conditions = tuple(
        ConditionSpec(
            name=str(condition["name"]),
            freeze_pheromone=_as_bool(condition["freeze_pheromone"], "condition.freeze_pheromone"),
        )
        for item in cast("list[object]", raw_conditions)
        for condition in (_as_dict(item, "condition"),)
    )
    protocol = ConfirmatoryProtocol(
        protocol_version=_as_int(raw["protocol_version"], "protocol_version"),
        study_id=str(raw["study_id"]),
        benchmark_spec=_repo_path(raw["benchmark_spec"]),
        test_lock=_repo_path(raw["test_lock"]),
        public_corpus=_repo_path(raw["public_corpus"]),
        public_splits=_repo_path(raw["public_splits"]),
        sealed_corpus=_repo_path(raw["sealed_corpus"]),
        sealed_splits=_repo_path(raw["sealed_splits"]),
        config=_repo_path(raw["config"]),
        expected_config_hash=str(raw["expected_config_hash"]),
        expected_spec_sha256=str(raw["expected_spec_sha256"]),
        expected_test_corpus_sha256=str(raw["expected_test_corpus_sha256"]),
        expected_test_certificate_sha256=str(raw["expected_test_certificate_sha256"]),
        output_dir=_repo_path(raw["output_dir"]),
        required_tag=str(raw["required_tag"]),
        global_seed=_as_int(raw["global_seed"], "global_seed"),
        seeds=_as_int_list(raw["seeds"], "seeds"),
        constructed_path_budget=_as_int(raw["constructed_path_budget"], "constructed_path_budget"),
        bootstrap_replicates=_as_int(raw["bootstrap_replicates"], "bootstrap_replicates"),
        bootstrap_seed=_as_int(raw["bootstrap_seed"], "bootstrap_seed"),
        confidence_level=_as_float(raw["confidence_level"], "confidence_level"),
        practical_effect=_as_float(raw["practical_effect"], "practical_effect"),
        primary_estimand=str(raw["primary_estimand"]),
        bootstrap_unit=str(raw["bootstrap_unit"]),
        rng_coupling=str(raw["rng_coupling"]),
        conditions=conditions,
    )
    validate_protocol(protocol)
    return protocol


def validate_protocol(protocol: ConfirmatoryProtocol) -> None:
    """Check the scientific invariants that must not change after test unlock."""
    if protocol.protocol_version != 1 or protocol.study_id != "zipmould-challenge-v1-confirmatory":
        msg = "unsupported confirmatory protocol identity"
        raise ValueError(msg)
    if protocol.seeds != EXPECTED_SEEDS:
        msg = "confirmatory seeds must be exactly 0..29 in order"
        raise ValueError(msg)
    if protocol.condition_map() != EXPECTED_CONDITIONS or len(protocol.conditions) != len(EXPECTED_CONDITIONS):
        msg = "conditions must be exactly full-feedback and feedback-frozen"
        raise ValueError(msg)
    if protocol.bootstrap_replicates != EXPECTED_BOOTSTRAP_REPLICATES or protocol.bootstrap_seed < 0:
        msg = "confirmatory bootstrap must use 10,000 replicates and a non-negative seed"
        raise ValueError(msg)
    if (
        protocol.confidence_level != EXPECTED_CONFIDENCE_LEVEL
        or protocol.practical_effect != EXPECTED_PRACTICAL_EFFECT
    ):
        msg = "confirmatory interval/effect thresholds must remain 0.95 and 0.05"
        raise ValueError(msg)
    if protocol.bootstrap_unit != "puzzle_within_frozen_stratum":
        msg = "bootstrap unit drifted from the frozen puzzle-within-stratum design"
        raise ValueError(msg)
    if protocol.rng_coupling != "same_initial_seed_not_common_random_numbers_after_intervention":
        msg = "RNG comparison behavior drifted from the frozen design"
        raise ValueError(msg)
    config = SolverConfig.from_toml(protocol.config)
    if config.config_hash() != protocol.expected_config_hash:
        msg = "confirmatory config hash drifted from the frozen protocol"
        raise ValueError(msg)
    actual_budget = config.population * config.iter_cap
    if actual_budget != protocol.constructed_path_budget:
        msg = f"config budget {actual_budget} does not match protocol {protocol.constructed_path_budget}"
        raise ValueError(msg)
    spec = load_challenge_spec(protocol.benchmark_spec)
    lock = _as_dict(json.loads(protocol.test_lock.read_text(encoding="utf-8")), "test lock")
    if challenge_spec_sha256(spec) != protocol.expected_spec_sha256:
        msg = "challenge spec hash drifted from the frozen protocol"
        raise ValueError(msg)
    lock_matches = (
        lock.get("spec_sha256") == protocol.expected_spec_sha256
        and lock.get("corpus_sha256") == protocol.expected_test_corpus_sha256
        and lock.get("certificate_sha256") == protocol.expected_test_certificate_sha256
        and lock.get("test_count") == EXPECTED_TEST_COUNT
    )
    if not lock_matches:
        msg = "test lock does not match the frozen challenge spec/count"
        raise ValueError(msg)


def file_sha256(path: Path) -> str:
    """Hash one release artifact without normalizing its bytes."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()

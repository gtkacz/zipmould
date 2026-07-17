"""Deterministic synthetic challenge generation and sealed-test commitments.

The generator plants a Hamiltonian path, derives ordered waypoints from that
path, and adds walls only to edges outside the certificate.  Train/dev seeds
are public.  A test seed can remain secret while hashes commit to the exact
corpus and certificates produced from it.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from itertools import pairwise
from pathlib import Path
from typing import Any, Literal, cast

Coord = tuple[int, int]
CellEdge = tuple[int, int]
SplitName = Literal["train", "dev", "test"]
WaypointMode = Literal["balanced", "deceptive"]

_MASK64 = (1 << 64) - 1
_MIN_GRID_SIZE = 4
_MIN_WAYPOINTS = 2
_MIN_BACKBITE_DISTANCE = 2
_GENERATOR_DOMAIN = b"zipmould-challenge-v1\0"
_TEST_SEED_DOMAIN = b"zipmould-challenge-v1:test-seed\0"


@dataclass(frozen=True, slots=True)
class FamilySpec:
    """One structural family in the challenge distribution."""

    name: str
    wall_rate: float
    waypoint_fraction: float
    min_waypoints: int
    max_waypoints: int
    waypoint_mode: WaypointMode
    partition_period: int
    partition_wall_rate: float


@dataclass(frozen=True, slots=True)
class ChallengeSpec:
    """Frozen public generator specification."""

    format_version: int
    generator_version: str
    sizes: tuple[int, ...]
    counts: dict[SplitName, int]
    public_seeds: dict[Literal["train", "dev"], str]
    backbite_steps_per_cell: int
    families: tuple[FamilySpec, ...]
    strata: tuple[tuple[str, int], ...]
    calibration: dict[str, object]
    confirmatory: dict[str, object]


@dataclass(frozen=True, slots=True)
class GeneratedPuzzle:
    """One generated puzzle together with its hidden solution certificate."""

    puzzle: dict[str, object]
    solution: tuple[Coord, ...]
    metrics: dict[str, int | float | str]


class StableRng:
    """Small SplitMix64 RNG with stable cross-Python behavior."""

    __slots__ = ("_state",)

    def __init__(self, seed: int) -> None:
        self._state = seed & _MASK64

    def next_u64(self) -> int:
        self._state = (self._state + 0x9E3779B97F4A7C15) & _MASK64
        z = self._state
        z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & _MASK64
        z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & _MASK64
        return (z ^ (z >> 31)) & _MASK64

    def randbelow(self, upper: int) -> int:
        if upper <= 0:
            msg = f"upper must be positive, got {upper}"
            raise ValueError(msg)
        limit = (1 << 64) - ((1 << 64) % upper)
        while True:
            value = self.next_u64()
            if value < limit:
                return value % upper

    def random(self) -> float:
        return float(self.next_u64() >> 11) / float(1 << 53)

    def shuffle(self, values: list[Any]) -> None:
        for i in range(len(values) - 1, 0, -1):
            j = self.randbelow(i + 1)
            values[i], values[j] = values[j], values[i]


def _as_dict(value: object, *, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        msg = f"{label} must be an object"
        raise ValueError(msg)
    return cast("dict[str, Any]", value)


def _as_int_dict(value: object, *, label: str) -> dict[str, int]:
    raw = _as_dict(value, label=label)
    return {str(k): int(v) for k, v in raw.items()}


def _as_str_dict(value: object, *, label: str) -> dict[str, str]:
    raw = _as_dict(value, label=label)
    return {str(k): str(v) for k, v in raw.items()}


def load_challenge_spec(path: Path | str) -> ChallengeSpec:  # noqa: PLR0912, PLR0915
    """Load and validate a challenge-v1 JSON specification."""
    raw = _as_dict(json.loads(Path(path).read_text(encoding="utf-8")), label="spec")
    raw_families = raw.get("families")
    if not isinstance(raw_families, list) or not raw_families:
        msg = "spec families must be a non-empty list"
        raise ValueError(msg)

    families: list[FamilySpec] = []
    for item in cast("list[object]", raw_families):
        f = _as_dict(item, label="family")
        mode = str(f["waypoint_mode"])
        if mode not in {"balanced", "deceptive"}:
            msg = f"unknown waypoint mode {mode!r}"
            raise ValueError(msg)
        family = FamilySpec(
            name=str(f["name"]),
            wall_rate=float(f["wall_rate"]),
            waypoint_fraction=float(f["waypoint_fraction"]),
            min_waypoints=int(f["min_waypoints"]),
            max_waypoints=int(f["max_waypoints"]),
            waypoint_mode=cast("WaypointMode", mode),
            partition_period=int(f["partition_period"]),
            partition_wall_rate=float(f["partition_wall_rate"]),
        )
        if not family.name or any(ch not in "abcdefghijklmnopqrstuvwxyz0123456789-" for ch in family.name):
            msg = f"family name must be lowercase kebab-case, got {family.name!r}"
            raise ValueError(msg)
        if not 0.0 <= family.wall_rate <= 1.0 or not 0.0 <= family.partition_wall_rate <= 1.0:
            msg = f"family {family.name}: wall rates must be in [0, 1]"
            raise ValueError(msg)
        if not 0.0 < family.waypoint_fraction <= 1.0:
            msg = f"family {family.name}: waypoint_fraction must be in (0, 1]"
            raise ValueError(msg)
        if not _MIN_WAYPOINTS <= family.min_waypoints <= family.max_waypoints:
            msg = f"family {family.name}: invalid waypoint bounds"
            raise ValueError(msg)
        families.append(family)

    raw_sizes = raw["sizes"]
    if not isinstance(raw_sizes, list):
        msg = "sizes must be a list of integers"
        raise ValueError(msg)
    raw_size_items = cast("list[object]", raw_sizes)
    if not all(isinstance(n, int) and not isinstance(n, bool) for n in raw_size_items):
        msg = "sizes must be a list of integers"
        raise ValueError(msg)
    sizes = tuple(cast("list[int]", raw_size_items))
    if not sizes or any(n < _MIN_GRID_SIZE for n in sizes):
        msg = "sizes must contain grid widths >= 4"
        raise ValueError(msg)

    raw_counts = _as_int_dict(raw["counts"], label="counts")
    counts: dict[SplitName, int] = {
        "train": raw_counts["train"],
        "dev": raw_counts["dev"],
        "test": raw_counts["test"],
    }
    family_names = {family.name for family in families}
    raw_strata = raw.get("strata")
    if not isinstance(raw_strata, list) or not raw_strata:
        msg = "spec strata must be a non-empty list"
        raise ValueError(msg)
    strata: list[tuple[str, int]] = []
    for raw_stratum in cast("list[object]", raw_strata):
        stratum = _as_dict(raw_stratum, label="stratum")
        family_name = str(stratum["family"])
        size = int(stratum["N"])
        if family_name not in family_names:
            msg = f"stratum references unknown family {family_name!r}"
            raise ValueError(msg)
        if size not in sizes:
            msg = f"stratum references size {size} outside declared sizes"
            raise ValueError(msg)
        pair = (family_name, size)
        if pair in strata:
            msg = f"duplicate stratum {family_name}/{size}"
            raise ValueError(msg)
        strata.append(pair)

    n_strata = len(strata)
    for split, count in counts.items():
        if count <= 0 or count % n_strata != 0:
            msg = f"{split} count {count} must be a positive multiple of {n_strata}"
            raise ValueError(msg)

    raw_seeds = _as_str_dict(raw["public_seeds"], label="public_seeds")
    public_seeds: dict[Literal["train", "dev"], str] = {
        "train": raw_seeds["train"],
        "dev": raw_seeds["dev"],
    }
    return ChallengeSpec(
        format_version=int(raw["format_version"]),
        generator_version=str(raw["generator_version"]),
        sizes=sizes,
        counts=counts,
        public_seeds=public_seeds,
        backbite_steps_per_cell=int(raw["backbite_steps_per_cell"]),
        families=tuple(families),
        strata=tuple(strata),
        calibration={str(k): v for k, v in _as_dict(raw["calibration"], label="calibration").items()},
        confirmatory={str(k): v for k, v in _as_dict(raw["confirmatory"], label="confirmatory").items()},
    )


def spec_to_dict(spec: ChallengeSpec) -> dict[str, object]:
    """Convert a validated spec to its canonical JSON-compatible form."""
    return {
        "format_version": spec.format_version,
        "generator_version": spec.generator_version,
        "sizes": list(spec.sizes),
        "counts": dict(spec.counts),
        "public_seeds": dict(spec.public_seeds),
        "backbite_steps_per_cell": spec.backbite_steps_per_cell,
        "families": [
            {
                "name": family.name,
                "wall_rate": family.wall_rate,
                "waypoint_fraction": family.waypoint_fraction,
                "min_waypoints": family.min_waypoints,
                "max_waypoints": family.max_waypoints,
                "waypoint_mode": family.waypoint_mode,
                "partition_period": family.partition_period,
                "partition_wall_rate": family.partition_wall_rate,
            }
            for family in spec.families
        ],
        "strata": [{"family": family, "N": n} for family, n in spec.strata],
        "calibration": spec.calibration,
        "confirmatory": spec.confirmatory,
    }


def canonical_json_bytes(value: object) -> bytes:
    """Serialize JSON deterministically for public commitments."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def sha256_hex(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def challenge_spec_sha256(spec: ChallengeSpec) -> str:
    return sha256_hex(canonical_json_bytes(spec_to_dict(spec)))


def sealed_seed_commitment(secret_seed: str) -> str:
    """Return a domain-separated commitment to a high-entropy test seed."""
    return sha256_hex(_TEST_SEED_DOMAIN + secret_seed.strip().encode("ascii"))


def _instance_seed(master_seed: str, split: SplitName, family: str, n: int, ordinal: int) -> int:
    material = (
        _GENERATOR_DOMAIN
        + master_seed.encode("utf-8")
        + b"\0"
        + split.encode("ascii")
        + b"\0"
        + family.encode("ascii")
        + b"\0"
        + str(n).encode("ascii")
        + b"\0"
        + str(ordinal).encode("ascii")
    )
    return int.from_bytes(hashlib.sha256(material).digest()[:8], "big")


def _coord(cell: int, n: int) -> Coord:
    return (cell // n, cell % n)


def _canonical_cell_edge(a: int, b: int) -> CellEdge:
    return (a, b) if a < b else (b, a)


def _grid_neighbours(cell: int, n: int) -> tuple[int, ...]:
    r, c = divmod(cell, n)
    out: list[int] = []
    if r > 0:
        out.append(cell - n)
    if r + 1 < n:
        out.append(cell + n)
    if c > 0:
        out.append(cell - 1)
    if c + 1 < n:
        out.append(cell + 1)
    return tuple(out)


def _serpentine_path(n: int) -> list[int]:
    path: list[int] = []
    for r in range(n):
        columns = range(n) if r % 2 == 0 else range(n - 1, -1, -1)
        path.extend(r * n + c for c in columns)
    return path


def _randomised_hamiltonian_path(n: int, rng: StableRng, steps: int) -> list[int]:
    """Randomize a serpentine Hamiltonian path using endpoint backbite moves."""
    path = _serpentine_path(n)
    position = [0] * (n * n)
    for i, cell in enumerate(path):
        position[cell] = i

    for _ in range(steps):
        front = rng.randbelow(2) == 0
        endpoint = path[0] if front else path[-1]
        candidates: list[int] = []
        for neighbour in _grid_neighbours(endpoint, n):
            idx = position[neighbour]
            if (front and idx >= _MIN_BACKBITE_DISTANCE) or (
                not front and idx <= len(path) - (_MIN_BACKBITE_DISTANCE + 1)
            ):
                candidates.append(neighbour)
        if not candidates:
            continue
        chosen = candidates[rng.randbelow(len(candidates))]
        idx = position[chosen]
        if front:
            path[:idx] = reversed(path[:idx])
            changed = range(idx)
        else:
            path[idx + 1 :] = reversed(path[idx + 1 :])
            changed = range(idx + 1, len(path))
        for i in changed:
            position[path[i]] = i
    return path


def _manhattan(a: int, b: int, n: int) -> int:
    ar, ac = divmod(a, n)
    br, bc = divmod(b, n)
    return abs(ar - br) + abs(ac - bc)


def _balanced_waypoint_indices(length: int, k: int, rng: StableRng) -> list[int]:
    indices = [0]
    nominal_gap = float(length - 1) / float(k - 1)
    for j in range(1, k - 1):
        target = int(round(float(j) * nominal_gap))
        radius = max(1, int(round(nominal_gap * 0.25)))
        lo = max(indices[-1] + 1, target - radius)
        hi = min(length - (k - j), target + radius)
        hi = max(hi, lo)
        indices.append(lo + rng.randbelow(hi - lo + 1))
    indices.append(length - 1)
    return indices


def _deceptive_waypoint_indices(path: list[int], n: int, k: int, rng: StableRng) -> list[int]:
    """Prefer long path gaps whose endpoints are geometrically close."""
    length = len(path)
    indices = [0]
    nominal_gap = float(length - 1) / float(k - 1)
    for j in range(1, k - 1):
        target = int(round(float(j) * nominal_gap))
        radius = max(2, int(round(nominal_gap * 0.45)))
        lo = max(indices[-1] + 2, target - radius)
        hi = min(length - (k - j), target + radius)
        if hi < lo:
            lo = indices[-1] + 1
            hi = min(length - (k - j), lo)
        previous = indices[-1]
        scored = [
            ((float(i - previous) / float(_manhattan(path[previous], path[i], n) + 1)), i)
            for i in range(lo, hi + 1)
        ]
        scored.sort(reverse=True)
        top = scored[: min(5, len(scored))]
        indices.append(top[rng.randbelow(len(top))][1])
    indices.append(length - 1)
    return indices


def _waypoint_indices(path: list[int], n: int, family: FamilySpec, rng: StableRng) -> list[int]:
    k = int(round(float(len(path)) * family.waypoint_fraction))
    k = min(max(k, family.min_waypoints), family.max_waypoints, len(path))
    if family.waypoint_mode == "deceptive":
        return _deceptive_waypoint_indices(path, n, k, rng)
    return _balanced_waypoint_indices(len(path), k, rng)


def _all_grid_edges(n: int) -> list[CellEdge]:
    edges: list[CellEdge] = []
    for r in range(n):
        for c in range(n):
            cell = r * n + c
            if r + 1 < n:
                edges.append((cell, cell + n))
            if c + 1 < n:
                edges.append((cell, cell + 1))
    return edges


def _crosses_partition(edge: CellEdge, n: int, period: int) -> bool:
    if period <= 0:
        return False
    (ar, ac), (br, bc) = _coord(edge[0], n), _coord(edge[1], n)
    if ar != br:
        return max(ar, br) % period == 0
    if ac != bc:
        return max(ac, bc) % period == 0
    return False


def _sample_walls(path: list[int], n: int, family: FamilySpec, rng: StableRng) -> set[CellEdge]:
    path_edges = {_canonical_cell_edge(a, b) for a, b in pairwise(path)}
    walls: set[CellEdge] = set()
    for edge in _all_grid_edges(n):
        if edge in path_edges:
            continue
        probability = family.wall_rate
        if _crosses_partition(edge, n, family.partition_period):
            probability = max(probability, family.partition_wall_rate)
        if rng.random() < probability:
            walls.add(edge)
    return walls


def _open_adjacency(n: int, walls: set[CellEdge]) -> list[list[int]]:
    adjacency: list[list[int]] = [[] for _ in range(n * n)]
    for a, b in _all_grid_edges(n):
        if (a, b) in walls:
            continue
        adjacency[a].append(b)
        adjacency[b].append(a)
    return adjacency


def _articulation_count(adjacency: list[list[int]]) -> int:
    discovery = [-1] * len(adjacency)
    low = [0] * len(adjacency)
    parent = [-1] * len(adjacency)
    articulation: set[int] = set()
    tick = 0

    def visit(node: int) -> None:
        nonlocal tick
        discovery[node] = tick
        low[node] = tick
        tick += 1
        children = 0
        for neighbour in adjacency[node]:
            if discovery[neighbour] < 0:
                parent[neighbour] = node
                children += 1
                visit(neighbour)
                low[node] = min(low[node], low[neighbour])
                if parent[node] < 0 and children > 1:
                    articulation.add(node)
                if parent[node] >= 0 and low[neighbour] >= discovery[node]:
                    articulation.add(node)
            elif neighbour != parent[node]:
                low[node] = min(low[node], discovery[neighbour])

    visit(0)
    return len(articulation)


def _path_turns(path: list[int], n: int) -> int:
    directions: list[tuple[int, int]] = []
    for a, b in pairwise(path):
        ar, ac = divmod(a, n)
        br, bc = divmod(b, n)
        directions.append((br - ar, bc - ac))
    return sum(1 for before, after in pairwise(directions) if before != after)


def _metrics(
    path: list[int],
    waypoint_indices: list[int],
    walls: set[CellEdge],
    n: int,
    family: FamilySpec,
) -> dict[str, int | float | str]:
    adjacency = _open_adjacency(n, walls)
    gaps = [b - a for a, b in pairwise(waypoint_indices)]
    detours = [
        float(gap) / float(_manhattan(path[a], path[b], n) + 1)
        for gap, a, b in zip(gaps, waypoint_indices[:-1], waypoint_indices[1:], strict=True)
    ]
    open_edges = sum(len(values) for values in adjacency) // 2
    return {
        "family": family.name,
        "N": n,
        "K": len(waypoint_indices),
        "walls": len(walls),
        "open_edges": open_edges,
        "noncertificate_open_edges": open_edges - (len(path) - 1),
        "mean_degree": float(2 * open_edges) / float(len(path)),
        "articulation_points": _articulation_count(adjacency),
        "path_turns": _path_turns(path, n),
        "max_waypoint_gap": max(gaps),
        "mean_waypoint_detour": sum(detours) / float(len(detours)),
    }


def _edge_to_json(edge: CellEdge, n: int) -> list[list[int]]:
    a, b = _coord(edge[0], n), _coord(edge[1], n)
    return [[a[0], a[1]], [b[0], b[1]]]


def generate_puzzle(
    *,
    split: SplitName,
    family: FamilySpec,
    n: int,
    ordinal: int,
    master_seed: str,
    backbite_steps_per_cell: int,
) -> GeneratedPuzzle:
    """Generate one deterministic, certified challenge puzzle."""
    rng = StableRng(_instance_seed(master_seed, split, family.name, n, ordinal))
    path = _randomised_hamiltonian_path(n, rng, backbite_steps_per_cell * n * n)
    waypoint_indices = _waypoint_indices(path, n, family, rng)
    walls = _sample_walls(path, n, family, rng)
    puzzle_id = f"zc1-{split}-{family.name}-n{n}-{ordinal:03d}"
    solution = tuple(_coord(cell, n) for cell in path)
    waypoints = [solution[index] for index in waypoint_indices]
    puzzle: dict[str, object] = {
        "id": puzzle_id,
        "name": f"Challenge v1 / {family.name} / {n}x{n} / {ordinal:03d}",
        "difficulty": "Hard",
        "N": n,
        "K": len(waypoints),
        "waypoints": [[r, c] for r, c in waypoints],
        "walls": [_edge_to_json(edge, n) for edge in sorted(walls)],
        "blocked": [],
    }
    generated = GeneratedPuzzle(
        puzzle=puzzle,
        solution=solution,
        metrics=_metrics(path, waypoint_indices, walls, n, family),
    )
    validate_generated_puzzle(generated)
    return generated


def generate_split(spec: ChallengeSpec, split: SplitName, master_seed: str) -> list[GeneratedPuzzle]:
    """Generate a balanced split over every family/size stratum."""
    generated: list[GeneratedPuzzle] = []
    per_stratum = spec.counts[split] // len(spec.strata)
    by_family = {family.name: family for family in spec.families}
    for family_name, n in spec.strata:
        family = by_family[family_name]
        generated.extend(
            generate_puzzle(
                split=split,
                family=family,
                n=n,
                ordinal=ordinal,
                master_seed=master_seed,
                backbite_steps_per_cell=spec.backbite_steps_per_cell,
            )
            for ordinal in range(per_stratum)
        )
    generated.sort(key=lambda item: str(item.puzzle["id"]))
    return generated


def validate_generated_puzzle(generated: GeneratedPuzzle) -> None:
    """Validate the planted certificate independently of the solver."""
    puzzle = generated.puzzle
    n = int(cast("int", puzzle["N"]))
    solution = generated.solution
    if len(solution) != n * n or len(set(solution)) != len(solution):
        msg = f"{puzzle['id']}: solution is not Hamiltonian over the full grid"
        raise ValueError(msg)
    expected = {(r, c) for r in range(n) for c in range(n)}
    if set(solution) != expected:
        msg = f"{puzzle['id']}: solution does not cover the full grid"
        raise ValueError(msg)

    raw_walls = cast("list[list[list[int]]]", puzzle["walls"])
    walls = {
        tuple(sorted(((int(a[0]), int(a[1])), (int(b[0]), int(b[1])))))
        for a, b in raw_walls
    }
    for a, b in pairwise(solution):
        if abs(a[0] - b[0]) + abs(a[1] - b[1]) != 1:
            msg = f"{puzzle['id']}: certificate contains a non-adjacent step"
            raise ValueError(msg)
        if tuple(sorted((a, b))) in walls:
            msg = f"{puzzle['id']}: certificate crosses a wall"
            raise ValueError(msg)

    waypoints = [tuple(map(int, point)) for point in cast("list[list[int]]", puzzle["waypoints"])]
    positions = {cell: index for index, cell in enumerate(solution)}
    waypoint_positions = [positions[cast("Coord", point)] for point in waypoints]
    if waypoint_positions != sorted(waypoint_positions):
        msg = f"{puzzle['id']}: waypoints are not ordered along the certificate"
        raise ValueError(msg)
    if waypoints[0] != solution[0] or waypoints[-1] != solution[-1]:
        msg = f"{puzzle['id']}: endpoint waypoints do not match the certificate"
        raise ValueError(msg)


def corpus_payload(generated: list[GeneratedPuzzle]) -> dict[str, object]:
    return {
        "version": 1,
        "generator": "zipmould-challenge-v1",
        "count": len(generated),
        "puzzles": [item.puzzle for item in sorted(generated, key=lambda item: str(item.puzzle["id"]))],
    }


def certificate_payload(generated: list[GeneratedPuzzle]) -> dict[str, object]:
    return {
        "version": 1,
        "generator": "zipmould-challenge-v1",
        "count": len(generated),
        "certificates": [
            {
                "puzzle_id": str(item.puzzle["id"]),
                "solution": [[r, c] for r, c in item.solution],
            }
            for item in sorted(generated, key=lambda item: str(item.puzzle["id"]))
        ],
    }


def metrics_payload(generated: list[GeneratedPuzzle]) -> dict[str, object]:
    return {
        "version": 1,
        "generator": "zipmould-challenge-v1",
        "count": len(generated),
        "metrics": [
            {"puzzle_id": str(item.puzzle["id"]), **item.metrics}
            for item in sorted(generated, key=lambda item: str(item.puzzle["id"]))
        ],
    }


def corpus_sha256(generated: list[GeneratedPuzzle]) -> str:
    return sha256_hex(canonical_json_bytes(corpus_payload(generated)))


def certificate_sha256(generated: list[GeneratedPuzzle]) -> str:
    return sha256_hex(canonical_json_bytes(certificate_payload(generated)))


def _stratum_counts(
    generated: list[GeneratedPuzzle],
) -> tuple[dict[str, int], dict[str, int], dict[str, int]]:
    by_family: dict[str, int] = {}
    by_size: dict[str, int] = {}
    by_stratum: dict[str, int] = {}
    for item in generated:
        family = str(item.metrics["family"])
        size = str(item.metrics["N"])
        by_family[family] = by_family.get(family, 0) + 1
        by_size[size] = by_size.get(size, 0) + 1
        stratum = f"{family}/N{size}"
        by_stratum[stratum] = by_stratum.get(stratum, 0) + 1
    return (
        dict(sorted(by_family.items())),
        dict(sorted(by_size.items(), key=lambda pair: int(pair[0]))),
        dict(sorted(by_stratum.items())),
    )


def build_test_lock(spec: ChallengeSpec, secret_seed: str) -> dict[str, object]:
    """Generate test in memory and return non-revealing public commitments."""
    generated = generate_split(spec, "test", secret_seed.strip())
    by_family, by_size, by_stratum = _stratum_counts(generated)
    return {
        "format_version": 1,
        "generator_version": spec.generator_version,
        "sealed": True,
        "test_count": len(generated),
        "family_counts": by_family,
        "size_counts": by_size,
        "stratum_counts": by_stratum,
        "spec_sha256": challenge_spec_sha256(spec),
        "seed_commitment_sha256": sealed_seed_commitment(secret_seed),
        "corpus_sha256": corpus_sha256(generated),
        "certificate_sha256": certificate_sha256(generated),
        "unlock_policy": "final-analysis-only",
    }


def verify_test_lock(spec: ChallengeSpec, secret_seed: str, lock: dict[str, object]) -> list[GeneratedPuzzle]:
    """Regenerate a sealed test and verify every published commitment."""
    expected = build_test_lock(spec, secret_seed)
    mismatches = [key for key, value in expected.items() if lock.get(key) != value]
    if mismatches:
        msg = f"test lock verification failed for: {', '.join(mismatches)}"
        raise ValueError(msg)
    return generate_split(spec, "test", secret_seed.strip())

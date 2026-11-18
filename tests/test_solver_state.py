"""Regression tests for kernel state construction."""

from __future__ import annotations

from zipmould.config import SolverConfig
from zipmould.puzzle import Puzzle
from zipmould.solver.api import solve
from zipmould.solver.state import pack


def test_pack_removes_walled_edges_from_adjacency() -> None:
    puzzle = Puzzle(
        id="wall-edge",
        name="wall-edge",
        difficulty="Easy",
        N=2,
        K=2,
        waypoints=((0, 0), (1, 1)),
        walls=frozenset({((0, 0), (0, 1))}),
        blocked=frozenset(),
    )

    state = pack(puzzle, SolverConfig())

    left = 0
    right = 1
    assert right not in {int(c) for c in state.adjacency[left] if c >= 0}
    assert left not in {int(c) for c in state.adjacency[right] if c >= 0}


def test_unsolved_run_reports_every_executed_iteration() -> None:
    # (1, 1) keeps a single open edge, so no Hamiltonian path exists despite passing precheck.
    puzzle = Puzzle(
        id="dead-end",
        name="dead-end",
        difficulty="Easy",
        N=3,
        K=2,
        waypoints=((0, 0), (2, 2)),
        walls=frozenset({((0, 1), (1, 1)), ((1, 0), (1, 1)), ((1, 1), (1, 2))}),
        blocked=frozenset(),
    )
    config = SolverConfig(population=2, iter_cap=7, frame_interval=5)

    result = solve(puzzle, config, seed=0)

    assert not result.solved
    assert not result.infeasible
    assert result.iters_used == config.iter_cap

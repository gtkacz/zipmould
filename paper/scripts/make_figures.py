"""Generate manuscript SVG figures and LaTeX tables from frozen evidence."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import cast
from xml.sax.saxutils import escape

import polars as pl

REPO_ROOT = Path(__file__).resolve().parents[2]
RESULTS = REPO_ROOT / "paper" / "results" / "challenge-v1"
FIGURES = REPO_ROOT / "paper" / "figures"
GENERATED = REPO_ROOT / "paper" / "generated"

_INK = "#17202a"
_MUTED = "#5d6d7e"
_GRID = "#d5d8dc"
_BAND = "#eaf2f8"
_FULL = "#1f77b4"
_FROZEN = "#d35400"
_NEGATIVE = "#c0392b"
_POSITIVE = "#2471a3"
_ZERO = "#7f8c8d"
_LATEX_ROW_END = r"\\"


def _report() -> dict[str, object]:
    value: object = json.loads((RESULTS / "report.json").read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        msg = "confirmatory report must be a JSON object"
        raise ValueError(msg)
    return {str(key): item for key, item in cast("dict[object, object]", value).items()}


def _svg_start(width: int, height: int, title: str) -> list[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        f"<title>{escape(title)}</title>",
        "<style>",
        "text { font-family: Inter, 'Helvetica Neue', Arial, sans-serif; fill: #17202a; }",
        ".title { font-size: 22px; font-weight: 700; }",
        ".subtitle { font-size: 13px; fill: #5d6d7e; }",
        ".label { font-size: 13px; }",
        ".tick { font-size: 12px; fill: #5d6d7e; }",
        ".note { font-size: 12px; fill: #5d6d7e; }",
        "</style>",
        '<rect width="100%" height="100%" fill="white"/>',
    ]


def _line(x1: float, y1: float, x2: float, y2: float, *, stroke: str, width: float = 1.0, dash: str = "") -> str:
    dashed = f' stroke-dasharray="{dash}"' if dash else ""
    return (
        f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" '
        f'stroke="{stroke}" stroke-width="{width:.2f}"{dashed}/>'
    )


def _text(x: float, y: float, value: str, css: str, *, anchor: str = "start") -> str:
    return f'<text x="{x:.2f}" y="{y:.2f}" class="{css}" text-anchor="{anchor}">{escape(value)}</text>'


def _scale(value: float, minimum: float, maximum: float, left: float, right: float) -> float:
    return left + (value - minimum) * (right - left) / (maximum - minimum)


def _short_stratum(value: str) -> str:
    family, size = value.split("/", 1)
    return f"{family.replace('-deceptive', '')} / {size}"


def make_primary_figure(report: dict[str, object]) -> None:
    width, height = 1040, 560
    left, right = 285.0, 920.0
    top, bottom = 118.0, 475.0
    x_min, x_max = -0.06, 0.06
    primary = cast("dict[str, object]", report["primary"])
    strata = cast("list[dict[str, object]]", report["by_stratum"])
    rows = [("Overall (95% CI)", float(cast("float", primary["estimate"])), True)] + [
        (_short_stratum(str(row["stratum"])), float(cast("float", row["delta"])), False) for row in strata
    ]
    y_positions = [160.0 + 54.0 * index for index in range(len(rows))]
    svg = _svg_start(width, height, "Full-feedback minus frozen solve probability")
    svg.extend(
        [
            _text(28, 42, "Effect of edge feedback on solve probability", "title"),
            _text(28, 68, "Overall interval is confirmatory; stratum estimates are descriptive.", "subtitle"),
        ]
    )
    band_left = _scale(-0.05, x_min, x_max, left, right)
    band_right = _scale(0.05, x_min, x_max, left, right)
    svg.append(
        f'<rect x="{band_left:.2f}" y="{top:.2f}" width="{band_right - band_left:.2f}" '
        f'height="{bottom - top:.2f}" fill="{_BAND}"/>'
    )
    for tick in (-0.05, -0.025, 0.0, 0.025, 0.05):
        x = _scale(tick, x_min, x_max, left, right)
        svg.append(_line(x, top, x, bottom, stroke=_INK if tick == 0.0 else _GRID, width=1.5 if tick == 0.0 else 1.0))
        svg.append(_text(x, bottom + 26, f"{tick * 100:+.1f}", "tick", anchor="middle"))
    svg.append(
        _text(
            (left + right) / 2.0,
            bottom + 52,
            "Full minus frozen (percentage points)",
            "label",
            anchor="middle",
        )
    )
    for (label, estimate, overall), y in zip(rows, y_positions, strict=True):
        svg.append(_text(left - 18, y + 5, label, "label", anchor="end"))
        svg.append(_line(left, y + 18, right, y + 18, stroke="#edf0f2"))
        x = _scale(estimate, x_min, x_max, left, right)
        if overall:
            lower = _scale(float(cast("float", primary["ci_lower"])), x_min, x_max, left, right)
            upper = _scale(float(cast("float", primary["ci_upper"])), x_min, x_max, left, right)
            svg.append(_line(lower, y, upper, y, stroke=_FULL, width=4.0))
            svg.append(_line(lower, y - 7, lower, y + 7, stroke=_FULL, width=2.0))
            svg.append(_line(upper, y - 7, upper, y + 7, stroke=_FULL, width=2.0))
            radius = 7
        else:
            radius = 5
        svg.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{radius}" fill="{_FULL}"/>')
        svg.append(_text(right + 12, y + 5, f"{estimate * 100:+.2f} pp", "tick"))
    svg.append(
        _text(
            left,
            height - 22,
            "Shaded region: predeclared ±5 percentage-point practical-equivalence band",
            "note",
        )
    )
    svg.append("</svg>")
    FIGURES.mkdir(parents=True, exist_ok=True)
    (FIGURES / "challenge-primary.svg").write_text("\n".join(svg) + "\n", encoding="utf-8")


def make_puzzle_effect_figure() -> None:
    rows = cast("list[dict[str, object]]", pl.read_parquet(RESULTS / "puzzle_effects.parquet").to_dicts())
    strata = sorted({str(row["stratum"]) for row in rows})
    width, height = 940, 560
    left, right = 285.0, 885.0
    top, bottom = 118.0, 460.0
    x_min, x_max = -0.25, 0.45
    y_by_stratum = {stratum: 156.0 + 64.0 * index for index, stratum in enumerate(strata)}
    svg = _svg_start(width, height, "Per-puzzle full-feedback minus frozen effects")
    svg.extend(
        [
            _text(28, 42, "Per-puzzle effects across Challenge v1", "title"),
            _text(28, 68, "Each point is one puzzle's difference over 30 paired seeds.", "subtitle"),
        ]
    )
    for tick in (-0.2, -0.1, 0.0, 0.1, 0.2, 0.3, 0.4):
        x = _scale(tick, x_min, x_max, left, right)
        svg.append(_line(x, top, x, bottom, stroke=_INK if tick == 0.0 else _GRID, width=1.5 if tick == 0.0 else 1.0))
        svg.append(_text(x, bottom + 26, f"{tick * 100:+.0f}", "tick", anchor="middle"))
    grouped: dict[tuple[str, float], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[(str(row["stratum"]), float(cast("float", row["delta"])))].append(row)
    for stratum in strata:
        y = y_by_stratum[stratum]
        svg.append(_text(left - 18, y + 5, _short_stratum(stratum), "label", anchor="end"))
        svg.append(_line(left, y + 26, right, y + 26, stroke="#edf0f2"))
    for (stratum, delta), items in sorted(grouped.items()):
        x = _scale(delta, x_min, x_max, left, right)
        base_y = y_by_stratum[stratum]
        count = len(items)
        for index in range(count):
            offset = (float(index) - float(count - 1) / 2.0) * 3.2
            color = _POSITIVE if delta > 0.0 else _NEGATIVE if delta < 0.0 else _ZERO
            svg.append(
                f'<circle cx="{x:.2f}" cy="{base_y + offset:.2f}" '
                f'r="3.6" fill="{color}" fill-opacity="0.82"/>'
            )
    svg.append(
        _text(
            (left + right) / 2.0,
            bottom + 52,
            "Full minus frozen (percentage points)",
            "label",
            anchor="middle",
        )
    )
    svg.append(
        _text(
            left,
            height - 24,
            "Blue: favors full; red: favors frozen; grey: tie. Descriptive heterogeneity only.",
            "note",
        )
    )
    svg.append("</svg>")
    FIGURES.mkdir(parents=True, exist_ok=True)
    (FIGURES / "challenge-puzzle-effects.svg").write_text("\n".join(svg) + "\n", encoding="utf-8")


def make_tables(report: dict[str, object]) -> None:
    primary = cast("dict[str, object]", report["primary"])
    full = cast("dict[str, object]", report["full_feedback"])
    frozen = cast("dict[str, object]", report["feedback_frozen"])
    strata = cast("list[dict[str, object]]", report["by_stratum"])
    GENERATED.mkdir(parents=True, exist_ok=True)
    summary = "\n".join(
        [
            r"\begin{tabular}{lrr}",
            r"\toprule",
            r"Condition & Solved / 4,500 & Solve rate \\",
            r"\midrule",
            (
                f"Full feedback & {int(cast('int', full['solved'])):,} & "
                f"{float(cast('float', full['solve_rate'])):.3f} {_LATEX_ROW_END}"
            ),
            (
                f"Feedback frozen & {int(cast('int', frozen['solved'])):,} & "
                f"{float(cast('float', frozen['solve_rate'])):.3f} {_LATEX_ROW_END}"
            ),
            r"\midrule",
            (
                f"Difference (95\\% CI) & \\multicolumn{{2}}{{r}}{{"
                f"{float(cast('float', primary['estimate'])) * 100:+.2f} pp "
                f"[{float(cast('float', primary['ci_lower'])) * 100:+.2f}, "
                f"{float(cast('float', primary['ci_upper'])) * 100:+.2f}]}} {_LATEX_ROW_END}"
            ),
            r"\bottomrule",
            r"\end{tabular}",
            "",
        ]
    )
    (GENERATED / "confirmatory-summary.tex").write_text(summary, encoding="utf-8")
    stratum_lines = [
        r"\begin{tabular}{lrrr}",
        r"\toprule",
        r"Stratum & Full & Frozen & Difference \\",
        r"\midrule",
    ]
    stratum_lines.extend(
        (
            f"{_short_stratum(str(row['stratum'])).replace('/', r'\,/\,')} & "
            f"{float(cast('float', row['full_solve_rate'])):.3f} & "
            f"{float(cast('float', row['frozen_solve_rate'])):.3f} & "
            f"{float(cast('float', row['delta'])) * 100:+.2f} pp {_LATEX_ROW_END}"
        )
        for row in strata
    )
    stratum_lines.extend([r"\bottomrule", r"\end{tabular}", ""])
    (GENERATED / "confirmatory-strata.tex").write_text("\n".join(stratum_lines), encoding="utf-8")


def main() -> int:
    report = _report()
    make_primary_figure(report)
    make_puzzle_effect_figure()
    make_tables(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

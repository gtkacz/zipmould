"""Check manuscript claims, citations, figures, and archived evidence."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import cast

ROOT = Path(__file__).resolve().parents[2]
PAPER = ROOT / "paper"
RESULTS = PAPER / "results" / "challenge-v1"
PERCENT = 100.0
DISPLAY_DECIMALS = 2


def _load_json(path: Path) -> dict[str, object]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        msg = f"expected JSON object: {path}"
        raise TypeError(msg)
    return cast("dict[str, object]", raw)


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _verify_checksums() -> None:
    for line in (RESULTS / "checksums.sha256").read_text(encoding="utf-8").splitlines():
        expected, relative = line.split("  ", maxsplit=1)
        path = ROOT / relative
        _require(path.is_file(), f"missing checksummed evidence: {relative}")
        _require(_sha256(path) == expected, f"checksum drift: {relative}")


def _verify_claims(manuscript: str) -> None:
    report = _load_json(RESULTS / "report.json")
    primary = cast("dict[str, object]", report["primary"])
    full = cast("dict[str, object]", report["full_feedback"])
    frozen = cast("dict[str, object]", report["feedback_frozen"])
    manifest = _load_json(RESULTS / "run_manifest.json")

    expected_text = {
        f"{int(cast('int', full['solved'])):,}",
        f"{int(cast('int', frozen['solved'])):,}",
        f"{float(cast('float', full['solve_rate'])) * PERCENT:.{DISPLAY_DECIMALS}f}%",
        f"{float(cast('float', frozen['solve_rate'])) * PERCENT:.{DISPLAY_DECIMALS}f}%",
        f"{float(cast('float', primary['estimate'])) * PERCENT:+.{DISPLAY_DECIMALS}f}",
        f"{float(cast('float', primary['ci_lower'])) * PERCENT:+.{DISPLAY_DECIMALS}f}".replace(
            "-", "\N{MINUS SIGN}"
        ),
        f"{float(cast('float', primary['ci_upper'])) * PERCENT:+.{DISPLAY_DECIMALS}f}",
        str(primary["classification"]),
        f"{int(cast('int', manifest['rows'])):,}",
        f"{int(cast('int', manifest['solved_rows'])):,}",
    }
    for text in expected_text:
        _require(text in manuscript, f"manuscript is missing frozen result token: {text}")

    raw_hash = str(manifest["results_file_sha256"])
    _require(raw_hash == str(report["raw_results_sha256"]), "manifest/report raw hash mismatch")
    _require(raw_hash in manuscript, "manuscript is missing the raw-result checksum")


def _signed(value: float) -> str:
    return f"{value * PERCENT:+.{DISPLAY_DECIMALS}f}".replace("-", "\N{MINUS SIGN}")


def _verify_secondary(manuscript: str) -> None:
    secondary = _load_json(PAPER / "generated" / "secondary_analysis.json")
    expected_text = {
        f"{_signed(float(row['delta']))} ({_signed(float(row['ci_lower']))}, {_signed(float(row['ci_upper']))})"
        for row in cast("list[dict[str, float]]", secondary["budget_profile"])
    }
    dispersion = cast("dict[str, float]", secondary["effect_dispersion"])
    expected_text |= {
        f"{dispersion['observed_sd'] * PERCENT:.{DISPLAY_DECIMALS}f} points",
        f"{dispersion['null_sd_mean'] * PERCENT:.{DISPLAY_DECIMALS}f} points",
        f"{dispersion['p_value'] * PERCENT:.1f}%",
    }
    expected_text |= {
        f"[{_signed(low)}, {_signed(high)}]"
        for low, high in cast("dict[str, list[float]]", secondary["interval_sensitivity"]).values()
    }
    for text in expected_text:
        _require(text in manuscript, f"manuscript is missing secondary-analysis token: {text}")


def _verify_sweep(manuscript: str) -> None:
    quoted = {"dev": ("full", "full-z0", "full-alpha1", "full-z0-alpha1"), "train": ("full", "full-z0-alpha1")}
    for split, variants in quoted.items():
        summary_path = ROOT / "experiments" / "feedback_sweep" / "out" / split / "summary.json"
        rows = {
            str(row["variant"]): row
            for row in cast("list[dict[str, float]]", json.loads(summary_path.read_text(encoding="utf-8")))
        }
        for variant in variants:
            row = rows[variant]
            text = f"{_signed(row['delta'])} ({_signed(row['ci_lower'])}, {_signed(row['ci_upper'])})"
            _require(text in manuscript, f"manuscript is missing {split} sweep token: {text}")


def _verify_citations_and_figures(manuscript: str) -> None:
    bibliography = (PAPER / "references.bib").read_text(encoding="utf-8")
    bib_keys = set(re.findall(r"^@\w+\{([^,]+),", bibliography, flags=re.MULTILINE))
    references = set(re.findall(r"@([A-Za-z][A-Za-z0-9_-]+)", manuscript))
    cited_keys = references & bib_keys
    _require(cited_keys == bib_keys, f"uncited bibliography entries: {sorted(bib_keys - cited_keys)}")

    for relative in re.findall(r'image\("([^"]+)"', manuscript):
        path = PAPER / relative
        _require(path.is_file() and path.stat().st_size > 0, f"missing manuscript figure: {relative}")

    for marker in ("TODO", "TBD", "FIXME", "XXX"):
        _require(marker not in manuscript, f"unresolved manuscript marker: {marker}")


def main() -> None:
    manuscript_path = PAPER / "main.typ"
    _require(manuscript_path.is_file(), "missing manuscript source")
    manuscript = manuscript_path.read_text(encoding="utf-8")
    _verify_checksums()
    _verify_claims(manuscript)
    _verify_secondary(manuscript)
    _verify_sweep(manuscript)
    _verify_citations_and_figures(manuscript)


if __name__ == "__main__":
    main()

"""Restore the released test material to its ignored runtime location."""

from __future__ import annotations

import hashlib
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARCHIVED = ROOT / "paper" / "results" / "challenge-v1" / "test"
SEALED = ROOT / "benchmark" / "challenge" / "v1" / "sealed"
CHECKSUMS = ROOT / "paper" / "results" / "challenge-v1" / "checksums.sha256"
RELEASE_FILES = (
    "OPENED.json",
    "certificates.json",
    "metrics.json",
    "puzzles.cbor",
    "splits.json",
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _expected_checksums() -> dict[str, str]:
    checksums: dict[str, str] = {}
    for line in CHECKSUMS.read_text(encoding="utf-8").splitlines():
        expected, relative = line.split("  ", maxsplit=1)
        checksums[relative] = expected
    return checksums


def main() -> None:
    checksums = _expected_checksums()
    SEALED.mkdir(parents=True, exist_ok=True)
    for name in RELEASE_FILES:
        source = ARCHIVED / name
        destination = SEALED / name
        relative = source.relative_to(ROOT).as_posix()
        expected = checksums.get(relative)
        if expected is None or not source.is_file() or _sha256(source) != expected:
            msg = f"archived test release failed integrity check: {relative}"
            raise SystemExit(msg)
        if destination.exists():
            if _sha256(destination) != expected:
                msg = f"refusing to overwrite different sealed material: {destination}"
                raise SystemExit(msg)
            continue
        shutil.copy2(source, destination)


if __name__ == "__main__":
    main()

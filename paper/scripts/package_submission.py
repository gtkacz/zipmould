"""Build local journal/archive bundles without uploading or inventing metadata."""

from __future__ import annotations

import hashlib
import io
import json
import shutil
import subprocess
import tarfile
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parents[2]
PAPER = ROOT / "paper"
DIST = PAPER / "dist"
FROZEN = "06ef8bbfae5de29fe6cd4ebf0175a94f04880e9b"
ZIP_DATE = (2026, 10, 1, 0, 0, 0)
JOURNAL_FILES = (
    "main.tex",
    "references.bib",
    "sn-jnl.cls",
    "sn-basic.bst",
    "threeparttable.sty",
    "Fig1.pdf",
    "Fig2.pdf",
    "Fig1.eps",
    "Fig2.eps",
)
FROZEN_PATHS = (
    "LICENSE",
    "README.md",
    "pyproject.toml",
    "uv.lock",
    "Makefile",
    "src",
    "experiments/challenge_v1",
    "configs/challenge",
    "benchmark/scripts/challenge.py",
    "benchmark/challenge/v1",
)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def archive(path: Path, files: dict[str, bytes]) -> None:
    with ZipFile(path, "w", compression=ZIP_DEFLATED) as handle:
        for name, data in sorted(files.items()):
            info = ZipInfo(name, ZIP_DATE)
            info.compress_type = ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            handle.writestr(info, data)
    with ZipFile(path) as handle:
        if handle.testzip() is not None:
            raise SystemExit(f"Corrupt package: {path}")


def main() -> None:
    DIST.mkdir(exist_ok=True)
    journal = {name: (PAPER / "natural-computing" / name).read_bytes() for name in JOURNAL_FILES}
    archive(DIST / "natural-computing-source.zip", journal)
    files: dict[str, bytes] = {}
    fixed = ("LICENSE", "README.md", "pyproject.toml", "uv.lock", "Makefile")
    trees = (
        "src",
        "experiments/challenge_v1",
        "configs/challenge",
        "benchmark/challenge/v1/public",
        "paper/results/challenge-v1",
        "paper/scripts",
        "paper/generated",
        "paper/figures",
        "paper/archive",
    )
    selected = [ROOT / name for name in fixed]
    for tree in trees:
        selected.extend(p for p in (ROOT / tree).rglob("*") if p.is_file())
    selected.extend((ROOT / "benchmark/challenge/v1").glob("*.json"))
    selected.extend((ROOT / "benchmark/challenge/v1").glob("*.md"))
    selected.append(ROOT / "benchmark/scripts/challenge.py")
    selected.extend(PAPER.glob("*.md"))
    selected.extend(PAPER.glob("*.typ"))
    selected.extend(PAPER.glob("*.bib"))
    selected.extend([PAPER / "main.pdf", PAPER / "orcid.svg"])
    selected.extend(PAPER / "natural-computing" / name for name in JOURNAL_FILES)
    selected.extend((PAPER / "natural-computing").glob("*.md"))
    selected.extend([PAPER / "natural-computing/main.pdf", PAPER / "natural-computing/preamble.tex.in"])
    for path in selected:
        if path.is_symlink():
            raise SystemExit(f"Refusing symlink: {path}")
        if "__pycache__" in path.parts or path.suffix in {".pyc", ".nbc", ".nbi"}:
            continue
        name = path.relative_to(ROOT).as_posix()
        files[name] = path.read_bytes()
    git = shutil.which("git")
    if git is None:
        raise SystemExit("git is required to preserve the pre-test code snapshot")
    frozen = subprocess.run(  # noqa: S603 -- fixed, allowlisted Git archive arguments
        [git, "archive", "--format=tar", FROZEN, *FROZEN_PATHS], cwd=ROOT, check=True, capture_output=True
    ).stdout
    with tarfile.open(fileobj=io.BytesIO(frozen)) as handle:
        for item in handle.getmembers():
            if "benchmark/data" in item.name or "/.secrets/" in item.name:
                raise SystemExit(f"Disallowed frozen archive member: {item.name}")
    files["frozen-confirmatory-source.tar"] = frozen
    provenance = {
        "frozen_commit": FROZEN,
        "frozen_snapshot_paths": FROZEN_PATHS,
        "frozen_snapshot_sha256": digest(frozen),
        "manuscript_source_sha256": digest((PAPER / "main.typ").read_bytes()),
        "scope": "Local working manuscript and allowlisted evidence; not a published archive release",
    }
    files["PACKAGE_PROVENANCE.json"] = (json.dumps(provenance, indent=2) + "\n").encode()
    files["PACKAGE_SHA256SUMS"] = "".join(f"{digest(data)}  {name}\n" for name, data in sorted(files.items())).encode()
    archive(DIST / "zipmould-evidence.zip", files)
    inputs = json.loads((PAPER / "archive/author-inputs.json").read_text())
    pending = [key for key, value in inputs.items() if value is None or value is False]
    pending.extend(f"credit_roles.{name}" for name, roles in inputs["credit_roles"].items() if roles is None)
    status = {
        "submission_ready": False,
        "archive_published": False,
        "journal_submitted": False,
        "pending_author_inputs": pending,
        "evidence_members": len(files),
    }
    (DIST / "package-status.json").write_text(json.dumps(status, indent=2) + "\n")
    (DIST / "SHA256SUMS").write_text(
        "".join(
            f"{digest((DIST / name).read_bytes())}  {name}\n"
            for name in ("natural-computing-source.zip", "zipmould-evidence.zip")
        )
    )
    print(f"Built source and evidence ZIPs ({len(files)} evidence members); unresolved inputs: {len(pending)}")


if __name__ == "__main__":
    main()

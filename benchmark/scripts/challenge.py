"""Generate ZipMould Challenge v1 public data and sealed test commitments."""

from __future__ import annotations

import argparse
import json
import os
import secrets
from datetime import UTC, datetime
from pathlib import Path
from typing import cast

import cbor2

from zipmould.challenge import (
    build_test_lock,
    canonical_json_bytes,
    certificate_payload,
    challenge_spec_sha256,
    corpus_payload,
    corpus_sha256,
    generate_split,
    load_challenge_spec,
    metrics_payload,
    sha256_hex,
    verify_test_lock,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ROOT = REPO_ROOT / "benchmark" / "challenge" / "v1"
DEFAULT_SPEC = DEFAULT_ROOT / "spec.json"
_HEX_SEED_LENGTH = 64


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_cbor(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as handle:
        cbor2.dump(value, handle, canonical=True)


def _read_json(path: Path) -> dict[str, object]:
    value: object = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        msg = f"expected JSON object at {path}"
        raise ValueError(msg)
    raw = cast("dict[object, object]", value)
    return {str(key): item for key, item in raw.items()}


def _secret_seed(path: Path, *, create: bool) -> str:
    if path.exists():
        value = path.read_text(encoding="ascii").strip()
        if len(value) != _HEX_SEED_LENGTH or any(ch not in "0123456789abcdef" for ch in value):
            msg = f"invalid 256-bit hexadecimal test seed at {path}"
            raise ValueError(msg)
        return value
    if not create:
        msg = f"sealed test seed is missing: {path}"
        raise FileNotFoundError(msg)
    path.parent.mkdir(parents=True, exist_ok=True)
    value = secrets.token_hex(32)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        os.write(descriptor, f"{value}\n".encode("ascii"))
    finally:
        os.close(descriptor)
    return value


def generate_public(spec_path: Path, root: Path) -> None:
    spec = load_challenge_spec(spec_path)
    train = generate_split(spec, "train", spec.public_seeds["train"])
    dev = generate_split(spec, "dev", spec.public_seeds["dev"])
    combined = sorted([*train, *dev], key=lambda item: str(item.puzzle["id"]))

    public_dir = root / "public"
    corpus = corpus_payload(combined)
    certificates = certificate_payload(combined)
    metrics = metrics_payload(combined)
    splits = {
        "version": 1,
        "generator": spec.generator_version,
        "sealed_test": True,
        "train": [str(item.puzzle["id"]) for item in train],
        "dev": [str(item.puzzle["id"]) for item in dev],
        "test": [],
    }
    manifest = {
        "format_version": 1,
        "generator_version": spec.generator_version,
        "spec_sha256": challenge_spec_sha256(spec),
        "corpus_sha256": corpus_sha256(combined),
        "certificate_sha256": sha256_hex(canonical_json_bytes(certificates)),
        "metrics_sha256": sha256_hex(canonical_json_bytes(metrics)),
        "counts": {"train": len(train), "dev": len(dev), "test": "sealed"},
        "test_lock": "../test.lock.json",
    }
    _write_cbor(public_dir / "puzzles.cbor", corpus)
    _write_json(public_dir / "certificates.json", certificates)
    _write_json(public_dir / "metrics.json", metrics)
    _write_json(public_dir / "splits.json", splits)
    _write_json(public_dir / "manifest.json", manifest)
    print(
        json.dumps(
            {
                "generated": "public",
                "train": len(train),
                "dev": len(dev),
                "corpus_sha256": manifest["corpus_sha256"],
            },
            sort_keys=True,
        )
    )


def seal_test(spec_path: Path, root: Path) -> None:
    spec = load_challenge_spec(spec_path)
    seed_path = root / ".secrets" / "test_seed.txt"
    lock_path = root / "test.lock.json"
    secret_seed = _secret_seed(seed_path, create=True)
    lock = build_test_lock(spec, secret_seed)
    if lock_path.exists():
        existing = _read_json(lock_path)
        if existing != lock:
            msg = f"existing test lock does not match the current spec/secret: {lock_path}"
            raise ValueError(msg)
        print(json.dumps({"sealed": True, "status": "already-matched", "test_count": lock["test_count"]}))
        return
    _write_json(lock_path, lock)
    print(
        json.dumps(
            {
                "sealed": True,
                "test_count": lock["test_count"],
                "spec_sha256": lock["spec_sha256"],
                "seed_commitment_sha256": lock["seed_commitment_sha256"],
                "corpus_sha256": lock["corpus_sha256"],
            },
            sort_keys=True,
        )
    )


def verify_lock(spec_path: Path, root: Path) -> None:
    spec = load_challenge_spec(spec_path)
    secret_seed = _secret_seed(root / ".secrets" / "test_seed.txt", create=False)
    lock = _read_json(root / "test.lock.json")
    generated = verify_test_lock(spec, secret_seed, lock)
    print(
        json.dumps(
            {
                "verified": True,
                "sealed": True,
                "test_count": len(generated),
                "corpus_sha256": lock["corpus_sha256"],
                "test_material_written": False,
            },
            sort_keys=True,
        )
    )


def unlock_test(spec_path: Path, root: Path, *, acknowledged: bool) -> None:
    if not acknowledged:
        msg = (
            "refusing to open test: pass --acknowledge-final-analysis only after "
            "the clean confirmatory release is frozen"
        )
        raise ValueError(msg)
    sealed_dir = root / "sealed"
    opened_path = sealed_dir / "OPENED.json"
    if opened_path.exists():
        msg = f"test was already opened; audit marker exists at {opened_path}"
        raise ValueError(msg)

    spec = load_challenge_spec(spec_path)
    secret_seed = _secret_seed(root / ".secrets" / "test_seed.txt", create=False)
    lock = _read_json(root / "test.lock.json")
    generated = verify_test_lock(spec, secret_seed, lock)
    corpus = corpus_payload(generated)
    certificates = certificate_payload(generated)
    metrics = metrics_payload(generated)
    splits = {
        "version": 1,
        "generator": spec.generator_version,
        "sealed_test": False,
        "train": [],
        "dev": [],
        "test": [str(item.puzzle["id"]) for item in generated],
    }
    _write_cbor(sealed_dir / "puzzles.cbor", corpus)
    _write_json(sealed_dir / "certificates.json", certificates)
    _write_json(sealed_dir / "metrics.json", metrics)
    _write_json(sealed_dir / "splits.json", splits)
    _write_json(
        opened_path,
        {
            "opened_utc": datetime.now(UTC).isoformat(),
            "acknowledgement": "final-analysis",
            "spec_sha256": challenge_spec_sha256(spec),
            "corpus_sha256": lock["corpus_sha256"],
        },
    )
    print(json.dumps({"opened": True, "test_count": len(generated), "audit_marker": str(opened_path)}))


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, default=DEFAULT_SPEC)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("generate-public")
    subparsers.add_parser("seal-test")
    subparsers.add_parser("verify-test-lock")
    unlock = subparsers.add_parser("unlock-test")
    unlock.add_argument("--acknowledge-final-analysis", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    spec_path = Path(args.spec)
    root = Path(args.root)
    command = str(args.command)
    if command == "generate-public":
        generate_public(spec_path, root)
    elif command == "seal-test":
        seal_test(spec_path, root)
    elif command == "verify-test-lock":
        verify_lock(spec_path, root)
    elif command == "unlock-test":
        unlock_test(spec_path, root, acknowledged=bool(args.acknowledge_final_analysis))
    else:  # pragma: no cover - argparse enforces the choices
        msg = f"unknown command {command!r}"
        raise ValueError(msg)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

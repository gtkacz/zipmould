"""Check the generated journal source and final LaTeX compilation log."""

from __future__ import annotations

import re
from pathlib import Path

from check_manuscript import _verify_claims

PAPER = Path(__file__).resolve().parents[1]
JOURNAL = PAPER / "natural-computing"


def main() -> None:
    source = (JOURNAL / "main.tex").read_text()
    normalized = source.replace(r"\%", "%").replace(r"\(-\)", "\N{MINUS SIGN}")
    _verify_claims(normalized)
    bib = (PAPER / "references.bib").read_text()
    keys = set(re.findall(r"^@\w+\{([^,]+),", bib, re.M))
    cited = set(re.findall(r"\\citep\{([^}]+)\}", source))
    if keys != cited:
        raise SystemExit(f"Bibliography mismatch: missing={keys-cited}; unknown={cited-keys}")
    labels = re.findall(r"\\label\{([^}]+)\}", source)
    refs = set(re.findall(r"\\ref\{([^}]+)\}", source))
    if len(labels) != len(set(labels)) or refs != set(labels):
        raise SystemExit("Missing, duplicated, or unused table/figure labels")
    for filename in re.findall(r"\\includegraphics\[[^]]*\]\{([^}]+)\}", source):
        if not (JOURNAL / filename).is_file():
            raise SystemExit(f"Missing figure: {filename}")
    if (JOURNAL / "references.bib").read_text() != bib:
        raise SystemExit("Exported bibliography is stale")
    log = (JOURNAL / "build/main.log").read_text()
    for marker in ("undefined", "Missing character", "Overfull \\hbox", "! LaTeX Error"):
        if marker in log:
            raise SystemExit(f"Inspect final LaTeX log: {marker}")
    if not (JOURNAL / "main.pdf").is_file():
        raise SystemExit("Missing journal PDF")
    print("Journal checks passed: primary claims, citations, figure/table references, final compile log")


if __name__ == "__main__":
    main()

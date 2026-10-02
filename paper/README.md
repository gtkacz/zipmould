# Paper package

This directory contains the manuscript and the complete Challenge v1
evidence package for:

> **Does Edge Feedback Help? A Controlled Study of a Slime-Mould–Inspired
> Constructor for Ordered Hamiltonian Grid Paths**

The confirmatory result is a predeclared **practically equivalent** outcome:
full feedback minus frozen feedback was `+1.29` percentage points, with a 95%
stratified puzzle-bootstrap interval of `[-0.04, +2.64]` points. The interval
lies inside the frozen `[-5, +5]` point practical-effect band.

## Build and audit

For the Natural Computing submission version, run `make paper-package`.
It retains this Typst source as the manuscript master, exports editable
LaTeX into `natural-computing/`, compiles its PDF with the official Springer
class, and assembles source and evidence ZIPs in `paper/dist/`.
Additional requirements are pdfLaTeX/BibTeX (`latexmk`) and `rsvg-convert`.
See `SUBMISSION.md` for unresolved author facts and `archive/README.md` for
the durable-deposit handoff. Package creation does not publish or submit it.

Requirements are the synchronized project virtual environment and Typst
0.14.2 or compatible.

```bash
uv sync
make paper
```

Use `uv sync --extra viz` when also running the complete repository test and
type-check suites. The PDF creation timestamp is fixed to the archived run's
completion second, so rebuilding with the same Typst/font environment is
byte-reproducible rather than dirtying a clean clone with metadata-only drift.

That command verifies and restores the released test files to the ignored
runtime location, regenerates figures/tables from the frozen report,
independently reanalyzes all raw rows and revalidates every solved path,
compares all derived artifacts byte for byte, compiles `main.typ` to
`main.pdf`, checks every archived evidence checksum, and verifies that the
manuscript's primary counts, interval, classification, citations, and figure
paths match the frozen artifacts.

The scientific workflow remains available separately:

```bash
make paper-verify
make paper-smoke
make paper-restore-test
make paper-analyze
make paper-reproduce
```

The first two use public material. The analysis and reproduction commands
consume the completed confirmatory result; they do not rerun the 9,000 solver
trials.

## Important files

- `main.typ` / `main.pdf`: manuscript source and compiled PDF;
- `references.bib`: standard BibTeX bibliography;
- `CLAIM.md`: frozen contribution and prohibited overclaims;
- `PROTOCOL.md`: human-readable confirmatory protocol;
- `figures/` and `generated/`: displays derived from the frozen report;
- `results/challenge-v1/`: raw rows, paths, manifest, test release, bootstrap,
  per-puzzle effects, and checksums;
- `SUBMISSION.md`: remaining author- and venue-dependent submission work.
- `natural-computing/main.tex` / `main.pdf`: generated journal source and PDF;
- `natural-computing/COVER_LETTER.md`: journal cover-letter draft;
- `archive/`: deposit metadata and author-input record;
- `dist/`: locally built ZIP files, checksums, and package status (ignored).

The pre-test release is commit
`06ef8bbfae5de29fe6cd4ebf0175a94f04880e9b`, tagged
`challenge-v1-confirmatory-v1`. Do not move that tag to a post-analysis commit.
The audited post-analysis manuscript/evidence package is tagged separately as
`challenge-v1-paper-v1`.

# Local validation, 2026-10-01

This record describes tool checks, not author approval or independent peer review.

- `make paper-package` completed: Typst build, frozen-evidence checksums,
  manuscript checks, raw-row reanalysis, independent secondary analysis,
  journal export, pdfLaTeX/BibTeX compilation, and bundle creation.
- The primary result remains +1.29 percentage points, with the frozen 95%
  interval [−0.04, +2.64] points and practical-equivalence classification.
- The reanalysis validated all 4,020 returned paths from the 9,000 trial rows;
  the report, puzzle effects, and bootstrap files matched byte for byte.
- Extracting the evidence ZIP into a fresh temporary directory and running
  `make paper-reproduce` against the installed locked environment also passed.
  This reused the installed dependencies; it was not a fresh dependency install
  or a rerun of the solver trials.
- Every entry in the evidence ZIP's `PACKAGE_SHA256SUMS` matched its contents.
- The flat journal source ZIP compiled independently after extraction.
- The final journal PDF contains 16 pages; all listed fonts are embedded.
  No unresolved citations/references, missing glyphs, or horizontal overflow
  remained. The class emits vertical spacing warnings; spot inspection of the
  title/abstract and results display pages found no clipping there.
- The official `sn-jnl.cls` and `sn-basic.bst` match the downloaded publisher
  ZIP byte for byte. Their source and version are in `COMPLIANCE.md`.
- Ruff checks passed for all four new/edited Python preparation scripts.
- `git diff --check` passed for text changes (PDFs excluded because Git
  treats the existing tracked Typst PDF as text and flags binary bytes).

Neither an archive upload nor a journal submission was performed. Data-license
selection, contributions, the CNPq identifier, complete AI-use history, and
author approval remain unresolved in `../archive/author-inputs.json`.

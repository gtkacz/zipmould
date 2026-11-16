# Local validation, 2026-11-16

This record describes tool checks, not author approval or independent peer review.

- `make paper-package` completed: Typst build, frozen-evidence checksums,
  manuscript checks, raw-row reanalysis, independent secondary analysis,
  journal export, pdfLaTeX/BibTeX compilation, and bundle creation.
- The primary result remains +1.29 percentage points, with the frozen 95%
  interval [−0.04, +2.64] points and practical-equivalence classification.
- The reanalysis validated all 4,020 returned paths from the 9,000 trial rows;
  the report, puzzle effects, and bootstrap files matched byte for byte.
- Running `make paper-package` twice, with the LaTeX build directory removed in
  between, produced identical SHA-256 digests for the Typst PDF, the journal
  PDF, `main.tex`, all four figure files, and both ZIP files, and left the Git
  working tree clean.
- The flat journal source ZIP compiled independently after extraction into an
  empty directory. That PDF differs from the tracked one only in the trailer
  identifier, which pdfTeX derives from the output path.
- The final journal PDF contains 11 A4 pages in two columns; all 27 listed
  fonts are embedded. No unresolved citations/references, missing glyphs, or
  horizontal overflow remained. The class emits vertical spacing warnings.
- Every page was rendered and inspected. Both figures span the two columns,
  the three tables fit one column, and long hashes and URLs break inside the
  column. Both figures were also rendered in grayscale and remain readable.
- The shell commands in the reproducibility section print with their spaces
  (`make paper-verify`); the Natural Computing PDF printed `makepaper-verify`.
- The official `sn-jnl.cls` and `sn-basic.bst` are unchanged from the
  2026-10-01 package, which matched the downloaded publisher ZIP byte for byte.
  Their source and version are in `COMPLIANCE.md`.
- Ruff checks passed for the paper scripts.

- Extracting the evidence ZIP into a fresh temporary directory and running
  `make paper-reproduce` against the installed locked environment also passed,
  with the extracted `src/` on the import path. This reused the installed
  dependencies; it was not a fresh dependency install or a rerun of the solver
  trials.
- Every entry in the evidence ZIP's `PACKAGE_SHA256SUMS` matched its contents.

Not checked: the journal's instructions page could not be opened directly; see
`COMPLIANCE.md` for what was and was not confirmed.

Neither an archive upload nor a journal submission was performed. Data-license
selection, contributions, the CNPq identifier, complete AI-use history, and
author approval remain unresolved in `../archive/author-inputs.json`.

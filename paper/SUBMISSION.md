# Natural Computing submission handoff

Preparation date: 2026-10-01. Status: local package prepared; author inputs
and archival publication remain unresolved. No journal submission has occurred.

## Completed preparation

- Removed “statistically borderline” language and bootstrap-sign emphasis.
- Corrected the zero-effect-puzzle explanation: all 150 puzzles remain in the
  primary denominator and bootstrap; the 114-puzzle subset changes the target
  population and is descriptive only.
- Retained the frozen estimand, configuration, interval, ±5-point band, and
  practical-equivalence classification.
- Shortened the abstract to 217 words and applied author–year references.
- Created `natural-computing/main.tex` with the official Springer Nature class,
  MSC codes, numbered equations/tables/figures, author details, and declarations.
- Supplied vector PDF/EPS figures with larger labels and position-based
  interpretation independent of color.
- Added a disclosure of the AI assistance known from this editing session.
- Prepared a journal cover-letter draft and reproducible source/evidence ZIP
  builders. The evidence bundle excludes third-party legacy puzzle data and
  includes a selected snapshot of the exact pre-test code.

Run `make paper-package` to regenerate and verify the manuscript, independently
reanalyze all raw rows and returned paths, compile both formats, and create
the ZIP files and checksums in `paper/dist/`.

## Information still needed from the authors

Record these in `archive/author-inputs.json` and update the manuscript/metadata:

1. CNPq process number (or an explicit statement that no identifier applies).
2. CRediT contributions for each author. Roles have not been invented.
3. Any earlier AI use in research or manuscript preparation so the disclosure
   covers the full workflow. The current paragraph describes this session only.
4. Explicit license for synthetic Challenge v1 data/evidence. The existing
   software MIT license is retained; no new data license has been asserted.
5. Archive record URL and DOI. A local ZIP is not a durable public deposit.
6. Approval of the final manuscript and declarations by all authors, and
   confirmation that the paper is not under consideration elsewhere.

## Archive and submission

Use `archive/README.md` and `archive/metadata-draft.json` to prepare the archival
record. Reserve the real DOI, insert it in Data Availability, rebuild the
bundle, and publish the archive or obtain its supported reviewer-access link.
The manuscript no longer defers this work until acceptance.

Upload `paper/dist/natural-computing-source.zip` and the corresponding
`natural-computing/main.pdf` through the journal portal. Enter the author
contribution and competing-interest information in the portal as well as
the manuscript, following the checked journal instructions. Complete any
reviewer suggestions from the authors' knowledge of conflicts; no reviewer
identities or absence-of-conflict declarations have been fabricated.

The official requirements and template provenance are recorded in
`natural-computing/COMPLIANCE.md`. The cover letter remains marked as a working
draft until author approval and exclusive-submission status are confirmed.

## Frozen evidence integrity

`challenge-v1-confirmatory-v1` remains the original pre-test tag at
`06ef8bbfae5de29fe6cd4ebf0175a94f04880e9b`. Do not move it.
`challenge-v1-paper-v1` identifies the earlier audited paper package, not these
new manuscript revisions. No existing release tag was changed.

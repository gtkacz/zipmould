# Soft Computing submission handoff

Preparation date: 2026-11-16. Status: local package prepared; author inputs
and archival publication remain unresolved. No journal submission has occurred.

Soft Computing (Springer, ISSN 1433-7479) replaces Natural Computing as the
target because it is on the PPGEEC list of journals adherent to CAPES
Engenharias IV for 2021–2024 and Natural Computing is not. The Natural
Computing package remains in Git history at commit `517e1a1`.

## Completed preparation

- Removed “statistically borderline” language and bootstrap-sign emphasis.
- Corrected the zero-effect-puzzle explanation: all 150 puzzles remain in the
  primary denominator and bootstrap; the 114-puzzle subset changes the target
  population and is descriptive only.
- Retained the frozen estimand, configuration, interval, ±5-point band, and
  practical-equivalence classification.
- Shortened the abstract to 217 words and applied author–year references.
- Created `soft-computing/main.tex` with the official Springer Nature class in
  the two-column `iicol` layout that Soft Computing requests, numbered
  equations/tables/figures, author details, and declarations.
- Supplied vector PDF/EPS figures with larger labels and position-based
  interpretation independent of color; both span the two columns.
- Added a disclosure of the AI assistance known from the 2026-10-01 editing
  session.
- Prepared a journal cover-letter draft and reproducible source/evidence ZIP
  builders. The evidence bundle excludes third-party legacy puzzle data and
  includes a selected snapshot of the exact pre-test code.
- Pinned the build date so that rebuilding leaves every tracked artifact
  byte-identical.
- Added the publisher template's standard declaration headings (consent,
  data, materials, and code availability). Author contribution is the only
  standard heading still absent.

Run `make paper-package` to regenerate and verify the manuscript, independently
reanalyze all raw rows and returned paths, compile both formats, and create
the ZIP files and checksums in `paper/dist/`.

## Information still needed from the authors

Record these in `archive/author-inputs.json` and update the manuscript/metadata:

1. CNPq process number (or an explicit statement that no identifier applies).
2. CRediT contributions for each author. Roles have not been invented. Soft
   Computing collects author contributions in the submission interface; add
   an “Author contribution” declaration to `main.typ` from the same roles.
3. Any AI use before or after the 2026-10-01 session, including the Soft
   Computing retargeting, so the disclosure covers the full workflow. The
   current paragraph describes the 2026-10-01 session only.
4. Explicit license for synthetic Challenge v1 data/evidence. The existing
   software MIT license is retained; no new data license has been asserted.
5. Archive record URL and DOI. A local ZIP is not a durable public deposit.
6. Approval of the final manuscript and declarations by all authors, and
   confirmation that the paper is not under consideration elsewhere,
   including at any earlier target journal.
7. Confirmation, in a browser, of the requirement rows in
   `soft-computing/COMPLIANCE.md`. The journal pages could not be opened
   directly during preparation; length limit, whether the standardised
   declarations are mandatory, and the section list are the unconfirmed items.
8. The section to select at submission. The cover letter proposes Optimization.

## Open access under the CAPES agreement

Soft Computing is a hybrid journal and is row 1601 of the Springer portfolio
list for the CAPES–Springer Nature agreement (list updated 2025-12-31;
agreement valid for articles accepted from 2026-01-01 to 2028-12-31; CC BY).
The article processing charge is covered only if the corresponding author is
eligible on the submission date under Portaria CAPES nº 120/2024. Before
submitting, the corresponding author should confirm that:

- Mackenzie Presbyterian University is a participating institution;
- the ORCID in the byline is linked to “Meus Dados CAPES”;
- the affiliation and e-mail given at submission identify the institution.
  The byline currently uses a personal-domain address for the corresponding
  author, and the agreement checks institutional e-mail and affiliation.

Sources: https://www.springernature.com/br/open-science/oa-agreements/brazil/capes
and the eligible-journal spreadsheet linked from that page. The IEEE
spreadsheet in the PPGEEC folder lists IEEE titles only and does not cover
this journal. Publishing under the subscription model needs none of this.

## Archive and submission

Use `archive/README.md` and `archive/metadata-draft.json` to prepare the archival
record. Reserve the real DOI, insert it in Data Availability, rebuild the
bundle, and publish the archive or obtain its supported reviewer-access link.
The manuscript no longer defers this work until acceptance.

Upload `paper/dist/soft-computing-source.zip` and the corresponding
`soft-computing/main.pdf` through the journal portal. Enter the author
contribution and competing-interest information in the portal as well as
the manuscript, following the checked journal instructions. Complete any
reviewer suggestions from the authors' knowledge of conflicts; no reviewer
identities or absence-of-conflict declarations have been fabricated.

The official requirements and template provenance are recorded in
`soft-computing/COMPLIANCE.md`. The cover letter remains marked as a working
draft until author approval and exclusive-submission status are confirmed.

## Frozen evidence integrity

`challenge-v1-confirmatory-v1` remains the original pre-test tag at
`06ef8bbfae5de29fe6cd4ebf0175a94f04880e9b`. Do not move it.
`challenge-v1-paper-v1` identifies the earlier audited paper package, not these
new manuscript revisions. No existing release tag was changed.

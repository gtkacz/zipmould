# Soft Computing preparation record

Target: Soft Computing (Springer, ISSN 1433-7479, journal 500), research
article, initial submission. Requirements checked: 2026-11-16.

Soft Computing appears on the PPGEEC list of journals adherent to CAPES
Engenharias IV for 2021–2024 (`1433-7479 SOFT COMPUTING`). The previous
target, Natural Computing, does not; that package is preserved in Git history
at commit `517e1a1`.

- Instructions: https://link.springer.com/journal/500/submission-guidelines
- Official template: https://www.springernature.com/gp/authors/campaigns/latex-author-support
- Download: https://cms-resources.apps.public.k8s.springernature.io/springer-cms/rest/v1/content/18782940/data/v12
- Template version: Springer Nature 3.1, December 2024 (still the version
  offered on the template page on 2026-11-16).
- `sn-jnl.cls` and `sn-basic.bst` are unmodified publisher files, not project-authored files; their embedded notices govern them.

The unmodified `threeparttable.sty` dependency is included from
https://mirrors.ctan.org/macros/latex/contrib/threeparttable/threeparttable.sty
(accessed 2026-10-01); its header permits redistribution. The unmodified
`xurl.sty` (v0.10, 2022-01-09, LaTeX Project Public License) is included from
TeX Live 2026 so that the flat ZIP does not depend on the submission system's
TeX Live release; it uses only LaTeX2e-era macros.

Both publisher files were compared byte for byte with the template ZIP
downloaded again on 2026-11-16 and are identical.

## How the requirements were read

The journal pages on link.springer.com redirect automated clients to a
sign-in bounce and could not be opened directly during preparation; reading
an archived copy was also refused by the session's permission policy. The
journal rows below were therefore read from search-engine extracts of those
official pages on 2026-11-16. Open the instructions page in a browser and
confirm each row before upload; the last table lists what could not be
confirmed at all.

Three points were confirmed from the publisher's own template package
(`sn-article.tex` and `user-manual.pdf`, December 2024):

- “Should you need to switch to double column layout to suit journal-level
  submission requirements provide the [iicol] option”;
- in that layout, figures span the columns only inside `figure*`;
- where a journal wants standardised declarations, the headings are Funding,
  Conflict of interest/Competing interests, Ethics approval and consent to
  participate, Consent for publication, Data availability, Materials
  availability, Code availability, and Author contribution, and “if any of
  the sections are not relevant to your manuscript, please include the
  heading and write ‘Not applicable’”.

| Requirement (as extracted) | Status in this package |
| --- | --- |
| Manuscripts submitted in LaTeX, Springer Nature template, formatting option `[iicol]` | `\documentclass[pdflatex,sn-basic,iicol]{sn-jnl}`; two-column, 11 pages |
| Source with all style files and figures, plus a PDF of the compiled output | flat `paper/dist/soft-computing-source.zip` and `main.pdf` |
| Abstract of 150 to 250 words, no undefined abbreviations or unspecified references | 217 words, unstructured; the export fails outside 150–250 |
| 4 to 6 keywords | six keywords |
| “Cite references in the text by name and year in parentheses”; list only cited, published or accepted works | Springer Basic author–year (`sn-basic`); the journal check fails on any uncited or unknown key |
| Single-blind review | identified byline, affiliations, and e-mails retained |
| Data availability statement for original research, stating where the data can be found | Section “Reproducibility and data availability”; the archive DOI is still pending |
| Author contributions entered in the submission interface | pending author input; no roles have been invented |
| Plagiarism screening may be applied | no package action required |
| Hybrid journal; open access chosen after acceptance | see “Open access under the CAPES agreement” in `../SUBMISSION.md` |

| Not confirmed from the journal page | Choice made here |
| --- | --- |
| Page or word limit | none applied |
| Whether the journal requires the standardised declarations | all template headings are present except Author contribution, which awaits the authors' roles |
| Mathematics Subject Classification | omitted; the class does not print `\pacs` in the two-column layout |
| Submission system and its TeX Live version | package compiles with pdfLaTeX and BibTeX only; `xurl.sty` and `threeparttable.sty` are bundled, while `booktabs` and the class's own dependencies are expected from the system |
| Section to select at submission | Optimization is proposed in the cover letter; confirm in the submission form |

`main.tex` is generated from `../main.typ` by `../scripts/export_soft_computing.py`.
Edit the Typst manuscript and regenerate; do not maintain divergent text copies.
The publisher class controls layout without margin/font overrides.
The final source ZIP is flat and can be compiled with pdfLaTeX and BibTeX.
Journal figures are exported from the original data-derived SVGs using
librsvg: coordinates are retained, embedded headings/notes are moved to
captions, and label fonts are enlarged for legibility. Both PDF and EPS
are supplied. Both figures span the two columns. Direction is encoded by
position relative to zero as well as color, and the figures remain readable
when rendered in grayscale.

Author contribution and competing-interest information must also be entered
in the submission interface. Confirm coauthor approval, funding identifiers,
the complete AI-use statement, data licensing, and the archival DOI before
upload. None of these confirmations is implied by successful compilation.

The cover letter is a working draft. The manuscript and evidence are prepared
locally; neither a journal submission nor an archive publication has occurred.

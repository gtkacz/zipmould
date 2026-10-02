# Natural Computing preparation record

Target: Natural Computing, research article, initial submission.
Author instructions checked: 2026-10-01.

- Instructions: https://link.springer.com/journal/11047/submission-guidelines
- Official template: https://www.springernature.com/gp/authors/campaigns/latex-author-support
- Download: https://cms-resources.apps.public.k8s.springernature.io/springer-cms/rest/v1/content/18782940/data/v12
- Template version: Springer Nature 3.1, December 2024.
- `sn-jnl.cls` and `sn-basic.bst` are unmodified publisher files, not project-authored files; their embedded notices govern them.

The unmodified `threeparttable.sty` dependency is included from
https://mirrors.ctan.org/macros/latex/contrib/threeparttable/threeparttable.sty
(accessed 2026-10-01); its header permits redistribution.

The package uses the official class, author–year citations, editable LaTeX,
six keywords, an unstructured abstract below 250 words, MSC 2020 codes,
numbered sections, separate numbered tables/figures, and declarations.
MSC 68T20 (heuristics/search) and 68R10 (graph theory in computer science)
were checked against https://mathscinet.ams.org/msc/msc2020.html.
No journal-specific article page limit was identified in the instructions.
The published instructions request author information; this is an identified
initial submission, not an assertion about reviewer identity disclosure.

`main.tex` is generated from `../main.typ` by `../scripts/export_natural_computing.py`.
Edit the Typst manuscript and regenerate; do not maintain divergent text copies.
The publisher class controls layout without margin/font overrides.
The final source ZIP is flat and can be compiled with pdfLaTeX and BibTeX.
Journal figures are exported from the original data-derived SVGs using
librsvg: coordinates are retained, embedded headings/notes are moved to
captions, and label fonts are enlarged for legibility. Both PDF and EPS
are supplied. Direction is encoded by position relative to zero as well as color.

Author contribution and competing-interest information must also be entered
in the submission interface. Confirm coauthor approval, funding identifiers,
the complete AI-use statement, data licensing, and the archival DOI before
upload. None of these confirmations is implied by successful compilation.

The cover letter is a working draft. The manuscript and evidence are prepared
locally; neither a journal submission nor an archive publication has occurred.

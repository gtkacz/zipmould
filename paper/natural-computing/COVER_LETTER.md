Dear Editors of Natural Computing,

Please consider “Does Edge Feedback Help? A Controlled Study of a
Slime-Mould–Inspired Constructor for Ordered Hamiltonian Grid Paths” as a
research article.

The manuscript asks whether adaptive edge state improves a constraint-aware
stochastic constructor when the surrounding algorithm and construction budget
are held fixed. We introduce a synthetic benchmark with planted Hamiltonian
certificates and evaluate the complete feedback package against its frozen-state
ablation. The configuration, analysis, and practical-effect band were frozen
before opening a cryptographically committed test set.

Across 150 puzzles and 30 paired seeds per condition, the mean solve-probability
difference was +1.29 percentage points, with a 95% stratified puzzle-bootstrap
interval of [−0.04, +2.64] points. Its containment within the predeclared ±5-point
band yields a practically equivalent result for this implementation,
configuration, benchmark, and budget. The paper makes no claim of universal
equivalence or state-of-the-art solver performance.

We believe the study fits Natural Computing's experimental scope by providing
controlled evidence about a nature-inspired adaptive mechanism. The contribution
combines the mechanism study, the synthetic benchmark, and the released protocol,
raw outcomes, returned solution paths, and reproducible analysis. It addresses
the attribution of performance to adaptive feedback when the constructor itself
already encodes strong problem-specific constraints.

The public repository is https://github.com/gtkacz/zipmould. The accompanying
evidence package includes all 9,000 trial rows and 4,020 returned solutions.

Sincerely,

Gabriel Mitelman Tkacz, corresponding author  
School of Engineering, Mackenzie Presbyterian University  
gabriel@gtka.cz

---

Working draft: before sending, confirm approval from every coauthor and the
institution, originality/exclusive-submission status, and the final archival
DOI. Those declarations have deliberately not been asserted without author
confirmation. Remove this preparation note only after they are resolved.

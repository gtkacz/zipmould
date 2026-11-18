Dear Editors of Soft Computing,

Please consider “Does Edge Feedback Help? A Controlled Study of a
Slime-Mould–Inspired Constructor for Ordered Hamiltonian Grid Paths” as a
research article. We propose the Optimization section.

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
configuration, benchmark, and budget. Post hoc exploratory runs on public
puzzles add context: recalibrated feedback raised solve probability by about
21 points with the inherited heuristic weights, but a stateless constructor
with re-tuned weights solved more often still, and on top of it feedback added
under five points. The paper makes no claim of universal equivalence or
state-of-the-art solver performance.

We believe the study fits Soft Computing's coverage of metaheuristic
optimization methodologies by providing controlled evidence about a
population-based adaptive mechanism. The contribution combines the mechanism
study, the synthetic benchmark, and the released protocol, raw outcomes,
returned solution paths, and reproducible analysis. It addresses the
attribution of performance to adaptive feedback when the constructor itself
already encodes strong problem-specific constraints.

The public repository is https://github.com/gtkacz/zipmould. The accompanying
evidence package includes all 9,000 trial rows and 4,020 returned solutions.

The manuscript is original, has not been published or submitted elsewhere, and
is not under consideration by another journal. All authors have approved this
submission.

Sincerely,

Gabriel Mitelman Tkacz, corresponding author  
School of Engineering, Mackenzie Presbyterian University  
gabriel@gtka.cz

---

Working draft: before sending, publish the archival deposit and add its DOI to
the manuscript. Coauthor approval and exclusive submission were confirmed by
the corresponding author on 2026-11-16. Extracts of the journal's editorial-board page on 2026-11-16
named Raffaele Cerulli as Editor-in-Chief and Monica Gentili as Area Editor
for Optimization, should you prefer to address the letter by name. Remove
this preparation note once the DOI is in place.

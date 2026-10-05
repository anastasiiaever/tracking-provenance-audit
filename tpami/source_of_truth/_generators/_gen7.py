import os
V="<AUDIT_ROOT>/V6_SOURCE_OF_TRUTH"
def w(n,s): open(os.path.join(V,n),"w").write(s.lstrip("\n")); print("  wrote",n)

w("12_SECTION_PLAN.md", r"""
# SECTION PLAN, v6 MAIN TEXT

Target: TPAMI regular paper. v5 main is 9 numbered sections and 500 lines of
LaTeX. v6 keeps that shape, drops one section, and splits the results by evidence
type rather than by population.

## Proposed hierarchy

```
1  Introduction
2  Related Work
   2.1  Tracking evaluation and post-processing
   2.2  Benchmark audits and leakage
   2.3  Our scope
3  The Evaluated State and Its Admission
   3.1  The evaluated state of a tracking submission
   3.2  Scoreable-target admission
   3.3  Estimand eligibility
   3.4  What each operator structure permits          <- promoted from v5 S6
4  Audited Systems and Setup
   4.1  Released deployments and where their rules are documented
   4.2  The controlled DanceTrack arm
   4.3  Outcome knowledge and chronology
   4.4  Populations, detectors and operator settings
5  Results: Released Deployments
   5.1  Composition of the synthesized set, MOT17
   5.2  Metric change from R0 to R2
   5.3  Ordering under the documented transformation
   5.4  A second population: MOT20 eligibility and composition
   5.5  Operators that rewrite existing rows
6  Results: One Operator, Four Trackers, a Second Population
   6.1  Composition under a common operator
   6.2  Metric change in both directions
   6.3  Ordering under the common operator
   6.4  Where the reference is silent
   6.5  Row-local support: what admission does and does not measure
   6.6  A second operator family, and what it shares with the first
7  Verification
8  Discussion
9  Limitations
10 Conclusion
```

## What each section must do

**1 Introduction.** State the one central claim once: a benchmark score
characterises an evaluated output state, and for several widely used trackers that
state contains rows added by offline post-processing, so the audit available to a
reader depends on the structure of that transition. Open on a number from
`16_ABSTRACT_FACT_PACKET.md`, not on a general observation about benchmarks. Do
not restate the contribution list in later sections.

**2 Related Work.** v5's four subsections collapse to three. Name the specific
works; "prior work has shown" is not acceptable. v5's Sec. 2.3, reconstruction
evaluation and missing data, loses its main-text purpose when the skeleton branch
moves out, so its citations go to Sec. 2.2 where they bear on evaluation audits,
and the imputation literature goes with the branch.

**3 The Evaluated State and Its Admission.** Definitions only, from
`07_METHOD_DEFINITIONS.md`. Sec. 3.2 must state in its own words that admission
is a reference-side predicate and that the synthesized row's coordinates do not
enter it; that sentence is what stops the whole paper being misread. Sec. 3.4 is
new in the main text and carries Table T2: it tells the reader, before any result,
that STV exists on the row-additive path and not elsewhere.

**4 Audited Systems and Setup.** Sec. 4.2 is new. It must say plainly that the
DanceTrack operator is ours, that one detector is shared across four trackers,
and what that buys and costs. Sec. 4.3 must say that the DTI outcomes were known
before the GSI protocol was written.

**5 Results: Released Deployments.** v5's Sec. 4 with the MOT20 gate-stable
figure restored. Sec. 5.5 reports the GPR boundary case and the AFLink-and-GSI
structural case, promoted from v5's supplement because the boundary case now
carries argumentative weight in the Discussion.

**6 Results: One Operator, Four Trackers, a Second Population.** The new arm. Its
internal order matters: composition, then metric change, then ordering, then the
two sections that bound the interpretation. Sec. 6.4 and 6.5 are not caveats
appended to a result; they are results. Sec. 6.6 reports the GSI arm and states in
the same breath that its linear stage shares a mechanism with DTI, so it is not an
independent second mechanism.

This section will be the longest in the paper. That is correct and should not be
evened out against Sec. 5.

**7 Verification.** v5's Sec. 7 with one required correction: the 12,767-row
sentence. See `13_V5_REUSE_MAP.md`.

**8 Discussion.** v5's Sec. 8 holds up and keeps its order. Three changes: the
margin-size argument now has a second population to test it on; the boundary case
gets a paragraph, because an operator that rewrites the state and moves no metric
bounds the paper's own claim; and v5's final paragraph contrasting the controlled
and tracking arms is rewritten, since the controlled arm is now a tracking arm.

**9 Limitations.** From `08_LIMITATIONS_LEDGER.md`. The single-population
limitation changes status and must be stated in the allowed wording: the principal
single-population limitation is substantially reduced. Do not write that breadth
is closed.

**10 Conclusion.** Short. No new claims, no restatement of every result. See
`25_CONCLUSION_FACT_PACKET.md`.

## Length and balance

Do not aim for equal-length sections. Sec. 6 is the new contribution and should
run longest; Sec. 3 is definitional and can be compact; Sec. 10 is a paragraph.
Resist the symmetry of giving Sec. 5 and Sec. 6 the same number of subsections
with the same shape.

## Numbering changes from v5

| v5 | v6 | note |
|---|---|---|
| 1 Introduction | 1 | |
| 2 Related Work | 2 | 2.3 absorbed, 2.4 renamed 2.3 |
| 3 The Evaluated State and Its Admission | 3 | gains 3.4 |
| 4 Audited Systems and Setup | 4 | gains 4.2 |
| 5 Results on Released Tracking Pipelines | 5 | renamed, gains the structural subsection |
| 6 Controlled Evidence from a Second Domain | — | removed; see `13_V5_REUSE_MAP.md` |
| — | 6 | NEW: the controlled tracking arm |
| 7 Verification | 7 | one sentence corrected |
| 8 Discussion | 8 | |
| 9 Limitations | 9 | |
| 10 Conclusion | 10 | |

Every `\ref` and `\label` in reused prose must be re-pointed. v5's labels are
listed in `13_V5_REUSE_MAP.md`.
""")

w("13_V5_REUSE_MAP.md", r"""
# V5 REUSE MAP

v5 main: `TPAMI_main_submission_v5.tex`,
sha256 `628512b614c6fe32db1e2366dbb83fc677d79ca2b8c6193500c16e36519b2131`.
v5 supplement: `TPAMI_supplement_submission_v5.tex`,
sha256 `aae6151e97398eef139583f016d86f281bfc614200a3b243e94e5949cf3a2cd0`.
Both are frozen. Copy from them; never edit them.

## Build facts Codex needs before touching the LaTeX

- v5 main's bibliography command is `\bibliography{main_v4_docx}`. The file it
  resolves to is **`reconcile_20261003/main_v4_docx.bib`**, sha256
  `8bc5de9e2e0e1a9f001151d6c7b0932cc04364b956f3e2bb82d12b9905507f50`, 67 entries.
- The `main.bib` in the project root, sha256
  `640611bb4df1ea410cd755ee5f01df4f3dd5f223f2c9f6d511dd259a5a78b4d7`, has 66
  entries and is **missing `luiten2020trackeval`**, which v5 main cites at line
  133. Building against the root `main.bib` produces an undefined citation. Use
  the reconcile copy, or add the missing entry first.
- v5's supplement contains **zero `\cite` commands and no bibliography**. It is
  self-contained and refers to works by name in prose. v6's supplement should
  keep that property or gain its own bibliography deliberately, not by accident.
- Of the 67 bib entries, 44 are cited and 23 are not. Most of the uncited ones
  belong to the skeleton branch: `yan2018stgcn`, `zhu2023motionbert`,
  `wu2023skeletonmae`, `yan2023skeletonmae`, `zhao2025sphere`, `zheng2025hipart`,
  `wang2024di2pose`, `Marcard_2018_ECCV`, `andriluka2018posetrack`,
  `cho2014gru`, `kalman1960filtering`, `rauch1965rts`, `ipsen2021notmiwae`,
  `jaeger2021imputation`, `gama2025imputation`. They travel with the branch.

## Main text, section by section

| v5 section | lines | verdict | what changes |
|---|---|---|---|
| 1 Introduction | 129–156 | REWRITE | the contribution set changes; two populations and two operator families now |
| 2 Related Work | 157–182 | REUSE with edits | 2.3 "Reconstruction evaluation and missing data" loses its main-text purpose; keep the evaluation-audit citations, move the imputation ones |
| 3.1 The evaluated state | 188–203 | REUSE verbatim where possible | still correct |
| 3.2 Estimand eligibility | 204–210 | REUSE | still correct |
| 4.1 Where the documented rules are reported | 223–252 | REUSE | add the DanceTrack block |
| 4.2 Outcome knowledge and chronology | 253–259 | EXTEND | must now record that DTI outcomes preceded the GSI protocol |
| 4.3 Populations, detectors and operator settings | 260–270 | EXTEND | add DanceTrack-val, the shared detector, `n_min=25`, `n_dti=20`, `interval=20`, `tau=10` |
| 5.1 Composition of the synthesized set | 276–372 | REUSE | restore the MOT20 gate-stable figure in Table 2 |
| 5.2 Metric changes R0 to R2 | 373–379 | REUSE | still correct |
| 5.3 Ordering under the documented transformation | 380–388 | REUSE with added columns | add 3dp and 2dp survival, and the dependence caveat |
| 5.4 Operators that admit no row-additive decomposition | 389–395 | PROMOTE AND EXTEND | becomes v6 Sec. 5.5 plus Table T7; the 52-row figure stands and gains its tolerance |
| 5.5 MOT20 eligibility | 396–412 | REUSE | still correct |
| 6 Controlled Evidence from a Second Domain | 413–444 | SEE THE BRANCH CLASSIFICATION BELOW | |
| 7 Verification | 445–449 | REUSE WITH ONE REQUIRED CORRECTION | see below |
| 8 Discussion | 450–462 | REUSE, three edits | see `12_SECTION_PLAN.md` |
| 9 Limitations | 463–479 | REWRITE from `08_LIMITATIONS_LEDGER.md` | the single-population entry changes status |
| 10 Conclusion | 480–497 | REWRITE | |

### Required correction in Sec. 7, Verification

v5 main, Sec. 7, states:

> A generic implementation reproduced all 12,767 MOT17 synthesized-row admission
> decisions by row identity.

Step 9.1 established what was actually reproduced: the 12,767-row synthesized
population was reconstructed with all 12,767 identities unique, and every
available frozen count was reproduced at the **sequence-by-class** level, 105 of
105 cells for MOT17 and 130 of 130 including MOT20. No frozen per-row class table
exists, so per-row agreement against the frozen artifact could not be and was not
checked.

v6 must state the reproduction at the level at which it holds. Do not weaken the
claim to vagueness and do not keep the per-row phrasing.
Source: `posthoc_composition_20261003/step9_1/STEP9_REPORT_CORRECTIONS.md`,
sha256 `367460ed35323de5f82602e1e439a02218fb25ceb0a9b943f7854d4e48853730`.

### v5 labels that reused prose will reference

`sec:intro`, `sec:related`, `sec:related-tracking`, `sec:framework`,
`sec:framework-states`, `sec:framework-eligibility`, `sec:design`,
`sec:design-axes`, `sec:design-motdti`, `sec:external`, `sec:external-census`,
`sec:external-comp`, `sec:external-metrics`, `sec:external-order`,
`sec:external-structural`, `sec:external-mot20`, `sec:results`, `sec:toolkit`,
`sec:discussion`, `sec:limitations`, `sec:conclusion`, `tab:universe`,
`tab:composition`, `tab:metrics`, `fig:stv-cases`, `fig:overview`,
`fig:v9-states`, `fig:outcomes`, `eq:common-support`.

`sec:results` is attached to v5's Sec. 6, the branch that moves. Reusing it for
v6's new Sec. 6 would silently re-point every cross-reference. Rename it.

## Skeleton-branch classification

The branch is v5 main Sec. 6 (lines 413–444, with Fig. 4
`fig3_common_support_reversal.pdf`), v5 supplement **Part II** (lines 594–1554,
Secs. S9 through S23), and the parts of **Part III** that serve it.

Why it has to be classified at all: v5's Sec. 6 is titled "Controlled Evidence
from a Second Domain" and its job was to supply controlled evidence that the
tracking arm could not. DanceTrack now supplies controlled evidence inside the
tracking domain. v5's own Discussion already concedes that the two arms "concern
different evaluation issues": the skeleton defect scored a method outside its
support, while admission classifies synthesized rows on a file the standard
metrics are still defined on. With a controlled tracking arm in hand, keeping the
skeleton arm in the main text asks the reader to hold two different evaluation
problems at once for no remaining gain.

| item | v5 location | classification |
|---|---|---|
| Common-support definition, Eq. (1), `D = A ∩ C ∩ ⋂_m B_m` | main 415–421 | **KEEP_MAIN_MINIMAL** — it is the general eligibility statement the whole paper uses, not a skeleton result. Move it into v6 Sec. 3.3 and state it over tracking terms. |
| NTU RGB+D retrospective scoring defect, 900 of 181,275 rows, 0.50 % | main 425 | **PRESERVE_FOR_SEPARATE_WORK** |
| NTU pooled reversal, −1.21 to +3.64, with intervals | main 427 and Fig. 4 | **PRESERVE_FOR_SEPARATE_WORK** |
| NTU support-shift accounting, linear 5.24980 unchanged against MAE 9.52936 to 8.88685 | main 435 | **PRESERVE_FOR_SEPARATE_WORK** |
| PoseTrack21 prospective comparison, +2.12, +3.65, −0.0020 | main 437 | **PRESERVE_FOR_SEPARATE_WORK** |
| PoseTrack21 segmentation-rule eligibility set, 8.88 / 10.50 / 36.43 % | main 439 | **PRESERVE_FOR_SEPARATE_WORK** — but see the note below |
| JTA, BDD-derived, MOT17-trajectory, KITTI pointers | main 441 | **REMOVE_FROM_V6_TRACKING_NARRATIVE** |
| Supplement Part II, Secs. S9–S23 | supp 594–1554 | **PRESERVE_FOR_SEPARATE_WORK** in full |
| Supplement S24, frozen skeleton-study record chain | supp 1566 | **PRESERVE_FOR_SEPARATE_WORK** |
| Supplement S25, the audit framework implementation | supp 1688 | **MOVE_TO_SUPPLEMENT** — it documents the audit library, which v6 still ships; strip the Part II layer references and keep it |
| Supplement S26, claim ledger for the controlled arm | supp 1715 | **PRESERVE_FOR_SEPARATE_WORK** |
| Supplement S27, controlled-arm diagnostic ledger | supp 1791 | **PRESERVE_FOR_SEPARATE_WORK** |
| Supplement S28, Provenance, and Table S30 | supp 1849 | **MOVE_TO_SUPPLEMENT** — the minimal tracking-submission provenance record is a tracking contribution; drop its skeleton-record mapping paragraph |
| Supplement S29, extended limitations of the supplementary analyses | supp 1900 | **SPLIT** — skeleton-specific assumptions go with the branch; anything bearing on the tracking arm folds into v6's limitations |
| Supplement S30, excluded results | supp 1933 | **PRESERVE_FOR_SEPARATE_WORK** — it is an exclusion record for JTA learned-model values |

One qualification worth stating rather than hiding. The PoseTrack21
segmentation-rule result is the cleanest demonstration in the whole paper that an
eligible fraction is a function of an operational definition rather than a fact
about a dataset, and v6 has no tracking analogue of it: the admission-gate sweep
varies a threshold, not a segmentation rule. Dropping it costs the paper
something real. The recommendation is still to drop it from the tracking
narrative, because importing one skeleton result to make a definitional point
re-opens the whole branch for a reviewer. If v6 wants that point, it should be
made over the gate sweep and the `n_min` sensitivity, which are tracking facts
already in hand.

Nothing in this classification is a scientific correction. No skeleton number was
found to be wrong. The branch is being scoped out of this paper's narrative, and
every artifact stays where it is.
""")

w("14_SUPPLEMENT_PLAN.md", r"""
# SUPPLEMENT PLAN, v6

v5's supplement is 30 sections in three parts, with Part II devoted to the
skeleton domain. v6's supplement keeps the three-part shape and refills Part II.

## Structure

```
Part I   Tracking-provenance evidence: released deployments
  S1   Audited systems and documentation
  S2   Audited repository versions and commits
  S3   MOT17 composition, full
  S4   MOT17 metric values, full
  S5   MOT17 ordering, complete 50-cell matrix
  S6   Admission implementation and verification
  S7   Post-processing that rewrites existing rows
  S8   MOT20 eligibility
  S9   MOT20 evaluation
  S10  Admission sensitivity and anchor analysis

Part II  Controlled evidence: one operator, four trackers
  S11  DanceTrack protocol freeze and chronology
  S12  Asset acquisition, hashes and the evaluator check
  S13  Training-split disjointness and selection provenance
  S14  The common operator and its verbatim extraction
  S15  Reproducibility up to tracker-id relabelling
  S16  DanceTrack composition, full, with the gate sweep
  S17  DanceTrack metric states and deltas
  S18  DanceTrack ordering, complete 30-cell matrix
  S19  DTI parameter sensitivity
  S20  Where the reference is silent: the REFERENCE_ABSENT mechanism
  S21  Row-local geometric support
  S22  A second operator family: controlled GSI
  S23  GSI decomposed into its linear and Gaussian-process stages
  S24  Three-tracker provenance sensitivity

Part III Ledgers, reproducibility and limitations
  S25  The audit framework implementation
  S26  Execution, authorization and the frozen evidence chain
  S27  Bootstrap design and index hashes
  S28  Provenance, and the minimal tracking-submission record
  S29  Numeric ledger
  S30  Extended limitations
  S31  Excluded and superseded results
```

## What each new section must contain

**S11.** The protocol lock hash
`991a455fff6bd0ceffb879c50cee372822904c2d5fea07b1b4b131280d8514a9`, its 19
sections named, and the chronology: the protocol was frozen before any DanceTrack
result was inspected; the GSI protocol
(`6ac1b00bd6ef37bfc5c5b7bc416c33ad46c4735d2f0c910cb9c42ea8f31484b8`) was written
after the DTI outcomes were known and frozen before any GSI output was inspected.

**S12.** The D1A manifest, 77 entries, and the TrackEval pin
`12c8791b303e0a0b50f753af204249e622d0281a`. Record also that the evaluator was
not modified: the CLI argument-parsing problem encountered during setup was
worked around by relying on defaults, not by editing the pinned code.

**S14.** State that `common_dti.py`
(`e0f2289f7051225377455ac7033541c9dbb0113cff55b08be0b9b9e9a49315ea`) is a verbatim
extraction of `dti` and `write_results_score` from ByteTrack's
`tools/interpolation.py` at commit `d1bf0191`, and that the extracted segments
hash identically across the three repositories that ship this code. Give the
segment hashes.

**S15.** The tracker-id equivalence clarification,
`b5e008fc8fc7dfc5f66d3252cb27c94f001d60bfcc42aed1dc22b5ef2d969feb`. This section
must state the invariance results at the precision at which they were verified,
and in particular must not claim STV invariance under arbitrary permutations.
Explain the cause: `BaseTrack._count` is a class attribute and `clear_count()` is
never called, so a subset run shifts every id by a constant; the observed
ByteTrack mapping was the order-preserving shift +424.

**S20.** The positive mechanism, not just the count. All 16,019 REFERENCE_ABSENT
rows across four trackers and five gates lie strictly inside a gap in the
ground-truth track's own observed frame set; 250,470 of 250,470 independent
predicate evaluations agree with the frozen classifier; DanceTrack's scoreable
ground truth has 1,370 interior gaps over 209 of 273 tracks, MOT17's has none over
339. Corroborated by `Frag = 1370` from an independent evaluator computation.

**S21.** Both directions of the admission-against-geometry comparison, including
the 1.78 to 2.61 % of admitted rows below IoU 0.5. A table that shows only the
non-admitted side would read as a defence rather than a measurement.

**S23.** The three-state decomposition with the stage attribution: 7 of 30
crossings on R0→L_GSI, 0 of 30 on L_GSI→GSI, and the GP stage's own effect, all 20
cells moved, median share 0.181, opposing the linear stage in 8 of 20. Both halves
belong here. Reporting only the 0 of 30 would understate the GP stage; reporting
only the movement would overstate it.

**S31.** The corrections record, stated plainly, because a reader who finds an
earlier number elsewhere needs to be able to resolve it:
the GPR rewrite count, 212 superseded by 52 above 1e-6 px with 2,622 at exact
equality, and why a 2-decimal comparison produced a non-monotone series;
the MOT20 gate-stable figure, omitted from an intermediate report and restored;
the per-row against sequence-by-class replay phrasing;
the "25 independent sequences" phrasing;
and the reading of the GSI arm as an independent second mechanism, superseded by
the stage decomposition.

## Citation handling

v5's supplement has no `\cite` commands and no bibliography. Keep that, and refer
to works by name. If v6's supplement is given a bibliography, it needs its own
`.bib` and its own `\bibliography` line; do not assume it inherits the main
text's.

## Rules

- Every supplement section names the artifacts it draws on, with hashes.
- No supplement section may introduce a number absent from
  `05_NUMERIC_LEDGER.csv`.
- Part II of v6 contains no skeleton content. If a sentence of v5 Part II is
  reused anywhere, it is in S25 only, with its Part II layer references stripped.
""")

w("15_CITATION_AND_RELATED_WORK_NOTES.md", r"""
# CITATION AND RELATED-WORK NOTES

Style only for the ordering of this material; the factual content of each cited
work is the author's responsibility, and this file does not assert findings on
their behalf.

## The bibliography file to use

`reconcile_20261003/main_v4_docx.bib`,
sha256 `8bc5de9e2e0e1a9f001151d6c7b0932cc04364b956f3e2bb82d12b9905507f50`, 67
entries. The root `main.bib` is one entry short and will break the `luiten2020trackeval`
citation. See `13_V5_REUSE_MAP.md`.

## Cited in v5 main and still needed

Audited systems and their post-processing:
`zhang2022bytetrack`, `cao2023ocsort`, `maggiolino2023deepocsort`,
`maggiolino2023deepocsortarxiv`, `aharon2022botsort`, `yang2024hybridsort`,
`du2023strongsort`, `liu2025sparsetrack`, `zhou2022osnetain`, `ge2021yolox`.

Benchmarks and metrics:
`dendorfer2021motchallenge`, `dendorfer2020mot20`, `sun2022dancetrack`,
`luiten2021hota`, `luiten2020trackeval`, `bernardin2008clear`,
`ristani2016performance`.

Evaluation auditing, leakage and reporting practice:
`maierhein2018rankings`, `maierhein2020bias`, `kalischek2023biasbed`,
`northcutt2021labelerrors`, `recht2019imagenet`, `kapoor2023leakage`,
`zendel2017cvdata`, `kovatchev2024transparency`, `yu2024rethinking`,
`hu2026pooled`, `gebru2021datasheets`, `mitchell2019modelcards`.

Statistical and resampling background:
`field2007bootstrapping`, `little2019missing`.

## New citations v6 should add

- **DanceTrack as a population.** `sun2022dancetrack` is already in the bib and
  cited in v5 main. v6 needs it in the setup section with its validation-split
  size, and the dataset's own characterisation of uniform appearance and diverse
  motion is the reason the four trackers behave differently here.
- **Metric decomposition.** The point that DetA and AssA are factors of HOTA is
  attributable to `luiten2021hota` and should be cited where the dependence
  caveat is stated, not left as a bare assertion.
- **Gaussian-process smoothing in trackers.** `du2023strongsort` is the source of
  GSI, already cited. Cite it again where the controlled GSI arm is introduced, so
  the reader knows the operator is theirs and the application is ours.
- `ghosh2026evalcards` and `maierhein2024metrics` sit in the bib uncited. Both
  bear on reporting practice and belong in the Discussion paragraph on prediction
  provenance, where v5 currently cites only datasheets, BIAS and model cards.
- `traub2024selective` and `khurshid2024applicability` are uncited and concern
  applicability and selective prediction. They were presumably acquired for the
  skeleton branch. Cite them in Sec. 2.2 only if the eligibility argument actually
  uses them; otherwise let them go with the branch rather than carrying dead
  references.

## Citations that leave with the skeleton branch

`shahroudy2016ntu`, `sun2019hrnet`, `duan2022pyskl`, `doering2022posetrack21`,
`fabbri2018jta`, `geiger2012kitti`, `yu2020bdd100k`, `chib2024trajimpute`,
`gomes2021gapfilling`, `skurowski2021gap`, `yuhai2024recovery`,
`almaleh2025review`, plus the uncited skeleton set listed in
`13_V5_REUSE_MAP.md`.

Two of these need a decision rather than a reflex: `geiger2012kitti` and
`yu2020bdd100k` are tracking datasets, and a reviewer may ask why a paper about
tracking-submission provenance audits neither. The honest answer belongs in
Limitations, as L1's residual: two MOTChallenge-format pedestrian or dancer
populations, no vehicle or multi-camera population. Make that statement in the
limitations section rather than keeping the citations in Related Work with
nothing behind them.

## Related Work ordering

v5's order is defensible and should be kept: evaluation and post-processing
first, because that is where the object of study lives; then benchmark audits,
because that is the genre; then scope. The one change is that v5's Sec. 2.3 on
reconstruction evaluation and missing data no longer has a result behind it in
this paper, so it stops being a subsection and its evaluation-relevant citations
fold into Sec. 2.2.

Do not open Related Work with a general sentence about the growth of the
literature. Open with the specific practice the paper audits: that several
released trackers ship an offline interpolation stage and submit its output.

## Rules

- Name the work, not the category. "Prior work has shown" is not acceptable in
  v6; `maierhein2018rankings` showed a specific thing about ranking stability and
  the sentence should say which.
- Do not cite a work for a claim this project verified itself, and do not cite
  this project's artifacts as if they were literature. The artifact hashes belong
  in the supplement, the citations in the bibliography.
- Every citation added to v6 must be in the `.bib` before the sentence is written.
  A `\cite` to a missing key is how v5 arrived at its one broken reference.
""")

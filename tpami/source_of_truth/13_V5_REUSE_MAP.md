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
| 5.4 Operators that admit no row-additive decomposition | 389–395 | PROMOTE AND EXTEND | becomes v6 Sec. 6 plus Table T7; the 52-row figure stands and gains its tolerance |
| 5.5 MOT20 eligibility | 396–412 | REUSE | still correct |
| 6 Controlled Evidence from a Second Domain | 413–444 | SEE THE BRANCH CLASSIFICATION BELOW | |
| 7 Verification | 445–449 | REUSE WITH ONE REQUIRED CORRECTION | see below |
| 8 Discussion | 450–462 | REUSE, three edits | see `12_SECTION_PLAN.md` |
| 9 Limitations | 463–479 | REWRITE from `08_LIMITATIONS_LEDGER.md` | the single-population entry changes status |
| 10 Conclusion | 480–497 | REWRITE | |

### Required correction to v5's Verification paragraph

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
v6's new Sec. 5 would silently re-point every cross-reference. Rename it.

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
| v5 main Sec. 7, Verification | main 445–449 | **DISTRIBUTE** — see `12_SECTION_PLAN.md`; v6 has no numbered Verification section |
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

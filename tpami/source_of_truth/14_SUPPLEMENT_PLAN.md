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
the 1.7849 to 2.6080 % of admitted rows below IoU 0.5. A table that shows only the
non-admitted side would read as a defence rather than a measurement.

**S23.** The three-state decomposition with the stage attribution: 7 of 30
crossings on R0→L_GSI, 0 of 30 on L_GSI→GSI, and the GP stage's own effect, all 20
cells moved, median share 0.1812, opposing the linear stage in 8 of 20. Both halves
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

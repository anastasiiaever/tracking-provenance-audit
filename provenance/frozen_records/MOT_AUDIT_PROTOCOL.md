# MOT interpolation audit — frozen primary protocol
Frozen 2026-08-28, before any scientific outcome was computed.
Scope: ByteTrack, BoT-SORT, OC-SORT on MOT17 val-half. Nothing else.

## 1. Question
Published MOT trackers ship an offline interpolation post-processor that
fabricates detection rows for frames where the tracker emitted nothing. The
post-processed file is indistinguishable from raw tracker output: all four
audited writers emit the same 10-column MOTChallenge format, and TrackEval has
no field, flag or code path separating a synthesized row from a tracker-emitted
one. This audit measures, on a common population, how much of a published
metric rests on synthesized rows, and how many of those rows correspond to a
real, scoreable ground-truth target.

No directional hypothesis. No minimum effect size. A null result is valid.

## 2. Population
MOT17 train, FRCNN detector copy, second-half ("val-half") frames only:
`image_range = [n//2+1, n-1]` 0-based, rebased to 1..N. 7 sequences,
2,652 frames. Proven identical across the three trackers:
ByteTrack/OC-SORT via `val_half.json` from the authors' own
`convert_mot17_to_coco.py`; BoT-SORT via `files[len(files)//2+1:]` in
`tools/track.py` with `enumerate(files, 1)`. DPM/SDP copies are excluded;
their images are byte-identical to FRCNN and the frozen MOT17 record already
established the three GT copies byte-identical, 7/7.

## 3. Shared detector
All three use the same YOLOX-X ablation checkpoint
`bytetrack_ablation.pth.tar` and the same `yolox_x_ablation` exp at 800x1440.
Detector is therefore not a source of cross-tracker difference.

## 4. States
- **R0** raw tracker output, copied read-only and SHA-256'd before any
  post-processor runs (mandatory: BoT-SORT's `--save_path` defaults to
  overwriting its input).
- **R1** R0 + only the synthesized rows classified SEMANTICALLY_VALID.
- **R2** R0 + all rows the unmodified published `dti()` produces at the frozen
  call-site parameters.
- **R0w** R0 written through the authors' own `write_results_score`; a
  formatting control, since that writer hardcodes `s=-1` for every row.

`R0 ⊆ R1 ⊆ R2` is asserted by (frame, tracker_id) row identity, not cardinality.

## 5. Frozen call-site parameters
| tracker | n_min | n_dti | source |
|---|---|---|---|
| ByteTrack | 5 | 20 | `tools/interpolation.py` `__main__` |
| BoT-SORT | 5 | 20 | `tools/interpolation.py` argparse defaults |
| OC-SORT | 30 | 20 | `tools/interpolation.py` `__main__` |

Gap rule in all three: fill iff `1 < right_frame - left_frame < n_dti`, and the
track satisfies `n_frame > n_min`. Interior gaps only — at `i == 0` the source
sets `left = right`, so the guard is false and no extrapolation occurs.
Linear on columns 2:6 = (x, y, w, h).

## 6. STV — Semantic Trajectory Validity
NOT Gate 1R. A distinct, reference-side semantic audit.

Anchor assignment is frozen once on R0 and never recomputed after rows are
added: per-frame one-to-one Hungarian assignment on IoU against
MOT17-preprocessing-surviving pedestrian GT (`class == 1` and
`zero_marked != 0`), IoU gate 0.5. This is the stateless matcher form TrackEval
uses in `get_preprocessed_seq_data`. It is deliberately **not** the CLEAR
matcher (which adds a +1000 previous-frame continuity bonus) and **not** the
HOTA matcher (sequence-global Jaccard alignment over 19 alpha thresholds).
It is a semantic-classification device only and plays no part in metric
computation.

Class priority, exhaustive and mutually exclusive, asserted programmatically:
- **A ANCHOR_UNMATCHED** at least one R0 anchor has no frozen GT match
- **B ANCHOR_ID_MISMATCH** both matched, to different GT identities
- **C TARGET_REFERENCE_ABSENT** same GT identity g, no scoreable GT row for g at t
- **D SEMANTICALLY_VALID** same GT identity g, scoreable GT row for g at t

## 7. Estimands
- **E1** structural DTI coverage: synthesized instants / all intra-track missing instants.
- **E2** exact STV partition, counts and fractions.
- **E3** native TrackEval HOTA, DetA, AssA, IDF1, MOTA at R0, R1, R2.
- **E4** R1−R0, R2−R1, R2−R0 per metric. **R2−R1 is not an additive or causal
  attribution** — these metrics are non-additive in the detection set.
- **E5** pairwise ordering matrices per metric per state; descending, native
  float precision before rounding, exact equality is a tie, relations in
  {>, <, =}. An ordering change is categorical. No composite score, no
  averaging across metrics, no pooling across trackers.

## 8. Evaluator
TrackEval `12c8791b303e0a0b50f753af204249e622d0281a`, unmodified, run through
its own `scripts/run_mot_challenge.py`. `BENCHMARK=MOT17`,
`SPLIT_TO_EVAL=val_half`, `CLASSES_TO_EVAL=['pedestrian']`, `DO_PREPROC=True`,
`METRICS=HOTA CLEAR Identity`, `THRESHOLD=0.5`, `USE_PARALLEL=False`.
Environment pinned to numpy 1.23.5 because this commit uses `np.int`/`np.float`,
removed in numpy 1.24. The five metrics do not share one matcher; no claim is
made that they do.

## 9. Wording discipline
Results are reported as "the published interpolation pipeline instantiated on
MOT17 validation". They are **not** a reproduction of any published leaderboard
number: the leaderboard uses the test split, a different tracker state and the
server-side evaluator. None of those conditions holds here.

## 10. Integrity gates (hard-fail, never silently repaired)
Frames ascending; (frame, id) unique; finite coordinates; positive w/h;
>=7 columns. `dti()` assumes file order is temporal order and does not sort,
so violated order would silently change the result.

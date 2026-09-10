# MOT20 Semantic Completion — Amendment 09A

**Resolves `MOT20_POPULATION_RULE_UNDERSPECIFIED`. No data acquired, nothing
executed, no MOT20 scientific outcome exists.**

## Chronology, stated plainly

The MOT20 dataset, sequence universe and second-half frame rule were
**pre-specified before MOT17 execution**. The evaluator-native MOT20 GT
semantics, distractor handling, evaluator naming and manifest hashing
specification are being completed **after MOT17 results became known**, but
**before any MOT20 execution**.

The permitted wording is therefore:

> The MOT20 population and split rule were pre-specified before MOT17 execution;
> evaluator-native MOT20 GT semantics were completed afterward from the
> already-pinned TrackEval implementation, before any MOT20 execution.

It must **never** be claimed that the complete MOT20 estimand was fully
specified before all MOT17 results.

No choice here uses the MOT17 flip count, metric values, STV composition,
materiality result or GPR result. Every semantic below is mechanically derived
from TrackEval `12c8791b303e0a0b50f753af204249e622d0281a` and was verified
against that source (10/10 checks PASS).

## Source of semantics

MOT20 evaluation and GT semantics are defined by the **native MOT20 branch** of
the already-frozen evaluator, `trackeval/datasets/mot_challenge_2d_box.py`. They
are **not** copied from MOT17 — which matters, because the two differ.

## Scoreable GT predicate (STV reference population)

```
gt_zero_marked != 0   AND   gt_class == pedestrian (class id 1)
```

Evaluator evidence:
`gt_to_keep_mask = (np.not_equal(gt_zero_marked, 0)) & np.equal(gt_classes, cls_id)`.

**No additional filter** — no visibility, crowd-density, box-size or occlusion
threshold — because the frozen evaluator requires none for this predicate.

## Distractor preprocessing

| Benchmark | Distractor class ids |
|---|---|
| MOT17 | 2, 7, 8, 12 |
| **MOT20** | **2, 6, 7, 8, 12** |

MOT20 **adds `non_mot_vehicle` (class 6)**. Evidence:

```
distractor_class_names = ['person_on_vehicle', 'static_person', 'distractor', 'reflection']
if self.benchmark == 'MOT20':
    distractor_class_names.append('non_mot_vehicle')
```

TrackEval matches tracker predictions against GT using its frozen Hungarian/IoU
preprocessing and removes tracker detections matched to these distractor classes.
The MOT17 list must not be transferred.

## Crowd / ignore semantics

No additional crowd mask is invented. The pinned evaluator's behaviour is frozen
as-is: `crowd` (class 13) exists in the class map but is **not** in the MOT20
distractor list; **no crowd ignore regions** are used by MOTChallenge 2D-box
preprocessing (`gt_crowd_ignore_regions` is not referenced in
`get_preprocessed_seq_data`); and after preprocessing, non-pedestrian GT is not
part of the evaluated pedestrian GT set.

## STV and TrackEval are distinct operations

| | Set / behaviour |
|---|---|
| **STV reference set** | scoreable pedestrian GT only (`mark != 0`, `class == 1`) |
| **TrackEval preprocessing** | native MOT20 preprocessing, including distractor handling, before pedestrian-only GT retention |

Conflating them is forbidden. STV anchors may never match distractor, crowd or
non-pedestrian objects as scoreable references. The STV matcher is **unchanged**:
IoU 0.5, gate-before-assignment, one-to-one Hungarian, R0 anchors only. No
threshold changed.

## Evaluator naming

`BENCHMARK = MOT20`, `SPLIT_TO_EVAL = val`, physical split `MOT20-val`.

`BENCHMARK` must remain `MOT20` so the frozen evaluator activates MOT20 native
preprocessing including `non_mot_vehicle`. **`val` is a study-side split
identifier only** — MOTChallenge publishes no official MOT20-val split; the
population is constructed from MOT20 **train**. Deterministic seqmap:
`MOT20-01`, `MOT20-02`, `MOT20-03`, `MOT20-05`.

## Frame rule — unchanged, arithmetic verified independently

Zero-indexed `image_range = [N // 2 + 1, N - 1]`, hence native one-indexed frames
`[N // 2 + 2, N]`.

| Sequence | N | Included native frames | Count |
|---|---|---|---|
| MOT20-01 | 429 | 216–429 | 214 |
| MOT20-02 | 2782 | 1393–2782 | 1390 |
| MOT20-03 | 2405 | 1204–2405 | 1202 |
| MOT20-05 | 3315 | 1659–3315 | 1657 |
| **Total** | | | **4463** |

Recomputed independently from the rule and the published lengths: 214 + 1390 +
1202 + 1657 = **4463**. This is a pre-materialization arithmetic consequence of
the already-frozen split. **If the on-disk materialization does not match
exactly, STOP.**

## Population manifest specification

Defined in `09A_MOT20_POPULATION_MANIFEST_SPEC.json`: required fields, canonical
UTF-8 JSON with sorted keys, stable sequence order 01/02/03/05, and no wall-clock
value inside the hashed scientific object. GT and `seqinfo.ini` hashes are left
**unfilled** — they are not invented before acquisition.

## Cells unchanged

All seven documented MOT20 cells keep their frozen roles and remain
`STOPPED_UNSEEN` / `STOPPED_DATASET_NOT_ACQUIRED` until official data is
acquired. This amendment changes no role, family, audit mode or knowledge status.

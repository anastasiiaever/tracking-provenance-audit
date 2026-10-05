import os, csv
V = "<AUDIT_ROOT>/V6_SOURCE_OF_TRUTH"
def w(n, s):
    open(os.path.join(V, n), "w").write(s.lstrip("\n")); print("  wrote", n)
def wc(n, hdr, rows):
    with open(os.path.join(V, n), "w", newline="") as f:
        wr = csv.writer(f); wr.writerow(hdr); wr.writerows(rows)
    print(f"  wrote {n} ({len(rows)} rows)")

w("02_CURRENT_FACTS.md", r"""
# CURRENT FACTS

Every figure below was verified against a frozen artifact. Artifact paths and
hashes are in `09_PROVENANCE_LEDGER.csv`; every number also appears as a row of
`05_NUMERIC_LEDGER.csv`.

## A. MOT17, released-deployment audit

Population: FRCNN copy of the training sequences, second half of each sequence
under the trackers' own split rule, 7 sequences, 2,652 frames, frame indices
re-based to 1. Scoreable ground truth: `mark != 0 AND class == 1`.

Five released deployments, each applying its own documented linear DTI with its
own released parameters. Composition at the primary gate 0.50:

| deployment | synthesized | UNMATCHED | ID_MISMATCH | REFERENCE_ABSENT | ADMITTED | non-admitted | % non-admitted |
|---|---|---|---|---|---|---|---|
| Deep-OC-SORT | 2,960 | 570 | 286 | 0 | 2,104 | 856 | 28.9189 |
| OC-SORT | 2,622 | 408 | 375 | 0 | 1,839 | 783 | 29.8627 |
| BoT-SORT | 2,090 | 576 | 227 | 0 | 1,287 | 803 | 38.4211 |
| ByteTrack | 2,072 | 604 | 244 | 0 | 1,224 | 848 | 40.9266 |
| Hybrid-SORT | 3,023 | 1,266 | 216 | 0 | 1,541 | 1,482 | 49.0241 |

Range 28.92 to 49.02 %. **REFERENCE_ABSENT is zero for every MOT17 deployment.**

Gate-stable non-admission, non-admitted at all five gates:

| deployment | gate-stable non-admitted | % | gate-stable admitted | switching | persistent UNMATCHED | persistent ID_MISMATCH | persistent REFERENCE_ABSENT |
|---|---|---|---|---|---|---|---|
| Deep-OC-SORT | 694 | 23.4459 | 1,244 | 1,022 | 370 | 178 | 0 |
| OC-SORT | 666 | 25.4005 | 1,151 | 805 | 261 | 225 | 0 |
| BoT-SORT | 634 | 30.3349 | 882 | 574 | 369 | 87 | 0 |
| ByteTrack | 694 | 33.4942 | 824 | 554 | 417 | 77 | 0 |
| Hybrid-SORT | 1,327 | 43.8968 | 942 | 754 | 1,015 | 51 | 0 |

Range 23.45 to 43.90 %.

Pooled metric values, R0 and R2:

| deployment | state | HOTA | DetA | AssA | IDF1 | MOTA |
|---|---|---|---|---|---|---|
| BoT-SORT | R0 | 69.1951 | 67.2514 | 71.7077 | 81.6436 | 78.4394 |
| BoT-SORT | R2 | 70.4191 | 68.7403 | 72.6800 | 82.6976 | 80.4992 |
| ByteTrack | R0 | 67.9198 | 66.6298 | 69.7904 | 79.9037 | 77.9551 |
| ByteTrack | R2 | 68.9666 | 67.9707 | 70.5581 | 80.8204 | 79.7402 |
| Deep-OC-SORT | R0 | 68.3108 | 64.7875 | 72.4486 | 81.1332 | 75.1531 |
| Deep-OC-SORT | R2 | 70.2688 | 67.5234 | 73.6031 | 82.9009 | 78.9367 |
| Hybrid-SORT | R0 | 66.9485 | 65.9912 | 68.4727 | 77.7451 | 75.9918 |
| Hybrid-SORT | R2 | 67.8105 | 67.3117 | 68.9198 | 78.1933 | 77.5877 |
| OC-SORT | R0 | 66.3724 | 64.2377 | 69.0055 | 77.9321 | 74.5352 |
| OC-SORT | R2 | 67.9901 | 66.6442 | 69.8395 | 79.4175 | 77.8104 |

All 25 metric deltas are positive. That is the MOT17-specific fact that
DanceTrack does **not** reproduce.

Ordering: 5 of 50 exhaustive pairwise metric cells cross zero. All five survive
3-decimal and 2-decimal score reporting. Sequence-cluster bootstrap, 7
sequences, 10,000 draws, seed 20261003, index SHA-256
`8cd16bcc23a47d1f4ce8bd5275ad8df660fa69411390b8ee7e365970e2db7cd2`. Percentile
intervals exclude zero in 33 of 50 cells at R0, 28 of 50 at R2, 32 of 50 for the
delta margin.

Row-local geometric support, maximum IoU of each synthesized row against
scoreable GT in the same frame, at gate 0.50:

| deployment | class | n | % IoU = 0 | % 0 < IoU < 0.5 | % IoU >= 0.5 |
|---|---|---|---|---|---|
| BoT-SORT | ADMITTED | 1,287 | 0.00 | 2.25 | 97.75 |
| BoT-SORT | ANCHOR_UNMATCHED | 576 | 14.58 | 41.15 | 44.27 |
| BoT-SORT | ANCHOR_ID_MISMATCH | 227 | 0.00 | 14.54 | 85.46 |
| ByteTrack | ADMITTED | 1,224 | 0.00 | 1.88 | 98.12 |
| ByteTrack | ANCHOR_UNMATCHED | 604 | 12.91 | 41.72 | 45.36 |
| ByteTrack | ANCHOR_ID_MISMATCH | 244 | 0.00 | 19.67 | 80.33 |
| Deep-OC-SORT | ADMITTED | 2,104 | 0.05 | 1.38 | 98.57 |
| Deep-OC-SORT | ANCHOR_UNMATCHED | 570 | 19.65 | 40.53 | 39.82 |
| Deep-OC-SORT | ANCHOR_ID_MISMATCH | 286 | 3.50 | 8.74 | 87.76 |
| Hybrid-SORT | ADMITTED | 1,541 | 0.00 | 1.49 | 98.51 |
| Hybrid-SORT | ANCHOR_UNMATCHED | 1,266 | 16.43 | 48.42 | 35.15 |
| Hybrid-SORT | ANCHOR_ID_MISMATCH | 216 | 0.00 | 17.59 | 82.41 |
| OC-SORT | ADMITTED | 1,839 | 0.05 | 0.98 | 98.97 |
| OC-SORT | ANCHOR_UNMATCHED | 408 | 22.79 | 41.67 | 35.54 |
| OC-SORT | ANCHOR_ID_MISMATCH | 375 | 2.67 | 10.40 | 86.93 |

Taxonomy priority order, frozen: ANCHOR_UNMATCHED, then ANCHOR_ID_MISMATCH, then
TARGET_REFERENCE_ABSENT, then SEMANTICALLY_ADMITTED. The four classes partition
the synthesized set exactly at every deployment and every gate.

Gate dependence: non-admission rises monotonically with the gate for every
deployment on every population tested.

**Verification level, corrected by Step 9.1.** Re-execution reconstructed the
same 12,767-row MOT17 synthesized population with all 12,767 row identities
unique, and reproduced every available frozen sequence-by-class count exactly,
105 of 105 for MOT17 and 130 of 130 including MOT20. A retained frozen per-row
STV classification table does not exist, so a retrospective row-wise join to the
original execution could not be performed. The only two surviving frozen per-row
labels, in `FIGURE_CASES.json`, both agree with the replay including both anchor
frames.

## B. MOT20, secondary released population

Seven configurations were pre-specified before any MOT17 execution. One is
eligible for the held-out second-half comparison, five fail clause (i) through
detector-training overlap, and one is unresolved under clause (ii).

- clause (i) overlap: ByteTrack, BoT-SORT, OC-SORT linear, OC-SORT-GPR,
  Hybrid-SORT
- unresolved under clause (ii): StrongSORT++
- eligible: Deep-OC-SORT

Population: second half of MOT20-01, -02, -03 and -05, 4,463 frames. Released
settings `n_min=30`, `n_dti=20`, detector `bytetrack_x_mot17` trained on MOT17,
CrowdHuman, Cityperson and ETHZ without MOT20, appearance model
`osnet_ain_ms_d_c.pth.tar`.

| gate | synthesized | UNMATCHED | ID_MISMATCH | REFERENCE_ABSENT | ADMITTED | non-admitted | % |
|---|---|---|---|---|---|---|---|
| 0.30 | 34,814 | 4,179 | 2,589 | 0 | 28,046 | 6,768 | 19.4405 |
| 0.40 | 34,814 | 5,205 | 2,407 | 0 | 27,202 | 7,612 | 21.8648 |
| **0.50** | 34,814 | 6,586 | 2,165 | **0** | 26,063 | **8,751** | **25.1364** |
| 0.60 | 34,814 | 9,997 | 1,796 | 0 | 23,021 | 11,793 | 33.8743 |
| 0.70 | 34,814 | 17,813 | 1,078 | 0 | 15,923 | 18,891 | 54.2627 |

**Gate-stable non-admission is 6,631 / 34,814 = 19.0469 %.** It is not
missing. Partition 6,631 + 15,835 + 12,348 = 34,814 exactly; persistent
UNMATCHED 4,179, persistent ID_MISMATCH 1,053, persistent REFERENCE_ABSENT 0.
The D1B cross-population table omitted this value through a code filter; the
Step 9 artifact always contained it.

Row-local support: ADMITTED 26,063 rows at 99.99 % IoU >= 0.5;
ANCHOR_UNMATCHED 6,586 rows at 7.06 / 72.56 / 20.38 %; ANCHOR_ID_MISMATCH 2,165
rows at 0.00 / 4.90 / 95.10 %.

One deployment yields no tracker pair, so MOT20 supports a composition check on
a second population but no pairwise ordering analysis.

## C. DanceTrack, controlled DTI arm

**This is a post-hoc controlled intervention. The operator is ours.** It is not
released DanceTrack practice.

Population: the 25 official DanceTrack validation sequences, 25,508 frames,
225,148 GT rows, seqmap SHA-256
`792d9c4bc9ea6cce2c3e6afc98e4150a97c1a0d1a911d465cfac95877a472850`. All GT rows
have `mark = 1`, `class = 1`, `visibility = 1`, so the frozen scoreable predicate
`mark != 0 AND class == 1` is applicable unchanged but performs no filtering.
Track ids start at 0. Resolutions are not uniform: 19 sequences at 1920x1080,
5 at 1280x720, 1 at 1440x1080.

Four trackers, one shared detector: the official DanceTrack ByteTrack YOLOX-X
trained on `train.json` only, SHA-256
`b8d1afba08f801f3fe2cb122faf3fc9af6c7856405a0da94cf91cdd5eb9b3321`, with a
published upstream checksum that matches. Holding the detector fixed is
deliberate: the four deployments differ in association logic, not detection
quality. The cost is reduced detector diversity.

Operator, one common pair for all four: **primary `n_min=25`, `n_dti=20`**;
pre-specified sensitivity `n_min=30`, `n_dti=20`. Frozen implementation
`common_dti.py` SHA-256
`e0f2289f7051225377455ac7033541c9dbb0113cff55b08be0b9b9e9a49315ea`, a verbatim
extraction of `dti` and `write_results_score` from ByteTrack
`tools/interpolation.py` at `d1bf0191`, byte-identical in source text to the same
functions in OC_SORT `a9e24b67` and HybridSORT `396f8d30`.

| tracker | R0 rows | R2 primary | inserted | % of R2 | R2 sens30 | inserted |
|---|---|---|---|---|---|---|
| ByteTrack | 216,310 | 224,821 | 8,511 | 3.786 | 224,754 | 8,444 |
| OC-SORT | 202,787 | 217,890 | 15,103 | 6.931 | 217,726 | 14,939 |
| Deep-OC-SORT | 203,149 | 217,171 | 14,022 | 6.457 | 217,020 | 13,871 |
| Hybrid-SORT | 215,393 | 227,851 | 12,458 | 5.468 | 227,734 | 12,341 |

Composition at the primary gate 0.50:

| tracker | synthesized | UNMATCHED | ID_MISMATCH | REFERENCE_ABSENT | ADMITTED | non-admitted | % |
|---|---|---|---|---|---|---|---|
| Deep-OC-SORT | 14,022 | 2,015 | 2,790 | **1,089** | 8,128 | 5,894 | 42.03 |
| OC-SORT | 15,103 | 2,338 | 3,817 | **1,007** | 7,941 | 7,162 | 47.42 |
| Hybrid-SORT | 12,458 | 5,206 | 1,941 | **829** | 4,482 | 7,976 | 64.02 |
| ByteTrack | 8,511 | 3,659 | 1,642 | **526** | 2,684 | 5,827 | 68.46 |

Range 42.03 to 68.46 %.

Five-gate sweep, % non-admitted:

| tracker | 0.30 | 0.40 | 0.50 | 0.60 | 0.70 |
|---|---|---|---|---|---|
| Deep-OC-SORT | 38.32 | 39.02 | 42.03 | 49.09 | 60.65 |
| OC-SORT | 43.75 | 44.81 | 47.42 | 53.88 | 64.83 |
| Hybrid-SORT | 58.02 | 59.38 | 64.02 | 69.45 | 78.55 |
| ByteTrack | 63.34 | 65.01 | 68.46 | 76.27 | 85.13 |

Gate persistence:

| tracker | gate-stable non-admitted | % | gate-stable admitted | switching | persistent UNMATCHED | persistent ID_MISMATCH | persistent REFERENCE_ABSENT |
|---|---|---|---|---|---|---|---|
| Deep-OC-SORT | 5,335 | 38.05 | 5,469 | 3,218 | 1,062 | 1,564 | 743 |
| OC-SORT | 6,547 | 43.35 | 5,282 | 3,274 | 1,255 | 2,314 | 683 |
| Hybrid-SORT | 7,139 | 57.30 | 2,650 | 2,669 | 3,915 | 901 | 483 |
| ByteTrack | 5,330 | 62.62 | 1,243 | 1,938 | 2,805 | 581 | 264 |

Range 38.05 to 62.62 %. Persistent REFERENCE_ABSENT is non-zero here and zero on
MOT17 and MOT20.

Metric states and the 20 primary deltas:

| tracker | state | HOTA | DetA | AssA | IDF1 | MOTA |
|---|---|---|---|---|---|---|
| ByteTrack | R0 | 46.8928 | 70.6581 | 31.2483 | 51.6362 | 88.3086 |
| ByteTrack | R2 | 46.8092 | 70.1979 | 31.3474 | 51.5258 | 87.7183 |
| OC-SORT | R0 | 52.2352 | 77.3834 | 35.3804 | 51.8532 | 87.2955 |
| OC-SORT | R2 | 52.8939 | 78.7158 | 35.6934 | 52.3025 | 89.7445 |
| Deep-OC-SORT | R0 | 58.6547 | 77.6365 | 44.4570 | 59.4615 | 87.5788 |
| Deep-OC-SORT | R2 | 59.3333 | 79.0713 | 44.7004 | 59.8885 | 90.2202 |
| Hybrid-SORT | R0 | 59.3128 | 78.8666 | 44.8137 | 60.8756 | 89.5158 |
| Hybrid-SORT | R2 | 59.1231 | 78.3596 | 44.8379 | 60.6915 | 89.3777 |

| tracker | HOTA | DetA | AssA | IDF1 | MOTA |
|---|---|---|---|---|---|
| ByteTrack | -0.0836 | -0.4602 | **+0.0991** | -0.1104 | -0.5903 |
| OC-SORT | +0.6587 | +1.3324 | +0.3129 | +0.4493 | +2.4491 |
| Deep-OC-SORT | +0.6786 | +1.4348 | +0.2434 | +0.4269 | +2.6414 |
| Hybrid-SORT | -0.1897 | -0.5071 | **+0.0242** | -0.1841 | -0.1381 |

**12 positive, 0 zero, 8 negative of 20.** OC-SORT and Deep-OC-SORT rise on all
five; ByteTrack and Hybrid-SORT rise only on AssA and fall on the other four.
AssA rises for all four.

Ordering: 7 of 30 exhaustive pairwise metric cells cross zero, all seven
surviving 3-decimal and 2-decimal score reporting. Bootstrap support
`P(sign differs)` ranges 0.3240 to 0.9365; the weakest cell, Deep-OC-SORT
against Hybrid-SORT on HOTA at 0.3240, has percentile intervals straddling zero
in both states.

DTI parameter sensitivity: non-admission differs by at most 0.42 percentage
points between 25/20 and 30/20; metric differences do not exceed 0.0422. The
composition conclusion does not depend on that choice. Primary remains 25/20.

Bootstrap: 25 sequence-level clusters, 10,000 draws, seed 20261003, index
SHA-256 `50b2fb2240ffbdbc221d5a0f73681a4dfbec4ccc4f07a42f9cd01cc3c18516da`,
content hash `342b76e2d37fc633...`, verified to regenerate exactly from
`numpy.random.default_rng(20261003)`. Pooled through TrackEval
`combine_sequences` per draw, never by averaging per-sequence scores; verified
empirically, draw 0 pooled HOTA 45.739823 against a naive mean of 46.595438.

Provenance per tracker: training-split disjointness holds for all four.
Checkpoint-selection provenance is CONFIRMED_NO_VAL for ByteTrack, OC-SORT and
Hybrid-SORT, and **UNRESOLVED for Deep-OC-SORT**, whose released ReID is epoch
31 of 60 and whose code's own selection logic does not explain that choice.
Hyperparameter-selection provenance is UNRESOLVED for all four. These are
separate fields and must never be merged into one "held-out" label.

Three-tracker checkpoint-selection-provenance sensitivity subset, excluding
Deep-OC-SORT but **not** calling it ineligible: 3 of 15 cells cross zero under
DTI. The three are ByteTrack against OC-SORT on MOTA, and OC-SORT against
Hybrid-SORT on DetA and on MOTA.

## D. DanceTrack REFERENCE_ABSENT

The class is real. It is not a parser, annotation, frame-indexing, class-filter,
mark-filter, visibility-filter or identity-relabelling defect; every one of those
was tested exhaustively and none triggered.

Predicate: both bracketing anchors received a reference assignment, both were
assigned to the same ground-truth identity, and that identity is not present in
the scoreable reference set at the synthesized frame.

Mechanism, established positively: **all 16,019** REFERENCE_ABSENT rows summed
over four trackers and five gates lie strictly inside a genuine gap in the
ground-truth track's own observed frame set; **zero** lie outside the GT track
span. In 9,047 of them the identity is annotated at an immediately adjacent
frame.

The reason the class is empty on MOT17 and non-empty here:

| population | GT tracks | with at least one interior gap | gaps | missing frame-slots |
|---|---|---|---|---|
| DanceTrack val | 273 | **209 (76.6 %)** | **1,370** | 15,326 |
| MOT17 val-half | 339 | **0 (0.0 %)** | **0** | 0 |

The 1,370 figure is independently corroborated: feeding ground truth back as
tracker output in the D1A evaluator sanity test produced `Frag = 1370` over 273
tracks.

An independent re-implementation of the predicate agreed with the frozen
classifier on **250,470 of 250,470** row-gate decisions, with 0 disagreements.
Counts per tracker per gate:

| tracker | 0.30 | 0.40 | 0.50 | 0.60 | 0.70 | persistent at all five |
|---|---|---|---|---|---|---|
| ByteTrack | 620 | 595 | 526 | 413 | 264 | 264 |
| OC-SORT | 1,031 | 1,024 | 1,007 | 930 | 683 | 683 |
| Deep-OC-SORT | 1,132 | 1,124 | 1,089 | 992 | 743 | 743 |
| Hybrid-SORT | 935 | 905 | 829 | 693 | 484 | 483 |

The final column is NOT the gate-0.70 count. It is
`persistent_TARGET_REFERENCE_ABSENT` from `D1B_gate_persistence_summary.csv`:
rows carrying this class at every gate in the sweep. The two coincide for
ByteTrack, OC-SORT and Deep-OC-SORT and differ for Hybrid-SORT, 484 against 483,
because the classes are not nested across gates. One Hybrid-SORT row,
`dancetrack0094` frame 400 track_id 22, is REFERENCE_ABSENT at gates 0.30, 0.40,
0.60 and 0.70 but ANCHOR_ID_MISMATCH at 0.50, so it is in the strictest gate's
set and not in the persistent set. Never derive the persistent column from the
strictest gate.

The class declines with the gate because a stricter gate leaves more anchors
unassigned, so rows are captured by the earlier ANCHOR_UNMATCHED rule before the
reference-absence test is reached.

## E. DanceTrack row-local geometric support

Admission is defined through the R0 anchors and the availability of the
anchor-resolved reference identity. **The synthesized row's own coordinates are
not part of the predicate.** The row-local analysis is therefore a separate
diagnostic, not a restatement of admission.

| tracker | class | n | % IoU = 0 | % 0 < IoU < 0.5 | % IoU >= 0.5 |
|---|---|---|---|---|---|
| ByteTrack | ADMITTED | 2,684 | 0.00 | 2.61 | 97.39 |
| ByteTrack | ANCHOR_UNMATCHED | 3,659 | 0.16 | 48.48 | 51.35 |
| ByteTrack | ANCHOR_ID_MISMATCH | 1,642 | 0.00 | 13.82 | 86.18 |
| ByteTrack | TARGET_REFERENCE_ABSENT | 526 | 0.00 | 38.97 | 61.03 |
| ByteTrack | ALL NON_ADMITTED | 5,827 | 0.10 | 37.86 | **62.04** |
| OC-SORT | ADMITTED | 7,941 | 0.00 | 1.79 | 98.21 |
| OC-SORT | ANCHOR_UNMATCHED | 2,338 | 0.00 | 42.56 | 57.44 |
| OC-SORT | ANCHOR_ID_MISMATCH | 3,817 | 0.39 | 11.68 | 87.92 |
| OC-SORT | TARGET_REFERENCE_ABSENT | 1,007 | 0.00 | 43.59 | 56.41 |
| OC-SORT | ALL NON_ADMITTED | 7,162 | 0.21 | 26.25 | **73.54** |
| Deep-OC-SORT | ADMITTED | 8,128 | 0.00 | 2.26 | 97.74 |
| Deep-OC-SORT | ANCHOR_UNMATCHED | 2,015 | 0.00 | 41.24 | 58.76 |
| Deep-OC-SORT | ANCHOR_ID_MISMATCH | 2,790 | 0.11 | 12.33 | 87.56 |
| Deep-OC-SORT | TARGET_REFERENCE_ABSENT | 1,089 | 0.00 | 44.35 | 55.65 |
| Deep-OC-SORT | ALL NON_ADMITTED | 5,894 | 0.05 | 28.13 | **71.82** |
| Hybrid-SORT | ADMITTED | 4,482 | 0.00 | 1.78 | 98.22 |
| Hybrid-SORT | ANCHOR_UNMATCHED | 5,206 | 0.06 | 45.24 | 54.71 |
| Hybrid-SORT | ANCHOR_ID_MISMATCH | 1,941 | 0.62 | 11.70 | 87.69 |
| Hybrid-SORT | TARGET_REFERENCE_ABSENT | 829 | 0.36 | 32.21 | 67.43 |
| Hybrid-SORT | ALL NON_ADMITTED | 7,976 | 0.23 | 35.72 | **64.05** |

Two results matter here.

Positive control: ADMITTED rows reach IoU >= 0.5 in 97.392 to 98.2151 % of cases,
**not 100 %**. Between 1.7849 and 2.6080 % of admitted rows have maximum IoU below
0.5 against any scoreable GT in their frame, and none is exactly zero. This is
consistent with the predicate rather than contradictory.

Negative control, the consequential one: **62.0388 to 73.5409 % of non-admitted rows
overlap some scoreable GT at IoU >= 0.5.** Non-admission is not geometric
implausibility.

REFERENCE_ABSENT special check at gate 0.50, 3,451 rows:

| quantity | value |
|---|---|
| inside an independently verified internal GT-track gap | 3,451 / 3,451 |
| intended reference identity present at the frame | 0 / 3,451 |
| another GT identity geometrically overlaps the box | **3,448 / 3,451** |
| max IoU = 0 | 3 (0.09 %) |
| 0 < max IoU < 0.5 | 1,394 (40.39 %) |
| max IoU >= 0.5 | 2,054 (59.52 %) |

"The intended reference identity is absent" and "no other GT geometry is nearby"
are not equivalent, and on this population they diverge almost completely.

## F. DanceTrack GSI, controlled rewrite-heavy arm

Post-hoc, designed 2026-10-04 after the DTI outcomes were known. Operator:
StrongSORT GSI at commit `ee995076da5083e28d0da1f885297df62705ebd7`, `GSI.py`
SHA-256 `89e7d9577d6d48e1d903cc9b3597ae1663496a11515e049acec7374a064147a3`,
`interval=20`, `tau=10`, the only values anywhere in that repository or its
documentation. AFLink excluded, because its thresholds are tracker-specific by
upstream's own annotation. Deterministic: the RBF length scale is fixed, so no
optimiser restarts and no seed; repeat invocation is byte-identical.

Primary state inventory, R0 to GSI:

| tracker | R0 rows | GSI rows | inserted | deleted | surviving | coord rewrites | % | id changes |
|---|---|---|---|---|---|---|---|---|
| ByteTrack | 216,310 | 225,199 | 8,889 | 0 | 216,310 | 127,411 | 58.902 | 0 |
| OC-SORT | 202,787 | 218,591 | 15,804 | 0 | 202,787 | 136,814 | 67.4668 | 0 |
| Deep-OC-SORT | 203,149 | 218,075 | 14,926 | 0 | 203,149 | 123,954 | 61.0163 | 0 |
| Hybrid-SORT | 215,393 | 228,696 | 13,303 | 0 | 215,393 | 122,427 | 56.8389 | 0 |

KEY_SET_MONOTONIC is YES for all four; ROW_CONTENT_PRESERVED is NO for all four.
The operator is **key-additive but content-rewriting**. It is not row-additive.
The confidence column is overwritten with the constant 1 on every row.

Metric states and the 20 deltas:

| tracker | state | HOTA | DetA | AssA | IDF1 | MOTA |
|---|---|---|---|---|---|---|
| ByteTrack | GSI | 46.7486 | 70.0117 | 31.3620 | 51.5149 | 87.6663 |
| OC-SORT | GSI | 52.4878 | 77.7241 | 35.7047 | 52.2663 | 89.8174 |
| Deep-OC-SORT | GSI | 58.9708 | 78.2863 | 44.7098 | 59.8308 | 90.2668 |
| Hybrid-SORT | GSI | 58.7834 | 77.5052 | 44.9202 | 60.6222 | 89.2520 |

| tracker | HOTA | DetA | AssA | IDF1 | MOTA |
|---|---|---|---|---|---|
| ByteTrack | -0.1443 | -0.6464 | +0.1136 | -0.1212 | -0.6422 |
| OC-SORT | +0.2526 | +0.3407 | +0.3243 | +0.4131 | +2.5219 |
| Deep-OC-SORT | +0.3161 | +0.6498 | +0.2529 | +0.3693 | +2.6880 |
| Hybrid-SORT | -0.5294 | -1.3614 | +0.1065 | -0.2535 | -0.2638 |

12 positive, 0 zero, 8 negative of 20, with the same per-tracker pattern as DTI.

Ordering: 7 of 30 exhaustive pairwise metric cells cross zero, all surviving
3-decimal and 2-decimal reporting, and they are the **same seven** pair-and-metric
identities as the DTI arm.

Three-tracker provenance-sensitivity subset: 3 of 15, the same three cells as
DTI.

**Stage decomposition, the decisive D2C result.** `GSInterpolation` is literally
`li = LinearInterpolation(input_, interval); gsi = GaussianSmooth(li, tau)`, so
the intermediate state `L_GSI` is exactly `li`. It was materialised by importing
`LinearInterpolation` unmodified.

| transition | inserted | deleted | coord rewrites | id changes | score rewrites |
|---|---|---|---|---|---|
| R0 to L_GSI, all four | 8,889 / 15,804 / 14,926 / 13,303 | 0 | **0** | 0 | **0** |
| L_GSI to GSI, ByteTrack | 0 | 0 | 134,528 (59.74 %) | 0 | all |
| L_GSI to GSI, OC-SORT | 0 | 0 | 150,335 (68.77 %) | 0 | all |
| L_GSI to GSI, Deep-OC-SORT | 0 | 0 | 136,145 (62.43 %) | 0 | all |
| L_GSI to GSI, Hybrid-SORT | 0 | 0 | 133,187 (58.24 %) | 0 | all |

R0 to L_GSI is strictly row-additive, including the confidence column. L_GSI to
GSI inserts and deletes nothing and rewrites coordinates only.

Metric deltas are 12 / 0 / 8 on all three transitions. Pairwise crossings:

| transition | crossings | survive 3 dp | survive 2 dp |
|---|---|---|---|
| R0 to L_GSI | **7 / 30** | 7 | 7 |
| L_GSI to GSI | **0 / 30** | 0 | 0 |
| R0 to GSI | **7 / 30** | 7 | 7 |

The GP share of total absolute metric movement has median 0.1812, minimum 0.0421
and maximum 0.8722. In **8 of 20** cells the GP delta opposes the linear delta;
for OC-SORT and Deep-OC-SORT, the GP stage removes approximately 73 % and 53 %
of the linear-stage DetA gain respectively: linear +1.2642 against GP -0.9235 for
OC-SORT, and linear +1.3854 against GP -0.7356 for Deep-OC-SORT. ByteTrack and
Hybrid-SORT have negative linear DetA deltas, so for them the GP stage deepens a
loss rather than removing a gain.

Current interpretation: GSI changes the evaluated state through extensive
coordinate rewriting in addition to interpolation, while the observed ordering
crossings are already established by its interpolation stage. The two DanceTrack
operator arms are therefore **not** independent mechanisms.

STV and R1 are not defined for this state transition and were not computed.

## G. OC-SORT GPR, small-rewrite boundary case, MOT17

`G0` is the pre-GPR interpolated state and `G2` the rewritten state, 7 MOT17
sequences.

| quantity | value |
|---|---|
| G0 rows / G2 rows | 45,927 / 45,927 |
| duplicate keys | 0 in either state |
| insertions / deletions | 0 / 0 |
| rows differing at exact float equality | **2,622** |
| of those, x changed / y changed | 2,622 / 2,622 |
| w changed / h changed | **0 / 0**, bit-identical in all 45,927 rows |
| changed coordinate scalars at exact equality | 5,244 |
| **rows with change above 1e-6 px** | **52** |
| rows with change above 0.001 px | 0 |
| magnitude: min / median / p90 / max | 8.9e-12 / 3.7e-09 / 6.7e-08 / 1.7e-05 px |

The manuscript value of 52 is the count above 1e-6 px and reproduces exactly.
**v6 must state that tolerance**, because exact float equality gives 2,622 and a
reader who reproduces the comparison without the tolerance will get the larger
number.

Evaluator effect: `pedestrian_summary.txt` is byte-identical between the two
states, SHA-256
`b4ef939ee9b2fcd74d117d217f53e00d65ebdbd6676cd5bf1603269e31c62791`, while
`pedestrian_detailed.csv` differs in 197 fields, every one in the LocA family
and at about the eleventh significant digit. That pattern is expected: LocA
depends directly on coordinates, whereas HOTA, DetA, AssA, IDF1 and MOTA depend
on assignment and counts, which shifts of order 1e-9 px cannot move.

This is the informative boundary case: an operator that demonstrably rewrites
the evaluated state and moves every reported metric by 0.0000 to four decimals.

## H. StrongSORT++ AFLink + GSI, identity-reassociation structural case, MOT17

State naming in the frozen artifact, authoritative: **PRE** is the base tracker
state before AFLink, **S0** is post-AFLink and pre-GSI, **S2** is post-GSI.
There is no S1, because GSI is not row-additive and no R1 analogue was ever
built. Earlier S0/S1/S2 usage is superseded and must not be propagated.

AFLink, PRE to S0: 46,914 rows to 46,913, so one row is lost; 1,316 rows change
identity across 29 distinct remappings; 0 rows unmatched by geometry.

GSI, S0 to S2: 3,184 rows added by the linear stage, 0 dropped, 46,913 surviving
rows of which 46,866 have rewritten coordinates, a fraction of 99.8998 %;
S2 = 50,097 = 46,913 + 3,184. Metric deltas HOTA +1.220, DetA +1.278,
AssA +1.211, IDF1 +0.830, MOTA +1.561.

Two frozen prose claims from that artifact, to be preserved in substance:
containment of S0 in S2 is not claimed and not tested because GaussianSmooth
rewrites row coordinates; and the STV-valid-only state is not defined for GSI,
because removing invalid synthesized rows before smoothing would change the GP
fit and therefore the coordinates of the surviving rows.

One wording precision v6 should adopt: the frozen note says "row identity is not
preserved". The identity **key** is preserved and the key set grows
monotonically; the row **content** is not preserved. Report the subset relation
twice, once on keys and once on content.

The MOT17 GSI magnitudes are historical facts about a different population and a
different input state. They must not be carried as an expectation for
DanceTrack: the rewrite fraction depends on track length through
`clip(tau*log(tau**3/n), tau**-1, tau**2)`, which clips to 0.1 for tracks of
1,000 or more rows.
""")

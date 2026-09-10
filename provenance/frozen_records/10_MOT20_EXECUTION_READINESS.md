# MOT20 Execution Readiness Audit

Read-only audit of whether every frozen MOT20 quantitative cell is technically
ready for execution. **No MOT20 scientific execution took place.** No tracker,
interpolation, GPR, AFLink, GSI, TrackEval or STV was run; no MOT20 metric or
ordering value exists; the manuscript, the frozen population and the frozen GT
semantics are untouched. Execution remains **NOT AUTHORIZED**.

Population: MOT20, sequences MOT20-01/02/03/05, **4463 frames**, manifest SHA-256
`aabe4907077934fb834a7639b9722b9120de0a007553bbc98a6132b768d3e232` (independently
recomputed here), mirror source manifest SHA-256
`c2d55f8020c83833f31fc345a100875296d938227ba19d9199e80630ce407eba`. The corpus
came from a Kaggle mirror (`MIRROR_TRANSPORT_FALLBACK`); byte identity to an
official `MOT20.zip` is **not** established and no wording may claim a direct
MOTChallenge download.

## Verdict

| Cell | Role | Family | Command | Environment | Checkpoint | Indexing | Readiness |
|---|---|---|---|---|---|---|---|
| ByteTrack × MOT20 | SECONDARY_SPLIT_ADAPTED | LINEAR_DTI_ROW_ADDITIVE | traced, test-only | undefined | CONFIRMED_EVAL_LEAKAGE | double-halving | **BLOCKED_CHECKPOINT_PROVENANCE** |
| BoT-SORT × MOT20 | SECONDARY_SPLIT_ADAPTED | LINEAR_DTI_ROW_ADDITIVE | resolved | entry point verified | CONFIRMED (det) + POTENTIAL (ReID) | double-halving | **BLOCKED_CHECKPOINT_PROVENANCE** |
| OC-SORT linear × MOT20 | SECONDARY_SPLIT_ADAPTED | LINEAR_DTI_ROW_ADDITIVE | traced, test-only | undefined | CONFIRMED_EVAL_LEAKAGE | double-halving | **BLOCKED_CHECKPOINT_PROVENANCE** |
| OC-SORT-GPR × MOT20 | OPTIONAL_DOCUMENTED_FAMILY | GPR_REWRITE | resolved | verified | inherited CONFIRMED | inherited | **BLOCKED_ASSET** |
| Deep-OC-SORT × MOT20 | PRIMARY_DOCUMENTED_VALIDATION | LINEAR_DTI_ROW_ADDITIVE | resolved | verified | **NO_KNOWN_EVAL_LEAKAGE** | double-halving | **BLOCKED_ASSET** |
| Hybrid-SORT × MOT20 | SECONDARY_SPLIT_ADAPTED | LINEAR_DTI_ROW_ADDITIVE | no val config | reuse valid | CONFIRMED_EVAL_LEAKAGE | double-halving | **BLOCKED_COMMAND** |
| StrongSORT++ × MOT20 | SECONDARY_SPLIT_ADAPTED | LINK_PLUS_SMOOTHING | `KeyError: 'val'` | verified | AFLink clean; inputs UNKNOWN | undeterminable | **BLOCKED_COMMAND** |

**READY = 0 / 7.** Repository support for MOT20 was never treated as sufficient.

## The governing finding: MOT20 has no non-leaking public detector

Every MOT20 detector in this universe traces to one recipe. ByteTrack's
`tools/mix_data_test_mot20.py:17` loads `datasets/MOT20/annotations/train.json` —
the **complete** MOT20 train split, not `train_half.json` — and mixes it with
CrowdHuman to build `mix_mot20_ch`. The README states it plainly at line 164:
*"Train on CrowdHuman and MOT20, evaluate on MOT20 train."*

The frozen V9 validation population **is** the second half of MOT20 train
sequences 01/02/03/05. Every one of its 4463 frames is therefore a detector
training frame. `bytetrack_x_mot20` (ByteTrack, BoT-SORT, OC-SORT, and
transitively OC-SORT-GPR) and `ocsort_x_mot20` (Hybrid-SORT) are both
`CONFIRMED_EVAL_LEAKAGE`. Unlike MOT17, **no repository releases a MOT20
half-train "ablation" detector**: `yolox_x_ablation.py` and
`yolox_x_mot17_ablation_half_train.py` exist, and there is no MOT20 counterpart.

BoT-SORT makes this unavoidable rather than accidental. `tools/track.py:320-324`
ignores the ablation flag entirely when `MOT == 20`, so `--eval val` still loads
the full-train detector. That the population rule itself is compatible makes no
difference: `tools/track.py:151-153` slices `files[len(files)//2 + 1:]`, which
reproduces 216–429 / 1393–2782 / 1204–2405 / 1659–3315 exactly.

**The one exception is Deep-OC-SORT.** `main.py:71-78` routes the MOT20
*validation* branch to `bytetrack_x_mot17.pth.tar` under the authors' own comment
*"Just use the mot17 test model as the ablation model for 20"*, and
`embedding.py:183-193` routes ReID to `_get_general_model()` because *"The
MOT17/20 SBS models are trained over the half-val we evaluate on as well."*
Neither asset contains MOT20 data. `MOT20_CHECKPOINT_LEAKAGE` is **not** raised
for this cell. Its blocker is only that `bytetrack_x_mot17.pth.tar` is not present
locally, and substitution is forbidden without a new amendment.

BoT-SORT's `mot20_sbs_S50` is a genuinely intermediate case, recorded as
`POTENTIAL_EVAL_LEAKAGE`. `generate_mot_patches.py:117-120` sends `f <
num_frames//2` to `bounding_box_train` and the remainder to `bounding_box_test`,
so gradient training is frame-disjoint from the frozen population — but the frozen
second half is the ReID **gallery**, identities span both halves, and checkpoint
selection could have been informed by it. Not confirmed; not clean.

## Two cells cannot express MOT20 validation at all

**Hybrid-SORT.** Both MOT20 exps were instantiated in this audit.
`yolox_x_mix_mot20_ch_hybrid_sort.py` resolves to `ckpt=ocsort_x_mot20.pth.tar`,
`val_ann=test.json`, `dataset=mot20`, `hybrid_sort_with_reid=False`,
`track_thresh=0.4`, `asso=Height_Modulated_IoU` — a **test-split** deployment.
`yolox_x_mix_mot20_ch_valhalf.py` resolves to `val_ann=val_half.json` but carries
**zero** tracker attributes: `ckpt`, `dataset`, `hybrid_sort_with_reid`,
`track_thresh` and `asso` are all absent. It is a plain YOLOX detection exp and
cannot drive `run_hybrid_sort_dance.py` in the Hybrid-SORT deployment identity.
Authoring a val config would create a new experiment, not apply a documented rule
unchanged.

**StrongSORT++.** `opts.py:33-40` defines `data['MOT20']` with a `'test'` key
only, and `opts.py:145` does `opt.sequences = data[opt.dataset][opt.mode]`. Run as
a configuration-only smoke test, `strong_sort.py MOT20 val --BoT --NSA --EMA --MC
--woC --AFLink --GSI` raises **`KeyError: 'val'`**. Separately, StrongSORT runs no
detector or ReID of its own — it consumes precomputed `.npy` detections+features —
and README:63-65 publishes `MOT20_ECC_test.json`, `MOT20_test_YOLOX+BoT` and
`MOT20_test_YOLOX+simpleCNN` with **no** val counterparts. Those artifacts do not
exist, so their provenance stays `UNKNOWN` and unresolved. Either blocker
disqualifies the cell on its own.

## Indexing: the adapters would evaluate a quarter-split

This is the highest-priority correctable finding. The canonical population
preserves **native** frame ids; the TrackEval layout is a derived local-`1..N`
adapter. Both are correct. But the six **tracker-facing** adapters materialized in
09B symlink each repository's dataset directory to the **pre-halved** population
root — `MOT20-01/img1` holds 214 files beginning at `000216.jpg` — while every
MOT20 pipeline that touches images performs its **own** documented halving.

| Sequence | Adapter exposes | Pipeline would then evaluate | Frames |
|---|---|---|---|
| MOT20-01 | 214 | native 324–429 | 106 |
| MOT20-02 | 1390 | native 2089–2782 | 694 |
| MOT20-03 | 1202 | native 1806–2405 | 600 |
| MOT20-05 | 1657 | native 2488–3315 | 828 |
| **Total** | | | **2228** vs frozen **4463** |

The tracker-facing adapter must instead expose the **full** native sequences
(`1..seqLength`), so that each pipeline's own halving reproduces the frozen ranges.
Verified for all four: `seqLength//2 + 2 .. seqLength` equals 216–429, 1393–2782,
1204–2405 and 1659–3315, totalling 4463. This correction is **specified, not
performed** — changing the adapters is execution preparation, and this task
creates no execution capability.

Per-pipeline numbering: ByteTrack, OC-SORT, Deep-OC-SORT and Hybrid-SORT are class
**C** (COCO converted image ids, then local `1..N` `frame_id`); BoT-SORT is class
**B** (`enumerate(files, 1)`); OC-SORT-GPR inherits its input's numbering; and
StrongSORT++ is class **D**, fixed by precomputed detection files. Every emitted
numbering is local `1..N` or inherited, so the per-sequence affine map
`native = local + first − 1` is bijective and every future output maps back onto
the canonical native population without ambiguity.

## Source-commit reverification and one reconciliation

Six repositories match their required commits exactly and carry zero **tracked**
modifications; all dirty entries are untracked build artefacts, `__pycache__`,
dataset symlinks and weight files. No upstream repository was updated.

The OC-SORT requirement needs stating precisely rather than passing silently. The
task lists `8462e7e7…`; `01_SOURCE_MANIFEST.json` records that value as
`upstream_head_at_census` and `a9e24b67…` as `local_clone_head` — two distinct
frozen fields. Reverified here: `a9e24b67` is an ancestor of `8462e7e7` (25
commits), and `tools/interpolation.py` (blob `3eaf014ff261`) and
`tools/gp_interpolation.py` (blob `c46434d3a82d`) are **byte-identical at both
ends**, so the post-processing identity is pin-invariant. However, those 25 commits
**do** modify `trackers/ocsort_tracker/{association,kalmanfilter,ocsort}.py`. A
MOT20 run requires an actual OC-SORT tracker execution (unlike MOT17, which reused
released author outputs), so the raw R0 would **not** be pin-invariant and the
executing pin must be declared explicitly before any MOT20 tracker execution.

## Environments

`ENV-MOTAUDIT-PY39`, `ENV-DEEPOCSORT-MOT17-V9` and `ENV-HYBRIDSORT-MOT17-V9` all
report Python 3.9.23, torch 1.13.1+cu117, torchvision 0.14.1+cu117, numpy 1.23.5,
scipy 1.10.1, scikit-learn 1.0.2, pandas 2.3.3, OpenCV 4.11.0, CUDA 11.7, cuDNN
8500 on an A100-SXM4-80GB MIG 7g.80gb. They differ only in editable packages:
none / `yolox 0.3.0` + `torchreid 1.4.0` / `yolox 0.1.0`.

All smoke tests were import-only — module imports, `--help` parsing and
configuration-object instantiation. **No detector was loaded for inference, no
result file was created and not one MOT20 image was read.**

`ENV-HYBRIDSORT-MOT17-V9` reuse is **valid on package grounds**: Hybrid-SORT MOT20
base (`hybrid_sort_with_reid=False`) enters the same
`run_hybrid_sort_dance.py → evaluate_hybrid_sort` path as the MOT17 run, adds no
ReID dependency and no new package, and the MOT20 exp instantiates inside it. No
new environment identity is required — which does not unblock the cell.

Two cells have **no** environment at all. `ByteTrack/tools/track.py` and
`OC_SORT/tools/run_ocsort.py` raise `ModuleNotFoundError: yolox` in
`ENV-MOTAUDIT-PY39`, and `ENV-DEEPOCSORT-MOT17-V9` is worse, not better: its
editable `yolox 0.3.0` **shadows** each repository's vendored `yolox`, producing
`ImportError: cannot import name 'MOTEvaluator'` / `'plot_tracking'`. That
environment must never be reused for ByteTrack, BoT-SORT or OC-SORT.

## State contract

Row-additive cells (ByteTrack, BoT-SORT, OC-SORT, Deep-OC-SORT, Hybrid-SORT):
**R0** = raw tracker state before interpolation; **R2** = complete documented
linear-DTI output; **R1** = future diagnostic state built from R0 plus the
STV-admitted synthesized rows, never produced by any upstream tool.

Two preservation hazards. BoT-SORT's `tools/interpolation.py` defaults
`--save_path` to `None` and then aliases it to `txt_path`, **overwriting R0 in
place** — an explicit `--save_path` is mandatory. Deep-OC-SORT is safe:
`main.py:159-168` `copytree`s R0 to `<exp>_post` before applying `dti` in place.

**OC-SORT-GPR**: `S0` = the linear-DTI state entering GPR, `S2` = the GPR-rewritten
output; `R1` is **STRUCTURALLY_UNDEFINED** and its construction is forbidden;
R0/R2 must not be overloaded onto these states. Seed **20260830** is required, via
`tracking_provenance_audit.gpr_entry`, with a dedicated staging directory holding
exactly the four MOT20 sequence files, no `*_detections.txt` contamination, an
absolute output path, and a fresh-process same-seed replay.

**StrongSORT++**: `S0` = base tracker output before AFLink; `S1` = post-AFLink,
retained for provenance; `S2` = post-GSI. `R1` is **STRUCTURALLY_UNDEFINED**.
AFLink and GSI both take `path_in == path_out == path_save`, so S0 and S1 are
destroyed unless copied out before each stage. GSI is deterministic
(`RBF(len_scale,'fixed')`, no restarts), so no seed contract applies.

STV applies to **row-additive deployments only** and is forbidden for
OC-SORT-GPR and StrongSORT++.

## Frozen future contracts

TrackEval: `BENCHMARK=MOT20`, `SPLIT_TO_EVAL=val`, `CLASSES_TO_EVAL=pedestrian`,
commit `12c8791b303e0a0b50f753af204249e622d0281a`, metrics HOTA / DetA / AssA /
IDF1 / MOTA, MOT20-native preprocessing with distractor class ids `{2,6,7,8,12}`.
Not executed.

STV: IoU 0.5, gate-before-assignment, one-to-one Hungarian, R0 anchors only,
scoreable GT `mark != 0 AND class == 1`, classes `ANCHOR_UNMATCHED` /
`ANCHOR_ID_MISMATCH` / `TARGET_REFERENCE_ABSENT` / `SEMANTICALLY_ADMITTED`,
materiality `nonadmitted / synthesized ≥ 0.10` with companion `nonadmitted / R2`.
These thresholds are frozen and are **not** to be changed because MOT20 is denser
than MOT17. Not executed.

Ordering: if at least two comparable row-additive deployments ever complete, the
analysis must be exhaustive over every eligible pair × all five metrics with no
preselection; the MOT17 and MOT20 matrices are recorded separately; any
cross-dataset aggregate retains dataset identity and never pools raw metric
magnitudes as exchangeable. Not computed.

## Interpolation-parameter check (§5)

`n_min = 30, n_dti = 20` is frozen for OC-SORT MOT20 **on source evidence**, not
inherited from MOT17: `tools/interpolation.py::__main__` passes those values
unconditionally and is not dataset-branched, and `docs/GET_STARTED.md:141-148`
gives a single dataset-agnostic command naming MOT17 and MOT20 together. No
MOT20-specific parameter is documented anywhere. **No `COMMAND_RULE_CONFLICT`.**

For completeness the family splits at two operating points, unchanged for MOT20:
ByteTrack and BoT-SORT call `n_min=5`; OC-SORT, Deep-OC-SORT and Hybrid-SORT call
`n_min=30`; `n_dti=20` is universal. BoT-SORT's `dti` remains in the proven
ByteTrack-derived lineage — identical `dti(txt_path, save_path, n_min=25,
n_dti=20)` signature, differing by exactly one added `print(seq_name)`.

Three repositories' `interpolation.py` `__main__` blocks additionally call
`eval_mota` over a hardcoded MOT17 path with an `s.endswith('FRCNN')` sequence
filter, which is inert or empty on MOT20. The `dti()` transformation itself is
dataset-agnostic and unaffected.

## Universe integrity

Exactly seven cells were audited; none added, none removed. SparseTrack × MOT20
remains `DOCUMENTATION_ONLY_IMPLEMENTED` / `NO_QUANTITATIVE_OUTCOME_PLANNED` and is
not an eighth quantitative cell. Every cell keeps its frozen
`documentation_role`, `structural_family`, `audit_mode = STOPPED_BEFORE_EXECUTION`
and `outcome_knowledge_status = STOPPED_UNSEEN`. No command was selected using any
MOT17 outcome.

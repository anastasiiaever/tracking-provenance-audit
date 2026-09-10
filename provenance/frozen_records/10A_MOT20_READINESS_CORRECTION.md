# MOT20 Readiness Correction A1

Append-only amendment to record 10 (commit `4dbcf125acddcb5eb100cb55f2786f157c8919b4`,
tag `tpami-v9-mot20-execution-readiness-20260831`, tag object
`e028bf5db1c5d90cb62fba56fb5a0f1b46bffd05`). **The 10_\* records are byte-unchanged
and the readiness tag has not moved.** No MOT20 tracker, interpolation, TrackEval or
STV was run; no MOT20 metric exists; no model was trained; no checkpoint was
substituted; execution is **not** authorized.

## 1. Corrected blocker classifications

**OC-SORT-GPR × MOT20.** Record 10 headlined this cell `BLOCKED_ASSET`, which reads
as a procurable blocker. It is not. The missing artifact is `S0`, the OC-SORT MOT20
linear-DTI state, and `S0` can only be produced by the OC-SORT MOT20 detector whose
training set contains the frozen evaluation frames. No acquisition can make this cell
valid for the clean held-out V9 estimand.

| field | corrected value |
|---|---|
| `primary_scientific_blocker` | `BLOCKED_CHECKPOINT_PROVENANCE` |
| `checkpoint_provenance` | `CONFIRMED_EVAL_LEAKAGE` |
| `secondary_technical_blocker` | `BLOCKED_ASSET` |

**Hybrid-SORT × MOT20.** Record 10 headlined `BLOCKED_COMMAND`. The absence of a
MOT20 val experiment config is *not* the only blocker — record 10 already listed
leakage among `additional_blockers`, but the single headline understated it. Even
with a val config, the only MOT20 detector Hybrid-SORT documents
(`ocsort_x_mot20.pth.tar`) is built by the same full-MOT20-train `mix_mot20_ch`
recipe.

| field | corrected value |
|---|---|
| `command_blocker` | `BLOCKED_COMMAND` |
| `checkpoint_blocker` | `CONFIRMED_EVAL_LEAKAGE` |
| `terminal_scientific_blocker` | `BLOCKED_CHECKPOINT_PROVENANCE` |

## 2. Five cells are terminally leakage-blocked

For the current held-out MOT20 estimand, these are **not eligible for execution with
their documented public MOT20 checkpoints**:

ByteTrack × MOT20 · BoT-SORT × MOT20 · OC-SORT linear × MOT20 · OC-SORT-GPR × MOT20 · Hybrid-SORT × MOT20

Their required detector state is trained using the frozen MOT20 evaluation frames.
`mix_data_test_mot20.py:17` consumes `annotations/train.json` — the complete MOT20
train split — and ByteTrack README:164 states it plainly: *"Train on CrowdHuman and
MOT20, evaluate on MOT20 train."* `BoT-SORT tools/track.py:320-324` ignores the
ablation flag when `MOT == 20`, so even `--eval val` loads the full-train detector.
No repository in the frozen universe releases a MOT20 half-train ablation detector.

These checkpoints were **deliberately not downloaded**. No detector was substituted.
A future clean-detector controlled study would be a **new experiment** with its own
protocol and pre-registration — not execution of these frozen released-deployment
cells, and no result from it may be presented as such.

## 3. StrongSORT++ remains stopped

Final state `STOPPED_BEFORE_EXECUTION`. All blockers recorded:

- **MOT20 val command unsupported by the frozen entry point** — `opts.py:33-40`
  defines `data['MOT20']` with a `'test'` key only; `opts.py:145` does
  `opt.sequences = data[opt.dataset][opt.mode]`. `strong_sort.py MOT20 val …` raises
  `KeyError: 'val'`.
- **Required MOT20-val detection inputs absent** — `opt.dir_dets` resolves to
  `MOT20_val_YOLOX+BoT`; README:63-65 publishes test artifacts only. StrongSORT runs
  no detector or ReID of its own.
- **ECC input absent** — `opts.py:142-144` loads `MOT20_ECC_val.json`; only
  `MOT20_ECC_test.json` is published.
- **Base-input provenance UNKNOWN** — the artifacts do not exist upstream, so their
  training provenance cannot be resolved from source documentation.
- **Indexing not determinable** — StrongSORT performs no half-split of its own; its
  frame numbering is fixed by the precomputed `.npy` files.

No study-side command was constructed.

## 4. Deep-OC-SORT is the sole clean MOT20 cell

Role `PRIMARY_DOCUMENTED_VALIDATION`; checkpoint provenance `NO_KNOWN_EVAL_LEAKAGE`.
Confirmed independently by **executing** the upstream selection logic with every
model constructor stubbed, so nothing was built and no frame was read:

| argv | resolved detector |
|---|---|
| MOT20 validation (frozen command) | `external/weights/bytetrack_x_mot17.pth.tar` |
| MOT20 with `--test_dataset` (not used) | `external/weights/bytetrack_x_mot20.tar` |
| MOT17 validation (completed run) | `external/weights/bytetrack_ablation.pth.tar` |

`EmbeddingComputer.initialize_model()` with `dataset='mot20', test_dataset=False`
called `_get_general_model()` and loaded `osnet_ain_ms_d_c.pth.tar` (552 tensors,
`build_model(name='osnet_ain_x1_0', num_classes=2510, loss='softmax',
pretrained=False)`). It **never referenced** `mot20_sbs_S50.pth`, which is reachable
only under `--test_dataset` — a flag the frozen command does not pass.

Neither asset uses MOT20 training or evaluation frames: the detector is ByteTrack's
MOT17 test model (MOT17 train + CrowdHuman + Cityperson + ETHZ), and the ReID model
is a generic multi-source person-ReID network. Both substitutions are the upstream
authors' own explicit anti-leakage choices (`main.py:76`, `embedding.py:191-194`).

## 5. Chronology

1. The MOT20 sequence universe (MOT20-01/02/03/05) and the second-half split rule
   were frozen in `02_PROSPECTIVE_PROTOCOL` **before** any MOT17 execution.
2. MOT20 evaluator-native GT semantics (09A) were completed **after** MOT17 outcomes
   were known but **before** any MOT20 outcome existed.
3. The readiness audit (record 10) then established that most public MOT20
   checkpoints are unsuitable for the held-out half-train estimand because of
   evaluation leakage.
4. Deep-OC-SORT was carried forward for possible execution **only** because that
   pre-existing readiness audit classified its documented validation path as the sole
   `NO_KNOWN_EVAL_LEAKAGE` cell.

This selection must **not** be described as a prospectively selected winner, as
outcome-based selection, or as a best-performing method. **No MOT20 performance
outcome existed at selection time, and none exists now.**

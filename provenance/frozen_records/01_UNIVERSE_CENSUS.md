# V9 Candidate Post-Processing Universe Census

**READ-ONLY DOCUMENTATION / SOURCE-CODE CENSUS.**
**NO SCIENTIFIC OUTCOME IS COMPUTED IN THIS DOCUMENT.**
No tracker was run, no post-processing was executed, no TrackEval invocation was
made, no STV was computed, and no ranking or metric was produced or transcribed.

Generated 2026-08-30 on branch `tpami-v9-tracking-provenance-expansion-20260830`,
from the frozen V8 base `tpami-v8-pre-expansion-20260830`.

Authority order applied: official author repository, then its README/docs, then
released scripts/config, then the paper. No fork, blog, or third-party
reproduction was used as evidence.

## 1. Deployments (8) across 7 released systems

| # | Deployment | Repository | Upstream commit |
|---|---|---|---|
| 1 | ByteTrack | `ifzhang/ByteTrack` | `d1bf0191adff59bc8fcfeaa0b33d3d1642552a99` |
| 2 | BoT-SORT | `NirAharon/BoT-SORT` | `251985436d6712aaf682aaaf5f71edb4987224bd` |
| 3 | OC-SORT (linear) | `noahcao/OC_SORT` | `8462e7e729a93ccd3bd995c0a79a890336cb3a0b` |
| 4 | OC-SORT (GPR path) | `noahcao/OC_SORT` | `8462e7e729a93ccd3bd995c0a79a890336cb3a0b` |
| 5 | Deep OC-SORT | `GerardMaggiolino/Deep-OC-SORT` | `6bb51d027b137233f5c520b6fcc4f2ae387a6ba9` |
| 6 | Hybrid-SORT | `ymzis69/HybridSORT` | `396f8d30db13304c0cbaf1dcf2e16ded93ce1701` |
| 7 | StrongSORT++ (AFLink+GSI) | `dyhBUPT/StrongSORT` | `ee995076da5083e28d0da1f885297df62705ebd7` |
| 8 | SparseTrack | `hustvl/SparseTrack` | `499844f32c5bb2332f9811f26cd70cf4e517d4e7` |

`ifzhang/ByteTrack` and `FoundationVision/ByteTrack` resolve to the same HEAD
(organisation rename) — not a source conflict.

## 2. Pipeline x dataset documentation matrix (24 cells, none dropped)

| Deployment | MOT17 | MOT20 | DanceTrack |
|---|---|---|---|
| ByteTrack | DOCUMENTED_DEFAULT (test) | DOCUMENTED_DEFAULT (test) | NO_DOCUMENTED_RULE |
| BoT-SORT | DOCUMENTED_DEFAULT (test) | DOCUMENTED_DEFAULT (test) | NO_DOCUMENTED_RULE |
| OC-SORT (linear) | DOCUMENTED_DEFAULT (test/private) | DOCUMENTED_DEFAULT (test/private) | IMPLEMENTED_NOT_DATASET_DOCUMENTED |
| OC-SORT (GPR) | DOCUMENTED_OPTIONAL (test/private) | DOCUMENTED_OPTIONAL (test/private) | IMPLEMENTED_NOT_DATASET_DOCUMENTED |
| Deep OC-SORT | DOCUMENTED_DEFAULT (**val**) | DOCUMENTED_DEFAULT (**val**) | DOCUMENTED_DEFAULT (**val**) |
| Hybrid-SORT | DOCUMENTED_DEFAULT (test) | DOCUMENTED_DEFAULT (test) | IMPLEMENTED_NOT_DATASET_DOCUMENTED |
| StrongSORT++ | DOCUMENTED_DEFAULT (**val** and test) | DOCUMENTED_DEFAULT (test) | NO_DOCUMENTED_RULE |
| SparseTrack | IMPLEMENTED_NOT_DATASET_DOCUMENTED | IMPLEMENTED_NOT_DATASET_DOCUMENTED | IMPLEMENTED_NOT_DATASET_DOCUMENTED |

Counts: DOCUMENTED_DEFAULT 13, IMPLEMENTED_NOT_DATASET_DOCUMENTED 6,
NO_DOCUMENTED_RULE 3, DOCUMENTED_OPTIONAL 2, **AMBIGUOUS 0**.

## 3. The split question (census item 2C/2D)

This is the most consequential finding for protocol design, and it is a
documentation fact, not a result.

**Documented on the TEST split only** — ByteTrack, BoT-SORT, Hybrid-SORT, and
OC-SORT attach their interpolation instruction to test-set submission. BoT-SORT
is explicit: its MOT17-val block (`--eval "val"`) contains no interpolation call,
while its MOT17-test and MOT20-test blocks do. Applying these rules to a
validation population is therefore **a new author choice, an extension of the
documented rule — not a faithful execution of it.** The implementations are
split-agnostic (they read a directory of MOTChallenge-format txt files), so
extension is mechanically possible; that is a 2C fact and does not make it a 2D
fact.

**Documented on the VALIDATION split** — two deployments:
- **Deep OC-SORT**: the README `--post` commands do not pass `--test`, and
  `main.py:50-56` resolves the result folder to `MOT17-val` / `MOT20-val` /
  `DANCE-val`. Post-processing on the validation split is the documented default
  for all three datasets.
- **StrongSORT++**: `README.md:107` documents `--AFLink --GSI` on MOT17-val
  directly, alongside the test-split commands.

For a validation-population audit these two are faithful executions of the
documented rule; the other four would be extensions requiring explicit
declaration.

## 4. Post-processing family taxonomy (from source, not branding)

### LINEAR_DTI_ROW_ADDITIVE
ByteTrack, BoT-SORT, OC-SORT(linear), Deep OC-SORT, Hybrid-SORT, SparseTrack.
Row-additive: yes. Rewrites existing rows: no. Inserts rows: yes. Deletes rows:
no. Modifies IDs: no. Extrapolates: no (gate `1 < right-left < n_dti` is strictly
interior; requires both a left and a right anchor). Minimum track length `n_min`;
maximum gap `n_dti - 1` inserted frames. Deterministic. No learned component.
No smoothing/regression component. Runs once, after tracking.

### GPR_REWRITE
OC-SORT `tools/gp_interpolation.py`. Row-additive: **no**. Rewrites existing
rows: **yes** — but only rows absent from the raw file, i.e. rows the linear
stage created; it deletes the linear row then vstacks a GPR row. Inserts rows:
no (it consumes an already-interpolated file). Deletes rows: yes (as part of
rewrite). Modifies IDs: no. Extrapolates: no. **Requires the linear output as
input** (`reference_dir`), so execution order is raw to linear DTI to GPR.
**Non-deterministic**: `median_trick` calls `np.random.choice`, and
`GaussianProcessRegressor(n_restarts_optimizer=2)` restarts without a seed. The
repository separately warns of run-to-run randomness
(`docs/GET_STARTED.md:136`). Learned/regression component: yes (GPR, RBF kernel).
Dead code: the computed `bandwidth` is overwritten by `l = 1000.0/n_frame`
before use, and the `n_dti` parameter is accepted but never referenced.

### LINK_PLUS_SMOOTHING
StrongSORT++ (`AFLink/AppFreeLink.py` then `GSI.py`). Row-additive: **no**.
Rewrites existing rows: **yes — every row of every track**, because
`GaussianSmooth` rebuilds the output from GPR predictions over all timestamps,
not only over inserted ones. Inserts rows: yes (its own `LinearInterpolation`
stage). Deletes rows: no. Modifies IDs: **yes** — AFLink re-associates tracklets.
Extrapolates: no. Deterministic: yes (RBF length scale `'fixed'`, no restarts).
Execution order: AFLink (`strong_sort.py:35`) then GSI (`strong_sort.py:46`).

## 5. Call-site parameters as documented

| Deployment | parameters |
|---|---|
| ByteTrack | `n_min=5, n_dti=20` |
| BoT-SORT | `n_min=5, n_dti=20` (argparse defaults) |
| SparseTrack | `n_min=5, n_dti=20` |
| OC-SORT (linear) | `n_min=30, n_dti=20` |
| Hybrid-SORT | `n_min=30, n_dti=20` |
| Deep OC-SORT | `n_min=30, n_dti=20` (signature defaults; `--post` passes none) |
| OC-SORT (GPR) | `n_min=30, n_dti=20` (`n_dti` unused in body) |
| StrongSORT++ | GSI `interval=20, tau=10`; AFLink `thrT=(0,30), thrS=75, thrP=0.05` |

## 6. Every NO_DOCUMENTED_RULE cell (3)

- ByteTrack x DanceTrack — the repository contains no DanceTrack reference at all.
- BoT-SORT x DanceTrack — likewise.
- StrongSORT++ x DanceTrack — likewise.

These remain visible as census outcomes. They are **not** exclusions.

## 7. Every AMBIGUOUS cell

**None.** Every cell resolved on official evidence.

## 8. Source conflicts observed

1. **OC-SORT repository HEAD has moved** 25 commits past the local census clone
   (`a9e24b6` to `8462e7e`). Both post-processing files are byte-identical across
   that range, so the census is invariant to the pin. Recorded in
   `01_SOURCE_MANIFEST.json`.
2. **ByteTrack has two official URLs** (`ifzhang` and `FoundationVision`) that
   resolve to the same HEAD. Not a content conflict.
3. **ByteTrack documented call vs signature default** — the function default is
   `n_min=25` while the documented `__main__` call uses `n_min=5`. The documented
   value governs.
4. **Hybrid-SORT** carries a commented-out duplicate `dti(...)` call
   (`tools/interpolation.py:174`) directly above the live one at line 183. The
   live call governs; both use `n_min=30`.

## 9. Candidates deliberately NOT added

None encountered that met the bar. No pipeline is proposed as
CANDIDATE_FOR_LATER_REVIEW in this task.

## 10. Preliminary universe summary (inventory only)

- Candidate pipeline deployments: **8** (7 released systems).
- Dataset cells: **24**.
- Status counts: DOCUMENTED_DEFAULT 13, IMPLEMENTED_NOT_DATASET_DOCUMENTED 6,
  NO_DOCUMENTED_RULE 3, DOCUMENTED_OPTIONAL 2, AMBIGUOUS 0.
- Independent post-processing families: **3** (`LINEAR_DTI_ROW_ADDITIVE`,
  `GPR_REWRITE`, `LINK_PLUS_SMOOTHING`).
- Code-lineage groups: **3** (Group L with six deployments sharing one
  ByteTrack-derived `dti`; Group G; Group S).
- Cells whose transformation is **non-row-additive**: **6** — OC-SORT(GPR) x 3
  and StrongSORT++ x 3. A row-subset decomposition is not well defined for these.
- Cells structurally suited to a quantitative row-additive R0/R2 audit
  (row-additive family AND a documented rule): **12** — ByteTrack, BoT-SORT,
  OC-SORT(linear) and Hybrid-SORT on MOT17/MOT20 (documented split: test), plus
  Deep OC-SORT on MOT17/MOT20/DanceTrack (documented split: val). Of these, only
  the three Deep OC-SORT cells are documented on a validation split.
- Cells suitable only for documentation / no-rule reporting: **9** — the 6
  IMPLEMENTED_NOT_DATASET_DOCUMENTED cells and the 3 NO_DOCUMENTED_RULE cells.
- Unresolved ambiguities: **none**.

No hypothesis is called supported or failed. This document reports inventory only.

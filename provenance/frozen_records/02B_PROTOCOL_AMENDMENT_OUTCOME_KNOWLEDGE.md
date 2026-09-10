# Protocol Amendment A2 — Freeze Pre-V9 Outcome Knowledge Status

**Amendment date:** 2026-08-30
**Base commit:** `3a13cc828f4080b9326c4060cd20f598e60a4699` (executable freeze)
**Prior tags (NOT moved):** `…protocol-20260830`, `…protocol-a1-20260830`,
`…executable-20260830`

## Chronology

This amendment was made **before any new V9 outcome existed**. No tracker was
run, no post-processing was executed on new real outputs, no TrackEval
invocation was made, and no new STV was computed. The execution guard remained
closed throughout.

## Why the amendment was necessary

Some universe cells already had their scientific outcomes observed **in V8,
before the V9 prospective protocol existed**. Without an explicit axis, a
systematic V9 report would present those cells beside genuinely unseen cells,
and a reader could reasonably conclude that every reported outcome had been
prospectively frozen. That would be false for four cells.

A2 makes the distinction machine-readable so historical outcomes can never be
presented as prospective.

## Knowledge-state axis

Orthogonal to `documentation_role`, `structural_family`, `audit_mode`,
`execution_state` and `split_status`. Never inferred from any of them.

| Status | Count |
|---|---|
| `HISTORICAL_OUTCOME_KNOWN_PRE_V9` | 4 |
| `PROSPECTIVE_OUTCOME_UNSEEN_AT_V9_FREEZE` | 3 |
| `NO_QUANTITATIVE_OUTCOME_PLANNED` | 9 |
| `STOPPED_UNSEEN` | 8 |

### Historical cells and exactly what was known before V9

| Cell | Known pre-V9 | Evidence |
|---|---|---|
| ByteTrack x MOT17 | R0/R0w/R1/R2 states, synthesized composition, STV four-class counts, metrics at R0/R1/R2, ordering | `a86f2db` — `ByteTrack_states.json`, `eval_ByteTrack.json`, `eval_ALL.json`, `RESULTS.json` |
| BoT-SORT x MOT17 | same set | `a86f2db` — `BoTSORT_states.json`, `eval_ALL.json`, `RESULTS.json` |
| OC-SORT (linear) x MOT17 | same set | `a86f2db` — `OCSORT_states.json`, `eval_OCSORT.json`, `eval_ALL.json`, `RESULTS.json` |
| StrongSORT++ x MOT17 | S0/S1/S2 states and nesting, AFLink+GSI structural rewrite inventory, metrics S0/S2/S2-S0, explicit "STV state NOT DEFINED for GSI" verdict | `7bcbcfb` — `STRONGSORT_DECOMPOSITION.json`, `STRONGSORT_SECONDARY.json`, `STRONGSORT_STATE_HASHES.json` |

Note that StrongSORT++ did **not** have STV counts known; its pre-V9 record
states that the STV-valid-only state is undefined for GSI. Knowledge is recorded
per quantity, not assumed for the whole cell.

### Prospective cells — verified unseen, not asserted from memory

`Deep-OC-SORT x MOT17`, `Hybrid-SORT x MOT17`, `OC-SORT-GPR x MOT17`.

Verification: searched `results/`, `docs/wacv/` and reachable git history at and
before the V8 freeze `9fc3c38`. No artifact, file or commit references these
pipelines' post-processing outcomes. `gp_interpolation` appears nowhere pre-V9;
the only pre-V9 "GPR" mentions are StrongSORT's own GSI Gaussian-process fit
(`STRONGSORT_DECOMPOSITION.json`), which is a different transformation.

## Interpretation contract (frozen)

- `HISTORICAL_OUTCOME_KNOWN_PRE_V9` — may be replayed through the V9 CLI as
  implementation validation and as part of the systematic universe, but **must
  not** be described as a prospective V9 result.
- `PROSPECTIVE_OUTCOME_UNSEEN_AT_V9_FREEZE` — may receive prospective
  interpretation only if all protocol and executable conditions were frozen
  before execution.
- `NO_QUANTITATIVE_OUTCOME_PLANNED` — documentation / no-rule cells only.
- `STOPPED_UNSEEN` — unseen because execution is stopped.

**The paper must report how many executed cells were historical versus genuinely
prospective. A blanket "all outcomes were prospectively frozen" statement is
forbidden.**

## Implementation-semantics corrections (not scientific-rule changes)

### 1. Score field — `NON_EVALUATED_METADATA_NORMALIZATION`

The implementation previously called a score-only difference
"serialization-only". That was an assumption. It has now been **traced** in
TrackEval at the frozen pin `12c8791b`:

- `mot_challenge_2d_box.py:262` parses tracker column 6 into `tracker_confidences`;
- `get_preprocessed_seq_data` carries it only by index deletion alongside removed
  rows (`:386`); `to_remove_tracker` is decided from similarity scores and
  distractor classes, never from confidence;
- **no metric implementation reads it** — `hota.py`, `clear.py` and
  `identity.py` contain no reference, and no file under `trackeval/metrics/`
  does.

Verdict: score cannot affect HOTA, DetA, AssA, IDF1, MOTA or MOT17
preprocessing. A score change is therefore a normalization of a
**non-evaluated metadata field** and does not violate the scientifically
relevant R0-subset-R2 invariant. The concept was renamed accordingly and the
trace documented in `rowid.py`. No STOP condition was triggered.

### 2. ID-rewrite accounting

Because canonical row identity contains `track_id`, an ID change appears as a
deletion plus an insertion. The previous implementation paired them by position
at the same `(sequence, frame)` — that **invented a matching** between old and
new tracker rows.

Corrected: pairing is licensed only when unambiguous — exactly one deletion and
one insertion at that `(sequence, frame)` with identical coordinates. The
inventory now reports `uniquely_attributable_ID_rewrites` and
`id_change_attribution_ambiguous` separately, alongside deletions, insertions
and directly identifiable coordinate rewrites. No inferred count is reported
when attribution is unavailable.

This is implementation semantics only and altered no scientific result: the
historical V8 replay remains exactly **6,784 / 6,784**.

## What did NOT change

No population, threshold, STV rule, metric set, evaluator pin, seed, materiality
rule, ordering rule or ranking criterion changed. The MOT17 2,652-frame manifest
hash, IoU 0.5, the {0.3–0.7} descriptive gates, TrackEval `12c8791b`, seed
20260830 and the 0.10 materiality threshold are all unchanged. Deployment count
remains 8; independent family count remains 3; all 24 cells remain.

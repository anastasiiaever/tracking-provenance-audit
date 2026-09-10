# V9 Executable Audit Implementation — Pre-Outcome Freeze

**NO NEW V9 SCIENTIFIC OUTCOME EXISTED DURING IMPLEMENTATION.**

No tracker was run; no post-processing was executed on real V9 tracker outputs;
no OC-SORT GPR run touched real V9 outputs; no TrackEval invocation was made on
a V9 state; no V9 STV count, synthesized-row fraction or ranking was computed or
inspected. Development used only synthetic fixtures and immutable V8 artifacts
whose outcomes were already known before the V9 protocol existed.

## Execution path

`scripts/tracking_provenance_audit/` is the single scientific execution path.
There is no separate study-specific script whose outputs are copied in later.

```
python -m tracking_provenance_audit \
    --raw R0 --post R2 --ground-truth GT \
    --dataset-contract MOT17 --pipeline-contract ByteTrack \
    --protocol docs/tpami_v9_tracking_provenance/02_PROSPECTIVE_PROTOCOL.json \
    --sequence MOT17-02-FRCNN --output report.json
```

One code path serves all four modes, dispatched from the frozen cell's
`audit_mode`: `ROW_ADDITIVE_R0_R1_R2`, `NON_ROW_ADDITIVE_S0_S2`,
`DOCUMENTATION_ONLY` refusal, `STOPPED_BEFORE_EXECUTION` refusal.

## Modules

| File | Responsibility |
|---|---|
| `rowid.py` | canonical row identity, MOT/GT parsing, IoU |
| `transitions.py` | row transition inventory; row-additive invariant |
| `stv.py` | frozen STV rule, gate-before-assignment, Hungarian |
| `states.py` | R1 construction; non-row-additive refusal |
| `adapters.py` | MOT17 frozen population; stopped manifests |
| `gpr_wrapper.py` | external RNG wrapper + same-seed replay |
| `metrics.py` | frozen TrackEval interface, no fallback |
| `ordering.py` | pairwise ordering engine |
| `materiality.py` | secondary descriptive classification |
| `report.py` | deterministic canonical report |
| `guard.py` | no-real-V9-execution guard |
| `cli.py` | entry point |

## Row identity

Canonical identity is `(sequence, frame, track_id)`. Coordinates, score, class
and serialization formatting are carried separately, so a writer-only difference
(for example DTI rewriting score to `-1`) is **not** a rewrite. A track-id
rewrite cannot appear within a fixed identity and is detected as a paired
delete+insert at the same `(sequence, frame)`.

Row-additive requires every R0 identity to occur in R2 with unchanged
coordinates. On violation the CLI emits
`STRUCTURAL_DECOMPOSITION_UNAVAILABLE` and does **not** construct R1.

## STV

Exactly the frozen rule: reference assignment on R0 only, per frame, against
scoreable GT (`flag==1 and class==1`, visibility not thresholded), gate applied
**before** one-to-one Hungarian assignment, assignment frozen before synthesized
rows are introduced. Classes in priority order: `ANCHOR_UNMATCHED`,
`ANCHOR_ID_MISMATCH`, `TARGET_REFERENCE_ABSENT`, `SEMANTICALLY_ADMITTED`;
partition asserted exact. Only `ANCHOR_ID_MISMATCH` carries the "different
ground-truth identities under the frozen matcher" reason; `ANCHOR_UNMATCHED`
carries an explicit "NOT a false positive, NOT a demonstrated semantic error"
reason. Sensitivity gates run only when explicitly requested and are labelled
descriptive; 0.5 remains primary.

## Non-row-additive

`GPR_REWRITE` and `LINK_PLUS_SMOOTHING` receive S0/S2 structural analysis only.
No R1 analogue is forced. `R1_status = STRUCTURALLY_UNDEFINED`, because each
transformation rewrites values its own regression/smoothing fit consumes, so
removing a subset of generated rows would alter the fit. No artificial
intervention is synthesized.

## GPR RNG

Upstream `tools/gp_interpolation.py` is never edited. The wrapper seeds
`random` and `numpy.random` (and `PYTHONHASHSEED`) with the frozen seed
**20260830** before calling the unmodified entry point, records
Python/NumPy/scikit-learn versions, the upstream source SHA-256, the exact
invocation and the two discoverable stochastic APIs, and provides a same-seed
replay verifier. The replay is a reproducibility check only and is never
averaged or pooled with the first execution. Failure yields
`REPRODUCIBILITY_FAILURE` and licenses no quantitative GPR ranking claim. No
seed search is performed.

## Development guard

`prospective_v9` execution raises `ExecutionNotAuthorized` unless the release
marker `docs/tpami_v9_tracking_provenance/EXECUTION_AUTHORIZED` (or
`TPAMI_V9_EXECUTION_AUTHORIZED=1`) exists. **The marker does not exist at this
freeze.** `fixture` and `historical_v8` modes remain usable.

## Historical V8 regression

The generic implementation reproduces the frozen V8 STV decisions exactly:
**6,784 / 6,784** synthesized rows, with every per-class count matching for
ByteTrack (2,072), BoT-SORT (2,090) and OC-SORT (2,622), and each partitioning
exactly. This is software validation, not a V9 result; the numbers are
immutable and predate V9. V8's `SEMANTICALLY_VALID` maps to the protocol's
`SEMANTICALLY_ADMITTED` (naming only).

## Determinism

Reports serialize with sorted keys and fixed separators. No wall-clock value
enters hashed content; identical inputs produce identical bytes and an identical
`content_sha256`.

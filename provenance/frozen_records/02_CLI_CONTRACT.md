# V9 CLI Execution Contract

**Frozen before implementation. No V9 outcome exists.**

The V9 headline audit MUST be produced by the generic audit artifact. No
study-specific script may compute the headline numbers first and be replayed
through the CLI afterwards.

## Invocation

```
audit-tracking-postprocess
    --raw                R0 (pre-post-processing tracker output)
    --post               R2 (post-processing output)
    --ground-truth       GT for the frozen population
    --dataset-adapter    {mot17-valhalf, mot20-valhalf, dancetrack-val}
    --pipeline-contract  contract id (pipeline, family, callsite parameters)
    --population-manifest frozen population spec
    --evaluator-config   pinned TrackEval commit + config
    --seed               required only for stochastic families
    --output             audit record path
```

## Required output record

- input hashes (raw, post, GT, every file read)
- population manifest hash
- pipeline / family identifier and lineage group
- row transition inventory (inserted, deleted, coordinate-changed, id-changed)
- STV classification where licensed, with a reason code where not
- evaluator input manifests
- metric table (HOTA, DetA, AssA, IDF1, MOTA) or METRIC_NOT_AVAILABLE
- R0/R2 delta per metric
- case/row identifiers sufficient for replay
- deterministic certificate (inputs -> outputs reproducible)
- reason codes for structurally unavailable diagnostics

## Reason codes

`STRUCTURAL_DECOMPOSITION_UNAVAILABLE`, `STRUCTURALLY_UNDEFINED`,
`METRIC_NOT_AVAILABLE`, `REPRODUCIBILITY_FAILURE`, `NO_DOCUMENTED_RULE`,
`DATASET_NOT_ACQUIRED`.

## Development discipline (Sec. 14)

Implementation may be developed ONLY against synthetic fixtures, tiny
hand-constructed MOT-format fixtures, and frozen historical V8 artifacts whose
outcomes are already known. Development or debugging against new V9 real-data
outputs is prohibited.

## Required tests before the first real-data run

| # | Test | Expected |
|---|---|---|
| 1 | row-additive insertion | rows inserted, R0 preserved |
| 2 | existing-row rewrite | invariant violation detected |
| 3 | ID rewrite | id change detected |
| 4 | deletion | deletion detected |
| 5 | duplicate row identity | rejected, not silently merged |
| 6 | missing GT | TARGET_REFERENCE_ABSENT |
| 7 | unmatched anchor | ANCHOR_UNMATCHED |
| 8 | ID mismatch | ANCHOR_ID_MISMATCH |
| 9 | reference absent | TARGET_REFERENCE_ABSENT |
| 10 | admitted STV | SEMANTICALLY_ADMITTED |
| 11 | non-row-additive refusal | no R1 constructed; reason code emitted |
| 12 | same-seed GPR replay | identical output |
| 13 | ordering flip | FLIP |
| 14 | ordering survival | UNCHANGED |
| 15 | tie creation | TIE_CREATED |
| 16 | tie breaking | TIE_BROKEN |
| 17 | NO_DOCUMENTED_RULE handling | cell retained, no quantitative claim |

The CLI implementation commit MUST be frozen before the first new real-data run.

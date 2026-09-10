# Provenance fields

A reader's guide to the vocabulary in `provenance/frozen_records/` and the
released tables. Every term below appears verbatim in the data.

## Release manifest

`provenance/RELEASE_MANIFEST.json` has one entry per published data file:

| field | meaning |
|---|---|
| `public_file` | path in this repository |
| `role` | what the file is for |
| `source_frozen_artifact` | the frozen artifact it came from |
| `source_sha256` | SHA-256 of that source artifact, as frozen |
| `transformation` | what was done — `none (byte-identical copy)`, or a description |
| `redistribution` | the redistribution class (below) |
| `public_sha256`, `bytes` | of the file as published |

`provenance/MANIFEST.sha256` covers the whole published tree and is checkable
with `sha256sum -c`.

### Redistribution classes

| class | meaning |
|---|---|
| `OWN_RECORD` | authored by this study; released verbatim |
| `OWN_DERIVED_AGGREGATE` | aggregate table derived from the study's own frozen results |
| `REFERENCE_ONLY` | describes third-party material without containing any of it |
| `DATASET_DERIVED`, `CHECKPOINT_DERIVED` | **not used** — no file in this release is either |

## Outcome-knowledge status

The single most important field, because it says what a number can be used for.

| value | meaning |
|---|---|
| `PROSPECTIVE_OUTCOME_UNSEEN_AT_V9_FREEZE` | the protocol was frozen before this outcome existed |
| `HISTORICAL_OUTCOME_KNOWN_PRE_V9` | the outcome was already known when the protocol was frozen |
| `STOPPED_UNSEEN` | the cell was stopped before execution; no outcome was ever produced |

A historical cell is not relabelled as prospective anywhere. Where historical and
prospective deployments appear in one table — as they do in the ordering matrix —
each cell carries a `pair_class` naming which kinds it compares.

## Audit mode

| value | meaning |
|---|---|
| `ROW_ADDITIVE_R0_R1_R2` | the operator only inserts rows, so `R1` is defined |
| `NON_ROW_ADDITIVE_S0_S2` | the operator rewrites rows its own fit consumes; only `S0`/`S2` exist |
| `DOCUMENTATION_ONLY` | documented but no quantitative output exists to audit |
| `STOPPED_BEFORE_EXECUTION` | the cell remained in the universe carrying its stop reason |

A stopped cell is never deleted from the universe. `provenance/frozen_records/01_UNIVERSE_CENSUS.json`
holds all 24 cells (`provenance/frozen_records/01_UNIVERSE_CENSUS.json`); `universe.added` and `universe.removed` are both `0`.

## Admission classes

`ANCHOR_UNMATCHED`, `ANCHOR_ID_MISMATCH`, `TARGET_REFERENCE_ABSENT`,
`SEMANTICALLY_ADMITTED` — defined, with what each does and does not license, in
[ESTIMAND_ELIGIBILITY.md](ESTIMAND_ELIGIBILITY.md).

## Eligibility vocabulary (MOT20)

| value | meaning |
|---|---|
| `READY` | dataset ready **and** exact command frozen **and** assets verified **and** environment verified |
| `BLOCKED_CHECKPOINT_PROVENANCE` | the released checkpoint makes the estimand unavailable |
| `BLOCKED_ASSET` | a required asset does not exist publicly |
| `BLOCKED_COMMAND` | no documented command targets the required split |
| `BLOCKED_ENVIRONMENT`, `BLOCKED_INDEXING`, `BLOCKED_OTHER` | as named |

Checkpoint verdicts: `NO_KNOWN_EVAL_LEAKAGE`, `CONFIRMED_EVAL_LEAKAGE`,
`POTENTIAL_EVAL_LEAKAGE`, `INHERITED_CONFIRMED_EVAL_LEAKAGE`, or a `MIXED:`
string naming which component is which.

## Status labels on results

| value | meaning |
|---|---|
| `DESCRIPTIVE` | reported as a count or fraction; carries no significance or generalization claim |
| `POST-HOC` | specified after the primary result existed; carries no confirmatory weight |
| `STRUCTURALLY_UNDEFINED` | the quantity is not defined for this operator; none was manufactured |
| `METRIC_NOT_AVAILABLE` | the metric does not exist for this cell; never imputed |
| `UNDEFINED_NO_SYNTHESIZED_ROWS` | the conditional fraction has no denominator |

The IoU-gate sensitivity grid in `results/stv_sensitivity/` and the gap-length
stratification are both `POST-HOC`. The frozen `tau = 0.5` result remains primary
regardless of what the grid shows, and its specification
(`results/stv_sensitivity/gaplen_SPEC.md`) says so in its own header.

## Corpus provenance

| value | meaning |
|---|---|
| `FROZEN_AND_MATERIALISED` | the population is fixed and verified against its manifest |
| `MIRROR_TRANSPORT_FALLBACK` | structural verification passed; byte identity to an official archive is **not** established |

The MOT20 corpus carries the second. It is an explicit field in the frozen result
manifest rather than something a reader must infer from an absent table.

## Hash conventions

Two coexist and are not interchangeable:

- **Record objects** are hashed canonically: SHA-256 of the JSON serialization of
  the object with its own hash field removed, sorted keys, compact separators.
- **Artifacts on disk** are hashed as raw file bytes.

Any hash in a `*_sha256` field of a record is the first kind. Every other hash in
this repository, including all of `provenance/MANIFEST.sha256`, is the second.

# Protocol Amendment A1 — Separate Documentation Role from Structural Audit Mode

**Amendment date:** 2026-08-30
**Original protocol commit:** `343214bbbbea37aac9f279bf255b3b85343206a3`
**Original protocol tag (NOT moved, NOT recreated):** `tpami-v9-tracking-provenance-protocol-20260830`

## Chronology — this amendment preceded every V9 outcome

At the time of this amendment:

- no V9 tracker had been executed;
- no post-processing had been run on any real benchmark output;
- no TrackEval invocation had been made;
- no STV classification had been computed;
- no ordering or ranking had been computed;
- no V9 metric, STV count, synthesized-row count or result file had been
  inspected.

**No outcome existed that could have motivated this amendment.** It could not
have been outcome-driven, because there was no outcome to see.

## Reason

During protocol review it was found that the frozen schema used
`NON_ROW_ADDITIVE_STRUCTURAL` as a *governing scientific role*. That conflated
two orthogonal dimensions:

- **A. documentation / deployment status** — what the official release actually
  documents, and for which split;
- **B. structural audit semantics** — whether the transformation permits a
  row-subset decomposition.

The conflation was not cosmetic. It **destroyed documentation information**:
because a structural label occupied the single role slot, four cells lost their
documentation status entirely. Most consequentially, StrongSORT++ x MOT17 —
which the official repository documents on the **validation** split
(`README.md:107`, `--AFLink --GSI` on MOT17-val) — was recorded only as
"non-row-additive", hiding the fact that it is a `PRIMARY_DOCUMENTED_VALIDATION`
cell. Under the old schema `OPTIONAL_DOCUMENTED_FAMILY` was unusable and had
zero members, even though the census had positively established two optional
cells.

## Correction

Every cell now carries two independent axes plus supporting fields:

- `documentation_role` — derived **only** from census documentation status and
  documented split. It never encodes structural behaviour.
- `audit_mode` — derived **only** from structural family, corpus availability
  and documentation-executability. It never encodes documentation status.
- `structural_family`, `execution_state`, `split_status`, `stop_reason`, and the
  verbatim `census_documentation_status` retained separately.

`NON_ROW_ADDITIVE_STRUCTURAL` is removed as a documentation role. The
non-row-additive property is now carried by `audit_mode = NON_ROW_ADDITIVE_S0_S2`
together with `structural_family`.

Documentation status is never inferred from structural behaviour, and structural
behaviour is never inferred from documentation status.

### Role-count effect of the correction

| documentation_role | before A1 | after A1 |
|---|---|---|
| SECONDARY_SPLIT_ADAPTED | 8 | 9 |
| DOCUMENTATION_ONLY_IMPLEMENTED | 6 | 6 |
| PRIMARY_DOCUMENTED_VALIDATION | 3 | 4 |
| NO_DOCUMENTED_RULE | 3 | 3 |
| OPTIONAL_DOCUMENTED_FAMILY | 0 (unusable) | 2 |
| NON_ROW_ADDITIVE_STRUCTURAL | 4 | removed from this axis |

The four cells previously absorbed by the structural label are restored to their
census-derived documentation roles: OC-SORT-GPR x {MOT17, MOT20} to
`OPTIONAL_DOCUMENTED_FAMILY`, StrongSORT++ x MOT17 to
`PRIMARY_DOCUMENTED_VALIDATION`, StrongSORT++ x MOT20 to
`SECONDARY_SPLIT_ADAPTED`.

## What did NOT change

This amendment is **schema only**. Verified byte-identical across all 21
non-cell protocol keys:

populations (including the MOT17 2,652-frame manifest and its per-sequence GT
hashes), the MOT20/DanceTrack frozen rules, STV IoU 0.5 and its class priority,
the descriptive sensitivity gates {0.3, 0.4, 0.5, 0.6, 0.7}, the metric set,
the TrackEval pin `12c8791b303e0a0b50f753af204249e622d0281a`, the materiality
threshold 0.10 and its denominator, `GPR_AUDIT_SEED = 20260830`, the ordering
rules and estimand warning, the literature-audit coding spec, the CLI
execution-path requirement, the stop conditions, and the V8 wording-correction
contract.

No threshold, population, metric, STV rule, family membership, seed, deployment
or family count, or result interpretation was changed. Deployment count remains
8; independent family count remains 3. No cell was added or removed; all 24
remain.

## Dataset-absence handling

For corpora not yet acquired (MOT20, DanceTrack), the **documentation role is
unchanged** — absence of data is not a documentation fact. Instead
`execution_state = STOPPED_DATASET_NOT_ACQUIRED` and
`audit_mode = STOPPED_BEFORE_EXECUTION`.

Acquiring a corpus later **materialises** the already-frozen population. It must
not redefine the population or any decision rule.

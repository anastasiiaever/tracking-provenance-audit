# Paper artifact map

Reader entry point: where every quantity, record and verification step in the
manuscript and supplement lives in this repository. Paths are relative to the
repository root and are stable at the release tag.

This file indexes; it does not restate. Where an authoritative record already
exists it is pointed to rather than copied.

---

## 1. Numeric ledger

| | |
|---|---|
| path | `tpami/source_of_truth/05_NUMERIC_LEDGER.csv` |
| rows | 263 |
| columns | `id, population, arm, quantity, value, unit, artifact, status, note` |
| what it is | every quantity stated anywhere in the paper, with its unit and the artifact it came from |

The manuscript's own consistency checks run against this file: each numeral in a
quantifier or direction statement is resolved to a ledger row or to a released
artifact value at full precision. Supplement S26 renders it as a table.

Companion records:

- `tpami/source_of_truth/26_CLAIM_TO_ARTIFACT_MAP.csv` — 47 rows, claim → artifact
- `tpami/source_of_truth/34_PROSE_CLAIM_LEDGER.csv` — 58 rows, prose claim → artifact → verification method → status
- `tpami/source_of_truth/09_PROVENANCE_LEDGER.csv` — provenance fields per deployment

---

## 2. Bootstrap reproducibility record

One design across all three arms: 10,000 draws, the sequence as the resampling
cluster, percentile intervals, seed `20261003`. The draw-index matrix is
identified by sha256 so a reproduction can be checked without shipping the
binary.

| arm | summary | all cells | draw index |
|---|---|---|---|
| released MOT17 | `tpami/results/mot17_bootstrap/D1_bootstrap_summary.csv` and `.json` | `tpami/results/mot17_bootstrap/D1_bootstrap_10000.csv` | `tpami/results/mot17_bootstrap/D1_bootstrap_indices.sha256` |
| controlled DanceTrack, linear DTI | `tpami/results/dancetrack_dti/D1B_bootstrap_summary.csv` | `tpami/results/dancetrack_dti/D1B_bootstrap_10000.csv` | `indices_sha256` field in the summary |
| controlled DanceTrack, GSI | `tpami/results/dancetrack_gsi/D2C_bootstrap_summary.csv` and `.json` | — | `index_sha256`, with `index_reused_from = D1B` |

| | released MOT17 | controlled DTI | controlled GSI |
|---|---|---|---|
| draws | 10,000 | 10,000 | 10,000 |
| seed | 20261003 | 20261003 | 20261003 |
| clusters | 7 sequences | 25 sequences | 25 sequences |
| cells | 50 | 30 | 30 |
| sign changes | 5 | 7 | 7 at the linear stage, 0 added by the GP stage |
| draw-index sha256 | `8cd16bcc23a47d1f…` | `342b76e2d37fc633…` | reuses the DTI matrix |

The released-arm `.json` additionally carries the seven cluster names and the
per-deployment, per-state point estimates the intervals were built around.

`P(sign differs)` in the manuscript is the `frac_sign_differs` column of the
per-cell files. It is a bootstrap frequency, not a p-value.

---

## 3. Execution and authorisation record

| record | path |
|---|---|
| prospective protocol, frozen before execution | `provenance/frozen_records/02_PROSPECTIVE_PROTOCOL.md` and `.json` |
| protocol file hashes | `provenance/frozen_records/02_PROTOCOL_MANIFEST.json` |
| executable implementation contract | `provenance/frozen_records/03_EXECUTABLE_IMPLEMENTATION.md` |
| CLI contract | `provenance/frozen_records/02_CLI_CONTRACT.md` |
| universe census, pre-specified configurations | `provenance/frozen_records/01_UNIVERSE_CENSUS.md` and `.json` |
| MOT20 execution readiness | `provenance/frozen_records/10_MOT20_EXECUTION_READINESS.md` and `.json` |
| MOT20 readiness correction and amendment | `provenance/frozen_records/10A_MOT20_READINESS_CORRECTION.md` and `.json` |
| amendment: role and audit mode | `provenance/frozen_records/02A_PROTOCOL_AMENDMENT_ROLE_AUDITMODE.md` |
| amendment: outcome knowledge | `provenance/frozen_records/02B_PROTOCOL_AMENDMENT_OUTCOME_KNOWLEDGE.md` |
| independent result verification | `provenance/frozen_records/08_INDEPENDENT_RESULT_VERIFICATION.md` and `.json` |
| MOT20 independent verification | `provenance/frozen_records/14_MOT20_DEEP_INDEPENDENT_VERIFICATION.md` and `.json` |
| invariant matrix | `provenance/frozen_records/11_INVARIANT_MATRIX.json` |
| execution order and post-hoc status, in prose | `tpami/source_of_truth/02_CURRENT_FACTS.md` sections A–H |
| artifact precedence between generations | `tpami/source_of_truth/01_ARTIFACT_PRECEDENCE.md` |

**Second-operator status.** The GSI arm was designed after the first controlled
operator's outcomes were known and shares its linear stage with it. It is
post-hoc and is not an independent reproduction of the DTI ordering result. The
record is `tpami/source_of_truth/02_CURRENT_FACTS.md` section F and
`tpami/results/dancetrack_gsi/D2C_three_state_pairwise_margins.csv`.

**Evaluator identity.** TrackEval at commit
`12c8791b303e0a0b50f753af204249e622d0281a`, used unmodified, pin enforced in code
(`metrics.freeze_inputs` raises `EvaluatorPinMismatch` rather than falling back).
Recorded in `metadata/external_assets.csv` and
`provenance/frozen_records/02_PROSPECTIVE_PROTOCOL.json`.

---

## 4. Manifests and verification

| | path | expected |
|---|---|---|
| release manifest, machine-readable | `provenance/RELEASE_MANIFEST.json` | 270 file entries |
| release manifest, checksums | `provenance/MANIFEST.sha256` | 271 entries, all OK |
| sanitised source-of-truth manifest | `tpami/source_of_truth/RELEASE_MANIFEST_SANITISED.sha256` | 53 entries, all OK |
| original source-of-truth manifest | `tpami/source_of_truth/V6_SOURCE_OF_TRUTH_MANIFEST.sha256` | pre-sanitisation; 17 entries differ by design |

```bash
python scripts/verify_release.py                                   # 32 + 85 + 44 + 18 = 179 checks
sha256sum -c provenance/MANIFEST.sha256                            # 271 OK
cd tpami/source_of_truth && sha256sum -c RELEASE_MANIFEST_SANITISED.sha256   # 53 OK
python -m pytest -q tests/                                         # 214 tests
```

The release requires **Python 3.9 or newer**; the audit core uses PEP 584 dict
union. On 3.8 two tests fail by design, the version guard and its one downstream
consequence.

`provenance/RELEASE_MANIFEST.json` lists itself; that one entry's hash cannot be
self-consistent and is informational. `provenance/MANIFEST.sha256` carries the
authoritative checksum for it.

---

## 5. Full source mappings

| | path |
|---|---|
| claim → released file, with presence check | `tpami/ARTIFACT_MAP.md` |
| claim → artifact, machine-readable | `tpami/source_of_truth/26_CLAIM_TO_ARTIFACT_MAP.csv` |
| prose claim → artifact → verification method | `tpami/source_of_truth/34_PROSE_CLAIM_LEDGER.csv` |
| evidence architecture, what each arm supports | `tpami/source_of_truth/06_EVIDENCE_ARCHITECTURE.csv` |
| normative method and transition definitions | `tpami/source_of_truth/07_METHOD_DEFINITIONS.md` |
| allowed claims | `tpami/source_of_truth/03_ALLOWED_CLAIMS.md` |
| forbidden or superseded claims | `tpami/source_of_truth/04_FORBIDDEN_OR_OBSOLETE_CLAIMS.md` |
| limitations ledger | `tpami/source_of_truth/08_LIMITATIONS_LEDGER.md` |
| upstream pipelines, pinned commits | `metadata/upstream_pipelines.csv` |
| external assets, checkpoints and evaluator | `metadata/external_assets.csv` |
| post-processing documentation census, 24 cells | `metadata/postprocessing_universe.csv` |
| datasets | `metadata/datasets.csv` |
| path placeholders used in sanitisation | `provenance/path_map.json` |

---

## 6. Literature coverage record

| | path |
|---|---|
| machine-readable, twelve reviewed areas | `tpami/source_of_truth/35_LITERATURE_COVERAGE.csv` |
| review specification | `provenance/frozen_records/02_LITERATURE_AUDIT_SPEC.md` |
| citation and related-work notes | `tpami/source_of_truth/15_CITATION_AND_RELATED_WORK_NOTES.md` |

Columns: `area`, `representative_works_bibkeys`, `n_works`,
`what_the_area_covers_and_its_relation_to_evaluated_output_provenance`. Twelve
areas, 49 work references. This is the evidence behind the paper's scoped gap
statement, exported without changing its content; the supplement continues to
present the same record as Table S34.

---

## 7. What stays in the PDF

This repository holds machine-readable audit material. It is not a place to move
central scientific evidence out of the paper. The following remain in the
supplement:

gate sweeps; per-sequence evidence; the exhaustive pairwise matrices; MOT20
eligibility evidence; operator-parameter sensitivity; selection-provenance
sensitivity; rewrite-transition measurements; Figs. S1 and S2; and the
substantive limitations.

---

## 8. Figures

Generators under `tpami/figures/scripts/` rebuild every manuscript figure and
assert their own provenance against the frozen records, aborting rather than
drawing an unverified case. Figure 1 is `gen_fig1_fourclass.py`
(154 checks); `gen_fig1.py` and `gen_fig1_qualitative.py` are superseded and
retained as history. Machine-readable per-figure records are the
`tpami/figures/_fig*_provenance.json` files.

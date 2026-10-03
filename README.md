# Tracking Provenance Audit

Code and released audit artifacts for  
*Post-Processing Provenance and Estimand Eligibility in Multi-Object Tracking Evaluation*.

This repository contains the public audit implementation, frozen provenance records, result tables, and scripts for checking the results reported in the paper. It does not contain tracker training code, datasets, or model checkpoints.

## Quick verification

Python 3.9 or newer.

```bash
conda env create -f environment.yml
conda activate tracking-provenance-audit

python scripts/verify_release.py
sha256sum -c provenance/MANIFEST.sha256
python -m pytest -q
```

## Synthetic example

A small synthetic example runs without external data:

```bash
python examples/minimal_example/run.py
```

## Paper artifacts

`results/mot17/` contains the MOT17 state metrics, admission composition, row totals, and the complete 50-cell ordering matrix.

`results/mot20/` contains the seven-cell eligibility record and the results of the eligible Deep-OC-SORT deployment.

`results/controlled/` contains the frozen summaries for the controlled support-accounting analysis.

`provenance/frozen_records/` contains the protocol and frozen records used to check the released summaries.

`provenance/RELEASE_MANIFEST.json` maps published files to their frozen sources and recorded hashes.

## Verification

```bash
python scripts/verify_release.py
python scripts/verify_ordering.py
python scripts/verify_admission.py
python scripts/verify_mot20_eligibility.py
python scripts/verify_controlled_arm.py
python scripts/verify_support_accounting.py
```

The scripts recompute the released quantities and compare them with the corresponding frozen records. They do not rerun trackers or training.

`verify_support_accounting.py` runs a worked support-accounting example. The paper's controlled-arm results are checked by `verify_controlled_arm.py`.

### Headline claims

| paper claim | public artifact | command |
|---|---|---|
| MOT17: synthesized rows are 4.12%-6.36% of submitted rows | `results/mot17/row_totals.csv`, `results/mot17/stv_composition.csv` | `python scripts/verify_admission.py` |
| MOT17: 28.92%-49.02% of synthesized rows are not admitted | `results/mot17/stv_composition.csv` | `python scripts/verify_admission.py` |
| MOT17: all 25 deployment-by-metric values rise from R0 to R2 | `results/mot17/metrics_by_state.csv` | `python scripts/verify_release.py` |
| MOT17: 5 of 50 pairwise relations change, 45 remain unchanged | `results/mot17/ordering_matrix.csv` | `python scripts/verify_ordering.py` |
| MOT20: 1 eligible for the pre-specified held-out second-half comparison, 5 ineligible through training overlap, 1 unresolved | `results/mot20/eligibility.csv` | `python scripts/verify_mot20_eligibility.py` |
| MOT20: 34,814 synthesized rows, 25.14% not admitted | `results/mot20/deep_oc_sort_stv.csv` | `python scripts/verify_mot20_eligibility.py` |
| Controlled arm: the pooled comparison reverses on common support | `results/controlled/ntu_support_accounting.json` | `python scripts/verify_controlled_arm.py` |

`docs/CLAIM_MATRIX.md` gives the full claim-to-artifact mapping.

Two post-hoc descriptive tables extend the released results without changing
them: `results/stv_sensitivity/full_five_pipeline_summary.csv` carries the
admission-gate sweep over all five row-additive MOT17 pipelines, and
`results/mot17/sequence_ordering_heterogeneity_summary.csv` reports the
sequence-level heterogeneity of the five aggregate ordering changes. Each has a
README beside it stating its scope.

## Repository layout

```text
src/tracking_provenance_audit/   tracking audit implementation
src/applicability_audit/         support and applicability audit
scripts/                         verification entry points
results/                         released result tables
provenance/                      frozen records, manifests, and hashes
metadata/                        upstream repositories and external assets
docs/                            provenance and reproducibility documentation
tests/                           unit, integrity, and corruption-detection tests
examples/                        synthetic example
```

## Provenance

The reported experimental results were produced by the frozen research execution pipeline described in the paper. The code released here checks the audit logic and the recorded results; it was not the execution path that produced the original experimental outputs.

`docs/PROVENANCE.md` records the source commits, MOT17 population naming, MOT20 corpus status, eligibility vocabulary, and history normalization.

## Data and external assets

Datasets and third-party checkpoints are not redistributed.

Upstream tracker repositories are recorded by exact commit in `metadata/upstream_pipelines.csv`. External assets are recorded in `metadata/external_assets.csv`, including hashes where available.

Evaluation used TrackEval at commit `12c8791b303e0a0b50f753af204249e622d0281a`.

See `docs/DATASETS.md` and `docs/LICENSING_BOUNDARY.md` for dataset and licensing details.

## Citation

See `CITATION.cff`. Venue and DOI information will be added when available.

## Licence

The code and original material in this repository are released under the MIT License. Third-party datasets, repositories, and model assets retain their original licences.

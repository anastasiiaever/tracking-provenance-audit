# Post-Processing Provenance and Estimand Eligibility in Multi-Object Tracking Evaluation

Reference implementation and released audit artifacts.

A tracking submission is not the same object as the tracker's output. Between the
two sits post-processing — gap filling, tracklet linking, smoothing — that
inserts rows the tracker never observed. The evaluator scores those rows
identically to observed ones and cannot tell them apart. This repository
implements an audit that can: it separates what the tracker observed from what
post-processing synthesized, classifies every synthesized row against a frozen
reference-semantic admission rule, reports the full pairwise ordering of
deployments at both states, and records which benchmark cells have an available
estimand at all.

This is an **evaluation artifact**, not a tracker and not a proposed method. It
introduces no new metric and no new post-processing operator.

## What this repository reproduces

| | |
|---|---|
| **MOT17 ordering audit** | all 10 deployment pairs × 5 metrics at both states — 45 orderings unchanged, 5 reversed by post-processing alone |
| **MOT17 admission composition** | per deployment, how many synthesized rows the reference supports — 28.9% to 49.0% are not admitted |
| **MOT20 eligibility** | 7 pre-specified cells, the evidence behind each verdict, and the 1 cell whose estimand was available |
| **MOT20 executed cell** | 34,814 synthesized rows, 25.1% not admitted (1.55% of all submitted rows) |
| **Admission-gate sensitivity** | the full post-hoc grid over IoU gates 0.3–0.7 |
| **Controlled arm** | PoseTrack21, NTU, BDD100K/MOT17, KITTI, JTA, 3DPW and the learned-model diagnostics — every reader-facing controlled figure, as released summaries checked against their frozen records |

The post-processing universe census — 8 pipelines × 3 datasets, with what each
operator does to rows — is in `metadata/postprocessing_universe.csv`.

**What "reproduces" means here.** Every command below re-derives a published
result from released summaries and the released audit code, and checks it is
internally exact. It does **not** re-measure anything: no corpus, tracker or
checkpoint ships with this repository. `docs/REPRODUCIBILITY.md` sets out the
three levels and what each costs, and `docs/CLAIM_MATRIX.md` states, claim by
claim, which are checkable offline and which need an external asset.

## Quick start

No dataset, no checkpoint, no GPU. Python 3.9+.

```bash
git clone <this repository>
cd tracking-provenance-audit
pip install pyyaml pytest            # or: conda env create -f environment.yml

python scripts/verify_release.py
```

That re-derives every ordering relation and transition from the released
full-precision values, re-runs the admission classifier on fixtures with known
answers, recomputes every published fraction and materiality verdict from the
released integers, re-checks the MOT20 eligibility ledger, and confirms the
frozen configuration files still agree with the source constants.

To see the idea on eight rows you can read:

```bash
python examples/minimal_example/run.py
```

## Reproduce the MOT17 audit

```bash
python scripts/verify_ordering.py     # ordering matrix: 10 pairs x 5 metrics, R0 vs R2
python scripts/verify_admission.py    # admission composition and materiality
```

`scripts/verify_ordering.py` prints the five orderings that post-processing
reverses, with the margin before and after. `scripts/verify_admission.py`
exercises the released
classifier on fixtures — matched anchors, anchors resolving to different
identities, an absent reference, and the gate applied before assignment — then
checks the released tables against it.

Data: `results/mot17/ordering_matrix.csv`, `results/mot17/metrics_by_state.csv`,
`results/mot17/stv_composition.csv`,
`results/mot17/strongsort_decomposition.csv`.

StrongSORT++ and the GPR variant appear as `S0`/`S2` and
`STRUCTURALLY_UNDEFINED`. Their operators rewrite values their own fit consumes,
so a row-subset decomposition is not defined and none is manufactured. See
[docs/ESTIMAND_ELIGIBILITY.md](docs/ESTIMAND_ELIGIBILITY.md).

## Reproduce the MOT20 eligibility audit

```bash
python scripts/verify_mot20_eligibility.py
```

Seven cells were pre-specified before any MOT17 execution. Six are blocked, five
of them because the released checkpoint was trained on the evaluation frames — a
detector trained on the frames it is scored on makes the held-out estimand
unavailable regardless of what it scores. One cell was clean and is the one that
was executed.

The script checks that the ledger is complete, that no checkpoint was substituted
to rescue a blocked cell, that no MOT20 outcome existed when the cell was
selected, and that the corpus provenance caveat is still carried.

Data: `results/mot20/eligibility.csv`, `results/mot20/eligibility_context.json`,
`results/mot20/deep_oc_sort_stv.csv`, `results/mot20/deep_oc_sort_result.json`.

## Controlled arm

Two different things, kept apart.

**The released controlled summaries.**

```bash
python scripts/verify_controlled_arm.py
```

The paper's controlled evidence spans four populations. Their headline figures
are released as small tables under `results/controlled/`, together with the
frozen records they were derived from, and this script checks every one against
its record: that the classes partition the population exactly, that each
percentage recomputes from the integers it summarises, and that each interval
brackets its own point estimate.

| population | released | example figure |
|---|---|---|
| PoseTrack21 | Gate-1R partition under three segmentation rules, the support ladder by gap length, the sequence-clustered bootstrap | 8.88% / 10.50% / 36.43% eligible of 78,194 scoreable occluded targets |
| NTU RGB+D | the support-accounting reclassification and the common-support reversal | −1.20859 over 181,275 rows → +3.63705 over 180,375 |
| BDD100K-derived + MOT17 | object-trajectory Gate-1R partition, per population | 2.41% and 25.13% eligible |
| KITTI | applicability partition, pooled and stratified, plus the one frozen hypothesis | 12,554 / 16,096 = 0.779945, SUPPORTED |
| JTA | within-corpus structural replication partition and the frozen headline reading | 48,854,154 targets, 41.48% eligible, 58.52% refused |
| 3DPW | matched-predictor operator/aggregation validation and its four missed cells | Kalman 28/28 in band, spline 24/28, verdict FAIL_QUANTITATIVE_B |
| learned models | the noise-sensitivity grid and the frozen input contract | 17 slots, 13 available, 4 unavailable, no confidence channel |

**None of these corpora ships here**, so this is a check of the released
summaries against the frozen records, not a re-measurement. Re-measuring any of
them needs the corpus and, for the learned arms, checkpoints that are not
released — see `docs/DATASETS.md` and `docs/CLAIM_MATRIX.md`.

**The audit engine.**

```bash
python scripts/verify_support_accounting.py
```

`src/applicability_audit` is the dataset-agnostic audit that runs before ranking:
which targets are applicable, which cases each method actually supports, whether
the comparison support is identical, and whether the declared aggregation makes
the ranking readable. Headline values are computed on identical common support
only, and the difference from each method's own-support value is reported as a
quantity rather than absorbed.

This second script drives the engine over a **worked example with illustrative
numbers** — not paper data — in which reading each method on its own support
reverses the ranking, and checks the audit separates the two readings.
`src/applicability_audit/README.md` documents the five sets and the four layers.

## Verified outputs

Everything in `results/` is a small CSV, JSON or Markdown file derived from the
study's own frozen records. No raw predictions, no annotations, no imagery.

`provenance/RELEASE_MANIFEST.json` maps every published file to the frozen
artifact it came from, that artifact's SHA-256, and the transformation applied —
`none (byte-identical copy)` for the released records, a stated reshape for the
derived tables. `provenance/MANIFEST.sha256` covers the tree:

```bash
sha256sum -c provenance/MANIFEST.sha256
```

`provenance/frozen_records/` holds the protocol, census, eligibility ledger,
results and their independent verifications, released verbatim.

## Datasets and checkpoints

**None ship with this repository.** MOT17, MOT20 and BDD100K remain with their
own distributors under their own terms; detector and re-identification weights
are obtained from their own releases. `docs/DATASETS.md` says what you need for
each level of reproduction, and `metadata/external_assets.csv` pins the SHA-256
of each asset where the frozen record fixes it, so you can confirm you got the
same file.

One caveat is stated rather than left to inference: the study's MOT20 copy
reached it through a verified mirror. Structural verification passed; byte
identity to an official MOT20 archive is not established.

## Provenance and reproducibility

[docs/REPRODUCIBILITY.md](docs/REPRODUCIBILITY.md) describes three levels:
offline verification (seconds, no data), re-deriving the audit from tracker
outputs (hours, needs corpora), and re-running the one executed MOT20 cell (needs
corpus, checkpoints and a GPU).

The offline path verifies that the released logic produces the released numbers
and that they are internally consistent. It is not an independent
re-measurement — level 2 is.

Prospective execution is guarded in code rather than by convention:
authorization binds to `(dataset, pipeline, run_id)` simultaneously, a MOT17
marker can never license a MOT20 run, run identifiers are single-use, and the
guard refuses if a forbidden checkpoint is reachable from the sandbox. There is
no environment-variable bypass.

[docs/PROVENANCE_FIELDS.md](docs/PROVENANCE_FIELDS.md) is the reader's guide to
the vocabulary — what `PROSPECTIVE_OUTCOME_UNSEEN_AT_V9_FREEZE`,
`STRUCTURALLY_UNDEFINED`, `MIRROR_TRANSPORT_FALLBACK` and the rest mean, and what
each does and does not license.

## Tests

```bash
python -m pytest tests/ -q
```

No data required: the admission rule, the ordering engine, the materiality rule,
state construction, row identity and the execution guard, plus the applicability
audit's own suite and a release-integrity suite that checks the published tables
against the frozen configuration and the manifest. Counts and the verified
interpreter versions are in `docs/REPRODUCIBILITY.md`.

## Citation

See `CITATION.cff`. The manuscript is in preparation; the venue and DOI will be
filled in if and when they exist.

## Licence

The original work in this repository — the audit implementation, the
verification scripts, the tests, the documentation, and the frozen records and
derived summary tables authored by this study — is released under the **MIT
Licence**. See [LICENSE](LICENSE).

**That licence covers this repository's own contents and nothing else.** No
dataset, checkpoint, tracker implementation or external evaluation tool is
redistributed here, and no licence claim is made over any of them. Each remains
subject to its own licence and terms, which you obtain and accept directly from
its source:

| external asset | where it comes from |
|---|---|
| MOT17, MOT20 | [MOTChallenge](https://motchallenge.net/) |
| BDD100K | [BDD100K](https://bdd-data.berkeley.edu/) |
| KITTI tracking | [KITTI](https://www.cvlibs.net/datasets/kitti/) |
| PoseTrack21 | [PoseTrack21](https://github.com/anDoer/PoseTrack21) (access-gated) |
| NTU RGB+D 60 | [ROSE Lab](https://rose1.ntu.edu.sg/dataset/actionRecognition/) (request-based) |
| JTA, 3DPW | [JTA](https://github.com/fabbrimatteo/JTA-Dataset), [3DPW](https://virtualhumans.mpi-inf.mpg.de/3DPW/) |
| detector and re-identification checkpoints | the upstream releases listed in `metadata/external_assets.csv` |
| the eight tracker pipelines | the repositories and pinned commits in `metadata/upstream_pipelines.csv` |
| TrackEval | [TrackEval](https://github.com/JonathonLuiten/TrackEval) |

The released tables are aggregate counts, fractions, metric values and intervals
derived from those corpora. They contain no image, video, annotation row or
personally identifying material. `docs/DATASETS.md` says what each analysis
would need if you want to re-measure it rather than check it.

## Acknowledgements

No third-party source is vendored here. The audit reads the outputs of eight
tracker pipelines and never patches, imports or wraps them; each is listed with
its pinned commit in `metadata/upstream_pipelines.csv` and carries its own
licence and citation requirements:

ByteTrack · BoT-SORT · OC-SORT · Deep-OC-SORT · Hybrid-SORT · StrongSORT++ ·
SparseTrack

Evaluation used [TrackEval](https://github.com/JonathonLuiten/TrackEval) at
commit `12c8791b`, unmodified. MOT17 and MOT20 are from
[MOTChallenge](https://motchallenge.net/); BDD100K is from
[BDD100K](https://bdd-data.berkeley.edu/); KITTI is from
[the KITTI benchmark](https://www.cvlibs.net/datasets/kitti/). Please cite each
corpus and method you rely on.

# CITATION AND RELATED-WORK NOTES

Style only for the ordering of this material; the factual content of each cited
work is the author's responsibility, and this file does not assert findings on
their behalf.

## The bibliography file to use

`reconcile_20261003/main_v4_docx.bib`,
sha256 `8bc5de9e2e0e1a9f001151d6c7b0932cc04364b956f3e2bb82d12b9905507f50`, 67
entries. The root `main.bib` is one entry short and will break the `luiten2020trackeval`
citation. See `13_V5_REUSE_MAP.md`.

## Cited in v5 main and still needed

Audited systems and their post-processing:
`zhang2022bytetrack`, `cao2023ocsort`, `maggiolino2023deepocsort`,
`maggiolino2023deepocsortarxiv`, `aharon2022botsort`, `yang2024hybridsort`,
`du2023strongsort`, `liu2025sparsetrack`, `zhou2022osnetain`, `ge2021yolox`.

Benchmarks and metrics:
`dendorfer2021motchallenge`, `dendorfer2020mot20`, `sun2022dancetrack`,
`luiten2021hota`, `luiten2020trackeval`, `bernardin2008clear`,
`ristani2016performance`.

Evaluation auditing, leakage and reporting practice:
`maierhein2018rankings`, `maierhein2020bias`, `kalischek2023biasbed`,
`northcutt2021labelerrors`, `recht2019imagenet`, `kapoor2023leakage`,
`zendel2017cvdata`, `kovatchev2024transparency`, `yu2024rethinking`,
`hu2026pooled`, `gebru2021datasheets`, `mitchell2019modelcards`.

Statistical and resampling background:
`field2007bootstrapping`, `little2019missing`.

## New citations v6 should add

- **DanceTrack as a population.** `sun2022dancetrack` is already in the bib and
  cited in v5 main. v6 needs it in the setup section with its validation-split
  size, and the dataset's own characterisation of uniform appearance and diverse
  motion is the reason the four trackers behave differently here.
- **Metric decomposition.** The point that DetA and AssA are factors of HOTA is
  attributable to `luiten2021hota` and should be cited where the dependence
  caveat is stated, not left as a bare assertion.
- **Gaussian-process smoothing in trackers.** `du2023strongsort` is the source of
  GSI, already cited. Cite it again where the controlled GSI arm is introduced, so
  the reader knows the operator is theirs and the application is ours.
- `ghosh2026evalcards` and `maierhein2024metrics` sit in the bib uncited. Both
  bear on reporting practice and belong in the Discussion paragraph on prediction
  provenance, where v5 currently cites only datasheets, BIAS and model cards.
- `traub2024selective` and `khurshid2024applicability` are uncited and concern
  applicability and selective prediction. They were presumably acquired for the
  skeleton branch. Cite them in Sec. 2.2 only if the eligibility argument actually
  uses them; otherwise let them go with the branch rather than carrying dead
  references.

## Citations that leave with the skeleton branch

`shahroudy2016ntu`, `sun2019hrnet`, `duan2022pyskl`, `doering2022posetrack21`,
`fabbri2018jta`, `geiger2012kitti`, `yu2020bdd100k`, `chib2024trajimpute`,
`gomes2021gapfilling`, `skurowski2021gap`, `yuhai2024recovery`,
`almaleh2025review`, plus the uncited skeleton set listed in
`13_V5_REUSE_MAP.md`.

Two of these need a decision rather than a reflex: `geiger2012kitti` and
`yu2020bdd100k` are tracking datasets, and a reviewer may ask why a paper about
tracking-submission provenance audits neither. The honest answer belongs in
Limitations, as L1's residual: two MOTChallenge-format pedestrian or dancer
populations, no vehicle or multi-camera population. Make that statement in the
limitations section rather than keeping the citations in Related Work with
nothing behind them.

## Related Work ordering

v5's order is defensible and should be kept: evaluation and post-processing
first, because that is where the object of study lives; then benchmark audits,
because that is the genre; then scope. The one change is that v5's Sec. 2.3 on
reconstruction evaluation and missing data no longer has a result behind it in
this paper, so it stops being a subsection and its evaluation-relevant citations
fold into Sec. 2.2.

Do not open Related Work with a general sentence about the growth of the
literature. Open with the specific practice the paper audits: that several
released trackers ship an offline interpolation stage and submit its output.

## Rules

- Name the work, not the category. "Prior work has shown" is not acceptable in
  v6; `maierhein2018rankings` showed a specific thing about ranking stability and
  the sentence should say which.
- Do not cite a work for a claim this project verified itself, and do not cite
  this project's artifacts as if they were literature. The artifact hashes belong
  in the supplement, the citations in the bibliography.
- Every citation added to v6 must be in the `.bib` before the sentence is written.
  A `\cite` to a missing key is how v5 arrived at its one broken reference.

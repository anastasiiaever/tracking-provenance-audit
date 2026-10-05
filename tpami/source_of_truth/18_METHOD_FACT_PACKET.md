> **How to use a fact packet.** Every number below is traceable to
> `05_NUMERIC_LEDGER.csv` and from there to an artifact. Write prose from these
> facts; do not add a number that is not here. If a sentence needs a fact that is
> absent, write `[FACT NEEDED]` and stop. Read
> `04_FORBIDDEN_OR_OBSOLETE_CLAIMS.md` and `30_UNSLOPPING_RULES_FOR_CODEX.md`
> before writing.

# METHOD FACT PACKET

All definitions come from `07_METHOD_DEFINITIONS.md`. That file is normative; this
one says what the Method section must make the reader able to do.

## After reading the Method, a reader must be able to

1. say what R0, R1 and R2 are, and why R1 does not exist for every operator;
2. compute the four admission classes themselves from a submission file, its
   pre-operator file and the ground truth;
3. state what admission does not measure;
4. decide, for a new operator, which of the three audits it permits;
5. check the eligibility of a released configuration for a held-out comparison;
6. reproduce the bootstrap, including the resampling unit and the seed.

## Must be stated explicitly, because it is the most misreadable part

Admission is evaluated from the anchors and from the availability of the
anchor-resolved reference identity. The synthesized row's own coordinates never
enter the predicate. Therefore non-admission is a statement about reference
support, not about geometric plausibility, and TARGET_REFERENCE_ABSENT is a
statement about the reference being silent, not about the tracker being wrong.

Put this in the Method, in the subsection that defines the classes. Do not defer
it to the Discussion.

## Must be stated once and not repeated

- The classes are evaluated as an `if`/`elif` chain in the given priority order
  and partition the synthesized set exactly; counts sum to the synthesized total
  in every table.
- Scoreable ground truth is `mark != 0 AND class == 1`, matching the evaluator's
  own preprocessing.
- The primary gate is 0.50 and the sweep is 0.30 to 0.70 in steps of 0.10;
  gate-stable non-admission is non-admission at every gate and is therefore a
  conservative lower bound.
- R1 is realised by zeroing similarity before assignment, so a withheld row can
  neither match nor displace a match.
- DetA and AssA are factors of HOTA.

## The structural subsection, new in the main text

Table T2 from `06_EVIDENCE_ARCHITECTURE.csv` goes here. The text around it must
make the following four transition types distinguishable, with one audited
example each:

| transition | keys | surviving content | example |
|---|---|---|---|
| row-additive | grow | unchanged | linear DTI, five released deployments and our DanceTrack arm |
| key-additive, content-rewriting | grow | changed | StrongSORT GSI, released and in our DanceTrack arm |
| rewrite-only | unchanged | changed | OC-SORT's GPR stage |
| identity-remapping | may shrink | identity changed | StrongSORT++ AFLink |

The reason no R1 exists for the last three is one sentence: withholding a row
changes the fit, so the surviving rows would change too, and the withheld-row
state is therefore not a subset operation on the submitted file. The released
`states.py` records this in `r1_status_for_non_row_additive`.

## The controlled-arm subsection

Facts to state:

- one operator for four trackers: `dti` and `write_results_score` extracted
  verbatim from ByteTrack's `tools/interpolation.py` at commit `d1bf0191`, with
  `n_min=25`, `n_dti=20`;
- the extracted code hashes identically across the three repositories that ship
  it, so "the same operator" is a checkable statement, not an assertion;
- sensitivity at `n_min=30`: non-admission differs by at most 0.42 points and any
  metric by at most 0.0422;
- the second operator: StrongSORT's `GSInterpolation` with `interval=20`,
  `tau=10`, the values hardcoded at its only upstream call site; AFLink not
  applied;
- one shared detector across the four trackers, which removes detector variation
  as a confound and removes detector diversity at the same time.

## The reproducibility subsection

`BaseTrack._count` is a class attribute and `clear_count()` is never called
upstream, so running a subset of sequences shifts every tracker id by a constant.
Equivalence is therefore defined up to a bijective per-sequence relabelling, with
exact equality of frames, boxes and the track partition and no splits, merges,
missing or extra rows.

State the invariances at the precision at which they were verified, and no
further:

- TrackEval is invariant to arbitrary within-sequence bijective relabelling;
- DTI is invariant modulo the corresponding relabelling;
- STV is verified invariant for the observed order-preserving constant shift
  +424; arbitrary non-order-preserving permutations are not guaranteed, because
  `assign_reference` sorts predictions by tracker id;
- no downstream analysis joins absolute tracker ids across sequences.

## The statistics subsection

- Resampling unit: the sequence cluster, 7 on MOT17, 25 on DanceTrack. Justified
  by the purity of TrackEval's `combine_sequences`, which recomputes pooled
  metrics from per-sequence accumulators without reference to other sequences.
- 10,000 draws, seed 20261003, multiplicity carried by distinct dictionary keys
  `"<sequence>#<slot>"`. Index matrices are hashed.
- Percentile intervals are descriptive. No hypothesis is tested, no p-value is
  computed, and `P(sign differs)` is a bootstrap frequency.
- Sequences are not claimed to be independent.
- The pairwise matrices are exhaustive and their cells are dependent. Say this in
  the Method, once, so no later section has to apologise for it.

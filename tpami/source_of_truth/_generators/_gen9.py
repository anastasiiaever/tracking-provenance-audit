import os
V="<AUDIT_ROOT>/V6_SOURCE_OF_TRUTH"
def w(n,s): open(os.path.join(V,n),"w").write(s.lstrip("\n")); print("  wrote",n)
HEAD = """
> **How to use a fact packet.** Every number below is traceable to
> `05_NUMERIC_LEDGER.csv` and from there to an artifact. Write prose from these
> facts; do not add a number that is not here. If a sentence needs a fact that is
> absent, write `[FACT NEEDED]` and stop. Read
> `04_FORBIDDEN_OR_OBSOLETE_CLAIMS.md` and `30_UNSLOPPING_RULES_FOR_CODEX.md`
> before writing.
"""

w("21_RESULTS_GSI_FACT_PACKET.md", HEAD + r"""
# RESULTS FACT PACKET: A SECOND OPERATOR FAMILY

Population: the same DanceTrack-val 25 sequences and the same four frozen R0
states as the DTI arm.
Operator: StrongSORT's `GSInterpolation`, `interval=20`, `tau=10`, applied by us.
AFLink not applied.
Evidence type: controlled, **post-hoc**. The DTI outcomes were known before this
protocol was written. The protocol was frozen before any GSI output was
inspected: `6ac1b00bd6ef37bfc5c5b7bc416c33ad46c4735d2f0c910cb9c42ea8f31484b8`.
Authoritative artifacts: `D2B_MANIFEST.sha256` =
`6276bff16669a585fbf94cf6eb71b6f3139e1a6ed6fa251eb1d722a6770d9a2f`, 285 of 285;
decomposition in `final_defense_20261004`, `c2fc4b5f…`, 241 of 241.

## The structural result

GSI is key-additive but content-rewriting. Across the four trackers:

| tracker | GSI rows | inserted | surviving rows rewritten | % rewritten |
|---|---|---|---|---|
| ByteTrack | 225,199 | 8,889 | 127,411 | 58.902 |
| OC-SORT | 218,591 | 15,804 | 136,814 | 67.467 |
| Deep-OC-SORT | 218,075 | 14,926 | 123,954 | 61.016 |
| Hybrid-SORT | 228,696 | 13,303 | 122,427 | 56.839 |

Deletions: 0. Tracker-id changes: 0. Rewrite range: 56.839 to 67.467 %.

Because surviving coordinates change, neither STV nor an R1 analogue is defined
for this transition. Withholding rows would change the Gaussian-process fit and
therefore the coordinates of the rows that remain, so the withheld-row state is
not a subset operation on the submitted file.

## The metric and ordering results

20 metric cells: 12 positive, 0 zero, 8 negative, with the same per-tracker
pattern as the DTI arm.

30 exhaustive pairwise cells, 7 cross zero, all surviving 3-decimal and 2-decimal
reporting. The seven are the **same pair-and-metric identities** as the DTI arm:
ByteTrack−Deep-OC-SORT MOTA; ByteTrack−OC-SORT MOTA; Deep-OC-SORT−Hybrid-SORT
HOTA, DetA and MOTA; OC-SORT−Hybrid-SORT DetA and MOTA.
`P(sign differs)` ranges 0.3148 to 0.9365. Appearances: Hybrid-SORT 5,
Deep-OC-SORT 4, OC-SORT 3, ByteTrack 2.

## The decomposition, and why it changes how the arm must be reported

GSI is `LinearInterpolation` followed by `GaussianSmooth`. Splitting it at the
intermediate state L_GSI:

| transition | coordinate rewrites | cells crossing zero |
|---|---|---|
| R0 → L_GSI, linear stage | 0 | 7 of 30 |
| L_GSI → GSI, GP stage | 133,187 to 150,335 rows, 58.24 to 68.77 % | 0 of 30 |
| R0 → GSI, total | as above | 7 of 30 |

Every ordering crossing in this arm is already established by the linear stage.
The Gaussian-process stage adds none.

GSI's linear stage *is* linear gap filling — the same mechanism as the DTI arm.
So the GSI arm is **not an independent second mechanism** for the ordering
result, and the paper must not present it as replication or confirmation. It is a
generality check across operator families that returned a specific and more
interesting answer than a confirmation would have.

## What the GP stage does do

It is not inert, and saying "0 of 30" alone would understate it:

- all 20 metric cells move;
- the GP stage's share of total absolute metric movement has median 0.181 and
  ranges 0.042 to 0.872;
- in 8 of 20 cells the GP delta opposes the linear delta.

So the GP stage changes the evaluated state and the reported scores measurably,
and on this population it does not change any pairwise ordering. Both halves
belong in the text; either alone is misleading.

## How to frame the arm

One honest sentence: the second operator family was chosen to test whether the
composition and ordering findings depend on linear interpolation specifically,
and the decomposition showed that within GSI they depend on exactly that.

Do not write: independent confirmation, second independent mechanism,
replication, pre-specified, or confirmatory.
Do not write that GSI reproduces released DanceTrack practice. Upstream
StrongSORT has no DanceTrack entry in `opts.py` at all.

## The released structural cases, for contrast

Both are on MOT17 and both are released, not ours.

**OC-SORT GPR, rewrite-only.** G0 and G2 both have 45,927 rows; 0 inserted, 0
deleted. 52 rows change by more than 1e-6 px, 0.1132 %; 2,622 rows differ at exact
floating-point equality, in x and y only, by 8.9e-12 to 1.7e-05 px with median
3.69e-09; no row changes by more than 0.001 px; w and h are bit-identical in all
45,927. The three-decimal summary file is byte-identical between states, and the
full-precision detailed output differs in 197 LocA-family fields. All five
reported metrics change by 0.0000.

State the 1e-6 px criterion whenever the 52 appears. Without it, a reader who
recomputes at exact equality gets 2,622 and concludes the paper is wrong. The
earlier figure of 212 was a two-decimal rounding-boundary artifact: counting at
0, 1, 2, 3, 6 and 9 decimals gives 59, 239, 212, 69, 87 and 2,255, a non-monotone
series, against 2,622 at exact equality.

**StrongSORT++ AFLink and GSI, released.** AFLink changes the identity of 1,316
rows across 29 remappings, reduces distinct identities from 435 to 406, and loses
one row, 46,914 to 46,913. GSI then adds 3,184 rows, drops none, and rewrites
46,866 of 46,913 surviving coordinates, 99.8998 %. The GSI stage moves HOTA
+1.220, DetA +1.278, AssA +1.211, IDF1 +0.830, MOTA +1.561. The base tracker
output was written but not scored, so the AFLink comparison is structural only.
Containment of the pre-GSI state in the post-GSI state holds on identity keys and
fails on row content.

Note the state-naming collision with v5 before writing either of these; see
`04_FORBIDDEN_OR_OBSOLETE_CLAIMS.md`.
""")

w("22_RESULTS_MOT20_FACT_PACKET.md", HEAD + r"""
# RESULTS FACT PACKET: MOT20

Population: MOT20 validation half, 4 sequences, 4,463 frames.
Evidence type: released-deployment audit. The eligibility census was
pre-specified and frozen before any MOT17 execution.
Authoritative artifacts: Step 9 `B2_mot20_gate_summary.csv` and
`C3_gate_stability_summary.csv`; v5 supplement Secs. S6 and S7.

## The eligibility census

Seven configurations were pre-specified. Of those:

- 1 is eligible for the held-out comparison;
- 5 fail clause (i), detector-training overlap;
- 1 is unresolved under clause (ii).

The point this census makes is the one the Discussion needs: public code and
public weights do not establish that a held-out comparison is available. Running
an ablation on MOT20 validation frames does not make them held out if the selected
detector checkpoint was trained on them.

## The eligible cell: Deep-OC-SORT's released DTI, `n_min=30`

| quantity | value |
|---|---|
| synthesized rows | 34,814 |
| non-admitted at gate 0.50 | 8,751 |
| non-admitted % at gate 0.50 | 25.1364 |
| gate-stable non-admitted | 6,631 |
| gate-stable non-admitted % | 19.046935 |
| TARGET_REFERENCE_ABSENT, every gate | 0 |

Across the gate sweep:

| gate | non-admitted | % |
|---|---|---|
| 0.30 | 6,768 | 19.4405 |
| 0.40 | 7,612 | 21.8648 |
| 0.50 | 8,751 | 25.1364 |
| 0.60 | 11,793 | 33.8743 |
| 0.70 | 18,891 | 54.2627 |

**The gate-stable figure is available and must be reported.** It was present in
v5 and was dropped from an intermediate report by a code filter that selected
`population == "mot17"`. D1B.1 restored it. Any v6 table that gives gate-stable
non-admission for MOT17 and leaves the MOT20 cell blank is reproducing a bug.

## What this arm can and cannot support

It supports a composition check on a second population: one deployment, one
operator, 34,814 added rows, a quarter of them non-admitted at the primary gate
and nearly a fifth at every gate.

It supports no ordering analysis. One deployment yields no pair. Do not count
MOT20 toward the ordering evidence, and do not present it as a second population
for the ordering result; DanceTrack is that.

## Verification

One MOT20 execution was authorised and run. A separate implementation recomputed
its counts, admission fractions and metrics from the stored output files, deriving
the set arithmetic itself rather than reading the execution record's summary
values, and matched. The R1 writer was checked on all 2,223,712 MOT20
coordinates: every written value equals the source rounded to two decimals,
97.11 % are already bit-identical, and the maximum deviation is 0.005, the
half-step of two-decimal rendering. Coordinates are read by the evaluator, so this
rendering is visible to it. The same writer reproduces the frozen MOT17 R1 files
exactly.
""")

w("23_DISCUSSION_FACT_PACKET.md", HEAD + r"""
# DISCUSSION FACT PACKET

v5's Discussion is five paragraphs and its structure holds. Keep the order; change
what the evidence now supports.

## 1. Composition and metric change answer different questions — KEEP, EXTEND

v5's point: the non-admitted fraction of the synthesized set describes what the
operator added; its fraction of the submitted set describes their share of the
benchmark input; a metric change measures the net effect on evaluation. A score
gain alone does not describe the composition of the added rows.

New evidence: on MOT17 all 25 deltas were positive, which left open the reading
that non-admission and metric gain travel together. Under one common operator on
DanceTrack, 12 deltas are positive and 8 negative: OC-SORT and Deep-OC-SORT rise
on all five metrics, while ByteTrack and Hybrid-SORT fall on four of five and
rise only on AssA. Substantial non-admission occurs in both directions.

Both fractions are now available on two populations with different operators, so
state the two-denominator point with the DanceTrack inserted-fraction numbers,
3.79 to 6.93 % of the submitted file against 42.03 to 68.46 % of the added set.

## 2. Comparisons depend on the evaluated state — KEEP, CORRECT

v5's point stands: admission composition does not determine which pairwise
comparisons change, and a small margin permits a reversal without predicting one.

v5 supported it with an ordering coincidence: Hybrid-SORT had the highest
non-admitted fraction and appeared in four of five changed comparisons,
Deep-OC-SORT the lowest and three. **That coincidence does not replicate.** On
DanceTrack, ByteTrack has the highest non-admitted fraction, 68.46 %, and the
fewest appearances in crossing cells, 2; Deep-OC-SORT has the lowest, 42.03 %,
and four.

This strengthens v5's own conclusion rather than weakening it, and it should be
reported that way: the second population shows the composition-to-ordering
association was a small-sample coincidence, which is precisely why composition
cannot be read off a score change or vice versa.

Margin-size facts for both populations:

- MOT17: crossing cells' initial absolute margins 0.5104 to 1.4567; 17 of 45
  unchanged cells at or below 1.4567; smallest unchanged 0.1869.
- DanceTrack: crossing cells 0.6581 to 2.2203; 6 of 23 unchanged cells at or
  below 2.2203; smallest unchanged 0.2170.

## 3. Eligibility belongs to a released configuration — KEEP

v5's paragraph is correct and needs no new evidence. The MOT20 census is its
support: 1 eligible of 7, 5 failing through detector-training overlap. Keep the
sentence that running an ablation on MOT20 validation frames does not make them
held out if the detector checkpoint was trained on them.

Add one sentence from the DanceTrack arm: training-split disjointness and
selection provenance are separate questions, and on DanceTrack the first is
satisfied for all four trackers while the second is unresolved for all four at the
hyperparameter level. A single "held out" label would hide that.

## 4. Reporting prediction provenance — KEEP

v5's recommendation stands: a tracking release should retain raw output,
submitted output and the transformation settings together. Related practices:
datasheets, the BIAS guideline, model cards; `ghosh2026evalcards` and
`maierhein2024metrics` are in the bibliography and belong here too.

The DanceTrack arm adds a concrete argument for it. Holding the operator fixed
across four trackers required extracting the operator from source and verifying
that the extraction hashes identically across the three repositories that ship it.
That work would have been unnecessary had the releases recorded their
transformation settings alongside the submitted file.

## 5. What the arms do and do not share — REWRITE

v5's final paragraph contrasted the tracking arm with the skeleton arm. The
skeleton arm leaves the narrative, so this paragraph is rewritten around the two
contrasts v6 actually has.

**Contrast one: which audit an operator permits.** Row-additive transitions admit
a row-level decomposition and a withheld-row diagnostic state. Transitions that
rewrite surviving rows admit neither, because withholding a row changes the fit.
This is a structural property, so a reader can determine it from the operator
without running anything.

**Contrast two, the boundary case.** OC-SORT's GPR stage rewrites 52 rows above
1e-6 px and moves all five reported metrics by 0.0000. This bounds the paper's own
claim: a change to the evaluated state is necessary for a reported-score effect
and is not sufficient. A paper that argued only that post-processing changes the
state would be making a weaker point than this one, and the counterexample is what
shows the difference.

## 6. What admission does not measure — NEW PARAGRAPH

The row-local support measurement belongs in the Discussion as well as the
Results, because it is the limit of the diagnostic the paper proposes. Between
62.04 and 73.54 % of non-admitted DanceTrack rows reach maximum IoU 0.5 against
some scoreable identity, and 3,448 of 3,451 TARGET_REFERENCE_ABSENT rows have
another identity overlapping the box while 0 of 3,451 have the intended one.
Admission asks whether the reference supports the row's intended identity at that
frame. On a population of heavily overlapping targets, that question and "is there
a target here" come apart almost completely.

## Forbidden in the Discussion

Any causal statement from non-admission to metric change; "robust"; "significant";
"independent confirmation"; "breadth is closed"; a closing paragraph that
synthesises the preceding ones. The Discussion should end on the strongest
remaining substantive point, not on a summary.
""")

w("24_LIMITATIONS_FACT_PACKET.md", HEAD + r"""
# LIMITATIONS FACT PACKET

Full ledger with status labels: `08_LIMITATIONS_LEDGER.md`. This packet says what
the section must say and in what order.

## Order

Put the limitation whose status changed first, because a reader of v5 will look
for it. Then the ones that bound the new arm. Then the structural ones. Then
population scope.

1. Single-population ordering evidence — REDUCED
2. The DanceTrack operator is ours — OPEN
3. Operator-family breadth, and what the two controlled operators share — REDUCED
4. The GSI arm is post-hoc — by design
5. Shared detector on DanceTrack — OPEN
6. Selection provenance — OPEN
7. Dependence inside the ordering matrices, and no statistical test — by design
8. Sequence independence is not established — OPEN
9. Admission is reference-side only — OPEN, and quantified
10. Rewriting operators admit no row-level audit — by design
11. Eligibility rules exclude most released systems — OPEN
12. Population sizes — OPEN

## Required wording on the first entry

Allowed: "the principal single-population limitation is substantially reduced."

Forbidden: "breadth is closed", "generality is established", "the effect
universally generalises", or any phrasing that implies the question is settled.

Supporting facts: v5's ordering evidence was 50 cells on one population. v6 has
50 cells on MOT17-val across five released deployments, 30 on DanceTrack-val
across four controlled trackers under one common operator, and 30 more under a
second operator family, over 25 sequence-level clusters.

Residual, which must be stated in the same breath: two populations, both
MOTChallenge-format pedestrian or dancer video; no vehicle, aerial or
multi-camera population; MOT20 contributes composition and no ordering pair.

## The entry that must not read as a defence

Entry 9. Write it as a measurement with numbers: 62.04 to 73.54 % of non-admitted
rows reach maximum IoU 0.5; 1.78 to 2.61 % of admitted rows do not; 3,448 of
3,451 REFERENCE_ABSENT rows have another identity overlapping the box. Then state
what admission measures instead. Do not preface it with a reassurance.

## The entry most likely to be written too softly

Entry 3. The two controlled DanceTrack operators share a linear interpolation
stage, and D2C established that every ordering crossing in the GSI arm arises at
that stage. So the second operator arm does not provide independent mechanistic
support for the ordering result. Say that directly. A reader who discovers it
after the fact will trust nothing else in the section.

## The entry a reviewer will raise first

Entry 2. No released DanceTrack submission is audited; the operator is ours. State
it without softening, and state what the arm therefore does establish: what a
common post-processing operator does to a controlled comparison.

## Do not

- claim any limitation is closed that is labelled OPEN or REDUCED in the ledger;
- apply a multiplicity correction and present it as addressing entry 7; none is
  appropriate to an exhaustive dependent census, and the right response is to
  stop reading the counts as trials;
- hedge entries 7, 10 and 12 into vagueness; each has a precise statement
  available.
""")

w("25_CONCLUSION_FACT_PACKET.md", HEAD + r"""
# CONCLUSION FACT PACKET

Target: one short paragraph, or at most two. The WSOL reference merges its
discussion and conclusion into roughly 224 words and ends by naming where the
problem it studied recurs, not by summarising itself.

## What the conclusion may contain

- One restatement of the central claim, in different words from the abstract and
  the introduction: a benchmark score characterises an evaluated output state, and
  which audit of that state is available is determined by the structure of the
  transition that produced it.
- One sentence naming what the paper measured, with no numbers or at most one.
- One sentence on what a release would have to record for the audit to be
  unnecessary: raw output, submitted output, and the transformation settings
  together.

## What the conclusion must not contain

- a list of the paper's results;
- any number that has not already appeared in the text;
- a new claim of any kind;
- "future work will", "we hope that", "as benchmarks continue to";
- the words "in conclusion", "ultimately", "in the end";
- a resolution that balances competing considerations;
- a sentence about the importance of the problem.

## The ending

End on where the problem recurs rather than on the paper. The honest candidates,
in order of preference:

1. Any benchmark whose submission format cannot distinguish a produced row from an
   added one has this property, and the format is shared across the MOTChallenge
   family.
2. The boundary case: an operator that rewrote the evaluated state and moved no
   reported metric is what distinguishes a claim about states from a claim about
   scores.

Do not append a final sentence after either of these. The conclusion ends one
sentence earlier than it feels like it should.
""")

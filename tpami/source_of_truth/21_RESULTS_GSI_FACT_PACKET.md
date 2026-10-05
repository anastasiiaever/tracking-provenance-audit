> **How to use a fact packet.** Every number below is traceable to
> `05_NUMERIC_LEDGER.csv` and from there to an artifact. Write prose from these
> facts; do not add a number that is not here. If a sentence needs a fact that is
> absent, write `[FACT NEEDED]` and stop. Read
> `04_FORBIDDEN_OR_OBSOLETE_CLAIMS.md` and `30_UNSLOPPING_RULES_FOR_CODEX.md`
> before writing.

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
| OC-SORT | 218,591 | 15,804 | 136,814 | 67.4668 |
| Deep-OC-SORT | 218,075 | 14,926 | 123,954 | 61.0163 |
| Hybrid-SORT | 228,696 | 13,303 | 122,427 | 56.8389 |

Deletions: 0. Tracker-id changes: 0. Rewrite range: 56.8389 to 67.4668 %.

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
| L_GSI → GSI, GP stage | 133,187 to 150,335 rows, 58.2376 to 68.7746 % | 0 of 30 |
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
- the GP stage's share of total absolute metric movement has median 0.1812 and
  ranges 0.0421 to 0.8722;
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

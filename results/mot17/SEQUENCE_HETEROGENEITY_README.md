# Sequence-level heterogeneity of the five aggregate ordering changes

STATUS: **POST-HOC / DESCRIPTIVE DIAGNOSTIC.**

## What is authoritative

The five ordering changes in `ordering_matrix.csv` are pooled-corpus comparisons
over the whole MOT17 validation half. Those aggregate comparisons are the reported
result and remain authoritative.

The per-sequence values here are descriptive diagnostics. They are read from the
per-sequence evaluator outputs that already existed when the aggregate results
were produced. No tracker and no evaluator was re-run to produce this table.

## This is not a decomposition

HOTA, DetA, AssA and IDF1 are alpha-averaged or corpus-level ratios and are **not
additive across sequences**. MOTA is a ratio of summable counts, not a sum. The
aggregate cannot be reconstructed by averaging the seven sequence scores, and no
sequence row is a component of the aggregate.

A sequence that does not change relation therefore does not contradict the
aggregate change. The two quantities are computed over different units.

## Result

| # | comparison | metric | same-direction sequence changes |
|---|---|---|---|
| 1 | BoT-SORT vs Deep-OC-SORT | IDF1 | 0 / 7 |
| 2 | Deep-OC-SORT vs Hybrid-SORT | DetA | 2 / 7 |
| 3 | Deep-OC-SORT vs Hybrid-SORT | MOTA | 2 / 7 |
| 4 | Hybrid-SORT vs OC-SORT | HOTA | 0 / 7 |
| 5 | Hybrid-SORT vs OC-SORT | MOTA | 0 / 7 |

No sequence changed relation in the direction opposite to its aggregate, and no
tie was created or broken. Sequence-level relations are heterogeneous in sign at
both `R0` and `R2`; the per-sequence counts and margins are in
`sequence_ordering_heterogeneity_summary.csv`, and the 35 underlying rows are in
`sequence_ordering_heterogeneity.csv`.

The relation rule is the frozen engine's own `ordering.relation` with its default
`tol = 0.0`, so a tie requires exact equality. No tolerance was introduced.

## Scope of the claim

This table reports **sequence-level heterogeneity and consistency** of the five
aggregate ordering changes. It makes no statistical significance claim, no
majority-vote interpretation, and no claim of robustness across sequences.

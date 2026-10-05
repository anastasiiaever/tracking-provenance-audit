> **How to use a fact packet.** Every number below is traceable to
> `05_NUMERIC_LEDGER.csv` and from there to an artifact. Write prose from these
> facts; do not add a number that is not here. If a sentence needs a fact that is
> absent, write `[FACT NEEDED]` and stop. Read
> `04_FORBIDDEN_OR_OBSOLETE_CLAIMS.md` and `30_UNSLOPPING_RULES_FOR_CODEX.md`
> before writing.

# RESULTS FACT PACKET: MOT17 RELEASED DEPLOYMENTS

Population: MOT17 validation half, 7 sequences, 2,652 frames.
Evidence type: released-deployment audit, pre-specified, retrospective.
Authoritative artifacts: `posthoc_composition_20261003/results/` with
`MANIFEST.sha256` = `829bd398f2ac264f7d393c4219e291406554dabe7503007cc231cfd964148b77`,
45 of 45 verified, plus the Step 9.1 corrections.

## Composition at the primary gate, 0.50

| deployment | synthesized | U | ID | ABS | ADM | non-admitted | % | gate-stable | % |
|---|---|---|---|---|---|---|---|---|---|
| Deep-OC-SORT | 2,960 | 570 | 286 | 0 | 2,104 | 856 | 28.9189 | 694 | 23.4459 |
| OC-SORT | 2,622 | 408 | 375 | 0 | 1,839 | 783 | 29.8627 | 666 | 25.4005 |
| BoT-SORT | 2,090 | 576 | 227 | 0 | 1,287 | 803 | 38.4211 | 634 | 30.3349 |
| ByteTrack | 2,072 | 604 | 244 | 0 | 1,224 | 848 | 40.9266 | 694 | 33.4942 |
| Hybrid-SORT | 3,023 | 1,266 | 216 | 0 | 1,541 | 1,482 | 49.0241 | 1,327 | 43.8968 |

Totals: 12,767 synthesized rows across the five deployments.
Ranges, each with its own quantity named: synthesized rows per deployment 2,072
to 3,023; admitted rows per deployment 1,224 to 2,104; non-admission 28.92 to
49.02 %; gate-stable non-admission 23.45 to 43.90 %.

The ABS column is zero for every deployment at every gate in the sweep. This is
not a null result to pass over: it is the fact that makes the DanceTrack ABS
column meaningful, and the reason is the reference, not the tracker. MOT17's
scoreable ground truth has no interior gaps in any of its 339 tracks.

## Metric change

All 25 cells, five deployments by five metrics, are positive from R0 to R2.
Values per state are in v5 Table 3 and in the frozen detailed evaluator output.

## Ordering

50 exhaustive pairwise metric cells, 5 cross zero. Named:

| pair | metric | R0 margin | R2 margin | 3dp | 2dp | P(sign differs) |
|---|---|---|---|---|---|---|
| BoT-SORT − Deep-OC-SORT | IDF1 | +0.5104 | −0.2033 | survives | survives | 0.3585 |
| Deep-OC-SORT − Hybrid-SORT | DetA | −1.2037 | +0.2117 | survives | survives | 0.5532 |
| Deep-OC-SORT − Hybrid-SORT | MOTA | −0.8387 | +1.3490 | survives | survives | 0.5859 |
| OC-SORT − Hybrid-SORT | HOTA | −0.5761 | +0.1796 | survives | survives | 0.4332 |
| OC-SORT − Hybrid-SORT | MOTA | −1.4567 | +0.2227 | survives | survives | 0.4260 |

Bootstrap: 33 of 50 percentile intervals exclude zero at R0, 28 of 50 at R2, and
32 of 50 for the change in margin.

## The margin-size observation and its limit

The five crossing cells had initial absolute margins between 0.5104 and 1.4567,
comparable to the post-processing gains. But 17 of the 45 unchanged cells also
had initial margins at or below 1.4567, the smallest being 0.1869. A small margin
permits a reversal and does not predict one.

Appearances in crossing cells: Hybrid-SORT 4, Deep-OC-SORT 3, OC-SORT 2,
BoT-SORT 1. Hybrid-SORT has the highest non-admitted fraction and the most
appearances; Deep-OC-SORT has the lowest and three appearances. With four of five
deployments involved and five cells in total, this is an ordering coincidence in a
very small sample. Report it as such; see the DanceTrack packet, where it does not
replicate.

## Verification, with the required correction

Re-execution reconstructed the 12,767-row synthesized population with all 12,767
identities unique, and reproduced every available frozen count at the
sequence-by-class level: 105 of 105 cells for MOT17, 130 of 130 including MOT20.

No frozen per-row class table exists, so per-row agreement against the frozen
artifact was not checked and must not be claimed. v5's Verification sentence must be
corrected, and in v6 it lands with the MOT17 composition rather than in a
separate Verification section. Source: `step9_1/STEP9_REPORT_CORRECTIONS.md`.

Other verification facts from v5 Sec. 7 that remain correct: one authorised MOT20
execution, recomputed independently from stored output files; the MOT17 ordering
matrix recomputed from full-precision output with no mismatches; the R1 writer
checked on all 2,223,712 MOT20 coordinates, 97.11 % bit-identical and maximum
deviation 0.005, the half-step of two-decimal rendering.

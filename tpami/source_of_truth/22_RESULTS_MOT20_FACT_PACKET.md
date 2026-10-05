> **How to use a fact packet.** Every number below is traceable to
> `05_NUMERIC_LEDGER.csv` and from there to an artifact. Write prose from these
> facts; do not add a number that is not here. If a sentence needs a fact that is
> absent, write `[FACT NEEDED]` and stop. Read
> `04_FORBIDDEN_OR_OBSOLETE_CLAIMS.md` and `30_UNSLOPPING_RULES_FOR_CODEX.md`
> before writing.

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
| gate-stable non-admitted % | 19.0469 |
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

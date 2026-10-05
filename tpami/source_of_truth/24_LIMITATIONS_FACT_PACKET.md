> **How to use a fact packet.** Every number below is traceable to
> `05_NUMERIC_LEDGER.csv` and from there to an artifact. Write prose from these
> facts; do not add a number that is not here. If a sentence needs a fact that is
> absent, write `[FACT NEEDED]` and stop. Read
> `04_FORBIDDEN_OR_OBSOLETE_CLAIMS.md` and `30_UNSLOPPING_RULES_FOR_CODEX.md`
> before writing.

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

Entry 9. Write it as a measurement with numbers: 62.0388 to 73.5409 % of non-admitted
rows reach maximum IoU 0.5; 1.7849 to 2.6080 % of admitted rows do not; 3,448 of
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

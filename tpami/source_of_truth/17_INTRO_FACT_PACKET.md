> **How to use a fact packet.** Every number below is traceable to
> `05_NUMERIC_LEDGER.csv` and from there to an artifact. Write prose from these
> facts; do not add a number that is not here. If a sentence needs a fact that is
> absent, write `[FACT NEEDED]` and stop. Read
> `04_FORBIDDEN_OR_OBSOLETE_CLAIMS.md` and `30_UNSLOPPING_RULES_FOR_CODEX.md`
> before writing.

# INTRODUCTION FACT PACKET

Target: 5 to 7 paragraphs. v5's introduction is lines 129 to 156 and is being
rewritten, because the contribution set changed.

## Opening

Open on the concrete practice. The specific, checkable facts available for an
opening paragraph:

- The MOTChallenge submission format is ten columns per row and carries no field
  distinguishing a tracker-produced row from one added afterwards
  (`dendorfer2021motchallenge`; TrackEval, `luiten2020trackeval`).
- ByteTrack, OC-SORT, Deep-OC-SORT, BoT-SORT, Hybrid-SORT and StrongSORT++ each
  ship an offline post-processing stage, and five of them apply it on the path
  that produces the submitted file.
- On MOT17-val, each deployment adds 2,072 to 3,023 rows, 12,767 synthesized rows
  in total across the five deployments. Of those added rows, 1,224 to 2,104 per
  deployment are admitted; the two ranges are different quantities and must not
  be combined into one.

## The problem statement

Two things are true at once and the introduction must hold both:

- the added rows are not errors, and the audit does not claim they are;
- the score that is reported and compared is computed on a file that contains
  them.

So the question is not whether post-processing is legitimate. It is what a reader
of a benchmark table can determine about the state that table scored.

## What the paper contributes

1. A definition of the evaluated state and of scoreable-target admission, with
   the four classes and their exact partition.
2. A statement of which audit each operator structure permits: row-additive
   transitions admit a row-level decomposition and a withheld-row diagnostic
   state; transitions that rewrite surviving rows admit neither.
3. An estimand-eligibility condition for when a held-out comparison is available
   from a released configuration, applied as a census: on MOT20, 1 of 7
   pre-specified configurations is eligible, 5 fail through detector-training
   overlap, 1 is unresolved.
4. A released-deployment audit on MOT17-val, 7 sequences and 2,652 frames, and the
   eligible MOT20 cell, 4 sequences and 4,463 frames.
5. A controlled audit on DanceTrack-val, 25 sequences and 25,508 frames, in which
   one operator is applied by us to four trackers, so tracker differences cannot
   be attributed to differences in post-processing.
6. Two bounding results: an operator that rewrites the state and moves no metric,
   and a measurement showing that non-admission does not mean geometric
   implausibility.

## The honest framing of the second population

The DanceTrack arm is ours, not an author's. Say so in the introduction, not only
in the limitations. The sentence a reviewer needs is that no released DanceTrack
submission is audited and that the arm exists to hold the operator fixed.

## What must not appear in the introduction

- a contribution list that is then restated at the head of every results section;
- "to the best of our knowledge";
- a claim that the ordering results are statistically significant;
- the words "independent confirmation" for the GSI arm;
- a general observation about the growth of the tracking literature.

## Available numbers

See `05_NUMERIC_LEDGER.csv`. For the introduction the useful ones are the
population sizes (7 / 2,652; 4 / 4,463; 25 / 25,508), the synthesized totals
(12,767; 34,814; 8,511 to 15,103), the non-admission ranges, and the crossing
counts with their denominators (5 of 50; 7 of 30).

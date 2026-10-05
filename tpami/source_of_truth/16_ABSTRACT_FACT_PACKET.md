> **How to use a fact packet.** Every number below is traceable to
> `05_NUMERIC_LEDGER.csv` and from there to an artifact. Write prose from these
> facts; do not add a number that is not here. If a sentence needs a fact that is
> absent, write `[FACT NEEDED]` and stop. Read
> `04_FORBIDDEN_OR_OBSOLETE_CLAIMS.md` and `30_UNSLOPPING_RULES_FOR_CODEX.md`
> before writing.

# ABSTRACT FACT PACKET

Target: one paragraph, roughly 170 to 200 words. The WSOL reference abstract is
179 words in 8 sentences with no numerals; see `29_WSOL_STYLE_OBSERVATIONS.md`.
This paper's abstract should carry a small number of numerals, because the
quantities are the result, but it does not need more than three or four.

## The one statement the abstract exists to make

A benchmark score characterises an evaluated output state, not a tracker in
isolation. For several widely used trackers the submitted file contains rows that
the tracker did not produce, and which audit a reader can perform on that file
depends on the structure of the transition that produced it.

## Facts available, in descending order of priority

1. Five released MOT17 deployments add rows that fail scoreable-target admission
   in 28.92 to 49.02 % of the added set at the primary gate, and in 23.45 to
   43.90 % at every gate in the sweep.
2. All 25 metric deltas are positive; 5 of the 50 exhaustive pairwise metric
   cells change sign, and all five survive 2-decimal reporting.
3. Under one common operator applied by us to four trackers on DanceTrack,
   non-admission is 42.03 to 68.46 %, 7 of 30 pairwise cells change sign, and the
   metric deltas go both ways: 12 positive and 8 negative.
4. A second operator family reproduces the same 7 cells, but its own
   interpolation stage accounts for all of them.
5. One released operator rewrites the evaluated state and moves all five reported
   metrics by 0.0000.

## Sentence-level guidance

- Open on the practice, not on the field. The first sentence should let a reader
  who knows MOTChallenge recognise the thing being audited.
- The four-class admission decomposition needs naming once, without listing all
  four classes in the abstract.
- The abstract must not promise generality. Two populations, four controlled
  trackers, two operator families.
- Do not write "we propose a framework" as the opening move; the framework exists
  to make a measurement possible, and the measurement is the result.
- Do not end on an outlook sentence. The last sentence should be the strongest
  remaining fact, most likely the boundary case or the bidirectional metric
  result.

## Forbidden in the abstract

"significant", "robust", "independent confirmation", "universally", "we are the
first", any count presented as a rate, and the word "reveal".

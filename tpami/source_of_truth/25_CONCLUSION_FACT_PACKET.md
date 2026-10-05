> **How to use a fact packet.** Every number below is traceable to
> `05_NUMERIC_LEDGER.csv` and from there to an artifact. Write prose from these
> facts; do not add a number that is not here. If a sentence needs a fact that is
> absent, write `[FACT NEEDED]` and stop. Read
> `04_FORBIDDEN_OR_OBSOLETE_CLAIMS.md` and `30_UNSLOPPING_RULES_FOR_CODEX.md`
> before writing.

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

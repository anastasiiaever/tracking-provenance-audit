# UNSLOPPING RULES FOR CODEX

Derived from the two installed skills, read from disk rather than from memory.
Paths and hashes are in `28_WRITING_STYLE_REFERENCE.md`.

## Source A, primary: `anti-ai-tells`

A discourse-level skill based on StoryScope (Russell et al., arXiv:2604.03136).
Its central mechanism: a language model **over-determines meaning**, stating the
inference instead of leaving it to the reader.

The skill contains nine rules and **scopes itself explicitly**: for a scientific
paper, apply only rules 1, 2, 3 and 8. The remaining rules — addressing the
reader directly, breaking chronology, sensory openings, ambiguous endings,
escalating intensity — are written for essays and are counter-productive in an
IEEE-format paper. That scoping is the skill's own instruction and is adopted
here unchanged.

### Rule 1, applicable: do not explain your own point twice

The strongest single signal in the underlying study. In a paper it appears as a
"what this means" paragraph, a summary at the end of every subsection, a final
synthesis, and connectives such as "this is important because", "in other words",
"the key takeaway is".

For v6: state each claim **once**, in one place. After that, only new facts.
Delete a closing summary paragraph by default; a section usually ends one
paragraph earlier than it feels like it should.

### Rule 2, applicable: names, not allusions

Humans name specific works and numbers roughly twice as often; models drift to
vague attribution. In a paper this is "some studies show", "prior work has
demonstrated", "several trackers", "recent years".

For v6: name the tracker, the commit, the dataset, the section, the number. We
have identifiers for everything; there is no reason to write "several
deployments" when the count and the names are in `05_NUMERIC_LEDGER.csv`. Where
a value genuinely is not available, write `[FACT NEEDED]`.

### Rule 3, applicable: do not level the structure

Models produce three roughly equal items, an answer for every objection, and
symmetric subheadings with nothing left hanging.

For v6: let sections differ in length according to their evidence. The MOT17
released audit and the DanceTrack controlled arm do not deserve equal space just
because they are both results. Leave the genuinely unresolved things unresolved
and say so — Deep-OC-SORT checkpoint selection, hyperparameter provenance for all
four, the dependence of the ordering matrix.

### Rule 8, applicable: do not take the first phrasing

The first structure, analogy or heading that comes to mind is the centre of the
distribution. Headings of the form "X: Why Y" and openings that begin from a
broad generalisation are the obvious cases.

For v6: when a sentence arrives fully formed and smooth, write the second
version and compare.

### Rules 4, 5, 6, 7, 9: out of scope here

Broken chronology, sensory openings, second-person address, deliberately
ambiguous endings, and rising intensity. The skill itself excludes them for
scientific writing. Do not apply them.

## Source B, secondary: `writing-anti-ai`

A lexical and phrase-level skill based on Wikipedia's "Signs of AI writing".
Take its concrete lists; leave its "Personality and Soul" section alone, since
first-person opinion, humour and expressions of mixed feeling do not belong in
this paper.

### Phrases to cut, from `references/phrases-to-cut.md`

"it is important to note that", "it should be emphasized that", "due to the fact
that", "serves as a testament to", "in today's rapidly evolving landscape".

### Vocabulary to avoid, from `references/patterns-english.md`

additionally, align with, crucial, delve, emphasizing, enduring, enhance,
fostering, garner, highlight as a verb, interplay, intricate, intricacies, key
as an adjective, landscape as an abstract noun, pivotal, showcase, tapestry,
testament, underscore as a verb, valuable, vibrant.

Project-specific additions, because they are the words most likely to overstate
this paper: comprehensive, robust, novel, substantial, significant, extensive,
thorough. Each is permitted only where a number in
`05_NUMERIC_LEDGER.csv` supports it. "Robust" additionally requires a defined
uncertainty criterion, which this paper does not have for the ordering results;
prefer naming the evidence.

### Constructions to avoid

- copula avoidance: "serves as", "represents", "stands as", "boasts" — write
  "is" or "has"
- negative parallelism: "it is not just X, it is Y"
- forced rule of three
- em-dash reveals: WSOL uses one em dash in 11,533 words; match that
- elegant variation: substituting synonyms for an already-defined technical term

### Constructions to prefer

- direct statement over softened announcement
- varied sentence length, matching the measured WSOL distribution in `29`
- specific attribution over "experts believe"

## What unslopping must NOT do here

The brief is explicit and it is adopted verbatim as a constraint. Unslopping does
**not** mean:

- making every sentence short
- removing a necessary caveat
- deleting a technical definition
- turning prose into bullet-like fragments
- avoiding all transitions
- changing the author's logical order
- replacing precise repeated terminology to increase lexical variety

The target is natural, compact scientific prose, not artificial terseness. The
frozen terms — evaluated state, scoreable target, admission, row-additive,
key-additive but content-rewriting, ANCHOR_UNMATCHED, ANCHOR_ID_MISMATCH,
TARGET_REFERENCE_ABSENT, SEMANTICALLY_ADMITTED, released-deployment audit,
controlled intervention — repeat verbatim every time. Repetition of a defined
term is correctness, not a style fault.

## Paste-ready style block for the Codex writer prompt

```
STYLE INSTRUCTIONS

Write the prose yourself. Do not copy sentences from any reference.

Facts: use only V6_SOURCE_OF_TRUTH. Every number must come from
05_NUMERIC_LEDGER.csv. If a fact you need is absent, write [FACT NEEDED] and
stop. Do not browse other artifacts and do not infer a value.

Style reference: WSOL_TPAMI_2023.pdf, for structure and rhythm only, never for
content or phrasing. Target its measured rhythm: mean about 18 words, median
about 15, roughly a third of sentences under 12 words, under one em dash per
10,000 words. Its abstract is 179 words in 8 sentences with no numerals; its
Discussion and Conclusion are merged, about 224 words, and end by naming where
the problem appears next rather than by summarising.

Apply the anti-ai-tells rules 1, 2, 3 and 8 only:
  1. state each claim once; delete closing summary paragraphs
  2. name the tracker, commit, dataset, section and number; never "several
     studies" or "recent years"
  3. let sections differ in length; leave unresolved things visibly unresolved
  8. do not keep the first phrasing that arrives

Apply the writing-anti-ai lexical lists: cut "it is important to note that",
"due to the fact that", "serves as a testament to"; avoid additionally, crucial,
delve, enhance, landscape, pivotal, showcase, testament, underscore, interplay,
intricate, key as an adjective; avoid "serves as" and "represents" where "is"
works. Use comprehensive, robust, novel, substantial, significant, extensive
only where a ledger number supports it, and avoid "robust" entirely for the
ordering results.

Preserve the user's logical order. Do not reorder sections or arguments for
narrative effect.

Keep technical terminology stable and verbatim: evaluated state, scoreable
target, admission, row-additive, key-additive but content-rewriting, the four
STV class names, released-deployment audit, controlled intervention. Repetition
of a defined term is correct.

Where v5 already contains a correct and concise sentence, reuse it rather than
paraphrasing it for novelty. 13_V5_REUSE_MAP.md marks which sentences those are.

Never drop a caveat to improve a sentence. If a caveat and smooth prose
conflict, keep the caveat.

Do not write promotional framing, do not announce the paper's own structure
beyond bare section pointers, and do not restate the contributions in the
conclusion.
```

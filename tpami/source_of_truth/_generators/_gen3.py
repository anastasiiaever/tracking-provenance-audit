import os
V="<AUDIT_ROOT>/V6_SOURCE_OF_TRUTH"
def w(n,s):
    open(os.path.join(V,n),"w").write(s.lstrip("\n")); print("  wrote", n)

w("28_WRITING_STYLE_REFERENCE.md", r"""
# WRITING STYLE REFERENCE AND PRECEDENCE

Style guidance only. **Neither source in this file may be used for a scientific
fact.** Facts come from `02_CURRENT_FACTS.md` and `05_NUMERIC_LEDGER.csv`.

## Located sources

| role | path | identity | status |
|---|---|---|---|
| human scientific-writing reference | `<AUDIT_ROOT>/reference/WSOL_TPAMI_2023.pdf` | SHA-256 `7623cb9d8a83807cb2981f44171626a2498f32d9a425c4dd788d97689e82874b`, 8,700,561 bytes, 16 pages, pdfTeX-1.40.21; Choe, Oh, Chun, Lee, Akata, Shim, *Evaluation for Weakly Supervised Object Localization: Protocol, Metrics, and Datasets*; arXiv:2007.04178v2 | **CURRENT**, the only WSOL file on disk |
| discourse-level anti-AI skill | `/root/.claude/skills/anti-ai-tells/SKILL.md` | SHA-256 prefix `b0583563c36920e6`, 11,632 bytes, mtime 2026-09-02 10:59:45 | **CURRENT, PRIMARY** |
| lexical-level anti-AI skill | `/root/.claude/skills/writing-anti-ai/SKILL.md` | SHA-256 prefix `b86ea0c271598071`, 9,072 bytes, v1.0.0, author gaoruizhang, MIT, mtime 2026-09-02 10:49:31, plus `references/{patterns-english,patterns-chinese,phrases-to-cut,wikipedia-source}.md` and `examples/{english,chinese}.md` | **CURRENT, SECONDARY** |

Duplicate copies found and checked: `/tmp/anti-ai-tells-SKILL.md` is
byte-identical to the installed `anti-ai-tells`;
`/tmp/claude-scholar/skills/writing-anti-ai/` is byte-identical to the installed
`writing-anti-ai`. The `/tmp` copies are staging artifacts, not separate
versions, and were not used.

Both skills are installed and neither supersedes the other: they operate at
different levels. `anti-ai-tells` is the later file, was the one actually
invoked in this project, and is the only one that scopes itself for scientific
papers, so it takes precedence where the two conflict. `writing-anti-ai` is
retained for its concrete lexical lists, which `anti-ai-tells` does not provide.

## Style precedence, frozen

**Scientific facts:**
`V6_SOURCE_OF_TRUTH` > frozen authoritative artifacts > current v5.

**Writing style:**
1. the user's already-approved human-authored wording, wherever it exists in v5
2. the WSOL structural and stylistic reference
3. the actual `anti-ai-tells` rules, then `writing-anti-ai` for lexical items
4. valid concise wording already in v5

**Scientific accuracy always overrides style.** If a caveat makes a sentence
clumsy, the caveat stays and the sentence stays clumsy.
""")

w("29_WSOL_STYLE_OBSERVATIONS.md", r"""
# WSOL STYLE OBSERVATIONS

Structural and rhythmic properties measured from the located PDF. These are
properties to reference, **not sentences to imitate**. No WSOL phrasing is
reproduced here beyond the minimum needed to name a pattern.

## Abstract

Measured: **179 words, 8 sentences**, sentence lengths 22, 30, 23, 37, 22, 26,
11, 8; mean 22.4, median 22.5. **Zero numerals.** Four occurrences of "we". One
hedge.

Functional sequence of the eight sentences:

1. what the subfield is and why it is attractive, one sentence
2. what the field has been optimising since the seminal method
3. the defect in that practice, introduced with a plain "However"
4. what this paper argues and proposes, the longest sentence in the abstract
5. the first empirical finding, stated as an absence of improvement
6. the second empirical finding, a baseline not reached
7. one sentence saying future directions are discussed
8. one sentence giving the code and data URL

Two properties worth copying. First, **the abstract carries no numbers at all** —
findings are stated qualitatively and the reader is sent to the body for values.
Second, the two findings are **negative** and are stated without softening.

For v6 this suggests: state the framework and the two or three findings
qualitatively, keep at most one or two numbers if any, and do not pad the
abstract with the full results matrix.

## Introduction

Opens with the practical motivation in a single clause, then names the seminal
method and what it does, then the defect. Prior methods are cited in a dense
bracketed run rather than discussed individually. The problem statement arrives
within the first few sentences, not after a page of framing.

There is **no "in recent years" opening and no survey paragraph** before the
problem.

## How prior work is discussed

Related Work is one short section with grouped citations, not a method-by-method
catalogue. Individual prior methods reappear later, in the results, where they
are compared numerically. The paper spends its prose budget on its own protocol
rather than on describing others.

## How contributions are stated

Embedded in the argument rather than set out as a decorated list. The paper says
what it argues, what it proposes, and what it observed. It does not label any of
it novel.

## How results are summarised

The body carries the numbers; the narrative carries the direction. A mid-paper
paragraph headed "Conclusion." closes an interlude with four numbered one-clause
observations, each a single finding, no elaboration. That compact device is worth
reusing for the gate sweeps and the composition tables.

## Sentence rhythm, measured

525 body sentences: mean **18.5 words**, median **15**, standard deviation
**13.4**. **36.4 % of sentences are under 12 words** and **9.0 % are over 35**.

That is the target rhythm: a strong majority of short declaratives, a minority of
long sentences where a definition or a qualification genuinely needs the length,
and a high variance. Uniform 25-word sentences are the AI tell; so is uniform
8-word sentences.

Punctuation across 11,533 body words: **one em dash**, 60 colons. Em dashes are
effectively absent.

## Caveats and hedging

Hedges are rare and specific. Where the paper limits a claim it does so by naming
the condition, not by adding a modal: the restriction is stated as a fact about
scope rather than as uncertainty about the result.

## Discussion and Conclusion

**Merged into one section**, about **224 words in 13 sentences**, mean 15 words.
Structure: one sentence framing the retrospective; two sentences recalling what
was argued and proposed, each ending with a bare section reference; one sentence
giving the empirical conclusions; then numbered future directions; then two
sentences on implications for adjacent tasks.

It does **not** restate the contribution list, does not summarise the results
table, and does not end on a flourish. It ends by naming where the same problem
appears next.

## AI-vocabulary audit of WSOL itself

Per 11,533 body words: "additionally" 1, "moreover" 1, "robust" 1,
"significant" 14. Zero occurrences of delve, enhance, landscape, pivotal,
showcase, testament, underscore, vibrant, intricate, interplay, foster, garner,
comprehensive, novel, leverage, or "it is important to note".

"Significant" appears 14 times and is almost always statistical or quantified.
In v6, "significant" should be used only where a number or an interval supports
it, and never as a synonym for "large".

## Meta-narration

Near zero. The paper does not announce its own structure beyond bare section
pointers, does not explain why a section exists, and does not tell the reader
what they are about to read.

## What NOT to take from WSOL

- Its subject matter, phrasing and sentence constructions.
- Its merged Discussion and Conclusion is a reasonable option for v6, but the
  decision should follow from v6's own content, not from imitation.
- Its zero-numeral abstract is a strong default, not a rule; one or two numbers
  in the v6 abstract are acceptable if they are the paper's headline quantities.
""")

w("30_UNSLOPPING_RULES_FOR_CODEX.md", r"""
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
""")

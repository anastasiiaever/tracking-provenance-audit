# V6 BUILD GUARDRAILS

Binding on anyone writing v6, including a model. Read this file,
`04_FORBIDDEN_OR_OBSOLETE_CLAIMS.md` and `30_UNSLOPPING_RULES_FOR_CODEX.md`
before writing a sentence.

## 1. Precedence

`01_ARTIFACT_PRECEDENCE.md` is the only tie-breaker. A later-dated artifact with
a verified manifest beats an earlier one. A correction record beats the report it
corrects. A filename containing FINAL proves nothing.

When two sources disagree and the precedence rule does not settle it, do not pick
one. Write `[CONTRADICTION]` with both values and both paths, and stop.

## 2. Numbers

- Every number in v6 comes from `05_NUMERIC_LEDGER.csv`. Nothing is retyped from
  prose, not even this directory's own prose.
- A number not in the ledger is written `[FACT NEEDED]`. Do not estimate, do not
  interpolate, do not derive a percentage from two other percentages.
- Report at the precision the ledger gives. If the main text rounds, the
  supplement must carry the full precision so the figure stays checkable.
- Counts and percentages with different denominators never share a column or a
  sentence without their denominators named.
- Every tolerance-dependent count carries its tolerance. The GPR 52 is the
  standing example.
- Name the quantity before writing a range, and take both endpoints from the same
  column of the same artifact. A class count is never a total and never a
  denominator; see the standing rule in `04_FORBIDDEN_OR_OBSOLETE_CLAIMS.md`.

## 3. Claims

- Only claims in `03_ALLOWED_CLAIMS.md` may be asserted.
- Claims in `04_FORBIDDEN_OR_OBSOLETE_CLAIMS.md` may not appear, in any
  paraphrase. Paraphrase does not launder a forbidden claim: "replicated
  independently" is forbidden for the GSI arm whatever words carry it.
- Each claim's section, artifact and ledger ids are in
  `26_CLAIM_TO_ARTIFACT_MAP.csv`.

## 4. Statistics

- No p-values. No "significant". No "robust" in a technical sense.
- No multiplicity correction, and no sentence implying one was needed and
  omitted.
- Crossing counts are counts out of an exhaustive dependent matrix. Never a rate,
  never a trial, never a binomial.
- `P(sign differs)` is a bootstrap frequency. Say so where it first appears.
- Percentile intervals are descriptive.
- "25 sequence-level clusters", never "25 independent sequences".

## 5. Evidence category

Every result carries its category, and the categories do not blur:

| category | arms |
|---|---|
| released-deployment audit | MOT17 five deployments; MOT20 eligible cell; OC-SORT GPR; StrongSORT++ |
| controlled intervention, operator applied by us | DanceTrack DTI and GSI |
| pre-specified | everything except the GSI arm |
| post-hoc | the GSI arm and its decomposition |

Do not describe a controlled arm as released practice, and do not describe the
post-hoc arm as confirmatory.

## 6. Interpretation

- Non-admission is reference-side. It is not error, not false positive, not
  implausibility.
- No causal language from composition to metric change, in either direction.
- State change does not imply score change. The GPR case is the counterexample
  and should be cited wherever the temptation arises.
- Do not claim breadth is closed. The allowed sentence is that the principal
  single-population limitation is substantially reduced.

## 7. Reuse

- v5 is frozen. Copy from it; never edit it. Hashes are in
  `09_PROVENANCE_LEDGER.csv`.
- Reuse decisions are in `13_V5_REUSE_MAP.md`, including the one required
  correction to v5's Verification section and the bibliography-file trap.
- Re-point every `\ref` and `\label` carried over from v5. v5's `sec:results`
  belongs to the removed section and must not be reused for v6's new Sec. 5.

## 8. Writing

- Style precedence and the full rule set are in
  `28_WRITING_STYLE_REFERENCE.md`, `29_WSOL_STYLE_OBSERVATIONS.md` and
  `30_UNSLOPPING_RULES_FOR_CODEX.md`. The style files govern wording only and
  carry no scientific authority.
- Terminology is frozen. `R0`, `R1`, `R2`, `ANCHOR_UNMATCHED`,
  `ANCHOR_ID_MISMATCH`, `TARGET_REFERENCE_ABSENT`, `SEMANTICALLY_ADMITTED`,
  `scoreable-target admission`, `gate-stable`, `row-additive`,
  `key-additive but content-rewriting`, `rewrite-only`, `evaluated state`,
  `estimand eligibility`. Do not vary these for readability.
- State the thesis once. Do not restate the contribution set at the head of each
  results section, and do not end sections with summaries of themselves.
- Do not even out section lengths. Sec. 5 is the new contribution and should be
  the longest.

## 9. Stop conditions

Stop writing and report, rather than working around, if any of these occurs:

1. A required number is absent from the ledger and absent from every artifact.
2. Two authoritative artifacts disagree and precedence does not resolve it.
3. A claim needed for the argument is in the forbidden list.
4. A manifest fails verification.
5. An artifact referenced by this directory is missing from disk.

## 10. What this directory does not authorise

No new experiments. No new datasets, trackers, operator families or parameter
searches. No modification of v5, of the public repository, or of any frozen
experimental artifact. The experimental expansion is closed.

If writing v6 appears to require a new measurement, that is a stop condition
under item 1, not a licence.

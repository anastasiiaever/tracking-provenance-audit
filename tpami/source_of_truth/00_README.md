# V6 SOURCE OF TRUTH

Assembled 2026-10-04. This directory is the **only** source Codex should consult
for scientific facts while writing v6. It contains no manuscript prose.

Nothing outside this directory was modified to build it. v5, the public
repository and every frozen experimental artifact are untouched.

## What this is

- `01_ARTIFACT_PRECEDENCE.md` — which artifact wins when two disagree
- `02_CURRENT_FACTS.md` — the verified facts, by population and operator
- `03_ALLOWED_CLAIMS.md` / `04_FORBIDDEN_OR_OBSOLETE_CLAIMS.md` — what may and
  may not be written
- `05_NUMERIC_LEDGER.csv` — every number v6 may cite, with its artifact
- `06_EVIDENCE_ARCHITECTURE.csv` — the eight evidence arms and their type
- `07_METHOD_DEFINITIONS.md` — frozen definitions, verbatim semantics
- `08_LIMITATIONS_LEDGER.md` — the limitations that must survive into v6
- `09_PROVENANCE_LEDGER.csv` — artifact paths, hashes, manifest status
- `10`-`12` — table, figure and section plans
- `13_V5_REUSE_MAP.md` — per-section disposition of v5
- `14_SUPPLEMENT_PLAN.md`, `15_CITATION_AND_RELATED_WORK_NOTES.md`
- `16`-`25` — per-section fact packets, one per manuscript section
- `26_CLAIM_TO_ARTIFACT_MAP.csv` — claim to evidence, machine readable
- `27_V6_BUILD_GUARDRAILS.md` — writing rules for Codex
- `28`-`30` — writing-style reference, WSOL style observations, and the
  unslopping rules. Style only; they carry no scientific authority.
- `31_INTERNAL_CONSISTENCY_AUDIT.md`, `32_DUPLICATE_CLAIM_LEDGER.csv` — the
  internal-consistency sweep and its claim ledger.
- `_generators/` — the scripts that wrote these files, kept for provenance.
  `run_all.py` rebuilds the packet from them in order. They are inputs to the
  build, not sources of fact.
- `V6_SOURCE_OF_TRUTH_MANIFEST.sha256` — hashes of every file above

## Rules for Codex

1. Use only the facts in `02`, `05` and the `16`-`25` packets.
2. If a needed fact is not here, write `[FACT NEEDED]` and stop. Do not browse
   the server artifacts and do not infer a value.
3. `04_FORBIDDEN_OR_OBSOLETE_CLAIMS.md` is binding. Several of its entries
   correct statements that appeared in earlier reports.
4. Keep released-deployment evidence and controlled-intervention evidence
   separate in every sentence that mentions both.
5. Every numeric claim must cite a row of `05_NUMERIC_LEDGER.csv`.
6. If two authoritative artifacts disagree and `01` does not resolve it, write
   `[CONTRADICTION]` with both values and both paths, and stop.
7. Style is governed by `28`-`30`. Those files may change wording and may never
   change a number, a definition, or a caveat.

## The one central paper

Benchmark scores characterise an evaluated output state, not a tracker in
isolation. Post-processing provenance is therefore necessary for interpreting
benchmark comparisons, and the audit that is actually available depends on the
structural transition from the pre-processed to the post-processed state.

That is the conceptual target, not final wording. The third clause is the part
the new evidence strengthened: row-additive transitions admit a row-level
admission decomposition, rewrite-heavy ones do not, and the available analysis
changes accordingly.

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

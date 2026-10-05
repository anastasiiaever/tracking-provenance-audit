# ARTIFACT PRECEDENCE

Verified by chronology (directory mtimes), by correction records inside the
artifacts, and by manifest status. All eight manifests verify with zero
failures, so precedence here resolves *interpretation*, not integrity.

## Hierarchy, highest first

| rank | generation | date | status | what it governs |
|---|---|---|---|---|
| 1 | final pre-v6 GPR correction audit, inside `final_defense_20261004/` | 2026-10-04 | **CURRENT** | the GPR rewrite counts and their tolerance criterion |
| 2 | final experimental defence pass, `final_defense_20261004/` | 2026-10-04 | **CURRENT** | GSI stage decomposition, DanceTrack row-local support, unified ordering schema, evidence architecture |
| 3 | D2B GSI execution, `gsi_exec_20261004/` | 2026-10-04 | **CURRENT** | DanceTrack GSI state inventory and metric states |
| 4 | D2A GSI protocol, `gsi_protocol_20261004/` | 2026-10-04 | **CURRENT** | the GSI operator contract and parameter freeze |
| 5 | D1B.1, `step_d1b_1/` | 2026-10-04 | **CURRENT** | MOT20 gate-stable correction, REFERENCE_ABSENT semantics, flip precision audit, bootstrap interpretation |
| 6 | D1B, `dancetrack_controlled_20261003/` | 2026-10-03/04 | **CURRENT** for its own numbers, **SUPERSEDED** for the MOT20 cross-population cell and for two wordings | DanceTrack DTI results |
| 7 | Step 9.1, `posthoc_composition_20261003/step9_1/` | 2026-10-03 | **CURRENT** | the corrected 12,767 verification level, the non-nesting counterexample |
| 8 | Step 9, `posthoc_composition_20261003/` | 2026-10-03 | **CURRENT** for its numbers, **SUPERSEDED** for two report narratives corrected by 9.1 | MOT17 and MOT20 composition, gate sweeps, bootstrap |
| 9 | frozen primary experimental artifacts, `<MOT_AUDIT_ROOT>/` | 2026-08 | **CURRENT** as raw state | R0/R2 state files, StrongSORT PRE/S0/S2, OC-SORT GPR G0/G2 |
| 10 | v5 manuscript and supplement | 2026-09/10 | **CURRENT** except where 1-8 correct it | prose, structure, terminology |
| 11 | v4, v4_docx, v3, choe_v2, DOCX candidates, historical reports | earlier | **HISTORICAL_ONLY** | wording history; never a source of fact |

## Specific overrides

| claim | superseded source | current source | current value |
|---|---|---|---|
| MOT20 gate-stable non-admission | D1B `D1B_cross_population_comparison.json` rendered it absent | Step 9 `C3_gate_stability_summary.csv`, confirmed by D1B.1 | 6,631 / 34,814 = 19.0469 % |
| GPR coordinate rewrites | the first draft of the final-defence report said 212 rows, 0.4616 % | `FINAL_gpr_rewrite_recount.csv` | 52 rows above 1e-6 px; 2,622 rows at exact float equality |
| GSI as a second independent mechanism | how the D2B report could be read | D2C in `final_defense_20261004/` | all 7 crossings arise at the linear stage; the GP stage adds 0 |
| "25 independent sequences" | D1B report section Q | D1B.1 `D1B1_bootstrap_interpretation.json` | write "25 sequences" or "25 sequence-level clusters" |
| 12,767 per-row reproduction | Step 9 closing block | Step 9.1 `STEP9_REPORT_CORRECTIONS.md` | population and identities reproduced; no frozen per-row class table exists |
| bibliography file for the main text | the root `main.bib`, 66 entries, missing `luiten2020trackeval` | `reconcile_20261003/main_v4_docx.bib`, 67 entries, which `\bibliography{main_v4_docx}` actually resolves to | use the reconcile copy, or add the missing entry to the root copy first |

## Status labels

- **CURRENT** — cite directly.
- **SUPERSEDED** — a specific statement was corrected; the rest of the artifact
  stands. Named above.
- **HISTORICAL_ONLY** — never a source of fact.
- **STRUCTURAL_REFERENCE_ONLY** — `TPAMI_Main_Candidate_EN.docx`,
  `TPAMI_Supplement_Candidate_EN.docx`, `preamble.tex`, `main.bib`,
  `reconcile_20261003/*`: use for layout, bibliography and build tooling, never
  for scientific values.

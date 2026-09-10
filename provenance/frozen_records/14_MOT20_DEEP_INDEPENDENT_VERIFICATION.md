# Independent Verification — Deep-OC-SORT × MOT20

Verifies the frozen result `9a5109a65d5da2ed85273cfe255e3e0cf5194fb0`
(`tpami-v9-mot20-deep-results-20260831`). **Nothing was rerun** — no tracker, no
DTI, no STV via the frozen module, no TrackEval — and no state, metric file,
protocol or manuscript was touched. **Record 13 was never used as the computation
oracle**; it was opened only to compare against numbers already derived.

**Verdict: PASS.** 17 checks, 16 critical, all critical PASS, 0 mismatches, 0 silent
repairs.

## 1–2. Execution completion, and what remains unknown

`PROCESS_EXIT_CODE = UNAVAILABLE`. The job was detached under the standing
long-GPU-job policy, so no integer shell exit code was preserved. **It is not
inferred as 0**, and this stays a permanent provenance limitation of the run.

`EXECUTION_COMPLETION_EVIDENCE = PASS`, on artifact and log evidence alone: **zero**
occurrences of Traceback / Exception / Error / Killed / CUDA-out-of-memory /
segmentation fault / assertion across 108,500 B of stdout and 630 B of stderr; the
entire stderr is one PyTorch `UserWarning`; both terminal messages appear exactly
once; 4 R0 + 4 R2 files; 4 embedding caches + 1 detector cache; monotone timestamps
from 10:43:08 to 11:49:37; no live process.

## 3. Execution identity

`run_id`, cwd, environment and argv identical to both 10A and 12B. Population,
detector and ReID hashes identical at launch **and now**. The V9-B36 `fast_reid`
prerequisite resolves into the frozen repository. Effective audit mode
`ROW_ADDITIVE_R0_R1_R2`.

## 4. Population, parsed from the result files

Not taken from any manifest. Every R0 and R2 file parsed: exactly
MOT20-01/02/03/05; local domains 1–214 / 1–1390 / 1–1202 / 1–1657; mapping by
+215 / +1392 / +1203 / +1658 onto **216–429 / 1393–2782 / 1204–2405 / 1659–3315**;
**zero** test, MOT17 or out-of-population frames.

## 5–6. Structural transition, recomputed by own set arithmetic

| quantity | recomputed |
|---|---|
| n_R0 | **529,865** |
| n_R2 | **564,679** |
| shared | 529,865 (= n_R0) |
| R0-only (deletions) | **0** |
| R2-only (synthesized) | **34,814** |
| coordinate rewrites | **0** |
| ID rewrites | **0** |
| ambiguous identity changes | **0** |

`n_R2 − n_R0 = 34,814 = n_synthesized`. Row-additive invariant **PASS**,
independently. Synthesized identity-set SHA-256
`b8205e6a9e54a2b4906928badc9977c9ba91daa4b948c467bbac2388b1c08dcf`.

## 7. STV, independently re-implemented

The frozen `stv` module was **not invoked**. Own IoU, own gate-before-assignment
cost matrix (sub-gate pairs set to a prohibitive cost and rejected after
assignment), `scipy.linear_sum_assignment`, own anchor bracketing, own four-way
classification.

| class | recomputed | record 13 |
|---|---|---|
| `ANCHOR_UNMATCHED` | 6,586 | 6,586 |
| `ANCHOR_ID_MISMATCH` | 2,165 | 2,165 |
| `TARGET_REFERENCE_ABSENT` | 0 | 0 |
| `SEMANTICALLY_ADMITTED` | 26,063 | 26,063 |
| sum | **34,814** | 34,814 |

Per-sequence counts agree exactly as well. Classes mutually exclusive and
exhaustive.

## 8. R1 equality

Row-identity set equals R0 + the `SEMANTICALLY_ADMITTED` synthesized rows in every
sequence; `n_R1 = 529,865 + 26,063 = 555,928`; **zero** non-admitted rows entered R1.

One characteristic worth stating precisely: **R1 coordinates are the two-decimal
rendering of their source, not bit-identical copies.** Every R1 coordinate equals
`round(source, 2)` — **zero exceptions over 2,223,712 coordinates**; 97.11 % are
already bit-identical and the maximum deviation is 0.005, the half-ulp of
two-decimal rendering, occurring only where a DTI-interpolated value ended in
`.xx5`. Unlike the tracker `score` field, coordinates *are* evaluated, so this
rendering is visible to the evaluator. It is the same writer convention as the
frozen MOT17 V9 R1 files, which the execution task reproduced byte-for-byte, so R1
remains comparable across the two datasets. R1 stays **`GT_INFORMED_DIAGNOSTIC`**,
**`NON_DEPLOYABLE`**.

## 9. Fractions and materiality, recomputed from integer counts

| quantity | value |
|---|---|
| synthesized / R2 | 0.061653 |
| UNMATCHED / synthesized | 0.189177 |
| ID_MISMATCH / synthesized | 0.062188 |
| REF_ABSENT / synthesized | 0.000000 |
| ADMITTED / synthesized | 0.748636 |
| nonadmitted / synthesized | **0.251364** |
| nonadmitted / R2 | 0.015497 |
| ID_MISMATCH / R2 | 0.003834 |

0.251364 ≥ 0.10 → **`STV_COMPOSITION_MATERIAL`**, agreeing with record 13.

## 10. TrackEval input identity

Pin `12c8791b303e0a0b50f753af204249e622d0281a` verified in the working clone.
`BENCHMARK=MOT20`, `SPLIT_TO_EVAL=val`, `CLASSES_TO_EVAL=['pedestrian']`,
`DO_PREPROC=True` read from the frozen run log. Seqmap is exactly the four
sequences; all four GT hashes and seqLengths (214 / 1390 / 1202 / 1657) match the
09B adapter record. `mot_challenge_2d_box.py:326-327` appends `non_mot_vehicle` for
`BENCHMARK == 'MOT20'` — MOT20-native preprocessing active.

## 11. Metrics, read from source at full precision

| state | HOTA | DetA | AssA | IDF1 | MOTA |
|---|---|---|---|---|---|
| R0 | 57.38379576900605 | 57.93580751849612 | 57.00105326223428 | 74.75204391327709 | 69.94263066601424 |
| R1 | 59.47967992531304 | 60.82552526542012 | 58.335160113284914 | 76.55716468212978 | 74.1363306060276 |
| R2 | 59.53556725148849 | 60.97593181226089 | 58.3061070749342 | 76.4479036805716 | 74.01099267317687 |

R2 − R0: +2.151771 / +3.040124 / +1.305054 / +1.695860 / +4.068362
R1 − R2: −0.055887 / −0.150407 / +0.029053 / +0.109261 / +0.125338

All 15 values and 10 deltas agree with record 13 within 1e-12. No hand
transcription.

## 12. Hashes

**29 artifacts recomputed, 0 mismatches** — 4 R0, 4 R1, 4 R2, 3 detailed CSVs, 3
summaries, 4 audit reports, 5 record-13 self-hashes, 2 execution logs.

## 13. Post-execution test transition — PASS

The diff touches **only** zero-output and sandbox-emptiness assertions. **Zero**
authorization or refusal assertions were deleted. The replacements are exact
allowlists, not relaxations: `list(...) == []` became
`sorted(...) == [RUN__R0, RUN__R1, RUN__R2]`, and a passing
`require_no_run_artifacts` became `pytest.raises(RunIdReuse)`. Adversarially probed:
a ByteTrack MOT20 `_post` path, a foreign audit path and a `-002` path **all still
fail** the new assertions. No scientific validation logic was altered.

## 14. Spent run id — PASS

Seven canonical artifacts are present; `require_no_run_artifacts` and `preflight`
both raise `REFUSE_RUN_ID_REUSE`. `-002` and `-003` raise `CellNotAuthorized`.
`run_guard` contains no `rmtree`, `os.remove` or `unlink`; nothing was cleaned up.

One coverage gap found and recorded, not repaired: `run_guard`'s `trackeval_output`
leg names `<trackers>/MOT20-val/<run_id>`, but the evaluator was staged as
`<run_id>__R0/__R1/__R2`, so that path never exists and that one leg never fires.
The single-use property still holds via the other seven legs.

## 15–16. Non-regression

All MOT17 tracker-state hashes, evaluator summary hashes and 21 audit-report content
hashes unchanged. **Ordering matrix still 50 cells with exactly 5 flips and 45
unchanged**, with no MOT20 entry. MOT17 population manifest still verifies. All six
other MOT20 cells remain `STOPPED_BEFORE_EXECUTION` historically and effectively,
unlicensed, refused by the live guard, and have produced no output. **No MOT20
ranking matrix exists or was computed.**

## 17. Interpretation boundary

This verification establishes a second-dataset clean quantitative Deep-OC-SORT
audit, the row-additive composition result, STV composition materiality, and
R0/R1/R2 evaluator behaviour. It does **not** establish MOT20 pairwise ranking
replication, multi-pipeline MOT20 ranking instability, prevalence of ranking flips
across datasets, or direct official-download byte provenance for the MOT20 corpus.

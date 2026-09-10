# V7-M0 — Matched-predictor comparison RESULT

Date: 2026-08-28
Status: **FAIL_QUANTITATIVE_B**

> ## `M0_ROOT_CAUSE_PROVEN = NO`
>
> The matched predictor was sealed before unsealing, the historical criterion was applied
> unchanged, and it **fails**. The negative result is frozen exactly as it came out. Nothing
> was repaired, tuned, excluded or rerun.

## Provenance

| item | sha256 |
|---|---|
| sealed prediction table `m0_final_predictions.csv` (56 rows) | `49f4d79bd5ddadaa77e2e2c89f57fbbd96170e095b621b87cb98896bdc430409` |
| measured `t4_cell_results.csv` | `b9337bfa06c864d06b3de01ac66311337184176af70ef45d1ca09c3d4b4c0ab9` |
| bootstrap `t4_bootstrap.json` | `c00d4226fd5eb3781124dfd40f6032ec2c09bbfad41fc299ea0e0e2d92c686a8` |
| comparison table (56 rows) | `a9a4d077c63e02492f466f4fca6b4589a5a1542a5cf8ae2dda5fd7c68f23ed5f` |

Implementation gate: **`REPAIR_A_PRIME = PASS`**, frozen and passed before execution — 0
failures over 12432 geometries × 4 probes × 3 operators. The historical full-population
absolute-A extrapolation remains a diagnostic and did not enter this decision path.

Completeness: **28 planned = 28 reported = 28 evaluable** for both methods, 56 of 56 cells,
all ratios finite. **No cell was excluded.**

## Criterion B, applied unchanged

| | spline | kalman |
|---|---|---|
| ratio min | **0.527324** | **0.990923** |
| ratio median | **0.996523** | **0.999585** |
| ratio max | **1.072278** | **1.008730** |
| max &#124;ratio − 1&#124; | **0.472676** | **0.009077** |
| worst cell | `iid φ=0.00 g=20`, ratio 0.527324 | `ar1 φ=0.85 g=20`, ratio 0.990923 |
| cells within ±25 % | **24 / 28** | **28 / 28** |
| median deviation from 1 | 0.003477 | 0.000415 |
| **per-cell B** | **FAIL** | PASS |
| **median B** | PASS | PASS |

> **Overall verdict: `FAIL_QUANTITATIVE_B`.**

Kalman agrees with the conditional-expectation prediction to within **0.91 %** in the worst of
28 cells. Spline agrees to within a few tenths of a percent in the median, but four cells miss
the band badly.

## The four failing cells

| method | process | φ | g | predicted | measured | ratio | measured R² |
|---|---|---|---|---|---|---|---|
| spline | ar1 | 0.50 | **20** | 597.601810 | 321.843082 | 0.538558 | 0.848740 |
| spline | ar1 | 0.70 | **20** | 326.882557 | 178.867062 | 0.547191 | 0.827373 |
| spline | ar1 | 0.85 | **20** | 153.045248 | 84.928921 | 0.554927 | 0.801792 |
| spline | iid | 0.00 | **20** | 1512.947627 | 797.813755 | 0.527324 | 0.892251 |

Spline ratio by gap length, all four arms:

| g | ar1 0.50 | ar1 0.70 | ar1 0.85 | iid 0.00 |
|---|---|---|---|---|
| 1 | 0.9929 | 0.9950 | 0.9963 | 0.9927 |
| 2 | 1.0021 | 1.0021 | 1.0017 | 1.0007 |
| 3 | 0.9953 | 0.9966 | 0.9976 | 0.9938 |
| 5 | 1.0103 | 1.0097 | 1.0072 | 1.0064 |
| 8 | 1.0150 | 1.0013 | 0.9964 | 1.0723 |
| 10 | 0.9391 | 0.9310 | 0.9427 | 1.0407 |
| **20** | **0.5386** | **0.5472** | **0.5549** | **0.5273** |

Stated as fact and nothing more: **the failure is confined entirely to `g = 20` for spline**,
in all four arms, at a ratio near 0.53–0.55, while spline at `g ≤ 10` and kalman at every `g`
sit close to 1. **No interpretation of this pattern is offered here, and none may be used to
alter the verdict.**

## R² — descriptive, never a gate

Historical role preserved exactly: the coefficient of determination of the measured 8-point
subject-mean MSE-versus-σ² OLS within each cell. It never touches the analytic value.

| | spline | kalman |
|---|---|---|
| R² min / median / max | 0.801792 / 0.999978 / 0.999999 | 0.999961 / 0.999992 / 1.000000 |
| cells with R² ≥ 0.95 | 24 / 28 | 28 / 28 |

The four spline cells with R² < 0.95 are **exactly** the four cells outside the band —
complete overlap. This is recorded as an observation. **It did not and cannot change the
Criterion-B verdict**, and the independent audit confirms the verdict is a function of the
ratios alone.

## Bootstrap — descriptive, no threshold

Read only after the ratio comparison was computed. Whether the matched prediction lies inside
the frozen per-cell track-clustered 95 % interval:

| | inside | excluded cells |
|---|---|---|
| spline | **28 / 28** | none |
| kalman | **26 / 28** | `ar1 φ=0.50 g=5`, `ar1 φ=0.70 g=5` |

**No pass threshold. No `24/28` rule. No simultaneous-coverage claim.** These counts entered
no verdict. Note the spline `g=20` predictions lie inside their intervals while failing the
ratio band — the two diagnostics disagree, and the frozen criterion is the ratio band.

## Independent comparison audit — 24 checks, 0 failures

Imports nothing from the production comparison; rebuilds the join with a dict keyed on the
tuple rather than a pandas merge. Re-hashed all three source artifacts; verified the exact
56-cell key identity on both sides with no duplicates; recomputed all 56 ratios
(`max_abs_dev = 2.220e-16`), all Criterion-B booleans, both medians and the verdict —
independently obtaining **`FAIL_QUANTITATIVE_B`**; confirmed the verdict is a function of the
ratios alone with R² and bootstrap inclusion outside the decision path; confirmed no cell
exclusion (56 evaluable of 56 planned), unchanged tolerances 0.25 / 0.10, and that the
implementation gate is A′ rather than the historical absolute A.

## Conclusion, bounded

`M0_ROOT_CAUSE_PROVEN` **remains NO**, and no further work on it is authorised by this record.

What is established: for **kalman**, the conditional injected-noise expectation on the exact
historical clean-p95-retained population, exact track-equalised weights, exact absolute-frame
AR(1) covariance and measurement-source operator semantics reproduces the historical
MSE-vs-σ² slope in all 28 cells to within 0.91 %. For **spline** it reproduces 24 of 28 cells
but fails four.

What is **not** established: the mechanism claim itself, which requires Criterion B to pass
for **both** methods. Nothing here validates the old 12-layout predictor, explains historical
heavy-tail behaviour, accounts for all 3DPW phenomena, or asserts that finite-seed empirical
slopes equal their expectations.

No repair, tuning, cell exclusion, tolerance change or predictor rerun was performed, and none
is permitted in response to this outcome.

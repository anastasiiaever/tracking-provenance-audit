# applicability_audit

**Before ranking reconstruction methods, determine which targets are applicable,
which cases each method supports, whether comparison support is identical, and
whether the declared aggregation makes the ranking interpretable.**

This is a pre-ranking *evaluation audit*. It is **not** a reconstruction
algorithm, it proposes no new estimator, and it contains no dataset-specific
annotation semantics. It takes observations whose semantics an adapter has
already resolved, and reports whether a ranking computed from them is
structurally readable.

## The five sets

| symbol | meaning |
|---|---|
| `T` | scoreable targets --- the evaluation population |
| `A` | admitted cases --- targets that pass the applicability gate and the run-length grid |
| `B_m` | the cases method *m* actually supports |
| `C` | metric-valid cases --- those on which the error is even defined |
| `D` | `A ∩ C ∩ ⋂_m B_m` --- the identical common support |

Headline ranking uses **`D` only**. A method may also be reported on its own
terms over `A ∩ C ∩ B_m`, and the difference between the two is the
`support_shift`, reported without any threshold attached.

## Four layers that must not be merged

1. **population / scoreability** --- which observations are in scope at all?
2. **applicability / admission** --- can this target be evaluated under the
   declared target-anchor continuity contract?
3. **method support and metric validity** --- can method *m* produce a result
   here, and is the metric defined here?
4. **ranking** --- how do methods compare on identical common support?

## The distinction this exists for

**Low applicability and method-support mismatch are different failures, and one
is routinely mistaken for the other.**

A benchmark can be *almost entirely inapplicable* and still have **perfect**
conditional agreement between methods: every admitted case supported by every
method, `A = B_m = C = D`, retention `1.0`. Nothing is wrong with the ranking on
`D` — but it describes a sliver of the population, and that sliver is invisible
if you only look at the leaderboard.

Conversely a benchmark can be *broadly applicable* and still be uncomparable,
because the methods were evaluated on different cases. Equal row counts in two
result files are not evidence of equal support.

The audit therefore reports **coverage** and **support geometry** separately,
and never substitutes one for the other:

```
applicability_rate                              target-level, over the population
per_method_conditional_on_A                     case-level, conditional on admission
common_support_retention_conditional_on_A       case-level, conditional on admission
```

A low applicability rate **never** makes a ranking inadmissible on its own. If
cases were admitted, `D` is non-empty, alignment is exact, metric validity holds
and the aggregation is declared, the ranking on `D` is admissible — and the low
coverage is reported next to it.

The toolkit invents **no thresholds**. It will not tell you that 30% coverage is
"too low"; scientific materiality belongs to your protocol, not to this package.

## Mode 1 — run the methods

```python
from applicability_audit import (ApplicabilityContract, CanonicalObservation,
                                 MethodContract, run_applicability_audit,
                                 simple_case_ladder)

def obs(seq, traj, frame, role, value=0.0):
    kw = {"sequence_id": seq, "target": role == "T", "anchor": role == "A"}
    return CanonicalObservation(traj, frame, (value, 0.0),
                                metric_scale=(1.0 if role == "T" else None), **kw)

observations = []
for i, off in enumerate((0.2, 0.4, 0.6, 0.8)):       # four applicable targets
    observations += [obs("s%d" % i, "t%d" % i, 0, "A"),
                     obs("s%d" % i, "t%d" % i, 1, "T", off),
                     obs("s%d" % i, "t%d" % i, 2, "A")]
for j in range(2):                                    # eight inapplicable ones
    observations += [obs("s9", "u%d" % j, k, "T") for k in range(4)]

def interpolate(mi):                    # sees anchor times, anchor values,
    return [(0.0, 0.0) for _ in mi.tgt_t]   # and target *times* only

methods = [
    MethodContract("linear",  lambda mi: mi.n_anchors >= 2, interpolate),
    MethodContract("spline",  lambda mi: mi.n_anchors >= 2,
                   lambda mi: [(0.1, 0.0) for _ in mi.tgt_t]),
    MethodContract("shallow", lambda mi: mi.key[1] != "s3", interpolate),
]

audit = run_applicability_audit(
    observations, methods,
    ApplicabilityContract(run_length_grid=(1, 2, 3)),
    simple_case_ladder())

print(audit.render_report())
```

Output:

```
# Applicability Audit Certificate

Mode: executable

Population contract          PASS
Applicability partition      PASS
Natural-run integrity        PASS
Case identity                PASS
Method-support accounting    PASS
Metric validity              PASS
Common-support identity      PASS
Aggregation declaration      PASS
Outcome-leakage safeguards   PASS

Ranking admissible           YES

Scoreable targets            12
Applicable targets           4
Applicability rate           0.333333
Admitted cases               4
Common-support cases         3
Common-support retention     0.750000
```

Two thirds of the targets never reach the leaderboard, and the ranking that does
exist is still perfectly readable. Both facts are reported.

The pairwise support geometry shows *which* method narrowed the comparison:

```
Pairwise support overlap (jaccard)
         linear   shallow  spline
linear   1.000    0.750    1.000
shallow  0.750    1.000    0.750
spline   1.000    0.750    1.000
```

## Mode 2 — audit a benchmark you did not run

You often have only published per-case outputs. That is enough.

```python
from applicability_audit import audit_precomputed_results, simple_case_ladder

cases = [{"case_id": "case_1", "sequence_id": "s1", "run_length": 1},
         {"case_id": "case_2", "sequence_id": "s1", "run_length": 1},
         {"case_id": "case_3", "sequence_id": "s2", "run_length": 1}]

method_a_results = {"case_1": {"normalized": [0.10]},
                    "case_2": {"normalized": [0.20]}}
method_b_results = {"case_2": {"normalized": [0.30]},
                    "case_3": {"normalized": [0.40]}}

audit = audit_precomputed_results(
    cases, {"method_a": method_a_results, "method_b": method_b_results},
    simple_case_ladder())
```

Each method reports two cases, so a naive reading compares `0.15` against
`0.35` and declares `method_a` the winner. The audit shows why that comparison
is not like-for-like:

- `B_method_a = {case_1, case_2}`, `B_method_b = {case_2, case_3}`
- Jaccard overlap `1/3`
- `D = {case_2}`
- on `D`: `method_a = 0.20`, `method_b = 0.30`

The published aggregates came from different case sets; only the `D` comparison
is admissible. Results are aligned **by case identifier** — never by position,
and a result naming a case that is not admitted is reported as
`CASE_ALIGNMENT_MISMATCH` rather than quietly intersected away.

## The certificate

`audit.certificate()` is a deterministic structural verdict:
`RANKING_ADMISSIBLE` or `RANKING_NOT_ADMISSIBLE`, with reason codes drawn from a
fixed taxonomy (`NO_ADMITTED_CASES`, `NO_COMMON_SUPPORT`,
`CASE_ALIGNMENT_MISMATCH`, `METHOD_SUPPORT_INCOMPLETE`,
`METRIC_VALIDITY_FAILURE`, `AGGREGATION_CONTRACT_INVALID`,
`DUPLICATE_CASE_KEYS`, `INCOMPLETE_METHOD_RESULTS`, `OUTCOME_LEAKAGE_DETECTED`).

It carries a configuration fingerprint, no clock reading, and serializes
byte-identically for identical input.

## Declaring aggregation

Every rung names its grouping keys, its unit and its weighting; nothing is
weighted implicitly by case count, target count or sequence length.

```python
from applicability_audit import AggregationContract, AggregationLevel

AggregationContract(
    levels=(AggregationLevel("sequence_and_run_length", ("sequence_id", "run_length")),
            AggregationLevel("sequence", ("sequence_id",)),
            AggregationLevel("headline", ())),
    metric_fields=("normalized", "raw"),
    reported_grid=(1, 2, 3, 5, 8, 10, 20))
```

`simple_case_ladder()` is the minimal alternative: target error → case mean →
equal-weight case mean.

## What this package does not do

No reconstruction algorithm. No dataset parsing, download or annotation
interpretation. No statistical test, no model training, no plotting, no GUI, no
service. No universal claim about how applicable any dataset is. No threshold of
its own.

Target, anchor and breaker semantics belong to an adapter; the core consumes the
resolved flags and never re-reads a raw annotation field.

## Running the tests

The canonical, self-contained command --- no dataset download, no external
artifact, no network:

```
python -m pytest tests/ -q
```

Expected on a clean checkout: **all tests pass, with skips**. Nothing should
FAIL or ERROR. Two dependencies are optional and only affect parts of the suite:

| package | needed for | if absent |
|---|---|---|
| `pyarrow` **or** `fastparquet` | parquet-backed legacy and extended-analysis tests | those 43 tests **skip explicitly**, naming the missing dependency; the suite stays green |

`pyarrow`/`fastparquet` is **optional**. The canonical command is clean in a base
environment without either: 686 passed, 65 skipped. With one installed the same
command runs the parquet paths in full: 729 passed, 22 skipped. Nothing is
substituted for parquet and no assertion is relaxed in either mode.

Tests that read large frozen result artifacts which this repository does not
ship (`results/` is not tracked) **skip explicitly**, naming the missing file.
They run in full, including byte-level checksum guards, in a checkout where
those artifacts are present. Absence is a supported state; a silent pass is not.

To audit third-party tracker output through the generic core, see
`src/applicability_audit/adapters/motchallenge.py` and
`provenance/frozen_records/MOT_AUDIT_ADAPTER_SPEC.md`.

# applicability_audit

A dataset-agnostic audit that runs before a ranking is read. It decides which
targets are evaluable, which cases each method actually supports, whether the
methods were compared on identical support, and whether the declared aggregation
makes the ranking readable.

## The five sets

| symbol | meaning |
|---|---|
| `T` | scoreable targets, the evaluation population |
| `A` | admitted cases: targets passing the applicability gate and the run-length grid |
| `B_m` | the cases method *m* supports |
| `C` | metric-valid cases, those on which the error is defined |
| `D` | `A ∩ C ∩ ⋂_m B_m`, the identical common support |

Headline ranking uses `D`. A method may also be reported on its own terms over
`A ∩ C ∩ B_m`; the difference between the two readings is the `support_shift`,
reported as a quantity with no threshold attached.

## Four layers

1. population and scoreability: which observations are in scope.
2. applicability and admission: whether a target can be evaluated under the
   declared target-anchor continuity contract.
3. method support and metric validity: whether method *m* produces a result and
   whether the metric is defined there.
4. ranking: how methods compare on identical common support.

The layers are reported separately. Collapsing them hides whether a ranking
difference comes from the methods or from the sets they were scored on.

## Inputs and outputs

Input is a set of canonical observations plus contracts declaring the
applicability gate, each method, and the aggregation. Output is an `AuditResult`
carrying the five set sizes, per-method support, the common-support estimates,
the per-method own-support estimates, the support shift, and a ranking verdict of
`RANKING_ADMISSIBLE` or `RANKING_NOT_ADMISSIBLE` with reason codes. A certificate
object serialises the same content deterministically.

## Two modes

`run_applicability_audit` executes the declared methods over the observations.
`audit_precomputed_results` takes results you already have and audits their
support, for a benchmark you did not run.

## Usage

Two cases, two methods, audited in precomputed mode. Run it from the repository
root with `src` importable, for example `PYTHONPATH=src python example.py`.

```python
from applicability_audit import (AggregationContract, AggregationLevel,
                                 audit_precomputed_results)

# Two admitted cases. The metadata fields are the ones a ladder may group by.
cases = [
    {"case_id": "c1", "sequence_id": "s1", "trajectory_id": "t1",
     "first_target_frame": 0, "run_length": 10, "stratum": None},
    {"case_id": "c2", "sequence_id": "s2", "trajectory_id": "t2",
     "first_target_frame": 0, "run_length": 10, "stratum": None},
]

# Keyed by method id, then by case id, never by position. Each entry holds the
# per-target errors for that case, which the first rung averages into a case
# mean. Lower is better.
method_results = {
    "linear": {"c1": {"normalized": [0.25, 0.75]},
               "c2": {"normalized": [0.75, 1.25]}},
    "learned": {"c1": {"normalized": [0.25, 0.25]},
                "c2": {"normalized": [1.25, 1.75]}},
}

# The declared ladder: target error -> case mean -> mean within sequence ->
# equal-weight mean across sequences. The final rung must group everything.
ladder = AggregationContract(
    levels=(AggregationLevel("sequence", ("sequence_id",)),
            AggregationLevel("headline", ())),
    metric_fields=("normalized",),
)

result = audit_precomputed_results(cases=cases, method_results=method_results,
                                   aggregation=ladder)
cert = result.certificate()

print("ranking_verdict ", cert["ranking_verdict"])
print("reason_codes    ", cert["reason_codes"])
print("admitted A      ", result["cases"]["admitted_A"])
print("common support D", result["common_support"]["D"])
print("retention       ", result["support_retention"])
print("method_support  ", result["method_support"])
for m in sorted(result["common_support_estimates"]):
    print(m, "on D      ",
          result["common_support_estimates"][m]["normalized"]["headline"],
          "| on own support",
          result["method_specific_estimates"][m]["normalized"]["headline"],
          "| support_shift", result["support_shift"][m]["normalized"])
```

Output:

```
ranking_verdict  RANKING_ADMISSIBLE
reason_codes     []
admitted A       2
common support D 2
retention        1.0
method_support   {'learned': 2, 'linear': 2}
learned on D       0.875 | on own support 0.875 | support_shift 0.0
linear on D       0.75 | on own support 0.75 | support_shift 0.0
```

Both methods report both cases here, so `D` is the whole admitted set and each
`support_shift` is `0.0`. `scripts/verify_support_accounting.py` runs the same
entry point on a worked example where the supports differ and reading each method
on its own support reverses the ranking.

`applicability` is optional: without it the audit reports the applicability block
as unavailable rather than assuming a partition. Pass `applicability` to have the
population counts and the exact-partition check reported too.

## Tests

```bash
python -m pytest tests/test_applicability_audit.py -q
```

## Scope

The package decides support and admissibility. It does not choose a metric,
propose an estimator, or rank methods by any criterion other than the one
declared in the aggregation contract. It carries no dataset-specific code: the
adapter in `adapters/` converts one external format into canonical observations,
and the core never imports a corpus module.

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

```python
import applicability_audit as aa
from applicability_audit.audit import audit_precomputed_results

result = audit_precomputed_results(
    observations=observations,     # CanonicalObservation sequence
    results=results,               # {(method, case_key): error}
    applicability=applicability_contract,
    methods=method_contracts,
    aggregation=aggregation_contract,
)
print(result["ranking_status"], result["support"]["D"])
```

`scripts/verify_support_accounting.py` runs this on a worked example in which
reading each method on its own support reverses the ranking.

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

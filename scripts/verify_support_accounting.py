#!/usr/bin/env python3
"""Exercise the controlled support-accounting audit on a worked example.

The controlled arm of the paper rests on one structural claim: two methods
evaluated on different sets of cases are not comparable, and equal result counts
are not evidence of equal support. This script drives the released audit
(src/applicability_audit) over a small constructed benchmark in which reading
each method on its own support reverses the ranking, and checks that the audit
separates the two readings instead of silently reporting one of them.

The numbers here are illustrative, not results from the paper. They are chosen so
the reversal is arithmetically obvious; the audit's behaviour is what is checked.

Needs no dataset and no GPU.
"""
from __future__ import annotations

import sys

from _common import Checks

import applicability_audit as aa
from applicability_audit import aggregation as agg
from applicability_audit.audit import audit_precomputed_results

LADDER = agg.simple_case_ladder()

# Six admitted cases. `linear` produces a result everywhere. `learned` produces
# one only on the three easy cases -- exactly the cases it does best on. Lower
# is better throughout.
ALL_CASES = ["c1", "c2", "c3", "c4", "c5", "c6"]
LINEAR = {"c1": 0.5, "c2": 0.6, "c3": 0.7, "c4": 3.0, "c5": 3.2, "c6": 3.4}
LEARNED = {"c1": 0.8, "c2": 0.9, "c3": 1.0}


def cases(ids):
    return [{"case_id": c, "sequence_id": "s", "trajectory_id": "t",
             "first_target_frame": 0, "run_length": 1, "stratum": None}
            for c in ids]


def results(mapping):
    return {m: {c: {"normalized": [v], "raw": [v * 10.0]}
                for c, v in rows.items()} for m, rows in mapping.items()}


def mean(d, keys):
    return sum(d[k] for k in keys) / len(keys)


def main() -> int:
    c = Checks("Controlled support accounting")
    common = sorted(set(LINEAR) & set(LEARNED))

    r = audit_precomputed_results(cases(ALL_CASES),
                                  results({"linear": LINEAR, "learned": LEARNED}),
                                  LADDER)
    cert = r.certificate()
    own = {m: v["normalized"]["headline"] for m, v in r["method_specific_estimates"].items()}
    dset = {m: v["normalized"]["headline"] for m, v in r["common_support_estimates"].items()}

    # The audit must find the support geometry, not assume it.
    c.equal("admitted cases A", cert["coverage"]["support_retention"]["admitted_cases_A"], 6)
    c.equal("linear supports every admitted case", r["method_support"]["linear"], 6)
    c.equal("learned supports only three", r["method_support"]["learned"], len(common))
    c.equal("common support D", r["common_support"]["D"], len(common))
    c.check("the audit records that the supports are not identical",
            r["common_support"]["identical_across_methods"] is False)
    c.check("and says so in the support geometry",
            cert["support_geometry"]["all_supports_identical"] is False)
    c.equal("common-support retention conditional on A",
            cert["coverage"]["support_retention"]["common_support_retention_conditional_on_A"],
            len(common) / 6, tol=1e-12)

    # Both readings are produced, and they disagree.
    c.equal("own-support value, linear", own["linear"], mean(LINEAR, LINEAR), tol=1e-9)
    c.equal("own-support value, learned", own["learned"], mean(LEARNED, LEARNED), tol=1e-9)
    c.equal("common-support value, linear", dset["linear"], mean(LINEAR, common), tol=1e-9)
    c.equal("common-support value, learned", dset["learned"], mean(LEARNED, common), tol=1e-9)
    c.check("read on its own support the learned method looks better",
            own["learned"] < own["linear"])
    c.check("read on identical common support the ordering reverses",
            dset["linear"] < dset["learned"])

    # The gap between the two readings is reported as a quantity, not hidden.
    shift = r["support_shift"]
    c.equal("the support shift is reported for the mismatched method",
            shift["linear"]["normalized"],
            dset["linear"] - own["linear"], tol=1e-9)
    c.check("and is zero for the method whose support already equals D",
            shift["learned"]["supports_identical"] is True
            and shift["learned"]["normalized"] == 0.0)

    # Equal result counts must not be mistaken for equal support.
    trimmed = {k: LINEAR[k] for k in ["c1", "c2", "c4"]}
    r2 = audit_precomputed_results(cases(ALL_CASES),
                                   results({"linear": trimmed, "learned": LEARNED}),
                                   LADDER)
    c.equal("two methods reporting equally many cases", len(trimmed), len(LEARNED))
    c.check("equal counts are still not read as equal support",
            r2["common_support"]["D"] < len(trimmed)
            and r2["common_support"]["identical_across_methods"] is False)

    # A clean benchmark must pass, so the flag above is not unconditional.
    r3 = audit_precomputed_results(cases(common),
                                   results({"linear": {k: LINEAR[k] for k in common},
                                            "learned": LEARNED}), LADDER)
    c3 = r3.certificate()
    c.check("identical support is reported as identical",
            r3["common_support"]["identical_across_methods"] is True)
    c.check("a clean benchmark is ranking-admissible",
            c3["ranking_admissible"] is True)
    c.equal("and carries no reason code", c3["reason_codes"], [])
    c.equal("every named structural check passes",
            sorted({v for v in c3["checks"].values()}), ["PASS"])
    c.check("the certificate declares its own schema version",
            isinstance(c3["schema_version"], str)
            and c3["schema_version"].startswith("applicability_audit/"))
    c.check("the package declares a serialization schema version",
            isinstance(aa.SCHEMA_VERSION, str) and bool(aa.SCHEMA_VERSION))

    failed = c.report()
    print("\n  worked example (lower is better):")
    print(f"    on each method's own support : linear {own['linear']:.3f}   "
          f"learned {own['learned']:.3f}   -> learned looks better")
    print(f"    on identical common support  : linear {dset['linear']:.3f}   "
          f"learned {dset['learned']:.3f}   -> the ordering reverses")
    print(f"    support retention on A       : linear "
          f"{cert['coverage']['support_retention']['per_method_conditional_on_A']['linear']:.2f}   "
          f"learned "
          f"{cert['coverage']['support_retention']['per_method_conditional_on_A']['learned']:.2f}")
    print(f"    reported support shift       : linear "
          f"{shift['linear']['normalized']:+.3f}   learned "
          f"{shift['learned']['normalized']:+.3f}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())

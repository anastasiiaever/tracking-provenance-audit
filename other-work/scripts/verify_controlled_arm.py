#!/usr/bin/env python3
"""Verify the released controlled-arm summaries against their frozen records.

The controlled arm of the paper is audited on four populations. None of their
corpora ships here, so this script does not re-measure anything. What it does is
check that every released controlled summary is internally exact and agrees
cell-for-cell with the frozen record it was derived from:

  PoseTrack21   the Gate-1R partition under three segmentation rules, the support
                ladder by gap length, and the sequence-clustered bootstrap
  NTU RGB+D     the support-accounting reclassification and the common-support
                reversal
  BDD100K/MOT17 the object-trajectory Gate-1R partition
  KITTI         the applicability partition and the one frozen hypothesis
  JTA           the within-corpus structural replication partition
  learned models the noise-sensitivity grid and the frozen input contract

Needs no dataset, no checkpoint and no GPU. See docs/DATASETS.md for what a full
re-measurement of each population would require.
"""
from __future__ import annotations

import sys

from _common import Checks, read_csv, read_json

FR = ("provenance", "frozen_records", "controlled")


def close(a, b, tol=1e-12):
    return abs(float(a) - float(b)) <= tol


def check_posetrack(c):
    rows = read_csv("results", "controlled", "posetrack21_applicability.csv")
    rec = read_json(*FR, "56_POSETRACK21_SEGMENTATION_SENSITIVITY.json")

    c.equal("PT21: three segmentation rules audited", len(rows), 3)
    for r in rows:
        v = rec["variants"][r["rule"]]
        g = v["gate_1r"]
        tot = int(r["scoreable_occluded_targets"])
        parts = sum(int(r[k]) for k in ("eligible", "leading", "trailing", "no_anchor"))
        c.equal(f"PT21 [{r['rule']}]: classes partition the targets exactly", parts, tot)
        c.equal(f"PT21 [{r['rule']}]: partition sum agrees with the record", tot, g["sum"])
        c.equal(f"PT21 [{r['rule']}]: eligible count matches the record",
                int(r["eligible"]), g["eligible"])
        c.check(f"PT21 [{r['rule']}]: eligible % recomputes from the integers",
                close(float(r["eligible_pct"]), 100.0 * g["eligible"] / tot, 1e-9))
        c.check(f"PT21 [{r['rule']}]: eligible % + ineligible % = 100",
                close(float(r["eligible_pct"]) + float(r["ineligible_pct"]), 100.0, 1e-9))

    tots = {int(r["scoreable_occluded_targets"]) for r in rows}
    c.equal("PT21: the target count is invariant across all three rules", len(tots), 1)
    c.check("PT21: and the record asserts that invariance",
            rec["internal_validation"]["target_count_invariant_across_rules"] is True)
    c.equal("PT21: invariant target count",
            tots.pop(), rec["internal_validation"]["target_count"])
    c.check("PT21: the frozen primary rule is B",
            rec["frozen_primary_variant"] == "B")
    c.check("PT21: rule B reproduces the prospective result record",
            all(rec["internal_validation"]["variant_B_matches_record_54"][k] is True
                for k in ("variant_B_reproduces_record_54_eligible_count",
                          "variant_B_reproduces_record_54_partition",
                          "variant_B_reproduces_record_54_target_count")))
    c.check("PT21: the primary result was not replaced by the sensitivity analysis",
            rec["confirmations"]["frozen_8_88_percent_replaced"] is False
            and rec["replaces_frozen_values"] is False)
    c.check("PT21: no fourth rule was invented",
            rec["confirmations"]["fourth_rule_invented"] is False)
    c.check("PT21: the analysis ran no reconstruction and no model",
            rec["reconstruction_performed"] is False
            and rec["model_prediction_performed"] is False)

    # support ladder
    sup = read_csv("results", "controlled", "posetrack21_support_by_gap.csv")
    r54 = read_json(*FR, "54_POSETRACK21_PROSPECTIVE_EVALUATION_RESULT.json")
    c.equal("PT21: seven frozen gap lengths", len(sup), len(r54["support"]["frozen_grid"]))
    c.equal("PT21: evaluated cases sum to the released total",
            sum(int(r["cases"]) for r in sup), r54["support"]["evaluated_cases_total"])
    prim = [int(r["gap_length"]) for r in sup if r["in_primary_aggregate"] == "True"]
    c.equal("PT21: primary gap grid", prim, r54["support"]["primary_g"])

    # bootstrap
    bs = read_csv("results", "controlled", "posetrack21_bootstrap.csv")
    r55 = read_json(*FR, "55_POSETRACK21_SEQUENCE_UNCERTAINTY.json")
    marg = [r for r in bs if r["kind"] == "marginal"]
    pair = [r for r in bs if r["kind"] == "paired"]
    c.equal("PT21: marginal estimates released", len(marg), len(r55["results"]))
    c.equal("PT21: paired differences released", len(pair), len(r55["paired_differences"]))
    for r in marg:
        v = r55["results"][r["name"]]
        c.check(f"PT21 bootstrap [{r['name']}]: point estimate matches the record",
                close(r["point_estimate"], v["frozen_point_estimate"]))
        c.check(f"PT21 bootstrap [{r['name']}]: interval brackets the point estimate",
                float(r["ci95_lo"]) <= float(r["point_estimate"]) <= float(r["ci95_hi"]))
    for r in pair:
        v = r55["paired_differences"][r["name"]]
        c.check(f"PT21 paired [{r['name']}]: difference matches the record",
                close(r["point_estimate"], v["observed_difference"]))
        inc = float(r["ci95_lo"]) <= 0.0 <= float(r["ci95_hi"])
        c.check(f"PT21 paired [{r['name']}]: zero-inclusion label agrees with the interval",
                inc == v["interval_includes_zero"]
                and (r["zero"] == "includes zero") == inc)


def check_ntu(c):
    d = read_json("results", "controlled", "ntu_support_accounting.json")
    app, head = d["applicability"], d["headline"]
    c.equal("NTU: result rows", d["n_result_rows"], 25500)
    c.equal("NTU: evaluation cells", app["_n_cells"], 5100)
    c.check("NTU: result rows are a whole number of methods per cell",
            app["_n_rows"] % app["_n_cells"] == 0)
    c.equal("NTU: five methods scored per evaluation cell",
            app["_n_rows"] // app["_n_cells"], 5)
    c.check("NTU: each classical operator is scored once per cell",
            all(app[op]["n_rows"] == app["_n_cells"]
                for op in ("linear", "spline", "kalman")))
    for op in ("linear", "spline", "kalman"):
        a = app[op]
        c.equal(f"NTU [{op}]: 300 cells reclassified", a["n_undefined_cells"], 300)
        c.check(f"NTU [{op}]: failure rate recomputes from the counts",
                close(a["applicability_failure_rate"], a["n_undefined_cells"] / a["n_cells"]))
    c.equal("NTU: affected gap rows", d["n_gap_rows_linear_inapplicable"], 900)
    c.equal("NTU: common support is all rows minus the affected ones",
            head["after"]["n_gaps_common_support"], d["n_gap_rows"] - 900)

    b, a = head["before"], head["after"]
    c.check("NTU: the all-support paired difference favours the autoencoder",
            b["paired_mae_minus_linear"] < 0 and b["ci_excludes_zero"] is True)
    c.check("NTU: the common-support paired difference favours linear",
            a["paired_mae_minus_linear_common_support"] > 0
            and a["ci_excludes_zero_common_support"] is True)
    c.check("NTU: both intervals exclude zero, in opposite directions",
            b["ci_hi"] < 0 < a["ci_lo_common_support"])
    c.check("NTU: all-support interval brackets its estimate",
            b["ci_lo"] <= b["paired_mae_minus_linear"] <= b["ci_hi"])
    c.check("NTU: common-support interval brackets its estimate",
            a["ci_lo_common_support"] <= a["paired_mae_minus_linear_common_support"]
            <= a["ci_hi_common_support"])
    c.check("NTU: the paired difference is mae mean minus linear mean, all support",
            close(b["paired_mae_minus_linear"], b["mae_mean"] - b["linear_mean"], 5e-3))
    c.check("NTU: and on common support",
            close(a["paired_mae_minus_linear_common_support"],
                  a["mae_mean_common_support"] - a["linear_mean_common_support"], 5e-3))
    c.check("NTU: no error value was edited, only the support changed",
            d["source_untouched"] is True)
    c.equal("NTU: the same subject count on both supports",
            b["n_subjects"], a["n_subjects_common_support"])


def check_objecttraj(c):
    rows = read_csv("results", "controlled", "objecttraj_applicability.csv")
    c.equal("object-traj: two populations", len(rows), 2)
    for r in rows:
        tot = int(r["scoreable_targets"])
        parts = sum(int(r[k]) for k in ("eligible", "leading", "trailing", "no_anchor"))
        c.equal(f"object-traj [{r['population']}]: classes partition exactly", parts, tot)
        c.check(f"object-traj [{r['population']}]: the record asserts the partition",
                r["exact_partition"] == "True")
        c.check(f"object-traj [{r['population']}]: fractions sum to one",
                close(sum(float(r[k]) for k in ("eligible_fraction", "leading_fraction",
                                                "trailing_fraction", "no_anchor_fraction")),
                      1.0, 1e-9))
        c.check(f"object-traj [{r['population']}]: eligible fraction recomputes",
                close(float(r["eligible_fraction"]), int(r["eligible"]) / tot, 1e-9))
    c.check("object-traj: the two populations are not pooled",
            len({r["population"] for r in rows}) == 2)


def check_kitti(c):
    rows = read_csv("results", "controlled", "kitti_applicability.csv")
    hyp = read_json("results", "controlled", "kitti_hypothesis.json")
    pooled = next(r for r in rows if r["stratum"] == "all")

    for r in rows:
        tot = int(r["scoreable_targets"])
        parts = sum(int(r[k]) for k in ("eligible", "leading", "trailing", "no_anchor"))
        c.equal(f"KITTI [{r['stratum']}]: classes partition exactly", parts, tot)
        c.equal(f"KITTI [{r['stratum']}]: ineligible is everything but eligible",
                int(r["ineligible"]), tot - int(r["eligible"]))
        c.check(f"KITTI [{r['stratum']}]: ineligible fraction recomputes",
                close(float(r["ineligible_fraction"]), int(r["ineligible"]) / tot, 1e-9))

    occ = [r for r in rows if r["stratum"].startswith("occlusion=")]
    cat = [r for r in rows if r["stratum"].startswith("category=")]
    for name, group in (("occlusion", occ), ("category", cat)):
        c.equal(f"KITTI: {name} strata sum to the pooled total",
                sum(int(r["scoreable_targets"]) for r in group),
                int(pooled["scoreable_targets"]))

    c.equal("KITTI: hypothesis total matches the pooled partition",
            hyp["total_scoreable_targets"], int(pooled["scoreable_targets"]))
    c.equal("KITTI: hypothesis ineligible count matches",
            hyp["ineligible"], int(pooled["ineligible"]))
    c.check("KITTI: the observed fraction clears the pre-frozen threshold",
            hyp["ineligible_fraction"] >= hyp["threshold"])
    c.equal("KITTI: recorded status", hyp["status"], "SUPPORTED")
    c.check("KITTI: the scope disclaims superpopulation inference",
            "no superpopulation claim" in hyp["scope"])



def check_jta(c):
    rows = read_csv("results", "controlled", "jta_applicability.csv")
    rec = read_json(*FR, "51_JTA_PROSPECTIVE_EVALUATION_RESULT.json")
    head = read_json("results", "controlled", "jta_headline.json")
    g = rec["applicability"]["gate_1r"]

    c.equal("JTA: one population row", len(rows), 1)
    r = rows[0]
    tot = int(r["primary_targets"])
    parts = sum(int(r[k]) for k in ("eligible_strictly_interior", "ineligible_leading",
                                    "ineligible_trailing", "no_anchor"))
    c.equal("JTA: classes partition the targets exactly", parts, tot)
    c.equal("JTA: partition sum agrees with the record", int(r["partition_sum"]), g["sum"])
    c.check("JTA: the record asserts the partition", r["exact_partition"] == "True")
    c.check("JTA: eligible rate recomputes from the integers",
            close(float(r["eligible_rate_pct"]),
                  100.0 * int(r["eligible_strictly_interior"]) / tot, 1e-9))
    c.check("JTA: eligible and excluded rates sum to 100",
            close(float(r["eligible_rate_pct"]) + float(r["excluded_undefined_rate_pct"]),
                  100.0, 1e-9))
    c.equal("JTA: excluded-undefined is everything but the eligible class",
            int(r["excluded_undefined"]), tot - int(r["eligible_strictly_interior"]))
    c.equal("JTA: sequence count matches the record", int(r["sequences"]), rec["sequences"])

    c.check("JTA: the learned estimate is far worse than the best classical one",
            head["learned_best_estimate"] > head["classical_best_estimate"])
    c.check("JTA: the reported factor recomputes",
            close(head["learned_worse_than_best_classical_by_factor"],
                  head["learned_best_estimate"] / head["classical_best_estimate"], 1e-9))
    c.check("JTA: the record refuses an architecture-quality reading",
            "NOT" in head["what_this_result_is_NOT"][:40]
            or "not" in head["what_this_result_is_NOT"][:80]
            or "no claim" in head["what_this_result_is_NOT"].lower())
    c.check("JTA: the result is labelled a deployment-sensitivity failure",
            "SENSITIVITY" in head["what_this_result_is"].upper())



def check_learned(c):
    ic = read_json("results", "controlled", "learned_input_contract.json")["input_contract"]
    c.equal("learned: seventeen input slots", ic["slots"], 17)
    c.equal("learned: thirteen available", ic["available"], 13)
    c.equal("learned: four unavailable", len(ic["unavailable_ntu_slots"]), 4)
    c.equal("learned: available plus unavailable equals the slot count",
            ic["available"] + len(ic["unavailable_ntu_slots"]), ic["slots"])
    c.check("learned: unavailable slots are native-invalid, never padded",
            ic["unavailable_state"] == "NATIVE_INVALID" and ic["never_padding"] is True)
    c.check("learned: no confidence channel, and none was synthesized",
            ic["confidence_available"] is False and ic["confidence_synthesized"] is False)

    beta = read_csv("results", "controlled", "learned_beta_by_phi.csv")
    rec = read_json(*FR, "45_THIRD_FAMILY_EVALUATION_RESULT.json")
    c.check("learned: every beta row carries a bracketing interval",
            all(float(r["ci95_lo"]) <= float(r["beta"]) <= float(r["ci95_hi"]) for r in beta))
    c.check("learned: every beta row uses the same subject count",
            len({r["n_subjects"] for r in beta}) == 1)
    fams = {r["family"] for r in beta}
    c.check("learned: the three classical operators are present",
            {"linear", "spline", "kalman"} <= fams)
    c.check("learned: all three checkpoints of the third family are present",
            sum(1 for f in fams if f.startswith("stgcn")) == 3
            or sum(1 for f in fams if "seed" in f) >= 3)

    diag = read_json("results", "controlled", "learned_architecture_diagnostics.json")
    c.check("learned: an estimand is declared", bool(diag["estimand"]))
    c.check("learned: the frozen interpretation is carried, not summarised away",
            isinstance(diag["frozen_interpretation"], dict)
            and len(diag["frozen_interpretation"]) > 0)
    c.check("learned: the release restates that magnitude is unresolved",
            "unresolved" in diag["note"].lower())
    c.check("learned: and that the third family is a probe, not a proposed method",
            "not a proposed method" in diag["note"].lower())


def main() -> int:
    c = Checks("Controlled arm: released summaries vs frozen records")
    check_posetrack(c)
    check_ntu(c)
    check_objecttraj(c)
    check_kitti(c)
    check_jta(c)
    check_learned(c)
    failed = c.report()

    pt = read_csv("results", "controlled", "posetrack21_applicability.csv")
    ntu = read_json("results", "controlled", "ntu_support_accounting.json")
    kit = read_json("results", "controlled", "kitti_hypothesis.json")
    print("\n  headline controlled figures, as released:")
    for r in pt:
        print(f"    PoseTrack21 [{r['rule']:2s}] eligible {float(r['eligible_pct']):6.2f}%"
              f"   ineligible {float(r['ineligible_pct']):6.2f}%"
              f"   of {int(r['scoreable_occluded_targets']):,} scoreable occluded targets")
    b, a = ntu["headline"]["before"], ntu["headline"]["after"]
    print(f"    NTU  all support     ({b['n_gaps']:,} rows): "
          f"mae-linear {b['paired_mae_minus_linear']:+.5f} "
          f"[{b['ci_lo']:+.5f}, {b['ci_hi']:+.5f}]")
    print(f"    NTU  common support  ({a['n_gaps_common_support']:,} rows): "
          f"mae-linear {a['paired_mae_minus_linear_common_support']:+.5f} "
          f"[{a['ci_lo_common_support']:+.5f}, {a['ci_hi_common_support']:+.5f}]")
    print(f"    KITTI ineligible {kit['ineligible']:,}/{kit['total_scoreable_targets']:,} "
          f"= {kit['ineligible_fraction']:.6f}  -> {kit['status']}")
    print("\n  These are read from frozen records, not re-measured. No corpus ships here.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())

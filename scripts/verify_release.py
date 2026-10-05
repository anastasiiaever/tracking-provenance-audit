#!/usr/bin/env python3
"""Run every offline verification in this repository and report one verdict.

This is the single command a reader should need. It runs the four audits, then
checks that the frozen configuration files, the released source constants and the
released result tables still agree with one another.

Needs no dataset, no tracker, no checkpoint and no GPU.
"""
from __future__ import annotations

import os
import subprocess
import sys

import yaml

from _common import Checks, ROOT, path, read_csv, read_json

# The TPAMI tracking paper's own verification stages. The two stages that
# verify the separate common-support paper now live under other-work/ and are
# run from there, so this release's default path covers the tracking paper only.
STAGES = ("verify_ordering.py", "verify_admission.py",
          "verify_mot20_eligibility.py")
OTHER_WORK_STAGES = ("verify_controlled_arm.py", "verify_support_accounting.py")


def run_stages(include_other_work=False):
    codes = {}
    for s in STAGES:
        print(f"\n{'-' * 72}\n$ python scripts/{s}")
        codes[s] = subprocess.call([sys.executable, path("scripts", s)])
    if include_other_work:
        for s in OTHER_WORK_STAGES:
            print(f"\n{'-' * 72}\n$ python other-work/scripts/{s}")
            codes[s] = subprocess.call(
                [sys.executable, path("other-work", "scripts", s)])
    return codes


def cross_checks():
    from tracking_provenance_audit import materiality, metrics, stv

    c = Checks("Cross-file consistency")

    stv_cfg = yaml.safe_load(open(path("configs", "frozen", "admission_stv.yaml")))
    ev_cfg = yaml.safe_load(open(path("configs", "frozen", "evaluator.yaml")))
    mat_cfg = yaml.safe_load(open(path("configs", "frozen", "materiality.yaml")))
    ord_cfg = yaml.safe_load(open(path("configs", "frozen", "ordering.yaml")))

    c.equal("config gate == source gate", stv_cfg["primary_iou_gate"], stv.PRIMARY_IOU_GATE)
    c.equal("config sensitivity grid == source grid",
            list(stv_cfg["sensitivity_gates"]), list(stv.SENSITIVITY_GATES))
    c.equal("config class priority == source class order",
            list(stv_cfg["classes_priority"]), list(stv.CLASSES))
    c.equal("config evaluator pin == source pin",
            ev_cfg["evaluator_commit"], metrics.TRACKEVAL_COMMIT)
    c.equal("config metric set == source metric set",
            list(ev_cfg["metrics"]), list(metrics.METRICS))
    c.equal("config materiality threshold == source threshold",
            mat_cfg["threshold_frozen_at"], materiality.THRESHOLD)
    c.equal("config transition vocabulary == source vocabulary",
            sorted(ord_cfg["classify"]),
            sorted(["UNCHANGED", "FLIP", "TIE_CREATED", "TIE_BROKEN"]))

    # The released tables must only use the frozen vocabulary.
    om = read_csv("results", "mot17", "ordering_matrix.csv")
    c.check("ordering table uses only frozen transitions",
            {r["transition"] for r in om} <= set(ord_cfg["classify"]))
    c.check("ordering table uses only frozen metrics",
            {r["metric"] for r in om} <= set(ev_cfg["metrics"]))

    mb = read_csv("results", "mot17", "metrics_by_state.csv")
    c.check("metric table uses only frozen metrics",
            {r["metric"] for r in mb} <= set(ev_cfg["metrics"]))
    c.check("metric table reports only defined states",
            {r["state"] for r in mb} <= {"R0", "R1", "R2", "S0", "S2"})

    # Every deployment appearing in the ordering matrix must have metric values,
    # and every value in the matrix must match the metric table.
    by = {(r["deployment"], r["state"], r["metric"]): float(r["value"]) for r in mb}
    deps = {r["deployment_a"] for r in om} | {r["deployment_b"] for r in om}
    c.check("every ordered deployment appears in the metric table",
            all(any(k[0] == d for k in by) for d in deps))
    disagree = []
    for r in om:
        for side, state in (("a", "R0"), ("b", "R0"), ("a", "R2"), ("b", "R2")):
            dep = r[f"deployment_{side}"]
            v = by.get((dep, state, r["metric"]))
            if v is None:
                continue
            if abs(v - float(r[f"{side}_{state}"])) > 5e-4:
                disagree.append((dep, state, r["metric"], v, float(r[f"{side}_{state}"])))
    c.check("ordering matrix agrees with the metric table where both carry a value",
            not disagree, f"{len(disagree)} disagreed: {disagree[:2]}")

    # The universe census must cover the datasets the results speak about.
    uni = read_csv("metadata", "postprocessing_universe.csv")
    c.equal("universe census has 24 cells", len(uni), 24)
    c.equal("universe census names 8 pipelines",
            len({r["pipeline"] for r in uni}), 8)
    c.check("every audited MOT17 deployment is in the census",
            {d.replace("-GPR", "") for d in deps} <= {r["pipeline"] for r in uni}
            | {r["pipeline"].replace("-GPR", "") for r in uni})

    # Nothing in the release may claim a dataset or checkpoint ships with it.
    man = read_json("provenance", "RELEASE_MANIFEST.json")
    c.check("release manifest lists every public data file",
            len(man["files"]) > 0)
    c.check("no released file is dataset or checkpoint material",
            all(f["redistribution"] not in ("DATASET_DERIVED", "CHECKPOINT_DERIVED")
                for f in man["files"]))
    return c.report()


def main() -> int:
    codes = run_stages('--with-other-work' in sys.argv)
    print(f"\n{'-' * 72}")
    failed_cross = cross_checks()

    print("\n" + "=" * 72)
    print("RELEASE VERIFICATION SUMMARY")
    print("=" * 72)
    for s, rc in codes.items():
        print(f"  [{'PASS' if rc == 0 else 'FAIL'}] scripts/{s}")
    print(f"  [{'PASS' if not failed_cross else 'FAIL'}] cross-file consistency")
    bad = [s for s, rc in codes.items() if rc != 0] + (["cross-file"] if failed_cross else [])
    if bad:
        print(f"\n  FAILED: {', '.join(bad)}")
        return 1
    print("\n  All offline verifications passed.")
    print("  Note: this verifies the released audit logic and the released summaries.")
    print("  It does not re-run any tracker; see docs/REPRODUCIBILITY.md for that path.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Re-derive the MOT17 pairwise ordering audit from the released metric values.

Reads results/mot17/ordering_matrix.csv, feeds the full-precision R0 and R2
values back through the released ordering engine (src/tracking_provenance_audit/
ordering.py) and checks that every relation, every transition and the headline
summary come out unchanged.

Needs no dataset, no tracker and no GPU.
"""
from __future__ import annotations

import sys

from _common import Checks, read_csv, read_json
from tracking_provenance_audit import ordering

METRICS = ("HOTA", "DetA", "AssA", "IDF1", "MOTA")


def main() -> int:
    rows = read_csv("results", "mot17", "ordering_matrix.csv")
    summary = read_json("results", "mot17", "ordering_summary.json")
    c = Checks("MOT17 ordering audit")

    c.equal("released matrix has 50 cells", len(rows), 50)
    pairs = {(r["deployment_a"], r["deployment_b"]) for r in rows}
    c.equal("10 eligible deployment pairs", len(pairs), 10)
    c.equal("5 metrics per pair", len(rows) // len(pairs), 5)
    c.check("every cell names a frozen metric",
            all(r["metric"] in METRICS for r in rows))

    # Re-derive each relation and transition from the released values.
    rel_bad, trans_bad = [], []
    for r in rows:
        for state in ("R0", "R2"):
            got = ordering.relation(float(r[f"a_{state}"]), float(r[f"b_{state}"]))
            if got != r[f"relation_{state}"]:
                rel_bad.append((r["deployment_a"], r["deployment_b"], r["metric"], state))
        got_t = ordering.transition(r["relation_R0"], r["relation_R2"])
        if got_t != r["transition"]:
            trans_bad.append((r["deployment_a"], r["deployment_b"], r["metric"]))
    c.check("all 100 relations re-derive from the released values", not rel_bad,
            f"{len(rel_bad)} disagreed: {rel_bad[:3]}")
    c.check("all 50 transitions re-derive", not trans_bad,
            f"{len(trans_bad)} disagreed: {trans_bad[:3]}")

    # Margins must be internally consistent with the values they summarise.
    marg_bad = [r for r in rows
                if abs((float(r["a_R0"]) - float(r["b_R0"])) - float(r["margin_R0"])) > 1e-9
                or abs((float(r["a_R2"]) - float(r["b_R2"])) - float(r["margin_R2"])) > 1e-9]
    c.check("every margin equals a - b at both states", not marg_bad,
            f"{len(marg_bad)} inconsistent")

    # The released summary must be exactly what the engine counts.
    engine = ordering.summary([
        dict(a=r["deployment_a"], b=r["deployment_b"], metric=r["metric"],
             r0=r["relation_R0"], r2=r["relation_R2"], transition=r["transition"])
        for r in rows])
    for key in ("n_pairs", "n_cells", "unchanged", "flips", "ties_created",
                "ties_broken", "metric_not_available"):
        c.equal(f"summary.{key}", engine[key], summary["summary"][key])

    # LAYER B. Compare the released matrix against the frozen provenance record
    # instead of trusting the summary's own self-report. The two fields
    # mismatches_against_frozen_matrix and rounding_artifacts are NOT read as
    # assertions here; they are re-derived below and only then compared.
    frozen = read_json("provenance", "frozen_records", "07_ORDERING_MATRIX.json")
    fcells = {(f["a"], f["b"], f["metric"]): f for f in frozen["matrix"]}
    c.equal("frozen record also holds 50 cells", len(fcells), 50)

    key_bad, rel_f_bad, trans_f_bad = [], [], []
    for r in rows:
        k = (r["deployment_a"], r["deployment_b"], r["metric"])
        f = fcells.get(k)
        if f is None:
            key_bad.append(k)
            continue
        if f["r0"] != r["relation_R0"] or f["r2"] != r["relation_R2"]:
            rel_f_bad.append(k)
        if f["transition"] != r["transition"]:
            trans_f_bad.append(k)
    c.check("every released cell exists in the frozen matrix", not key_bad,
            f"{len(key_bad)} missing: {key_bad[:3]}")
    c.check("every relation agrees with the frozen matrix", not rel_f_bad,
            f"{len(rel_f_bad)} disagreed: {rel_f_bad[:3]}")
    c.check("every transition agrees with the frozen matrix", not trans_f_bad,
            f"{len(trans_f_bad)} disagreed: {trans_f_bad[:3]}")

    # re-derived, not read from the summary
    recomputed_mismatches = len(key_bad) + len(rel_f_bad) + len(trans_f_bad)
    c.equal("recomputed mismatch count against the frozen matrix",
            recomputed_mismatches, 0)
    c.equal("the summary's self-reported mismatch count matches the recomputed one",
            summary["mismatches_against_frozen_matrix"], recomputed_mismatches)

    # A rounding artifact would be a cell whose relation depends on the printed
    # precision. Re-derive it: compare the relation at full precision with the
    # relation at the precision the paper prints (3 decimals).
    def _r3(x):
        return round(float(x), 3)
    rounding = [r for r in rows
                if ordering.relation(_r3(r["a_R0"]), _r3(r["b_R0"])) != r["relation_R0"]
                or ordering.relation(_r3(r["a_R2"]), _r3(r["b_R2"])) != r["relation_R2"]]
    c.equal("recomputed rounding-artifact count", len(rounding), 0)
    c.equal("the summary's rounding-artifact count matches the recomputed one",
            summary["rounding_artifacts"], len(rounding))

    # Flip identities must agree with the frozen record, not just the count.
    released_flips = {(r["deployment_a"], r["deployment_b"], r["metric"])
                      for r in rows if r["transition"] == "FLIP"}
    frozen_flips = {k for k, f in fcells.items() if f["transition"] == "FLIP"}
    c.check("flip identities agree with the frozen matrix",
            released_flips == frozen_flips,
            f"released-only {sorted(released_flips - frozen_flips)[:3]} "
            f"frozen-only {sorted(frozen_flips - released_flips)[:3]}")

    # Frozen headline counts must equal the engine's counts.
    for key in ("n_pairs", "n_cells", "unchanged", "flips",
                "ties_created", "ties_broken", "metric_not_available"):
        c.equal(f"frozen summary.{key}", frozen["summary"][key], engine[key])

    # A flip must be a genuine sign change, never a tie.
    flips = [r for r in rows if r["transition"] == "FLIP"]
    c.equal("flip count", len(flips), summary["summary"]["flips"])
    c.check("every flip reverses a strict relation",
            all(r["relation_R0"] != "TIE" and r["relation_R2"] != "TIE"
                and r["relation_R0"] != r["relation_R2"] for r in flips))

    failed = c.report()
    if flips:
        print("\n  flips (post-processing reverses the reported ordering):")
        for r in sorted(flips, key=lambda x: (x["metric"], x["deployment_a"])):
            print(f"    {r['deployment_a']:>13s} vs {r['deployment_b']:<13s} "
                  f"{r['metric']:5s}  {r['relation_R0']:>9s} -> {r['relation_R2']:<9s}"
                  f"  margin {float(r['margin_R0']):+.4f} -> {float(r['margin_R2']):+.4f}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())

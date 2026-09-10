#!/usr/bin/env python3
"""Re-derive the admission (STV) composition and its materiality verdict.

Two independent things are checked.

1. The released MOT17 and MOT20 composition tables are fed back through the
   released materiality rule (src/tracking_provenance_audit/materiality.py) and
   must reproduce the published fractions and verdicts. The four admission
   classes must partition the synthesized set exactly.

2. The admission classifier itself (src/tracking_provenance_audit/stv.py) is run
   on a small hand-built fixture whose correct answer is known by construction,
   so a passing run exercises the released code rather than only re-reading the
   released numbers.

Needs no dataset, no tracker and no GPU.
"""
from __future__ import annotations

import sys

from _common import Checks, read_csv, read_json
from tracking_provenance_audit import materiality, stv
from tracking_provenance_audit.rowid import Row

CLASS_COLS = ("semantically_admitted", "anchor_unmatched",
              "anchor_id_mismatch", "target_reference_absent")


def _row(seq, frame, tid, x, y, w=10.0, h=20.0):
    return Row(seq, frame, tid, x, y, w, h, 1.0, 1.0, ())


def check_engine(c):
    """Run the released classifier on a fixture with a known answer."""
    seq = "FIXTURE-01"
    # Track 1: anchors at frames 1 and 3 both match GT identity 1 -> admitted.
    # Track 2: anchors at frames 1 and 3 match GT identities 2 and 3 -> mismatch.
    # Track 3: anchors sit far from every GT box -> unmatched.
    r0 = [
        _row(seq, 1, 1, 0.0, 0.0), _row(seq, 3, 1, 0.0, 0.0),
        _row(seq, 1, 2, 100.0, 0.0), _row(seq, 3, 2, 200.0, 0.0),
        _row(seq, 1, 3, 900.0, 900.0), _row(seq, 3, 3, 900.0, 900.0),
    ]
    # GT identity 1 is offset so its overlap with track 1 is 0.6: above the
    # frozen 0.5 gate, below the 0.7 probe used at the end of this fixture.
    gt = [
        _row(seq, 1, 1, 0.0, 5.0), _row(seq, 2, 1, 0.0, 5.0), _row(seq, 3, 1, 0.0, 5.0),
        _row(seq, 1, 2, 100.0, 0.0), _row(seq, 2, 2, 100.0, 0.0),
        _row(seq, 3, 3, 200.0, 0.0), _row(seq, 2, 3, 200.0, 0.0),
    ]
    synth = [(seq, 2, 1), (seq, 2, 2), (seq, 2, 3)]
    got = stv.classify(synth, r0, gt, gate=stv.PRIMARY_IOU_GATE)

    c.equal("fixture: matched anchors, reference present -> admitted",
            got[(seq, 2, 1)], stv.SEMANTICALLY_ADMITTED)
    c.equal("fixture: anchors resolve to different identities -> id mismatch",
            got[(seq, 2, 2)], stv.ANCHOR_ID_MISMATCH)
    c.equal("fixture: anchors match no ground truth -> unmatched",
            got[(seq, 2, 3)], stv.ANCHOR_UNMATCHED)

    counts = stv.partition_counts(got)
    c.equal("fixture: the four classes partition the set exactly",
            sum(counts.values()), len(synth))

    # A target whose agreed identity is absent at the target frame.
    gt2 = [g for g in gt if not (g.frame == 2 and g.track_id == 1)]
    got2 = stv.classify([(seq, 2, 1)], r0, gt2, gate=stv.PRIMARY_IOU_GATE)
    c.equal("fixture: agreed identity absent at target frame -> reference absent",
            got2[(seq, 2, 1)], stv.TARGET_REFERENCE_ABSENT)

    # The gate must be applied before assignment: raising it past the fixture's
    # overlap turns a previously admitted row into an unmatched one.
    got3 = stv.classify([(seq, 2, 1)], r0, gt, gate=0.7)
    c.equal("fixture: gate is applied before assignment",
            got3[(seq, 2, 1)], stv.ANCHOR_UNMATCHED)

    c.equal("released primary gate", stv.PRIMARY_IOU_GATE, 0.5)
    c.equal("released sensitivity grid", list(stv.SENSITIVITY_GATES),
            [0.3, 0.4, 0.5, 0.6, 0.7])


def check_table(c, rows, label, r2_rows=None):
    for r in rows:
        dep = r["deployment"]
        if r["n_synthesized"] == "STRUCTURALLY_UNDEFINED":
            c.check(f"{label}: {dep} carries no manufactured composition",
                    all(r[k] == "" for k in CLASS_COLS))
            continue
        total = int(r["n_synthesized"])
        parts = {k: int(r[k]) for k in CLASS_COLS}
        c.equal(f"{label}: {dep} classes partition the synthesized set",
                sum(parts.values()), total)
        non_adm = total - parts["semantically_admitted"]
        c.equal(f"{label}: {dep} non-admitted count", int(r["non_admitted"]), non_adm)
        verdict = materiality.classify(non_adm, total, r2_rows or 0)
        c.equal(f"{label}: {dep} non-admitted fraction",
                float(r["non_admitted_fraction"]),
                verdict["fraction_of_synthesized"], tol=1e-9)
        c.check(f"{label}: {dep} materiality verdict is well-formed",
                verdict["classification"] in (materiality.MATERIAL,
                                              materiality.NOT_MATERIAL))
        c.equal(f"{label}: {dep} verdict is descriptive only",
                verdict["status"], "DESCRIPTIVE")


def main() -> int:
    c = Checks("Admission (STV) composition and materiality")

    check_engine(c)

    mot17 = read_csv("results", "mot17", "stv_composition.csv")
    check_table(c, mot17, "MOT17")

    m20 = read_csv("results", "mot20", "deep_oc_sort_stv.csv")
    agg = [r for r in m20 if r["sequence"] == "ALL"][0]
    per = [r for r in m20 if r["sequence"] != "ALL"]
    total = int(agg["n_synthesized"])
    c.equal("MOT20: per-sequence synthesized rows sum to the total",
            sum(int(r["n_synthesized"]) for r in per), total)
    for k in CLASS_COLS:
        c.equal(f"MOT20: per-sequence {k} sums to the total",
                sum(int(r[k]) for r in per), int(agg[k]))

    res = read_json("results", "mot20", "deep_oc_sort_result.json")
    non_adm = total - int(agg["semantically_admitted"])
    c.equal("MOT20: released non-admitted count", res["nonadmitted"], non_adm)
    v = materiality.classify(non_adm, total, 0)
    c.equal("MOT20: non-admitted fraction of synthesized",
            res["nonadmitted_over_synthesized"], v["fraction_of_synthesized"], tol=1e-12)
    c.equal("MOT20: materiality verdict", res["materiality"], v["classification"])
    c.equal("MOT20: frozen threshold", res["materiality_threshold"], materiality.THRESHOLD)
    c.check("MOT20: the submission-wide companion fraction is reported",
            "nonadmitted_over_R2" in res and res["nonadmitted_over_R2"] is not None)
    c.check("MOT20: the record asserts no interpretation",
            res["interpretation"].upper().startswith("NONE"))

    failed = c.report()

    print("\n  admission composition at the frozen gate tau = 0.5:")
    for r in mot17:
        if r["n_synthesized"] == "STRUCTURALLY_UNDEFINED":
            print(f"    {r['deployment']:>13s}  MOT17  no row-additive decomposition exists")
            continue
        print(f"    {r['deployment']:>13s}  MOT17  {int(r['n_synthesized']):6d} synthesized"
              f"   {float(r['non_admitted_fraction'])*100:5.1f}% not admitted")
    print(f"    {'Deep-OC-SORT':>13s}  MOT20  {total:6d} synthesized"
          f"   {res['nonadmitted_over_synthesized']*100:5.1f}% not admitted"
          f"   ({res['nonadmitted_over_R2']*100:.2f}% of submitted rows)")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())

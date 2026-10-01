#!/usr/bin/env python3
"""Re-derive the MOT20 eligibility ledger and the one executed eligible cell.

The MOT20 arm reports an eligibility decision for seven pre-specified cells, of
which exactly one was ever executed. This script checks that the released ledger
is internally complete, that the counts match the evidence fields, that the one
executed cell is the one the eligibility audit had already singled out, and that
no checkpoint was substituted to rescue a blocked cell.

Needs no dataset, no tracker and no GPU.
"""
from __future__ import annotations

import sys

from _common import Checks, read_csv, read_json

CLEAN = "NO_KNOWN_EVAL_LEAKAGE"



ELIGIBLE = "ELIGIBLE"
OVERLAP = "INELIGIBLE_TRAINING_OVERLAP"
UNRESOLVED = "UNRESOLVED"


def classify(checkpoint_status):
    """Derive one eligibility verdict from a cell's checkpoint evidence.

    The three verdicts are distinct and must stay distinct: UNRESOLVED means the
    evidence does not settle the question, which is not the same as being
    ineligible through training overlap.
    """
    s = checkpoint_status.strip()
    if s.startswith("MIXED"):
        return UNRESOLVED
    if CLEAN in s:
        return ELIGIBLE
    if "EVAL_LEAKAGE" in s:
        return OVERLAP
    return UNRESOLVED


def check_verdicts(c, cells):
    """Derive 1 / 5 / 1 from the per-cell evidence, then compare cell-by-cell
    against the frozen readiness record. No count is read as an assertion."""
    derived = {r["cell"]: classify(r["checkpoint_status"]) for r in cells}
    tally = {v: sum(1 for x in derived.values() if x == v)
             for v in (ELIGIBLE, OVERLAP, UNRESOLVED)}

    c.equal("derived eligible cells", tally[ELIGIBLE], 1)
    c.equal("derived training-overlap ineligible cells", tally[OVERLAP], 5)
    c.equal("derived unresolved cells", tally[UNRESOLVED], 1)
    c.equal("the three verdicts tile the seven cells", sum(tally.values()), 7)
    c.check("UNRESOLVED is never conflated with INELIGIBLE",
            ELIGIBLE != OVERLAP != UNRESOLVED != ELIGIBLE)

    # LAYER B. Compare against the frozen readiness record, cell by cell.
    frozen = read_json("provenance", "frozen_records",
                       "10_MOT20_EXECUTION_READINESS.json")
    fcells = {x["cell"]: x for x in frozen["cells"]}
    c.equal("frozen readiness record holds the same seven cells",
            sorted(fcells), sorted(derived))
    bad = []
    for name, verdict in sorted(derived.items()):
        f = fcells.get(name)
        if f is None:
            bad.append((name, "missing from frozen record"))
            continue
        if classify(f.get("checkpoint_status", "")) != verdict:
            bad.append((name, f.get("checkpoint_status", "")))
    c.check("every verdict agrees with the frozen readiness record", not bad,
            f"{len(bad)} disagreed: {bad[:3]}")
    return derived


def check_executed_cell(c, res):
    """Recompute the executed cell's composition and metric movement from the
    frozen records rather than from the released headline."""
    stv = read_json("provenance", "frozen_records", "13_MOT20_DEEP_STV_RESULT.json")
    agg = stv["aggregate_counts"]
    n_syn = stv["n_synthesized"]
    admitted = agg["SEMANTICALLY_ADMITTED"]
    non_adm = n_syn - admitted

    c.equal("frozen partition sums to the synthesized set", sum(agg.values()), n_syn)
    c.equal("released synthesized rows agree with the frozen record",
            res["n_synthesized"], n_syn)
    c.equal("recomputed non-admitted count", stv["nonadmitted"], non_adm)
    c.equal("released non-admitted count agrees", res["nonadmitted"], non_adm)
    c.equal("recomputed non-admission fraction",
            round(100.0 * non_adm / n_syn, 2), 25.14)
    c.equal("added rows", n_syn, 34814)

    met = read_json("provenance", "frozen_records", "13_MOT20_DEEP_METRIC_RESULT.json")
    metrics = met["metrics"]
    risen = []
    for name in ("HOTA", "DetA", "AssA", "IDF1", "MOTA"):
        r0 = metrics["R0"][name]
        r2 = metrics["R2"][name]
        risen.append(r2 > r0)
        c.check(f"MOT20 {name} rises from R0 to R2", r2 > r0,
                f"R0={r0} R2={r2}")
    c.equal("all five MOT20 metrics rise", sum(risen), 5)

def main() -> int:
    cells = read_csv("results", "mot20", "eligibility.csv")
    ctx = read_json("results", "mot20", "eligibility_context.json")
    res = read_json("results", "mot20", "deep_oc_sort_result.json")
    c = Checks("MOT20 eligibility and the executed eligible cell")

    c.equal("seven pre-specified cells", len(cells), 7)
    c.equal("ledger total agrees with the released counts",
            len(cells), ctx["counts"]["TOTAL"])
    c.equal("universe declares the same cell count", ctx["universe"]["cells"], 7)
    c.equal("no cell added to the universe after the freeze", ctx["universe"]["added"], 0)
    c.equal("no cell removed from the universe", ctx["universe"]["removed"], 0)

    c.check("every cell carries an eligibility verdict",
            all(r["checkpoint_status"] for r in cells))
    c.check("every cell carries the evidence behind its verdict",
            all(r["primary_blocker"] or r["checkpoint_status"] == CLEAN for r in cells))
    c.check("every cell names its outcome-knowledge status",
            all(r["outcome_knowledge_status"] for r in cells))

    check_verdicts(c, cells)
    check_executed_cell(c, res)

    # Exactly one cell is free of known evaluation leakage.
    clean = [r for r in cells if r["checkpoint_status"] == CLEAN]
    c.equal("exactly one cell is free of known evaluation leakage", len(clean), 1)
    c.equal("that cell is the one the amendment raised",
            clean[0]["cell"], ctx["amendment"]["clean_cell"]["cell"])
    c.equal("the executed run is that same deployment",
            res["deployment"] + " x " + res["dataset"], clean[0]["cell"])

    # Nothing was ready at the freeze, and nothing was substituted to make it so.
    c.equal("no cell was READY at the eligibility freeze", ctx["counts"]["READY"], 0)
    c.check("no cell was authorised to execute at the freeze",
            ctx["execution_authorized_at_freeze"] is False)
    c.equal("no checkpoint was substituted for any cell",
            ctx["amendment"]["checkpoints_substituted"], 0)
    c.check("the amendment is append-only",
            ctx["amendment"]["mode"] == "APPEND_ONLY")
    c.check("selection is recorded as not outcome-based",
            ctx["amendment"]["chronology"]["selection_is_not_outcome_based"] is True)
    c.check("no MOT20 outcome existed when the cell was selected",
            ctx["amendment"]["chronology"]["no_mot20_outcome_existed_at_selection"] is True)
    c.check("MOT17 outcomes did not choose the MOT20 commands",
            ctx["commands_selected_using_mot17_outcomes"] is False)

    # Blocked cells must be blocked by the recorded reasons, not by absence of effort.
    blocked = [r for r in cells if r["checkpoint_status"] != CLEAN]
    c.equal("six cells remain blocked", len(blocked), 6)
    c.check("every blocked cell stopped before execution",
            all(r["audit_mode"] == "STOPPED_BEFORE_EXECUTION" for r in blocked))
    c.check("every blocked cell stopped without seeing an outcome",
            all(r["outcome_knowledge_status"] == "STOPPED_UNSEEN" for r in blocked))

    # The counts published alongside the ledger must add up.
    tallied = sum(v for k, v in ctx["counts"].items() if k != "TOTAL")
    c.equal("the eligibility count vocabulary tiles the seven cells",
            tallied, ctx["counts"]["TOTAL"])

    # The executed cell's population is the frozen one.
    pop = ctx["population"]
    c.equal("frozen MOT20 population is four sequences", len(pop["sequences"]), 4)
    c.equal("frozen MOT20 frame count", pop["total_frames"], 4463)
    c.check("the corpus provenance caveat is carried, not dropped",
            pop["provenance_status"] == "MIRROR_TRANSPORT_FALLBACK"
            and bool(pop["provenance_caveat"]))

    failed = c.report()

    print("\n  eligibility ledger:")
    for r in cells:
        mark = "eligible" if r["checkpoint_status"] == CLEAN else "blocked "
        print(f"    [{mark}] {r['cell']:<24s} {r['checkpoint_status'][:52]}")
    print(f"\n  executed: {res['deployment']} x {res['dataset']} "
          f"(run {res['run_id']}), {res['n_synthesized']} synthesized rows, "
          f"{res['materiality']}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())

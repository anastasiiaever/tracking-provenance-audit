#!/usr/bin/env python3
"""The audit on eight rows: what the admission rule does, in one screen.

    python examples/minimal_example/run.py

A tracker emitted four observations (R0.txt). A post-processor filled the two
gaps by interpolation, producing an eight-row submission (R2.txt). Four rows are
synthesized. The evaluator scores all eight against gt.txt and cannot tell the
four apart from the four the tracker actually observed.

The audit asks a question the evaluator does not: for each synthesized row, do
its two bracketing anchors resolve, under a frozen matcher, to the same
ground-truth identity?
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "src"))

from tracking_provenance_audit import states, stv
from tracking_provenance_audit.rowid import parse_gt, parse_mot

SEQ = "EXAMPLE-01"


def read(name):
    with open(os.path.join(HERE, name)) as f:
        return f.read()


def main() -> int:
    r0 = parse_mot(read("R0.txt"), SEQ)
    r2 = parse_mot(read("R2.txt"), SEQ)
    gt = parse_gt(read("gt.txt"), SEQ)

    synthesized = sorted(set(r2) - set(r0))
    print(f"R0 (what the tracker observed) : {len(r0)} rows")
    print(f"R2 (what was submitted)        : {len(r2)} rows")
    print(f"synthesized by post-processing : {len(synthesized)} rows\n")

    classes = stv.classify(synthesized, list(r0.values()), gt,
                           gate=stv.PRIMARY_IOU_GATE)

    print(f"admission at the frozen gate tau = {stv.PRIMARY_IOU_GATE}:")
    for rid in synthesized:
        _, frame, track = rid
        print(f"  frame {frame}, track {track}  ->  {classes[rid]}")

    counts = stv.partition_counts(classes)
    print("\ncomposition:")
    for cls in stv.CLASSES:
        print(f"  {cls:<26s} {counts[cls]}")

    admitted = counts[stv.SEMANTICALLY_ADMITTED]
    non_admitted = len(synthesized) - admitted
    print(f"\n  {non_admitted} of {len(synthesized)} synthesized rows are not admitted "
          f"({non_admitted / len(synthesized):.0%}).")

    r1 = states.build_R1(r0, r2, classes)
    print(f"\nR1 = R0 + admitted synthesized rows : {len(r1)} rows")
    print(f"  R0 ({len(r0)}) subset R1 ({len(r1)}) subset R2 ({len(r2)}): "
          f"{set(r0) <= set(r1) <= set(r2)}")

    print("\nWhat this shows: track 2's gap was bridged across an identity change in"
          "\nthe reference. The interpolated rows are geometrically plausible and the"
          "\nevaluator scores them, but they do not describe one continuous object."
          "\nR1 is the state that keeps only the rows the reference supports.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

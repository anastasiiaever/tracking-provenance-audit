#!/usr/bin/env python3
"""Supplementary Figure S1: margin movement across all cells.

One segment per pairwise cell, from its margin before the transition to its
margin after, on a signed axis, with the zero line and the three- and
two-decimal reporting resolutions marked. Three panels, one per arm.

Source: FINAL_unified_pairwise_margins.csv, the same record behind Table 4 and
supplement Table S32. All 110 cells are plotted; nothing is filtered or binned.
"""
import csv, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import matplotlib.pyplot as plt
from _figstyle import TWOCOL, INK, MID, LIGHT, PALE

R   = "<AUDIT_ROOT>"
FIN = f"{R}/dancetrack_controlled_20261003/final_defense_20261004"
SOT = f"{R}/V6_SOURCE_OF_TRUTH"
OUT = os.path.dirname(os.path.abspath(__file__))

rows = list(csv.DictReader(open(f"{FIN}/FINAL_unified_pairwise_margins.csv")))
ARMS = [("A_MOT17_released_DTI", "(a) MOT17, released", 50),
        ("B_DanceTrack_controlled_DTI", "(b) DanceTrack, controlled \\textsc{linear dti}", 30),
        ("C_DanceTrack_controlled_GSI", "(c) DanceTrack, controlled smoothing", 30)]
TITLE = {"A_MOT17_released_DTI": "(a) MOT17, released",
         "B_DanceTrack_controlled_DTI": "(b) DanceTrack, interpolation",
         "C_DanceTrack_controlled_GSI": "(c) DanceTrack, smoothing"}
yes = lambda v: str(v).strip().upper() in ("YES", "1", "TRUE")

CHECKS = []
def check(label, ok, detail=""):
    CHECKS.append({"check": label, "pass": bool(ok), "detail": detail})
    assert ok, f"{label}: {detail}"

check("110 cells in the record", len(rows) == 110, str(len(rows)))
for key, _, n in ARMS:
    a = [x for x in rows if x["arm"] == key]
    check(f"{key} has {n} cells", len(a) == n, str(len(a)))
led = {x["id"]: x["value"] for x in csv.DictReader(open(f"{SOT}/05_NUMERIC_LEDGER.csv"))}
cross = {k: sum(1 for x in rows if x["arm"] == k and yes(x["zero_crossing"]))
         for k, _, _ in ARMS}
check("MOT17 crossings match M17-CROSS-2DP",
      cross["A_MOT17_released_DTI"] == int(led["M17-CROSS-2DP"]), str(cross))
check("DanceTrack DTI crossings match DTI-CROSS-2DP",
      cross["B_DanceTrack_controlled_DTI"] == int(led["DTI-CROSS-2DP"]), str(cross))
check("DanceTrack GSI crossings match GSI-CROSS-2DP",
      cross["C_DanceTrack_controlled_GSI"] == int(led["GSI-CROSS-2DP"]), str(cross))
for x in rows:
    b, a_ = float(x["margin_before"]), float(x["margin_after"])
    check(f"crossing flag agrees with the signs for {x['arm']} "
          f"{x['tracker_a']}|{x['tracker_b']}|{x['metric']}",
          yes(x["zero_crossing"]) == ((b > 0) != (a_ > 0)),
          f"before {b} after {a_} flag {x['zero_crossing']}")
check("every cell moves", all(abs(float(x["margin_after"]) - float(x["margin_before"])) > 0
                              for x in rows))

fig, axes = plt.subplots(1, 3, figsize=(TWOCOL, 3.00),
                         gridspec_kw={"width_ratios": [50, 30, 30]})
fig.subplots_adjust(wspace=0.16, bottom=0.20, top=0.90, left=0.05, right=0.995)

for ax, (key, _, n) in zip(axes, ARMS):
    arm = [x for x in rows if x["arm"] == key]
    arm.sort(key=lambda x: abs(float(x["margin_before"])))
    for i, x in enumerate(arm):
        b, a_ = float(x["margin_before"]), float(x["margin_after"])
        crosses = yes(x["zero_crossing"])
        ax.plot([i, i], [b, a_], color=INK if crosses else LIGHT,
                lw=1.5 if crosses else 0.8, solid_capstyle="butt",
                zorder=3 if crosses else 2)
        ax.plot([i], [a_], marker="_" if not crosses else "D",
                ms=2.6 if crosses else 3.4, color=INK if crosses else MID,
                mew=0.8, zorder=4)
    ax.axhline(0, color=INK, lw=0.7, zorder=5)
    ax.axhspan(-0.005, 0.005, color=PALE, zorder=0, lw=0)
    ax.axhline( 0.0005, color=MID, lw=0.4, ls=":", zorder=1)
    ax.axhline(-0.0005, color=MID, lw=0.4, ls=":", zorder=1)
    ax.set_title(TITLE[key], fontsize=6.8, loc="left", pad=3)
    ax.set_xlabel(f"{n} cells",
                  fontsize=6.0, labelpad=1.5)
    ax.set_xticks([])
    lo = min(min(float(x["margin_before"]), float(x["margin_after"])) for x in rows)
    hi = max(max(float(x["margin_before"]), float(x["margin_after"])) for x in rows)
    pad = 0.06 * (hi - lo)
    ax.set_ylim(lo - pad, hi + pad)
axes[0].set_ylabel("margin (metric points)")
for ax in axes[1:]: ax.tick_params(labelleft=False)

h = [plt.Line2D([], [], color=INK, lw=1.5),
     plt.Line2D([], [], color=LIGHT, lw=0.8),
     plt.Line2D([], [], color=PALE, lw=6),
     plt.Line2D([], [], color=MID, lw=0.4, ls=":")]
# two rows, so the legend fits inside the text width at 9 pt
fig.legend(h, ["cell whose margin changes sign", "cell whose margin does not",
               "two-decimal reporting resolution", "three-decimal resolution"],
           loc="lower center", ncol=2, bbox_to_anchor=(0.5, -0.085),
           handlelength=1.8, columnspacing=1.8)
fig.savefig(f"{OUT}/figS1_final.pdf", format="pdf", bbox_inches="tight", metadata={"CreationDate": None, "Producer": None, "Creator": None})
json.dump({"checks": CHECKS, "crossings": cross},
          open(f"{OUT}/_figS1_provenance.json", "w"), indent=1)
print(f"figS1_final.pdf written; {len(CHECKS)} assertions, all passed")
print("  crossings per arm:", cross)

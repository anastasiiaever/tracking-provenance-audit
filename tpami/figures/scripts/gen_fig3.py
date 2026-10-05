#!/usr/bin/env python3
"""Figure 3: composition of the added rows across all ten audited columns.

Two panels, released audit above and controlled evaluation below, each bar
normalised to its own synthesized set and segmented in the frozen priority order
ANCHOR UNMATCHED, ANCHOR ID MISMATCH, TARGET REFERENCE ABSENT, SEMANTICALLY
ADMITTED.

Every plotted value is read from the same records that generate Tables 2 and 3
and is asserted against them before the figure is written. No number is copied
from a PDF or retyped.
"""
import csv, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import matplotlib.pyplot as plt
from _figstyle import TWOCOL, INK, MID, LIGHT, PALE, finish

R   = "<AUDIT_ROOT>"
P9  = f"{R}/posthoc_composition_20261003/results"
D1B = f"{R}/dancetrack_controlled_20261003/summaries"
SOT = f"{R}/V6_SOURCE_OF_TRUTH"
OUT = os.path.dirname(os.path.abspath(__file__))

def rows(p):
    with open(p) as fh: return list(csv.DictReader(fh))

CLASSES = ["ANCHOR UNMATCHED", "ANCHOR ID MISMATCH",
           "TARGET REFERENCE ABSENT", "SEMANTICALLY ADMITTED"]
# grayscale-safe: four tones, each also carrying a distinct hatch
FILL  = [PALE, LIGHT, MID, "#ffffff"]
HATCH = ["", "///", "xxx", ""]
EDGE  = INK

# ---------------------------------------------------------------- released arm
b1 = {x["pipeline"]: x for x in rows(f"{P9}/B1_mot17_gate_summary.csv")
      if abs(float(x["iou_gate"]) - 0.5) < 1e-9}
b2 = [x for x in rows(f"{P9}/B2_mot20_gate_summary.csv")
      if abs(float(x["iou_gate"]) - 0.5) < 1e-9][0]
MOT17 = ["ByteTrack", "BoT-SORT", "OC-SORT", "Deep-OC-SORT", "Hybrid-SORT"]

released = []
for p in MOT17:
    x = b1[p]
    released.append((f"{p}\nMOT17", int(x["n_synthesized"]),
                     [int(x["n_unmatched"]), int(x["n_id_mismatch"]),
                      int(x["n_reference_absent"]), int(x["n_admitted"])]))
released.append(("Deep-OC-SORT\nMOT20", int(b2["n_synthesized"]),
                 [int(b2["n_unmatched"]), int(b2["n_id_mismatch"]),
                  int(b2["n_reference_absent"]), int(b2["n_admitted"])]))

# ---------------------------------------------------------------- controlled arm
stv = {x["tracker"]: x for x in rows(f"{D1B}/D1B_stv_primary.csv")}
DANCE = ["ByteTrack", "OC-SORT", "Deep-OC-SORT", "Hybrid-SORT"]
controlled = []
for p in DANCE:
    x = stv[p]
    controlled.append((f"{p}\nDanceTrack", int(x["synthesized"]),
                       [int(x["ANCHOR_UNMATCHED"]), int(x["ANCHOR_ID_MISMATCH"]),
                        int(x["TARGET_REFERENCE_ABSENT"]),
                        int(x["SEMANTICALLY_ADMITTED"])]))

# ---------------------------------------------------------------- assertions
CHECKS = []
def check(label, ok, detail=""):
    CHECKS.append({"check": label, "pass": bool(ok), "detail": detail})
    assert ok, f"{label}: {detail}"

for label, tot, seg in released + controlled:
    check(f"{label.replace(chr(10),' ')} partition sums to the synthesized total",
          sum(seg) == tot, f"{sum(seg)} vs {tot}")
check("ten columns", len(released) + len(controlled) == 10)
check("MOT17 synthesized total is 12,767",
      sum(t for _, t, _ in released[:5]) == 12767,
      str(sum(t for _, t, _ in released[:5])))

# against the table-generating values, not against the typeset tables
tab2 = open(f"{R}/V6_INTEGRATED_20261004/_generated/tab_composition.tex").read()
tab3 = open(f"{R}/V6_INTEGRATED_20261004/_generated/tab_dance.tex").read()
for label, tot, seg in released:
    nm = label.split("\n")[0]
    check(f"Table 2 carries {nm} {tot:,}", f"{tot:,}" in tab2)
for label, tot, seg in controlled:
    nm = label.split("\n")[0]
    check(f"Table 3 carries {nm} {tot:,}", f"{tot:,}" in tab3)

led = {x["id"]: x["value"] for x in rows(f"{SOT}/05_NUMERIC_LEDGER.csv")}
for key, nm, pos in (("M17-ByteTrack-NAPCT", "ByteTrack", 0),
                     ("M17-Hybrid-SORT-NAPCT", "Hybrid-SORT", 4),
                     ("DTI-ByteTrack-NAPCT", "ByteTrack", 0)):
    src = released if key.startswith("M17") else controlled
    _, tot, seg = src[pos]
    pct = 100.0 * sum(seg[:3]) / tot
    check(f"{key} non-admitted share reproduces as {pct:.2f}",
          abs(round(pct, 2) - round(float(led[key]), 2)) < 1e-9,
          f"figure {pct:.4f} vs ledger {led[key]}")
check("TARGET REFERENCE ABSENT empty on every released column",
      all(seg[2] == 0 for _, _, seg in released))
check("TARGET REFERENCE ABSENT non-empty on every controlled column",
      all(seg[2] > 0 for _, _, seg in controlled))

# ---------------------------------------------------------------- draw
fig, axes = plt.subplots(2, 1, figsize=(TWOCOL, 3.05),
                         gridspec_kw={"height_ratios": [6, 4]})
# the per-column "N rows" labels sit outside the axes; leaving room for them
# keeps the tight bounding box at the figure width, so the figure is not
# shrunk when it is placed at \textwidth and its text stays legible
fig.subplots_adjust(hspace=0.70, left=0.175, right=0.995, top=0.93, bottom=0.14)

def panel(ax, data, title):
    ys = list(range(len(data)))[::-1]
    for y, (label, tot, seg) in zip(ys, data):
        left = 0.0
        for k in range(4):
            w = 100.0 * seg[k] / tot
            if w <= 0: continue
            ax.barh(y, w, left=left, height=0.62, facecolor=FILL[k],
                    edgecolor=EDGE, linewidth=0.5, hatch=HATCH[k], zorder=3)
            if w >= 6.0:
                # a white backing box keeps the figure readable where a segment
                # is hatched; the hatch is what carries the class in grayscale
                ax.text(left + w / 2, y, f"{w:.1f}", ha="center", va="center",
                        fontsize=5.6, color="black", zorder=5,
                        bbox=dict(facecolor="white", edgecolor="none",
                                  pad=0.6, alpha=0.92))
            left += w
        ax.text(100.8, y, f"{tot:,} rows", va="center", fontsize=5.8, color=MID)
    ax.set_yticks(ys)
    ax.set_yticklabels([d[0].replace("\n", ", ") for d in data], fontsize=6.3)
    # the "N rows" labels are drawn just past 100; widening the limit keeps them
    # inside the axes so the tight bounding box equals the figure width and the
    # figure is not shrunk when placed at \textwidth
    ax.set_xlim(0, 119); ax.set_xticks([0, 20, 40, 60, 80, 100])
    ax.set_xlabel("per cent of that column's added rows", labelpad=1.5)
    ax.set_title(title, fontsize=7.0, loc="left", pad=3)
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0)

panel(axes[0], released, "(a) released audit: each deployment's own operator at its own parameters")
panel(axes[1], controlled, "(b) controlled evaluation: one operator of ours across four trackers")

handles = [plt.Rectangle((0, 0), 1, 1, facecolor=FILL[k], edgecolor=EDGE,
                         linewidth=0.5, hatch=HATCH[k]) for k in range(4)]
fig.legend(handles, [c.lower() for c in CLASSES], loc="lower center", ncol=4,
           bbox_to_anchor=(0.5, -0.025), handlelength=1.5, columnspacing=1.6)
fig.savefig(f"{OUT}/fig3_final.pdf", format="pdf", bbox_inches="tight", metadata={"CreationDate": None, "Producer": None, "Creator": None})

json.dump({"released": released, "controlled": controlled, "checks": CHECKS},
          open(f"{OUT}/_fig3_provenance.json", "w"), indent=1)
print(f"fig3_final.pdf written; {len(CHECKS)} assertions, all passed")
for c in CHECKS[-6:]: print(f"   {c['check']}")

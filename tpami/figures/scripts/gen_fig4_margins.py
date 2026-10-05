#!/usr/bin/env python3
"""Figure 4: pairwise margin movement, every exhaustive cell, both arms.

Simplified main-text view of the data behind supplement Fig. S1. Shows all
cells, not only the ones that cross zero: margin movement is the measurement and
a zero crossing is a consequence of it.
"""
import csv, json, hashlib, os
import matplotlib.pyplot as plt
import _figstyle as S

ROOT = "<AUDIT_ROOT>"
SRC = f"{ROOT}/dancetrack_controlled_20261003/final_defense_20261004/FINAL_unified_pairwise_margins.csv"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, "..", "fig4_final.pdf"))
PROV = {"figure": "Figure 4, pairwise margin movement", "checks": [], "arms": {}}

def ck(n, c, d=""):
    PROV["checks"].append({"check": n, "pass": bool(c), "detail": str(d)})
    assert c, f"FAILED: {n}: {d}"

def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 16), b""): h.update(b)
    return h.hexdigest()

R = list(csv.DictReader(open(SRC)))
ck("source carries 110 cells", len(R) == 110, len(R))

ARMS = [("A_MOT17_released_DTI", "(a) released audit: MOT17", 50,
         "five released deployments, ten pairs, five metrics"),
        ("B_DanceTrack_controlled_DTI", "(b) controlled evaluation: DanceTrack", 30,
         "four trackers, six pairs, five metrics, one operator")]

fig, axes = plt.subplots(1, 2, figsize=(S.TWOCOL, 2.45),
                         gridspec_kw=dict(wspace=0.17))

for ax, (arm, title, n_expect, sub) in zip(axes, ARMS):
    cells = [x for x in R if x["arm"] == arm]
    ck(f"{arm}: {n_expect} cells", len(cells) == n_expect, len(cells))
    for x in cells:
        b, a = float(x["margin_before"]), float(x["margin_after"])
        declared = x["zero_crossing"].strip().upper() in ("1", "TRUE", "YES")
        actual = (b > 0) != (a > 0)
        ck(f"{arm} {x['tracker_a']}-{x['tracker_b']} {x['metric']}: "
           f"recorded crossing matches the signs", declared == actual,
           f"recorded={x['zero_crossing']} before={b} after={a}")
    # order by the margin before the transition, so the crossing cells are seen
    # to be the ones that started near zero rather than the ones that moved most
    cells.sort(key=lambda x: float(x["margin_before"]))
    cross = sum(1 for x in cells if (float(x["margin_before"]) > 0) != (float(x["margin_after"]) > 0))
    ck(f"{arm}: crossing count", cross == (5 if "MOT17" in arm else 7), cross)
    PROV["arms"][arm] = {"cells": len(cells), "crossings": cross}

    ax.axvline(0.0, color=S.INK, lw=0.7, zorder=1)
    for i, x in enumerate(cells):
        b, a = float(x["margin_before"]), float(x["margin_after"])
        crossing = (b > 0) != (a > 0)
        ax.plot([b, a], [i, i], color=S.INK if crossing else S.LIGHT,
                lw=1.5 if crossing else 0.7, solid_capstyle="butt", zorder=3 if crossing else 2)
        ax.plot([b], [i], marker="o", ms=2.4, mfc="white",
                mec=S.INK if crossing else S.LIGHT, mew=0.7, zorder=4)
        ax.plot([a], [i], marker="o", ms=2.4,
                mfc=S.INK if crossing else S.LIGHT,
                mec=S.INK if crossing else S.LIGHT, mew=0.0, zorder=4)
    ax.set_yticks([])
    ax.set_ylim(-1.5, len(cells) + 0.5)
    ax.set_xlabel("pairwise margin (metric points)", fontsize=6.6, labelpad=1.8)
    ax.set_title(f"{title}\n{sub}", fontsize=6.6, pad=3.0, linespacing=1.3)
    ax.tick_params(pad=1.6)
    ax.text(0.02, 0.97, f"{len(cells)} cells, {cross} cross zero",
            transform=ax.transAxes, fontsize=6.0, va="top", ha="left")
    ax.spines["left"].set_visible(False)

h_b = plt.Line2D([], [], color=S.LIGHT, marker="o", ms=2.4, mfc="white",
                 mec=S.LIGHT, lw=0.7)
h_c = plt.Line2D([], [], color=S.INK, lw=1.5)
fig.legend([h_b, h_c],
           ["one cell: open marker before the transition, filled marker after",
            "cell whose pooled point estimate changes sign"],
           loc="lower center", ncol=2, bbox_to_anchor=(0.5, -0.09),
           handletextpad=0.5, columnspacing=1.6, fontsize=6.2)

S.finish(fig, OUT)
PROV["source"] = {"path": SRC, "sha256": sha(SRC)}
json.dump(PROV, open(os.path.join(HERE, "..", "_fig4_provenance.json"), "w"), indent=1)
print(f"fig4: {len(PROV['checks'])} checks, "
      f"{sum(1 for c in PROV['checks'] if not c['pass'])} failed -> {OUT}")

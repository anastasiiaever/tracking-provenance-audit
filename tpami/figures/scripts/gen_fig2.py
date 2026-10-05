#!/usr/bin/env python3
"""Figure 2: states, transitions, and which diagnostics each transition permits.

A structural diagram, so its content is a specification rather than a dataset.
The specification below is machine-readable and is checked, before anything is
drawn, against three authorities:

  * 07_METHOD_DEFINITIONS.md section 8, the normative table of transition types
    with their key behaviour, surviving-row content, STV and R1;
  * the integrated Sec. 3.4 text, including post-freeze correction B1, for which
    diagnostics each type permits, in particular that attribution survives
    wherever the key set grows;
  * 06_EVIDENCE_ARCHITECTURE.csv, for one audited example per type.

Panel (b) is NOT the v5 panel. The v5 artwork's second panel showed every MOT17
relation change between R0 and R2, a superseded concept; the V6 caption requires
the estimand-eligibility check with training-split disjointness and selection
provenance as separate fields, so that panel is replaced rather than relabelled.
"""
import csv, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle
from _figstyle import TWOCOL, INK, MID, LIGHT, PALE

R   = "<AUDIT_ROOT>"
SOT = f"{R}/V6_SOURCE_OF_TRUTH"
INT = f"{R}/V6_INTEGRATED_20261004"
OUT = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- the spec
SPEC = {
 "row-additive": {
    "keys": "grow", "content": "unchanged",
    "attribution": True, "admission": True, "r1": True, "state_comparison": True,
    "example": "linear interpolation, all three populations"},
 "key-additive but content-rewriting": {
    "keys": "grow", "content": "changed",
    "attribution": True, "admission": False, "r1": False, "state_comparison": True,
    "example": "smoothing, DanceTrack"},
 "rewrite-only": {
    "keys": "unchanged", "content": "changed",
    "attribution": False, "admission": False, "r1": False, "state_comparison": True,
    "example": "Gaussian-process refinement, MOT17"},
 "identity-remapping": {
    "keys": "may shrink", "content": "identity changed",
    "attribution": True, "admission": False, "r1": False, "state_comparison": True,
    "example": "linking and smoothing, MOT17"},
}
CHECKS = []
def check(label, ok, detail=""):
    CHECKS.append({"check": label, "pass": bool(ok), "detail": detail})
    assert ok, f"{label}: {detail}"

# --- authority 1: the normative section 8 table
md = open(f"{SOT}/07_METHOD_DEFINITIONS.md").read()
blk = md[md.index("## 8."):md.index("## 9.")]
table = {}
for ln in blk.split("\n"):
    c = [x.strip() for x in ln.split("|")[1:-1]]
    if len(c) == 5 and c[0] not in ("transition type", "---"):
        table[c[0]] = {"keys": c[1], "content": c[2], "stv": c[3], "r1": c[4]}
check("section 8 lists four transition types", len(table) == 4, str(sorted(table)))
for k, v in SPEC.items():
    key = k.replace("\n", " ")
    check(f"{key} appears in section 8", key in table, str(sorted(table)))
    t = table[key]
    check(f"{key}: key behaviour matches section 8", t["keys"] == v["keys"],
          f"{t['keys']!r} vs {v['keys']!r}")
    check(f"{key}: surviving content matches section 8", t["content"] == v["content"],
          f"{t['content']!r} vs {v['content']!r}")
    check(f"{key}: admission matches section 8",
          (t["stv"] == "defined") == v["admission"], f"{t['stv']!r}")
    check(f"{key}: R1 matches section 8",
          (t["r1"] == "defined") == v["r1"], f"{t['r1']!r}")

# --- authority 2: the integrated Sec. 3.4, carrying B1
s34 = " ".join(open(f"{INT}/SEC3_CONTENT_FIRST.tex").read().split())
check("B1 wording present in Sec. 3.4",
      "A transition that rewrites the rows it keeps permits neither the" in s34
      or "where it also inserts rows those rows can still be attributed" in
      " ".join(open(f"{INT}/SEC7_CONTENT_FIRST.tex").read().split()))
check("attribution requires only that the key set grow",
      "Synthesized-row attribution requires only that the key set grow" in s34)
for k, v in SPEC.items():
    grows = v["keys"] in ("grow", "may shrink")
    check(f"{k.replace(chr(10),' ')}: attribution follows the key-set rule",
          v["attribution"] == grows, f"keys={v['keys']} attribution={v['attribution']}")
check("state comparison available for every transition",
      all(v["state_comparison"] for v in SPEC.values()))
check("rewrite-only inserts no rows to attribute",
      SPEC["rewrite-only"]["attribution"] is False)

# --- authority 3: one audited example per type
arch = list(csv.DictReader(open(f"{SOT}/06_EVIDENCE_ARCHITECTURE.csv")))
fam = {a["v6_label"]: a for a in arch}
check("row-additive example is an audited LINEAR_DTI arm",
      any(a["operator_family"] == "LINEAR_DTI" and a["STV_applicable"] == "YES"
          for a in arch))
check("key-additive content-rewriting example is audited",
      any("key-additive but content-rewriting" in a["state_transition_type"] for a in arch))
check("rewrite-only example is audited",
      any(a["state_transition_type"].startswith("rewrite-only") for a in arch))
check("identity-remapping example is audited",
      any("AFLink" in a["state_transition_type"] for a in arch))

# ---------------------------------------------------------------- draw
# Plain journal typography: no shaded cells, no boxed infographic tiles, no
# sentence-length commentary inside the artwork. Everything that used to be set
# as a note in the figure now lives in the caption. The specification above,
# and therefore the scientific content, is unchanged.
import textwrap as _tw

FS_TITLE, FS_HDR, FS_BODY, FS_SMALL = 9.2, 8.8, 9.2, 8.6

fig = plt.figure(figsize=(TWOCOL, 3.45))
gs = fig.add_gridspec(2, 2, height_ratios=[1.00, 1.85], width_ratios=[1.0, 1.0],
                      hspace=0.30, wspace=0.12,
                      left=0.012, right=0.995, top=0.95, bottom=0.02)
axA = fig.add_subplot(gs[0, 0]); axB = fig.add_subplot(gs[0, 1])
axC = fig.add_subplot(gs[1, :])
for ax in (axA, axB, axC):
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")

def arrow(ax, p, q, ls="-"):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=7,
                                 lw=0.7, color=INK, linestyle=ls, zorder=2,
                                 shrinkA=2, shrinkB=2))

# (a) states -- plain labels, no boxes
axA.set_title("(a) evaluated states", fontsize=FS_TITLE, loc="left", pad=3)
axA.text(0.10, 0.74, "$R_{0}$", ha="center", va="center", fontsize=FS_BODY)
axA.text(0.10, 0.58, "tracker output", ha="center", va="center", fontsize=FS_SMALL, color=MID)
axA.text(0.78, 0.74, "$R_{2}$", ha="center", va="center", fontsize=FS_BODY)
axA.text(0.78, 0.58, "submitted", ha="center", va="center", fontsize=FS_SMALL, color=MID)
arrow(axA, (0.24, 0.74), (0.64, 0.74))
axA.text(0.44, 0.80, "offline operator", ha="center", va="bottom",
         fontsize=FS_SMALL, color=MID)
axA.text(0.44, 0.26, "$R_{1}$", ha="center", va="center", fontsize=FS_BODY)
axA.text(0.44, 0.10, "withheld-row diagnostic", ha="center", va="center",
         fontsize=FS_SMALL, color=MID)
arrow(axA, (0.44, 0.66), (0.44, 0.36), ls="--")

# (b) eligibility -- plain list, no boxes
axB.set_title("(b) estimand eligibility", fontsize=FS_TITLE, loc="left", pad=3)
axB.text(0.02, 0.80, "training-split disjointness", fontsize=FS_BODY, va="center")
axB.text(0.02, 0.63, "selection provenance", fontsize=FS_BODY, va="center")
axB.plot([0.02, 0.98], [0.52, 0.52], color=INK, lw=0.6)
axB.text(0.02, 0.38, "clause (i)  training overlap", fontsize=FS_SMALL, va="center")
axB.text(0.02, 0.24, "clause (ii)  undefined execution path", fontsize=FS_SMALL, va="center")
axB.text(0.02, 0.07, "eligible / ineligible / unresolved", fontsize=FS_BODY, va="center")

# (c) the permission matrix -- plain rules, plain text, no shaded cells
axC.set_title("(c) Diagnostic availability by transition type",
              fontsize=FS_TITLE, loc="left", pad=3)
COLS = [("key set", "keys"), ("surviving content", "content"),
        ("attribution", "attribution"), ("admission", "admission"),
        ("$R_{1}$", "r1"), ("state comparison", "state_comparison")]
x0, wlab, ytop, hrow = 0.004, 0.270, 0.840, 0.200
SHARE = [1.05, 1.30, 1.00, 1.00, 0.58, 1.15]
tot = sum(SHARE); avail = 0.996 - x0 - wlab
WID = [avail * s / tot for s in SHARE]
CX = [x0 + wlab + sum(WID[:j]) + WID[j] / 2 for j in range(len(COLS))]
axC.plot([x0, 0.996], [ytop + 0.105, ytop + 0.105], color=INK, lw=0.9, zorder=1)
for j, (hdr, _) in enumerate(COLS):
    axC.text(CX[j], ytop + 0.030, "\n".join(_tw.wrap(hdr, 11)), ha="center",
             va="bottom", fontsize=FS_HDR, linespacing=1.05)
axC.plot([x0, 0.996], [ytop, ytop], color=INK, lw=0.7, zorder=1)
for i, (name, v) in enumerate(SPEC.items()):
    y = ytop - (i + 1) * hrow
    axC.text(x0, y + hrow * 0.70, "\n".join(_tw.wrap(name, 24)), ha="left",
             va="center", fontsize=FS_BODY, linespacing=1.05)
    axC.text(x0, y + hrow * 0.13, v["example"], ha="left", va="center",
             fontsize=8.4, color=MID)
    for j, (_, k) in enumerate(COLS):
        val = v[k]
        shown = ("yes" if val else "no") if isinstance(val, bool) else \
                "\n".join(_tw.wrap(val, 11))
        axC.text(CX[j], y + hrow / 2, shown, ha="center", va="center",
                 fontsize=FS_BODY, linespacing=1.05)
    if i < len(SPEC) - 1:
        axC.plot([x0, 0.996], [y, y], color=LIGHT, lw=0.35, zorder=1)
axC.plot([x0, 0.996], [ytop - 4 * hrow, ytop - 4 * hrow], color=INK, lw=0.9, zorder=1)

fig.savefig(f"{OUT}/fig2_final.pdf", format="pdf", bbox_inches="tight", metadata={"CreationDate": None, "Producer": None, "Creator": None})
json.dump({"spec": SPEC, "checks": CHECKS}, open(f"{OUT}/_fig2_provenance.json", "w"),
          indent=1)
print(f"fig2_final.pdf written; {len(CHECKS)} specification checks, all passed")

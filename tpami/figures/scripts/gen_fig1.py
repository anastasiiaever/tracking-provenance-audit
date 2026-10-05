#!/usr/bin/env python3
"""Figure 1: what an admitted and a non-admitted added row look like, on frames.

Three panels, exactly the three cases the V6 caption promises. Every coordinate
comes from a frozen state or ground-truth file; every class, anchor identity and
gap bound comes from a frozen audit record. Nothing is drawn that is not asserted
against those records first.

Example selection is by stated rule, not by eye:
  (a) the longest SEMANTICALLY_ADMITTED run in the deployment and sequence used
      by panel (b), so the two MOT17 panels are comparable;
  (b) the example carried by the v5 artwork, re-verified in the frozen record:
      reference identities 15 and 18, BoT-SORT, MOT17-02-FRCNN, track 49;
  (c) among DanceTrack TARGET_REFERENCE_ABSENT rows that lie inside a verified
      internal gap AND overlap a second scoreable identity at or above the gate,
      the one with the longest verified gap, ties broken lexicographically.
"""
import csv, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import matplotlib.pyplot as plt
from _figstyle import TWOCOL, ROLE, INK, MID, LIGHT, panel_label, finish

R    = "<AUDIT_ROOT>"
AUD  = "<MOT_AUDIT_ROOT>"
P9   = f"{R}/posthoc_composition_20261003/results"
D1B  = f"{R}/dancetrack_controlled_20261003"
FIN  = f"{D1B}/final_defense_20261004"
OUT  = os.path.dirname(os.path.abspath(__file__))

def read_mot(path):
    """MOTChallenge rows -> {(frame, id): (cx, cy, w, h)}; cx is the box centre."""
    out = {}
    with open(path) as fh:
        for ln in fh:
            p = ln.strip().split(",")
            if len(p) < 6: continue
            f, i = int(p[0]), int(p[1])
            x, y, w, h = (float(p[2]), float(p[3]), float(p[4]), float(p[5]))
            out[(f, i)] = (x + w / 2.0, y + h / 2.0, w, h)
    return out

def seq_length(seq):
    import configparser
    c = configparser.ConfigParser()
    c.read(f"{AUD}/datasets/mot/train/{seq}/seqinfo.ini")
    return int(c["Sequence"]["seqLength"])

def read_gt(path):
    """Scoreable ground truth only: mark != 0 and class == 1, as the evaluator
    preprocesses the MOTChallenge two-dimensional box task."""
    out = {}
    with open(path) as fh:
        for ln in fh:
            p = ln.strip().split(",")
            if len(p) < 8: continue
            mark, cls = float(p[6]), int(float(p[7]))
            if mark == 0 or cls != 1: continue
            f, i = int(p[0]), int(p[1])
            x, y, w, h = (float(p[2]), float(p[3]), float(p[4]), float(p[5]))
            out[(f, i)] = (x + w / 2.0, y + h / 2.0, w, h)
    return out

PROV = []        # provenance rows, written out for FINAL_FIGURE_PROVENANCE.md
def note(**kw): PROV.append(kw)

# ---------------------------------------------------------------- panel data
c6 = [x for x in csv.DictReader(open(f"{P9}/C6_identity_support_rows.csv"))
      if x["population"] == "mot17"]
PIPE, SEQ = "BoT-SORT", "MOT17-02-FRCNN"

def contiguous_runs(rows):
    from collections import defaultdict
    g = defaultdict(list)
    for x in rows: g[x["track_id"]].append(int(x["frame"]))
    out = []
    for tid, fs in g.items():
        fs = sorted(fs); s = p = fs[0]
        for f in fs[1:] + [None]:
            if f != p + 1:
                out.append((tid, s, p)); s = f
            if f is not None: p = f
        
    return out

# --- (a) admitted
adm = [x for x in c6 if x["stv_class"] == "SEMANTICALLY_ADMITTED"
       and x["pipeline"] == PIPE and x["sequence"] == SEQ
       and x["left_anchor_id"] == x["right_anchor_id"] and x["left_anchor_id"] != "-1"]
runs_a = sorted(contiguous_runs(adm), key=lambda r: (-(r[2] - r[1]), int(r[0])))
tid_a, f0_a, f1_a = runs_a[0]
ref_a = {x["left_anchor_id"] for x in adm if x["track_id"] == tid_a
         and f0_a <= int(x["frame"]) <= f1_a}
assert len(ref_a) == 1, f"panel (a): {len(ref_a)} anchor identities, expected 1"
ref_a = int(ref_a.pop())

# --- (b) id mismatch, the v5 example re-verified
idm = [x for x in c6 if x["stv_class"] == "ANCHOR_ID_MISMATCH"
       and x["pipeline"] == PIPE and x["sequence"] == SEQ and x["track_id"] == "49"
       and {x["left_anchor_id"], x["right_anchor_id"]} == {"15", "18"}]
assert idm, "panel (b): the v5 example is absent from the frozen record"
fr_b = sorted(int(x["frame"]) for x in idm)
assert fr_b == list(range(fr_b[0], fr_b[-1] + 1)), "panel (b): run is not contiguous"
tid_b, f0_b, f1_b = "49", fr_b[0], fr_b[-1]
refL_b, refR_b = 15, 18

# --- (c) DanceTrack target reference absent
ab = [x for x in csv.DictReader(open(f"{FIN}/D1B2_reference_absent_local_support.csv"))
      if x["another_gt_identity_overlaps"] == "1" and x["bucket"] == "GE_GATE"
      and x["inside_verified_internal_gt_gap"] == "1"]
ab.sort(key=lambda x: (-(int(x["gt_next"]) - int(x["gt_prev"])), x["tracker"],
                       x["sequence"], int(x["frame"]), int(x["track_id"])))
pick = ab[0]
TRK_C, SEQ_C, TID_C = pick["tracker"], pick["sequence"], pick["track_id"]
GAP_PREV, GAP_NEXT = int(pick["gt_prev"]), int(pick["gt_next"])
REF_C, OTHER_C = int(pick["anchor_gt_id"]), int(pick["max_iou_gt_id"])
# The rule selects one row; the panel must show the whole contiguous synthesized
# run that row belongs to, not the sub-range that happens to satisfy the
# selection filter. The run is taken from the states and every frame in it is
# then required to be TARGET_REFERENCE_ABSENT in the frozen record.
_absent_all = [x for x in csv.DictReader(
                   open(f"{FIN}/D1B2_reference_absent_local_support.csv"))
               if x["tracker"] == TRK_C and x["sequence"] == SEQ_C
               and x["track_id"] == TID_C]
rows_c = sorted(int(x["frame"]) for x in _absent_all
                if GAP_PREV < int(x["frame"]) < GAP_NEXT)
assert rows_c, "panel (c): no rows inside the selected gap"
assert rows_c == list(range(rows_c[0], rows_c[-1] + 1)), \
    "panel (c): the absent-class rows are not one contiguous run"
assert pick["intended_reference_identity_present_at_frame"] == "0", \
    "panel (c): the intended identity must be absent at the frame"

# ---------------------------------------------------------------- raw states
# The MOT17 validation half is the second half of each sequence, re-indexed from
# 1 in the state files and in every frozen record; the ground-truth files keep the
# original numbering. The offset is seqLength // 2, and the check below is a
# validation of the admission labels as well as of the offset: every MOT17
# SEMANTICALLY_ADMITTED row must have its anchor-resolved identity present as
# scoreable ground truth at that row's own frame.
OFFSET = seq_length(SEQ) // 2

def _verify_offset():
    import collections
    gt_ids = collections.defaultdict(set)
    for ln in open(f"{AUD}/datasets/mot/train/{SEQ}/gt/gt.txt"):
        q = ln.strip().split(",")
        if len(q) < 8 or float(q[6]) == 0 or int(float(q[7])) != 1: continue
        gt_ids[int(q[1])].add(int(q[0]))
    rows = [x for x in c6 if x["sequence"] == SEQ
            and x["stv_class"] == "SEMANTICALLY_ADMITTED"
            and x["left_anchor_id"] == x["right_anchor_id"] != "-1"]
    ok = sum(1 for x in rows
             if int(x["frame"]) + OFFSET in gt_ids[int(x["left_anchor_id"])])
    assert ok == len(rows), (f"{SEQ}: {ok} of {len(rows)} admitted rows reconcile "
                             f"with offset {OFFSET}")
    return len(rows)
N_RECONCILED = _verify_offset()

r0m = read_mot(f"{AUD}/states/BoTSORT/R0/{SEQ}.txt")
r2m = read_mot(f"{AUD}/states/BoTSORT/R2/{SEQ}.txt")
gtm = read_gt(f"{AUD}/datasets/mot/train/{SEQ}/gt/gt.txt")
slug = {"ByteTrack": "bytetrack", "OC-SORT": "ocsort",
        "Deep-OC-SORT": "deepocsort", "Hybrid-SORT": "hybridsort"}[TRK_C]
r0d = read_mot(f"{D1B}/r0/{slug}/{SEQ_C}.txt")
r2d = read_mot(f"{D1B}/r2_primary/{slug}/{SEQ_C}.txt")
gtd = read_gt(f"{D1B}/inputs/gt/DANCE-val/{SEQ_C}/gt/gt.txt")

def added_and_anchors(r0, r2, tid, f0, f1, label):
    """Assert the synthesized rows really are in R2 and absent from R0, and
    return them with the two bracketing R0 anchors."""
    tid = int(tid)
    added = []
    for f in range(f0, f1 + 1):
        assert (f, tid) in r2, f"{label}: frame {f} missing from R2"
        assert (f, tid) not in r0, f"{label}: frame {f} is present in R0, not synthesized"
        added.append((f, r2[(f, tid)][0]))
    left = max((f for (f, i) in r0 if i == tid and f < f0), default=None)
    right = min((f for (f, i) in r0 if i == tid and f > f1), default=None)
    assert left is not None and right is not None, f"{label}: anchors missing in R0"
    anchors = [(left, r0[(left, tid)][0]), (right, r0[(right, tid)][0])]
    return added, anchors

add_a, anc_a = added_and_anchors(r0m, r2m, tid_a, f0_a, f1_a, "panel (a)")
add_b, anc_b = added_and_anchors(r0m, r2m, tid_b, f0_b, f1_b, "panel (b)")
add_c, anc_c = added_and_anchors(r0d, r2d, TID_C, rows_c[0], rows_c[-1], "panel (c)")

def gt_track(gt, ident, lo, hi, offset=0):
    """Ground-truth centres for one identity, returned on the record's frame axis."""
    return sorted((f - offset, gt[(f, ident)][0]) for (f, i) in gt
                  if i == ident and lo + offset <= f <= hi + offset)

# panel (c): the intended identity must genuinely be absent across the drawn gap
for f in range(GAP_PREV + 1, GAP_NEXT):
    assert (f, REF_C) not in gtd, f"panel (c): identity {REF_C} present at frame {f}"
assert (GAP_PREV, REF_C) in gtd and (GAP_NEXT, REF_C) in gtd, \
    "panel (c): the gap bounds must themselves be annotated"

# ---------------------------------------------------------------- draw
fig, axes = plt.subplots(1, 3, figsize=(TWOCOL, 1.95))
fig.subplots_adjust(wspace=0.30, bottom=0.30, top=0.88)

def draw(ax, added, anchors, tracks, gaps=(), xlab="frame"):
    for ident, pts, role in tracks:
        if not pts: continue
        ax.plot([p[0] for p in pts], [p[1] for p in pts], **ROLE[role],
                label=("anchor-resolved reference identity"
                       if role=="reference" else "another scoreable identity"), zorder=2)
    for lo, hi, y0, y1 in gaps:
        ax.plot([lo, hi], [y0, y1], **ROLE["gap"], zorder=1)
    ax.plot([p[0] for p in added], [p[1] for p in added], **ROLE["added"],
            label="added row", zorder=4)
    ax.plot([p[0] for p in anchors], [p[1] for p in anchors], **ROLE["anchor"],
            label="$R_{0}$ anchor", zorder=5)
    ax.set_xlabel(xlab)

# (a)
tr_a = gt_track(gtm, ref_a, anc_a[0][0], anc_a[1][0], OFFSET)
assert tr_a, "panel (a): the reference identity has no scoreable GT in the window"
draw(axes[0], add_a, anc_a, [(ref_a, tr_a, "reference")])
axes[0].set_ylabel("box centre $x$ (px)")
axes[0].set_title("(a) admitted, MOT17",
                  fontsize=6.8, pad=4, loc="left")

# (b)
trL = gt_track(gtm, refL_b, anc_b[0][0], anc_b[1][0], OFFSET)
trR = gt_track(gtm, refR_b, anc_b[0][0], anc_b[1][0], OFFSET)
assert trL and trR, "panel (b): a reference identity has no scoreable GT in the window"
draw(axes[1], add_b, anc_b, [(refL_b, trL, "reference"), (refR_b, trR, "reference_other")])
axes[1].set_title("(b) anchor id mismatch, MOT17",
                  fontsize=6.8, pad=4, loc="left")

# (c)
pre  = gt_track(gtd, REF_C, GAP_PREV - 20, GAP_PREV)
post = gt_track(gtd, REF_C, GAP_NEXT, GAP_NEXT + 20)
oth  = gt_track(gtd, OTHER_C, GAP_PREV - 20, GAP_NEXT + 20)
draw(axes[2], add_c, anc_c,
     [(REF_C, pre, "reference"), (REF_C, post, "reference"),
      (OTHER_C, oth, "reference_other")],
     gaps=[(GAP_PREV, GAP_NEXT, pre[-1][1], post[0][1])] if pre and post else [])
axes[2].set_title("(c) target reference absent, DanceTrack",
                  fontsize=6.8, pad=4, loc="left")
axes[2].annotate("reference identity absent\nacross this gap",
                 xy=((GAP_PREV + GAP_NEXT) / 2, (pre[-1][1] + post[0][1]) / 2),
                 xytext=(0.02, 0.97), textcoords="axes fraction", fontsize=5.8,
                 va="top",
                 color=MID, arrowprops=dict(arrowstyle="-", lw=0.5, color=LIGHT))

h, l = axes[0].get_legend_handles_labels()
h2, l2 = axes[2].get_legend_handles_labels()
seen, H, L = set(), [], []
for hh, ll in list(zip(h, l)) + list(zip(h2, l2)):
    if ll in seen: continue
    seen.add(ll); H.append(hh); L.append(ll)
fig.legend(H, L, loc="lower center", ncol=4, bbox_to_anchor=(0.5, -0.02),
           handlelength=1.8, columnspacing=1.8)

fig.savefig(f"{OUT}/fig1_final.pdf", format="pdf", metadata={"CreationDate": None, "Producer": None, "Creator": None})

# ---------------------------------------------------------------- provenance
note(panel="1(a)", case="SEMANTICALLY_ADMITTED",
     frame_convention=f"records index the validation half from 1; ground truth keeps "
                      f"the original numbering, offset seqLength//2 = {OFFSET} for {SEQ}. "
                      f"Verified: {N_RECONCILED} of {N_RECONCILED} admitted rows in {SEQ} "
                      f"have their anchor-resolved identity present at that frame",
     example=f"{PIPE}, {SEQ}, track {tid_a}, frames {f0_a}-{f1_a}, reference identity {ref_a}",
     record="C6_identity_support_rows.csv (stv_class, left_anchor_id, right_anchor_id)",
     coords=f"states/BoTSORT/R0|R2/{SEQ}.txt; datasets/mot/train/{SEQ}/gt/gt.txt",
     rule="longest admitted run in the panel-(b) deployment and sequence",
     rounded="no", reused_old_art="no")
note(panel="1(b)", case="ANCHOR_ID_MISMATCH",
     example=f"{PIPE}, {SEQ}, track {tid_b}, frames {f0_b}-{f1_b}, "
             f"reference identities {refL_b} and {refR_b}",
     record="C6_identity_support_rows.csv",
     coords=f"states/BoTSORT/R0|R2/{SEQ}.txt; datasets/mot/train/{SEQ}/gt/gt.txt",
     rule="the v5 artwork's example, re-verified as a contiguous run in the frozen record",
     rounded="no", reused_old_art="no, redrawn from the record")
note(panel="1(c)", case="TARGET_REFERENCE_ABSENT",
     example=f"{TRK_C}, {SEQ_C}, track {TID_C}, frames {rows_c[0]}-{rows_c[-1]}, "
             f"anchor-resolved identity {REF_C}, gap {GAP_PREV}-{GAP_NEXT}, "
             f"second overlapping identity {OTHER_C}",
     record="D1B2_reference_absent_local_support.csv (anchor_gt_id, gt_prev, gt_next, "
            "max_iou_gt_id, another_gt_identity_overlaps, inside_verified_internal_gt_gap)",
     coords=f"r0|r2_primary/{slug}/{SEQ_C}.txt; inputs/gt/DANCE-val/{SEQ_C}/gt/gt.txt",
     rule="longest verified internal gap among rows overlapping a second identity "
          "at or above the gate; ties lexicographic",
     rounded="no", reused_old_art="no")
import json
json.dump(PROV, open(f"{OUT}/_fig1_provenance.json", "w"), indent=1)
print("fig1_final.pdf written")
for p in PROV: print(f"  {p['panel']}: {p['example']}")

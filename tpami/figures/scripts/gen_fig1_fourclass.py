#!/usr/bin/env python3
"""Figure 1: all four admission classes, on real dataset frames.

2x2 layout; each class shows three frames -- left R_0 anchor, the synthesized
row, right R_0 anchor. Every displayed row is verified against the frozen V7
records before it is drawn; the script aborts rather than drawing an unverified
case. No trajectory plots: those moved to supplement Fig. S2.

Frame conventions, derived not assumed. MOT17-02-FRCNN: audit indexes the
validation half 1..299 and so do the state files and the TrackEval val-half
ground truth, so every lookup is offset-free; only the image file name needs
image_frame = audit_frame + 301, and 301 is the unique offset at which all
15,430 val-half GT rows reproduce in the original annotation file.
dancetrack0026: audit GT is byte-identical to the dataset GT, offset 0.
"""
import csv, json, hashlib, os, sys
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.gridspec import GridSpecFromSubplotSpec
import _figstyle as S

ROOT = "<AUDIT_ROOT>"
MOT = "<MOT_AUDIT_ROOT>"
DT = "<DATASETS_ROOT>/dancetrack/val"
DTC = f"{ROOT}/dancetrack_controlled_20261003"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, "..", "fig1_final.pdf"))

REC_MOT = f"{ROOT}/posthoc_composition_20261003/results/C6_identity_support_rows.csv"
REC_ABS = f"{DTC}/final_defense_20261004/D1B2_reference_absent_local_support.csv"
GT_MOT = f"{MOT}/repos/TrackEval/data/gt/mot_challenge/MOT17-val_half/MOT17-02-FRCNN/gt/gt.txt"
GT_MOT_ORIG = f"{MOT}/datasets/mot/train/MOT17-02-FRCNN/gt/gt.txt"
GT_DT = f"{DTC}/inputs/gt/DANCE-val/dancetrack0026/gt/gt.txt"
R0_MOT = f"{MOT}/states/ByteTrack/R0/MOT17-02-FRCNN.txt"
R2_MOT = f"{MOT}/states/ByteTrack/R2/MOT17-02-FRCNN.txt"
R0_DT = f"{DTC}/r0/bytetrack/dancetrack0026.txt"
R2_DT = f"{DTC}/r2_primary/bytetrack/dancetrack0026.txt"

PROV = {"figure": "Figure 1, four-class admission taxonomy on dataset frames",
        "panels": [], "checks": []}

def ck(name, cond, detail=""):
    PROV["checks"].append({"check": name, "pass": bool(cond), "detail": str(detail)})
    assert cond, f"FAILED: {name}: {detail}"

def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 16), b""):
            h.update(b)
    return h.hexdigest()

def states(path):
    d = {}
    for line in open(path):
        f = line.strip().split(",")
        if len(f) >= 6:
            d.setdefault(int(f[0]), {})[int(f[1])] = tuple(float(v) for v in f[2:6])
    return d

def scoreable_gt(path):
    d = {}
    for line in open(path):
        f = line.strip().split(",")
        if len(f) < 8 or int(float(f[6])) == 0 or int(float(f[7])) != 1:
            continue
        d.setdefault(int(f[0]), {})[int(f[1])] = tuple(float(v) for v in f[2:6])
    return d

def derive_mot_offset():
    def rows(p):
        out = set()
        for line in open(p):
            f = line.strip().split(",")
            if len(f) >= 6:
                out.add((int(f[0]), int(f[1]), round(float(f[2]), 1), round(float(f[3]), 1)))
        return out
    reb, orig = rows(GT_MOT), rows(GT_MOT_ORIG)
    good = [o for o in range(290, 315) if all((f + o, i, x, y) in orig for (f, i, x, y) in reb)]
    ck("MOT17-02 image offset is unique and derived", len(good) == 1, f"{good}, {len(reb)} rows")
    return good[0]

OFFSET_MOT = derive_mot_offset()
r0m, r2m, gtm = states(R0_MOT), states(R2_MOT), scoreable_gt(GT_MOT)
r0d, r2d, gtd = states(R0_DT), states(R2_DT), scoreable_gt(GT_DT)

# ------------------------------------------------------------- case records

def mot_case(track, lo, hi, want, want_case=None):
    R = [x for x in csv.DictReader(open(REC_MOT))
         if x["pipeline"] == "ByteTrack" and x["sequence"] == "MOT17-02-FRCNN"
         and int(x["track_id"]) == track and lo <= int(x["frame"]) <= hi]
    R.sort(key=lambda x: int(x["frame"]))
    ck(f"track {track}: run {lo}-{hi} present and contiguous",
       [int(x["frame"]) for x in R] == list(range(lo, hi + 1)), f"{len(R)} rows")
    ck(f"track {track}: every row is {want}",
       all(x["stv_class"] == want for x in R), sorted({x["stv_class"] for x in R}))
    if want_case:
        ck(f"track {track}: anchor case is {want_case}",
           {x["anchor_case"] for x in R} == {want_case}, {x["anchor_case"] for x in R})
    L = sorted({x["left_anchor_id"] for x in R}); Rt = sorted({x["right_anchor_id"] for x in R})
    ck(f"track {track}: one left and one right anchor identity", len(L) == 1 and len(Rt) == 1, f"{L} {Rt}")
    return R, int(L[0]), int(Rt[0])

ADM, A_L, A_R = mot_case(26, 51, 61, "SEMANTICALLY_ADMITTED", "A")
UNM, U_L, U_R = mot_case(36, 44, 50, "ANCHOR_UNMATCHED", "C")
MIS, M_L, M_R = mot_case(33, 232, 239, "ANCHOR_ID_MISMATCH", "B")
ck("admitted: both anchors resolve to the same identity", A_L == A_R, f"{A_L}=={A_R}")
ck("unmatched: exactly one anchor has no reference match",
   (U_L == -1) ^ (U_R == -1), f"L={U_L} R={U_R}")
ck("mismatch: anchors resolve to different identities", M_L != M_R and -1 not in (M_L, M_R),
   f"L={M_L} R={M_R}")

ABS_ = [x for x in csv.DictReader(open(REC_ABS))
        if x["tracker"] == "ByteTrack" and x["sequence"] == "dancetrack0026"
        and int(x["track_id"]) == 210 and 192 <= int(x["frame"]) <= 208]
ABS_.sort(key=lambda x: int(x["frame"]))
ck("absent: run 192-208 present and contiguous",
   [int(x["frame"]) for x in ABS_] == list(range(192, 209)), len(ABS_))
B_ID = sorted({int(x["anchor_gt_id"]) for x in ABS_})
ck("absent: one anchor-resolved identity", len(B_ID) == 1, B_ID); B_ID = B_ID[0]
ck("absent: every row inside a verified internal GT gap",
   all(x["inside_verified_internal_gt_gap"] == "1" for x in ABS_), "")
ck("absent: intended identity absent at every frame",
   all(x["intended_reference_identity_present_at_frame"] == "0" for x in ABS_), "")
ck("absent: another scoreable identity overlaps at every frame",
   all(x["another_gt_identity_overlaps"] == "1" for x in ABS_), "")
ck("absent: a single gap, 191 -> 209",
   {int(x["gt_prev"]) for x in ABS_} == {191} and {int(x["gt_next"]) for x in ABS_} == {209}, "")
B_OTHER = int([x for x in ABS_ if int(x["frame"]) == 200][0]["max_iou_gt_id"])

def anchors(r0, track, lo, hi):
    la = max(f for f in r0 if f < lo and track in r0[f])
    ra = min(f for f in r0 if f > hi and track in r0[f])
    ck(f"anchors bracket {lo}-{hi} for track {track}", la < lo and ra > hi, f"{la},{ra}")
    return la, ra

def synth(r0, r2, track, lo, hi):
    out = {}
    for f in range(lo, hi + 1):
        ck(f"row ({f},{track}) present in R2", track in r2.get(f, {}), "")
        ck(f"row ({f},{track}) absent from R0", track not in r0.get(f, {}), "")
        out[f] = r2[f][track]
    return out

# ----------------------------------------------------------------- panels
# Each panel: three frames. The middle frame carries the synthesized row; the
# outer two carry the R_0 anchors and the reference identity each anchor
# resolves to, which is what makes the class visible rather than asserted.
def build(tag, cls, dataset, seq, track, lo, hi, r0, r2, gt, imgdir, pat, offset,
          ids_at, note=None, gap=None):
    la, ra = anchors(r0, track, lo, hi)
    add = synth(r0, r2, track, lo, hi)
    mid = (lo + hi) // 2
    return dict(tag=tag, cls=cls, dataset=dataset, seq=seq, track=track, lo=lo, hi=hi,
                la=la, ra=ra, mid=mid, add=add, r0=r0, gt=gt, imgdir=imgdir, pat=pat,
                offset=offset, ids_at=ids_at, note=note, gap=gap)

MOTIMG = f"{MOT}/datasets/mot/train/MOT17-02-FRCNN/img1"
PANELS = [
 build("(a)", "SEMANTICALLY ADMITTED", "MOT17", "MOT17-02-FRCNN", 26, 51, 61,
       r0m, r2m, gtm, MOTIMG, "%06d.jpg", OFFSET_MOT,
       ids_at=lambda f: [A_L]),
 build("(b)", "ANCHOR UNMATCHED", "MOT17", "MOT17-02-FRCNN", 36, 44, 50,
       r0m, r2m, gtm, MOTIMG, "%06d.jpg", OFFSET_MOT,
       # the left anchor matches no scoreable reference at the gate, so no
       # reference box is drawn there; the right anchor resolves to GT 32
       ids_at=lambda f, U_R=U_R: ([] if f == 43 else [U_R]),
       note=("no GT match", None, None)),
 build("(c)", "ANCHOR ID MISMATCH", "MOT17", "MOT17-02-FRCNN", 33, 232, 239,
       r0m, r2m, gtm, MOTIMG, "%06d.jpg", OFFSET_MOT,
       # each anchor frame shows only the identity THAT anchor resolves to, so
       # the two different identities are explicit across the three frames
       ids_at=lambda f, M_L=M_L, M_R=M_R: ([M_L] if f == 231 else
                                           [M_R] if f == 240 else [M_L, M_R])),
 build("(d)", "TARGET REFERENCE ABSENT", "DanceTrack", "dancetrack0026", 210, 192, 208,
       r0d, r2d, gtd, f"{DT}/dancetrack0026/img1", "%08d.jpg", 0,
       ids_at=lambda f, B_ID=B_ID, B_OTHER=B_OTHER: ([B_ID] if f in (191, 209)
                                                      else [B_ID, B_OTHER]),
       note=(None, "GT 0 absent", None), gap=(191, 209)),
]
for p in PANELS:
    if p["tag"] == "(b)":
        ck("(b) left anchor frame draws no reference box", p["ids_at"](p["la"]) == [], "")
    if p["tag"] == "(d)":
        for f in range(192, 209):
            ck(f"(d) identity {B_ID} is NOT annotated at frame {f}", B_ID not in gtd.get(f, {}), "")

ASPECT = 0.80
def crop(p, f, W, H, pad=0.26):
    boxes = [p["add"][f]] if f in p["add"] else [p["r0"][f][p["track"]]]
    for gid in p["ids_at"](f):
        if gid in p["gt"].get(f, {}):
            boxes.append(p["gt"][f][gid])
    xs = [b[0] for b in boxes] + [b[0] + b[2] for b in boxes]
    ys = [b[1] for b in boxes] + [b[1] + b[3] for b in boxes]
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    w, h = max(xs) - min(xs), max(ys) - min(ys)
    chh = max(h * (1 + 2 * pad), 110.0); cw = max(w * (1 + 2 * pad), chh * ASPECT)
    chh = max(chh, cw / ASPECT)
    if chh > H: chh = float(H); cw = chh * ASPECT
    if cw > W:  cw = float(W);  chh = cw / ASPECT
    return min(max(0.0, cx - cw / 2), W - cw), min(max(0.0, cy - chh / 2), H - chh), cw, chh

fig = plt.figure(figsize=(S.TWOCOL, 4.75))
outer = fig.add_gridspec(2, 2, hspace=0.015, wspace=0.09)

for k, p in enumerate(PANELS):
    cell = GridSpecFromSubplotSpec(1, 3, subplot_spec=outer[k // 2, k % 2], wspace=0.045)
    frames = [p["la"], p["mid"], p["ra"]]
    roles = ["left $R_0$ anchor", "added row", "right $R_0$ anchor"]
    for j, f in enumerate(frames):
        ax = fig.add_subplot(cell[0, j])
        ipath = os.path.join(p["imgdir"], p["pat"] % (f + p["offset"]))
        ck(f"{p['tag']} frame {f}: image file exists", os.path.exists(ipath), ipath)
        im = Image.open(ipath); W, H = im.size
        x0, y0, cw, chh = crop(p, f, W, H)
        ck(f"{p['tag']} frame {f}: crop inside image",
           x0 >= 0 and y0 >= 0 and x0 + cw <= W and y0 + chh <= H, "")
        ax.imshow(np.asarray(im), interpolation="bilinear")
        ax.set_xlim(x0, x0 + cw); ax.set_ylim(y0 + chh, y0)
        ax.set_xticks([]); ax.set_yticks([])
        for s in ax.spines.values(): s.set_visible(True); s.set_linewidth(0.5)
        # reference identities this frame is supposed to show
        for i, gid in enumerate(p["ids_at"](f)):
            if gid not in p["gt"].get(f, {}): continue
            gx, gy, gw, gh = p["gt"][f][gid]
            tone = S.INK if i == 0 else S.MID
            ax.add_patch(Rectangle((gx, gy), gw, gh, fill=False, ec="white", lw=1.5,
                                   ls=(0, (1, 1.2)), zorder=3))
            ax.add_patch(Rectangle((gx, gy), gw, gh, fill=False, ec=tone, lw=0.8,
                                   ls=(0, (1, 1.2)), zorder=4))
            ax.text(gx + gw / 2, gy - 0.012 * chh if i == 0 else gy + gh + 0.012 * chh,
                    f"GT {gid}", color="white", fontsize=6.6, ha="center",
                    va="bottom" if i == 0 else "top", zorder=7,
                    bbox=dict(fc=tone, ec="none", pad=1.0))
        # the tracker row itself: solid for an anchor, dashed for a synthesized row
        if f in p["add"]:
            bx, by, bw, bh = p["add"][f]; style = (0, (2.4, 1.3)); lw = 1.0
        else:
            bx, by, bw, bh = p["r0"][f][p["track"]]; style = "-"; lw = 0.95
        ax.add_patch(Rectangle((bx, by), bw, bh, fill=False, ec="white", lw=lw + 0.9,
                               ls=style, zorder=5))
        ax.add_patch(Rectangle((bx, by), bw, bh, fill=False, ec=S.INK, lw=lw,
                               ls=style, zorder=6))
        ax.set_xlabel(f"{roles[j]}\nframe {f}", fontsize=7.0, labelpad=2.0,
                      linespacing=1.25)
        if p["note"] and p["note"][j]:
            at_top = p["tag"] == "(d)"      # bottom is taken by the second identity
            ax.text(0.5, 0.978 if at_top else 0.022, p["note"][j],
                    transform=ax.transAxes, fontsize=6.8, ha="center",
                    va="top" if at_top else "bottom", color="white", zorder=9,
                    clip_on=False, bbox=dict(fc=S.INK, ec="none", alpha=0.85, pad=1.0))
        if j == 1:
            ax.set_title(f"{p['tag']} {p['cls']}", fontsize=7.4, pad=3.4)

h_anchor = plt.Line2D([], [], color=S.INK, ls="-", lw=1.0)
h_added = plt.Line2D([], [], color=S.INK, ls=(0, (2.4, 1.3)), lw=1.0)
h_ref = plt.Line2D([], [], color=S.INK, ls=(0, (1, 1.2)), lw=1.0)
h_ref2 = plt.Line2D([], [], color=S.MID, ls=(0, (1, 1.2)), lw=1.0)
# two rows, so the legend fits inside the text width and the figure is placed
# at \textwidth without being shrunk
fig.legend([h_anchor, h_added, h_ref, h_ref2],
           ["$R_0$ anchor row (solid)", "added row (dashed)",
            "anchor-resolved reference identity (dotted)",
            "second reference identity (dotted, grey)"],
           loc="lower center", ncol=2, bbox_to_anchor=(0.5, -0.075),
           handletextpad=0.5, columnspacing=1.6, fontsize=7.0)

S.finish(fig, OUT)

for p in PANELS:
    PROV["panels"].append({
        "panel": p["tag"], "class": p["cls"], "dataset": p["dataset"], "sequence": p["seq"],
        "tracker": "ByteTrack", "track_id": p["track"],
        "synthesized_frames_audit": [p["lo"], p["hi"]], "n_synthesized_rows": len(p["add"]),
        "anchor_frames_audit": [p["la"], p["ra"]],
        "displayed_frames_audit": [p["la"], p["mid"], p["ra"]],
        "displayed_frames_image": [f + p["offset"] for f in (p["la"], p["mid"], p["ra"])],
        "reference_identities_drawn": {str(f): p["ids_at"](f) for f in (p["la"], p["mid"], p["ra"])},
        "image_files": [os.path.join(p["imgdir"], p["pat"] % (f + p["offset"]))
                        for f in (p["la"], p["mid"], p["ra"])],
        "image_sha256": [sha(os.path.join(p["imgdir"], p["pat"] % (f + p["offset"])))
                         for f in (p["la"], p["mid"], p["ra"])],
        "gt_gap": p["gap"],
    })
PROV["artifacts"] = {k: {"path": v, "sha256": sha(v)} for k, v in {
    "admission_record_mot17": REC_MOT, "reference_absent_record": REC_ABS,
    "gt_mot17_valhalf": GT_MOT, "gt_mot17_original": GT_MOT_ORIG, "gt_dancetrack": GT_DT,
    "R0_mot17": R0_MOT, "R2_mot17": R2_MOT, "R0_dancetrack": R0_DT, "R2_dancetrack": R2_DT,
}.items()}
PROV["mot17_image_offset"] = OFFSET_MOT
json.dump(PROV, open(os.path.join(HERE, "..", "_fig1_fourclass_provenance.json"), "w"), indent=1)
print(f"fig1: {len(PROV['checks'])} checks, "
      f"{sum(1 for c in PROV['checks'] if not c['pass'])} failed -> {OUT}")

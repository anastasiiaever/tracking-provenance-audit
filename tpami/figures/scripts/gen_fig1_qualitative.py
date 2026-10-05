#!/usr/bin/env python3
"""Figure 1: the three admission classes on real dataset frames.

Every illustrated row is verified against the frozen V6 admission records before
it is drawn; the script aborts rather than drawing an unverified case.

Frame conventions, both derived from the artifacts rather than assumed:
  MOT17-02-FRCNN  the audit indexes the validation half 1..299 and so do the
                  state files and the TrackEval val-half ground truth, so all
                  lookups are offset-free.  Only the IMAGE FILE name needs the
                  original numbering, image_frame = audit_frame + 301, and 301
                  is the unique offset at which all 15,430 val-half ground-truth
                  rows reproduce in the original annotation file.
  dancetrack0026  the audit ground truth is byte-identical to the dataset ground
                  truth and the images run 1..302, so the offset is 0.
"""
import csv, json, hashlib, os, sys
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
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

PROV = {"figure": "Figure 1, qualitative admission classes", "panels": [], "checks": []}

def ck(name, cond, detail=""):
    PROV["checks"].append({"check": name, "pass": bool(cond), "detail": str(detail)})
    assert cond, f"FAILED: {name}: {detail}"

def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 16), b""):
            h.update(b)
    return h.hexdigest()

# ------------------------------------------------------------------ data

def states(path):
    """frame -> track_id -> (x, y, w, h)"""
    d = {}
    for line in open(path):
        f = line.strip().split(",")
        if len(f) < 6:
            continue
        d.setdefault(int(f[0]), {})[int(f[1])] = tuple(float(v) for v in f[2:6])
    return d

def scoreable_gt(path):
    """frame -> gt_id -> box, keeping only mark != 0 and class == 1."""
    d = {}
    for line in open(path):
        f = line.strip().split(",")
        if len(f) < 8:
            continue
        if int(float(f[6])) == 0 or int(float(f[7])) != 1:
            continue
        d.setdefault(int(f[0]), {})[int(f[1])] = tuple(float(v) for v in f[2:6])
    return d

def gt_frames(gt, gid):
    return sorted(f for f, m in gt.items() if gid in m)

# ---- the MOT17 image offset, derived not assumed
def derive_mot_offset():
    def rows(p):
        out = set()
        for line in open(p):
            f = line.strip().split(",")
            if len(f) >= 6:
                out.add((int(f[0]), int(f[1]), round(float(f[2]), 1), round(float(f[3]), 1)))
        return out
    reb, orig = rows(GT_MOT), rows(GT_MOT_ORIG)
    good = [o for o in range(290, 315)
            if all((f + o, i, x, y) in orig for (f, i, x, y) in reb)]
    ck("MOT17-02 image offset is unique", len(good) == 1, f"candidates {good}")
    ck("MOT17-02 all val-half GT rows reproduce at that offset",
       True, f"{len(reb)} rows at offset {good[0]}")
    return good[0]

OFFSET_MOT = derive_mot_offset()

# ------------------------------------------------------------------ cases

def mot_case(track, lo, hi, want_class):
    R = [x for x in csv.DictReader(open(REC_MOT))
         if x["pipeline"] == "ByteTrack" and x["sequence"] == "MOT17-02-FRCNN"
         and int(x["track_id"]) == track and lo <= int(x["frame"]) <= hi]
    R.sort(key=lambda x: int(x["frame"]))
    ck(f"track {track}: run {lo}-{hi} present in the frozen record",
       len(R) == hi - lo + 1, f"{len(R)} of {hi-lo+1} rows")
    ck(f"track {track}: every row is {want_class}",
       all(x["stv_class"] == want_class for x in R),
       sorted(set(x["stv_class"] for x in R)))
    ck(f"track {track}: frames are contiguous",
       [int(x["frame"]) for x in R] == list(range(lo, hi + 1)), "")
    L = sorted(set(x["left_anchor_id"] for x in R))
    Rt = sorted(set(x["right_anchor_id"] for x in R))
    ck(f"track {track}: one left and one right anchor identity",
       len(L) == 1 and len(Rt) == 1, f"L={L} R={Rt}")
    return R, int(L[0]), int(Rt[0])

REC_A, A_L, A_R = mot_case(26, 51, 61, "SEMANTICALLY_ADMITTED")
REC_B, B_L, B_R = mot_case(33, 232, 239, "ANCHOR_ID_MISMATCH")
ck("panel (a) both anchors resolve to the same identity", A_L == A_R, f"{A_L}=={A_R}")
ck("panel (b) anchors resolve to different identities", B_L != B_R, f"{B_L}!={B_R}")

REC_C = [x for x in csv.DictReader(open(REC_ABS))
         if x["tracker"] == "ByteTrack" and x["sequence"] == "dancetrack0026"
         and int(x["track_id"]) == 210 and 192 <= int(x["frame"]) <= 208]
REC_C.sort(key=lambda x: int(x["frame"]))
ck("panel (c) run 192-208 present", len(REC_C) == 17, len(REC_C))
ck("panel (c) frames contiguous",
   [int(x["frame"]) for x in REC_C] == list(range(192, 209)), "")
C_ID = sorted(set(int(x["anchor_gt_id"]) for x in REC_C))
ck("panel (c) one anchor-resolved identity", len(C_ID) == 1, C_ID)
C_ID = C_ID[0]
ck("panel (c) every row lies inside a verified internal GT gap",
   all(x["inside_verified_internal_gt_gap"] == "1" for x in REC_C), "")
ck("panel (c) intended identity absent at every frame",
   all(x["intended_reference_identity_present_at_frame"] == "0" for x in REC_C), "")
ck("panel (c) another scoreable identity overlaps at every frame",
   all(x["another_gt_identity_overlaps"] == "1" for x in REC_C), "")
C_PREV = sorted(set(int(x["gt_prev"]) for x in REC_C))
C_NEXT = sorted(set(int(x["gt_next"]) for x in REC_C))
ck("panel (c) one gap, 191 -> 209", C_PREV == [191] and C_NEXT == [209],
   f"prev={C_PREV} next={C_NEXT}")
# the identity that overlaps the added box at the displayed frame
C_OTHER = int([x for x in REC_C if int(x["frame"]) == 200][0]["max_iou_gt_id"])

# ------------------------------------------------------------------ geometry

r0m, r2m = states(R0_MOT), states(R2_MOT)
gtm = scoreable_gt(GT_MOT)
r0d, r2d = states(R0_DT), states(R2_DT)
gtd = scoreable_gt(GT_DT)

def synthesized(r0, r2, track, frames):
    out = {}
    for f in frames:
        ck(f"row ({f},{track}) is in R2", track in r2.get(f, {}), "")
        ck(f"row ({f},{track}) is absent from R0", track not in r0.get(f, {}), "")
        out[f] = r2[f][track]
    return out

A_ADD = synthesized(r0m, r2m, 26, range(51, 62))
B_ADD = synthesized(r0m, r2m, 33, range(232, 240))
C_ADD = synthesized(r0d, r2d, 210, range(192, 209))

def anchors(r0, track, lo, hi):
    left = max(f for f in r0 if f < lo and track in r0[f])
    right = min(f for f in r0 if f > hi and track in r0[f])
    ck(f"anchors of track {track} bracket {lo}-{hi}", left < lo and right > hi,
       f"{left} < {lo}, {right} > {hi}")
    return (left, r0[left][track]), (right, r0[right][track])

A_AL, A_AR = anchors(r0m, 26, 51, 61)
B_AL, B_AR = anchors(r0m, 33, 232, 239)
C_AL, C_AR = anchors(r0d, 210, 192, 208)
ck("panel (c) anchor frames are the gap edges 191 and 209",
   (C_AL[0], C_AR[0]) == (191, 209), f"{C_AL[0]}, {C_AR[0]}")

# the GT identity must actually be present at the displayed frames for (a)
for f in range(51, 62):
    ck(f"(a) identity {A_L} is annotated at frame {f}", A_L in gtm.get(f, {}), "")
for f in range(192, 209):
    ck(f"(c) identity {C_ID} is NOT annotated at frame {f}",
       C_ID not in gtd.get(f, {}), "")

PANELS = [
    dict(tag="(a)", cls="SEMANTICALLY ADMITTED", seq="MOT17-02-FRCNN",
         dataset="MOT17", track=26, lo=51, hi=61, show=56,
         add=A_ADD, al=A_AL, ar=A_AR, ids=[A_L], gt=gtm, r0=r0m,
         imgdir=f"{MOT}/datasets/mot/train/MOT17-02-FRCNN/img1", pat="%06d.jpg",
         offset=OFFSET_MOT, gap=None),
    dict(tag="(b)", cls="ANCHOR ID MISMATCH", seq="MOT17-02-FRCNN",
         dataset="MOT17", track=33, lo=232, hi=239, show=235,
         add=B_ADD, al=B_AL, ar=B_AR, ids=[B_L, B_R], gt=gtm, r0=r0m,
         imgdir=f"{MOT}/datasets/mot/train/MOT17-02-FRCNN/img1", pat="%06d.jpg",
         offset=OFFSET_MOT, gap=None),
    dict(tag="(c)", cls="TARGET REFERENCE ABSENT", seq="dancetrack0026",
         dataset="DanceTrack", track=210, lo=192, hi=208, show=200,
         add=C_ADD, al=C_AL, ar=C_AR, ids=[C_ID, C_OTHER], gt=gtd, r0=r0d,
         imgdir=f"{DT}/dancetrack0026/img1", pat="%08d.jpg",
         offset=0, gap=(191, 209)),
]

# ------------------------------------------------------------------ drawing

ASPECT = 0.86          # crop width / height, one value for all three panels

def crop_box(p, f, W, H, pad=0.30):
    """Union of the drawn boxes, padded, forced to ASPECT, clipped inside the
    image so no panel shows an out-of-frame band."""
    boxes = [p["add"][f]]
    for gid in p["ids"]:
        if gid in p["gt"].get(f, {}):
            boxes.append(p["gt"][f][gid])
    xs = [b[0] for b in boxes] + [b[0] + b[2] for b in boxes]
    ys = [b[1] for b in boxes] + [b[1] + b[3] for b in boxes]
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    w, h = max(xs) - min(xs), max(ys) - min(ys)
    ch = max(h * (1 + 2 * pad), 110.0)
    cw = max(w * (1 + 2 * pad), ch * ASPECT)
    ch = max(ch, cw / ASPECT)
    if ch > H:                      # never taller than the image
        ch = float(H); cw = ch * ASPECT
    if cw > W:
        cw = float(W); ch = cw / ASPECT
    x0 = min(max(0.0, cx - cw / 2), W - cw)
    y0 = min(max(0.0, cy - ch / 2), H - ch)
    return x0, y0, cw, ch

fig = plt.figure(figsize=(S.TWOCOL, 3.52))
gs = fig.add_gridspec(2, 3, height_ratios=[2.70, 1.0], hspace=0.40, wspace=0.21)

for col, p in enumerate(PANELS):
    f = p["show"]
    # ---------------- image
    ax = fig.add_subplot(gs[0, col])
    ipath = os.path.join(p["imgdir"], p["pat"] % (f + p["offset"]))
    ck(f"{p['tag']} image file exists", os.path.exists(ipath), ipath)
    im = Image.open(ipath)
    W, H = im.size
    cx0, cy0, cw, chh = crop_box(p, f, W, H)
    ck(f"{p['tag']} crop lies inside the image",
       cx0 >= 0 and cy0 >= 0 and cx0 + cw <= W and cy0 + chh <= H,
       f"crop ({cx0:.0f},{cy0:.0f},{cw:.0f},{chh:.0f}) in {W}x{H}")
    ax.imshow(np.asarray(im), interpolation="bilinear")
    ax.set_xlim(cx0, cx0 + cw); ax.set_ylim(cy0 + chh, cy0)
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(True); s.set_linewidth(0.6)
    # reference identities (dotted), anchor-resolved first
    for k, gid in enumerate(p["ids"]):
        if gid not in p["gt"].get(f, {}):
            continue
        x, y, w, h = p["gt"][f][gid]
        ax.add_patch(Rectangle((x, y), w, h, fill=False, ec="white", lw=1.6,
                               ls=(0, (1, 1.2)), zorder=3))
        ax.add_patch(Rectangle((x, y), w, h, fill=False,
                               ec=S.INK if k == 0 else S.MID, lw=0.85,
                               ls=(0, (1, 1.2)), zorder=4))
        if k == 0:
            ax.text(x + w / 2, y - 0.012 * chh, f"GT {gid}", color="white",
                    fontsize=6.0, ha="center", va="bottom", zorder=7,
                    bbox=dict(fc=S.INK, ec="none", pad=1.0))
        else:
            ax.text(x + w / 2, y + h + 0.012 * chh, f"GT {gid}", color="white",
                    fontsize=6.0, ha="center", va="top", zorder=7,
                    bbox=dict(fc=S.MID, ec="none", pad=1.0))
    # the added row (dashed)
    x, y, w, h = p["add"][f]
    ax.add_patch(Rectangle((x, y), w, h, fill=False, ec="white", lw=2.0,
                           ls=(0, (2.6, 1.4)), zorder=5))
    ax.add_patch(Rectangle((x, y), w, h, fill=False, ec=S.INK, lw=1.05,
                           ls=(0, (2.6, 1.4)), zorder=6))
    ax.set_title(f"{p['tag']} {p['cls']}\n{p['dataset']} · {p['seq']} · ByteTrack",
                 fontsize=6.6, pad=2.6, linespacing=1.35)
    if p["gap"]:
        ax.text(0.5, 0.013, f"GT {p['ids'][0]} not annotated at this frame",
                transform=ax.transAxes, fontsize=5.9, ha="center", va="bottom",
                color="white", zorder=8,
                bbox=dict(fc=S.INK, ec="none", alpha=0.80, pad=1.4))
    ax.set_xlabel(f"added row at frame {f}", fontsize=6.3, labelpad=1.8)

    # ---------------- trajectory
    bx = fig.add_subplot(gs[1, col])
    lo, hi = p["lo"], p["hi"]
    span = range(p["al"][0] - 3, p["ar"][0] + 4)
    cen = lambda b: b[0] + b[2] / 2
    for k, gid in enumerate(p["ids"]):
        fr = [q for q in span if gid in p["gt"].get(q, {})]
        if not fr:
            continue
        st = S.ROLE["reference" if k == 0 else "reference_other"]
        # draw contiguous stretches separately so a gap stays a visible gap
        run = [fr[0]]
        for q in fr[1:]:
            if q == run[-1] + 1:
                run.append(q)
            else:
                bx.plot(run, [cen(p["gt"][z][gid]) for z in run],
                        **st, label=None if k else None)
                run = [q]
        bx.plot(run, [cen(p["gt"][z][gid]) for z in run], **st)
        # identity key at a fixed position inside the axes: attaching it to the
        # line end collides with the tick labels at this panel width
        bx.text(0.985, 0.95 if k == 0 else 0.07, f"GT {gid}",
                transform=bx.transAxes, fontsize=5.8,
                color=S.INK if k == 0 else S.MID, ha="right",
                va="top" if k == 0 else "bottom",
                bbox=dict(fc="white", ec="none", alpha=0.85, pad=0.6))
    if p["gap"]:
        g0, g1 = p["gap"]
        bx.axvspan(g0, g1, color=S.PALE, alpha=0.45, lw=0, zorder=0)
        bx.text((g0 + g1) / 2, bx.get_ylim()[1], "GT gap", fontsize=5.6,
                ha="center", va="bottom", color=S.MID)
    bx.plot([p["al"][0], p["ar"][0]], [cen(p["al"][1]), cen(p["ar"][1])],
            **S.ROLE["anchor"], zorder=5)
    bx.plot(sorted(p["add"]), [cen(p["add"][q]) for q in sorted(p["add"])],
            **S.ROLE["added"], zorder=4)
    bx.axvline(f, **S.ROLE["gap"], zorder=1)
    bx.set_xlabel("frame", fontsize=6.4, labelpad=1.4)
    if col == 0:
        bx.set_ylabel("box centre $x$ (px)", fontsize=6.4, labelpad=1.6)
    bx.tick_params(pad=1.4)

h_anchor = plt.Line2D([], [], **S.ROLE["anchor"])
h_added = plt.Line2D([], [], **S.ROLE["added"])
h_ref = plt.Line2D([], [], **S.ROLE["reference"])
h_oth = plt.Line2D([], [], **S.ROLE["reference_other"])
fig.legend([h_anchor, h_added, h_ref, h_oth],
           ["$R_0$ anchor (solid box)", "added row (dashed box)",
            "anchor-resolved reference identity (dotted box)",
            "second reference identity"],
           loc="lower center", ncol=4, bbox_to_anchor=(0.5, -0.055),
           handletextpad=0.5, columnspacing=1.5, fontsize=6.2)

S.finish(fig, OUT)

for p in PANELS:
    PROV["panels"].append({
        "panel": p["tag"], "class": p["cls"], "dataset": p["dataset"],
        "sequence": p["seq"], "tracker": "ByteTrack", "track_id": p["track"],
        "synthesized_frames_audit": [p["lo"], p["hi"]],
        "n_synthesized_rows": len(p["add"]),
        "anchor_frames_audit": [p["al"][0], p["ar"][0]],
        "reference_identities": p["ids"],
        "displayed_frame_audit": p["show"],
        "displayed_frame_image": p["show"] + p["offset"],
        "image_file": os.path.join(p["imgdir"], p["pat"] % (p["show"] + p["offset"])),
        "image_sha256": sha(os.path.join(p["imgdir"], p["pat"] % (p["show"] + p["offset"]))),
        "gt_gap": p["gap"],
    })
PROV["artifacts"] = {k: {"path": v, "sha256": sha(v)} for k, v in {
    "admission_record_mot17": REC_MOT, "reference_absent_record": REC_ABS,
    "gt_mot17_valhalf": GT_MOT, "gt_mot17_original": GT_MOT_ORIG, "gt_dancetrack": GT_DT,
    "R0_mot17": R0_MOT, "R2_mot17": R2_MOT, "R0_dancetrack": R0_DT, "R2_dancetrack": R2_DT,
}.items()}
PROV["mot17_image_offset"] = OFFSET_MOT
json.dump(PROV, open(os.path.join(HERE, "..", "_fig1_qualitative_provenance.json"), "w"), indent=1)
bad = [c for c in PROV["checks"] if not c["pass"]]
print(f"fig1: {len(PROV['checks'])} checks, {len(bad)} failed -> {OUT}")

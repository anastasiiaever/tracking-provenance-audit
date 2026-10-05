#!/usr/bin/env python3
"""Supplement Fig. S2: trajectory view of the four Figure 1 cases.

These are the plots that used to sit under main Figure 1. Main Figure 1 now
carries the dataset frames alone; the temporal structure each case has -- where
the anchors sit, how the added rows run between them, and where the reference
identity is or is not annotated -- is preserved here.

Cases, frame conventions and verification are identical to
gen_fig1_fourclass.py; this script re-derives them from the same artifacts
rather than importing, so it fails independently if an artifact moves.
"""
import csv, json, hashlib, os
import matplotlib.pyplot as plt
import _figstyle as S

ROOT = "<AUDIT_ROOT>"
MOT = "<MOT_AUDIT_ROOT>"
DTC = f"{ROOT}/dancetrack_controlled_20261003"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, "..", "figS2_final.pdf"))
REC_MOT = f"{ROOT}/posthoc_composition_20261003/results/C6_identity_support_rows.csv"
REC_ABS = f"{DTC}/final_defense_20261004/D1B2_reference_absent_local_support.csv"
GT_MOT = f"{MOT}/repos/TrackEval/data/gt/mot_challenge/MOT17-val_half/MOT17-02-FRCNN/gt/gt.txt"
GT_DT = f"{DTC}/inputs/gt/DANCE-val/dancetrack0026/gt/gt.txt"
R0_MOT = f"{MOT}/states/ByteTrack/R0/MOT17-02-FRCNN.txt"
R2_MOT = f"{MOT}/states/ByteTrack/R2/MOT17-02-FRCNN.txt"
R0_DT = f"{DTC}/r0/bytetrack/dancetrack0026.txt"
R2_DT = f"{DTC}/r2_primary/bytetrack/dancetrack0026.txt"
PROV = {"figure": "Supplement Fig. S2, trajectories of the four Figure 1 cases", "checks": []}

def ck(n, c, d=""):
    PROV["checks"].append({"check": n, "pass": bool(c), "detail": str(d)})
    assert c, f"FAILED: {n}: {d}"

def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 16), b""): h.update(b)
    return h.hexdigest()

def states(p):
    d = {}
    for l in open(p):
        f = l.strip().split(",")
        if len(f) >= 6: d.setdefault(int(f[0]), {})[int(f[1])] = tuple(float(v) for v in f[2:6])
    return d

def gt_s(p):
    d = {}
    for l in open(p):
        f = l.strip().split(",")
        if len(f) < 8 or int(float(f[6])) == 0 or int(float(f[7])) != 1: continue
        d.setdefault(int(f[0]), {})[int(f[1])] = tuple(float(v) for v in f[2:6])
    return d

r0m, r2m, gtm = states(R0_MOT), states(R2_MOT), gt_s(GT_MOT)
r0d, r2d, gtd = states(R0_DT), states(R2_DT), gt_s(GT_DT)

def mot(track, lo, hi, want):
    R = [x for x in csv.DictReader(open(REC_MOT))
         if x["pipeline"] == "ByteTrack" and x["sequence"] == "MOT17-02-FRCNN"
         and int(x["track_id"]) == track and lo <= int(x["frame"]) <= hi]
    ck(f"track {track} run {lo}-{hi} is {want} and contiguous",
       len(R) == hi - lo + 1 and all(x["stv_class"] == want for x in R), len(R))
    return int(R[0]["left_anchor_id"]), int(R[0]["right_anchor_id"])

A_L, A_R = mot(26, 51, 61, "SEMANTICALLY_ADMITTED")
U_L, U_R = mot(36, 44, 50, "ANCHOR_UNMATCHED")
M_L, M_R = mot(33, 232, 239, "ANCHOR_ID_MISMATCH")
ABS_ = [x for x in csv.DictReader(open(REC_ABS))
        if x["tracker"] == "ByteTrack" and x["sequence"] == "dancetrack0026"
        and int(x["track_id"]) == 210 and 192 <= int(x["frame"]) <= 208]
ck("absent run has 17 rows", len(ABS_) == 17, len(ABS_))
B_ID = int(ABS_[0]["anchor_gt_id"])
B_OTHER = int([x for x in ABS_ if int(x["frame"]) == 200][0]["max_iou_gt_id"])

CASES = [
 ("(a) semantically admitted", "MOT17-02-FRCNN", 26, 51, 61, r0m, r2m, gtm, [A_L], None),
 ("(b) anchor unmatched", "MOT17-02-FRCNN", 36, 44, 50, r0m, r2m, gtm,
  [i for i in (U_L, U_R) if i != -1], None),
 ("(c) anchor id mismatch", "MOT17-02-FRCNN", 33, 232, 239, r0m, r2m, gtm, [M_L, M_R], None),
 ("(d) target reference absent", "dancetrack0026", 210, 192, 208, r0d, r2d, gtd,
  [B_ID, B_OTHER], (191, 209)),
]
fig, axes = plt.subplots(1, 4, figsize=(S.TWOCOL, 1.62),
                         gridspec_kw=dict(wspace=0.30))
cen = lambda b: b[0] + b[2] / 2
for ax, (title, seq, track, lo, hi, r0, r2, gt, ids, gap) in zip(axes, CASES):
    la = max(f for f in r0 if f < lo and track in r0[f])
    ra = min(f for f in r0 if f > hi and track in r0[f])
    ck(f"{title}: anchors bracket the run", la < lo and ra > hi, f"{la},{ra}")
    add = {}
    for f in range(lo, hi + 1):
        ck(f"{title}: row {f} in R2 not R0",
           track in r2.get(f, {}) and track not in r0.get(f, {}), "")
        add[f] = r2[f][track]
    span = range(la - 3, ra + 4)
    for k, gid in enumerate(ids):
        fr = [q for q in span if gid in gt.get(q, {})]
        if not fr: continue
        st = S.ROLE["reference" if k == 0 else "reference_other"]
        run = [fr[0]]
        for q in fr[1:]:
            if q == run[-1] + 1: run.append(q)
            else:
                ax.plot(run, [cen(gt[z][gid]) for z in run], **st); run = [q]
        ax.plot(run, [cen(gt[z][gid]) for z in run], **st)
        ax.text(0.985, 0.95 if k == 0 else 0.07, f"GT {gid}", transform=ax.transAxes,
                fontsize=5.4, color=S.INK if k == 0 else S.MID, ha="right",
                va="top" if k == 0 else "bottom",
                bbox=dict(fc="white", ec="none", alpha=0.85, pad=0.5))
    if gap:
        ax.axvspan(gap[0], gap[1], color=S.PALE, alpha=0.45, lw=0, zorder=0)
    ax.plot([la, ra], [cen(r0[la][track]), cen(r0[ra][track])], **S.ROLE["anchor"], zorder=5)
    ax.plot(sorted(add), [cen(add[q]) for q in sorted(add)], **S.ROLE["added"], zorder=4)
    ax.set_title(f"{title}\n{seq} · track {track}", fontsize=6.0, pad=2.6, linespacing=1.3)
    ax.set_xlabel("frame", fontsize=6.2, labelpad=1.4)
    ax.tick_params(pad=1.4, labelsize=5.8)
axes[0].set_ylabel("box centre $x$ (px)", fontsize=6.2, labelpad=1.6)
fig.legend([plt.Line2D([], [], **S.ROLE["anchor"]), plt.Line2D([], [], **S.ROLE["added"]),
            plt.Line2D([], [], **S.ROLE["reference"]), plt.Line2D([], [], **S.ROLE["reference_other"])],
           ["$R_0$ anchor", "added row", "anchor-resolved reference identity",
            "second reference identity"],
           loc="lower center", ncol=4, bbox_to_anchor=(0.5, -0.30),
           handletextpad=0.5, columnspacing=1.5, fontsize=6.0)
S.finish(fig, OUT)
PROV["artifacts"] = {k: sha(v) for k, v in
                     dict(rec_mot=REC_MOT, rec_abs=REC_ABS, gt_mot=GT_MOT, gt_dt=GT_DT,
                          r0m=R0_MOT, r2m=R2_MOT, r0d=R0_DT, r2d=R2_DT).items()}
json.dump(PROV, open(os.path.join(HERE, "..", "_figS2_provenance.json"), "w"), indent=1)
print(f"figS2: {len(PROV['checks'])} checks, "
      f"{sum(1 for c in PROV['checks'] if not c['pass'])} failed -> {OUT}")

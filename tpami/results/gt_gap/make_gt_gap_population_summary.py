#!/usr/bin/env python3
"""Regenerate the ground-truth interior-gap population quantities.

These five numbers appear in the supplement's numeric ledger, whose frozen
artifact column points at an internal record directory rather than at a file.
This script recomputes them deterministically from the authoritative benchmark
annotations so the ledger can name a reader-facing artifact instead.

Interior gap: for one scoreable ground-truth identity in one sequence, a maximal
run of frames strictly between its first and last observed frame at which the
identity is not annotated. A track has an interior gap if it has at least one.
Scoreable ground truth is the evaluator's own preprocessing, mark != 0 and
class == 1, the same rule the admission criterion uses.
"""
import csv, glob, hashlib, json, os, subprocess, sys

ROOT = "<AUDIT_ROOT>"
MOT_GT = f"<MOT_AUDIT_ROOT>/repos/TrackEval/data/gt/mot_challenge/MOT17-val_half"
DT_GT = f"{ROOT}/dancetrack_controlled_20261003/inputs/gt/DANCE-val"
HERE = os.path.dirname(os.path.abspath(__file__))

def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 16), b""):
            h.update(b)
    return h.hexdigest()

def scoreable_tracks(path):
    """sequence file -> {gt_id: sorted set of frames}, scoreable rows only."""
    d = {}
    for line in open(path):
        f = line.strip().split(",")
        if len(f) < 8:
            continue
        if int(float(f[6])) == 0 or int(float(f[7])) != 1:
            continue
        d.setdefault(int(f[1]), set()).add(int(f[0]))
    return {k: sorted(v) for k, v in d.items()}

def analyse(gt_root, pattern):
    seqs = sorted(glob.glob(f"{gt_root}/{pattern}/gt/gt.txt"))
    assert seqs, f"no ground truth under {gt_root}/{pattern}"
    n_tracks = n_gapped = n_gaps = n_slots = 0
    per_seq, srcs = [], []
    for p in seqs:
        seq = p.split("/")[-3]
        tracks = scoreable_tracks(p)
        s_tracks = s_gapped = s_gaps = s_slots = 0
        for gid, frames in tracks.items():
            s_tracks += 1
            observed = set(frames)
            span = range(frames[0], frames[-1] + 1)
            missing = sorted(f for f in span if f not in observed)
            if not missing:
                continue
            s_gapped += 1
            s_slots += len(missing)
            # maximal runs of consecutive missing frames
            runs = 1
            for a, b in zip(missing, missing[1:]):
                if b != a + 1:
                    runs += 1
            s_gaps += runs
        per_seq.append(dict(sequence=seq, scoreable_tracks=s_tracks,
                            tracks_with_interior_gap=s_gapped,
                            interior_gaps=s_gaps, missing_frame_slots=s_slots))
        srcs.append(dict(path=p, sha256=sha(p)))
        n_tracks += s_tracks; n_gapped += s_gapped; n_gaps += s_gaps; n_slots += s_slots
    return dict(sequences=len(seqs), scoreable_tracks=n_tracks,
                tracks_with_interior_gap=n_gapped, interior_gaps=n_gaps,
                missing_frame_slots=n_slots), per_seq, srcs

mot, mot_seq, mot_src = analyse(MOT_GT, "MOT17-*")
dt, dt_seq, dt_src = analyse(DT_GT, "dancetrack*")

EXPECT = {
    "MOT17 scoreable GT tracks": (mot["scoreable_tracks"], 339),
    "MOT17 tracks with an interior gap": (mot["tracks_with_interior_gap"], 0),
    "DanceTrack scoreable GT tracks": (dt["scoreable_tracks"], 273),
    "DanceTrack tracks with an interior gap": (dt["tracks_with_interior_gap"], 209),
    "DanceTrack interior gaps": (dt["interior_gaps"], 1370),
    "DanceTrack missing GT frame-slots": (dt["missing_frame_slots"], 15326),
}
print("quantity                                  regenerated   ledger   match")
ok = True
for k, (got, want) in EXPECT.items():
    m = got == want
    ok &= m
    print(f"  {k:<40} {got:>10}   {want:>6}   {'YES' if m else 'NO'}")

out_csv = f"{HERE}/gt_gap_population_summary_20261005.csv"
with open(out_csv, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["population", "sequence", "scoreable_gt_tracks",
                "tracks_with_interior_gap", "interior_gaps", "missing_frame_slots"])
    for pop, rows, tot in (("MOT17-val_half", mot_seq, mot), ("DanceTrack-val", dt_seq, dt)):
        for r in rows:
            w.writerow([pop, r["sequence"], r["scoreable_tracks"],
                        r["tracks_with_interior_gap"], r["interior_gaps"],
                        r["missing_frame_slots"]])
        w.writerow([pop, "TOTAL", tot["scoreable_tracks"], tot["tracks_with_interior_gap"],
                    tot["interior_gaps"], tot["missing_frame_slots"]])

prov = {
    "what": "ground-truth interior-gap population summary",
    "generated": "2026-10-05",
    "definition_interior_gap": ("for one scoreable ground-truth identity in one sequence, a "
                               "maximal run of frames strictly between its first and last "
                               "observed frame at which the identity is not annotated"),
    "scoreable_rule": "mark != 0 and class == 1, the evaluator's own preprocessing",
    "script": os.path.basename(__file__),
    "script_sha256": sha(os.path.abspath(__file__)),
    "populations": {
        "MOT17-val_half": {"totals": mot, "per_sequence": mot_seq, "sources": mot_src},
        "DanceTrack-val": {"totals": dt, "per_sequence": dt_seq, "sources": dt_src},
    },
    "ledger_values_reproduced": {k: {"regenerated": g, "ledger": w, "match": g == w}
                                 for k, (g, w) in EXPECT.items()},
    "output_csv": os.path.basename(out_csv),
}
prov["output_csv_sha256"] = sha(out_csv)
json.dump(prov, open(f"{HERE}/gt_gap_population_summary_20261005.provenance.json", "w"), indent=1)
print(f"\nall five ledger values reproduced: {ok}")
print(f"csv sha256: {prov['output_csv_sha256']}")
sys.exit(0 if ok else 1)

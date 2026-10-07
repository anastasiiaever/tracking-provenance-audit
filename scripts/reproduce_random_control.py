#!/usr/bin/env python3
"""Reproduce the sequence-stratified random-subset control for R1.

    python3 reproduce_random_control.py <population> <tracker> [n_proc] [n_draws]

Control state, per draw: keep every row of R2 whose identity is in R0, then draw --
independently per sequence -- a uniform random sample of that sequence's inserted
rows, of exactly the size R1 took from that sequence. Rows are copied from R2
verbatim, so the only difference between R1 and a control draw is which insertions
were kept. Every draw is scored with the same unmodified pinned TrackEval
(12c8791b303e0a0b50f753af204249e622d0281a) under the same per-arm configuration.

Descriptive only: no hypothesis is tested and no p-value is computed.

SEEDING -- read this before changing it
---------------------------------------
The published draws were executed on CPython 3.8.10 with, literally:

    SEED = 20261006
    rng  = random.Random((SEED, draw_index))

A tuple is not an int, so CPython hashes it and casts the hash to size_t; the
MT19937 init key was therefore `hash((20261006, draw_index)) mod 2**64`. CPython
3.11 restricted seeds to None/int/float/str/bytes/bytearray, so that expression now
raises TypeError -- the draws are portable but the spelling is not.

This helper therefore seeds with the explicit integer key, read from
artifacts/R1_RANDOM_CONTROL_SEEDS.csv (or recomputed below when the file is absent).
`Random(int)` is stable across CPython versions, and
verification/_verify_random_control_seeds.py checks on every interpreter available
that the integer key reproduces the executed stream, and the executed row sets,
bit-for-bit. Seeding with anything else reproduces different draws.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS"):
    os.environ[_v] = "1"           # one worker, one thread: N pools of N threads thrash
import collections, csv, json, random, shutil, sys, tempfile
import multiprocessing as mp

HERE = os.path.dirname(os.path.abspath(__file__))
V7 = os.path.dirname(HERE)
def _root(var, what):
    """Required input location. No default: the published copy must not carry
    paths from the machine the audit was executed on."""
    v = os.environ.get(var)
    if not v:
        raise SystemExit(
            f"{var} is not set. Point it at {what}.\n"
            "This helper re-scores evaluated states, so it needs the pinned "
            "evaluator, the frozen R0/R2 states and the ground truth. See "
            "docs/REPRODUCIBILITY.md; the seed mapping it uses is released in "
            "tpami/results/random_control/R1_RANDOM_CONTROL_SEEDS.csv.")
    return v


TR = os.environ.get("TRACKEVAL_ROOT", "")   # required only to re-score
if TR:
    sys.path.insert(0, TR)
# TrackEval and numpy are imported inside score(), not here, so that the draw
# selection -- the only version-sensitive part of this file -- can be imported and
# checked on any interpreter without the evaluator being installed.

SEED = 20261006                     # seed root of the executed experiment
EXECUTED_SEED_EXPR = "random.Random((20261006, draw_index))   # CPython 3.8.10"
WANT = ("HOTA", "DetA", "AssA", "IDF1", "MOTA")
SEED_CSV = next(
    (c for c in (os.path.join(V7, "tpami", "results", "random_control",
                              "R1_RANDOM_CONTROL_SEEDS.csv"),
                 os.path.join(V7, "artifacts", "R1_RANDOM_CONTROL_SEEDS.csv"))
     if os.path.exists(c)),
    os.path.join(V7, "tpami", "results", "random_control",
                 "R1_RANDOM_CONTROL_SEEDS.csv"))


def seed_for(draw_index):
    """The explicit integer MT19937 key for one draw index.

    Prefers the recorded mapping; falls back to the derivation that produced it.
    Both are the same integer -- the fallback exists so this file stays runnable
    on its own, not so the two can disagree.
    """
    if _SEEDS:
        return _SEEDS[draw_index]
    return hash((SEED, draw_index)) % 2**64        # only valid where hash() matches 3.8


_SEEDS = {}
if os.path.exists(SEED_CSV):
    for _x in csv.DictReader(open(SEED_CSV)):
        _SEEDS[int(_x["draw_index"])] = int(_x["mt19937_init_key"])

# --- the audited systems, and where their frozen states live -------------------
P = os.environ.get("POSTHOC_ROOT", "")     # required only to re-score
D = os.environ.get("DANCE_ROOT", "")       # required only to re-score
TRK = f"{TR}/data/trackers/mot_challenge"
GTM = os.environ.get("GT_MOT_ROOT", "")     # MOT17-val_half, MOT17-val, MOT20-val (scoring only)
GTD = os.environ.get("GT_DANCE_ROOT", "")   # DANCE-val

SYS = {
 ("mot17", "ByteTrack"):    ("MOT17", "val_half", GTM, f"{TRK}/MOT17-val_half/ByteTrack_R0/data",  f"{TRK}/MOT17-val_half/ByteTrack_R2/data"),
 ("mot17", "BoT-SORT"):     ("MOT17", "val_half", GTM, f"{TRK}/MOT17-val_half/BoTSORT_R0/data",    f"{TRK}/MOT17-val_half/BoTSORT_R2/data"),
 ("mot17", "OC-SORT"):      ("MOT17", "val_half", GTM, f"{TRK}/MOT17-val_half/OCSORT_R0/data",     f"{TRK}/MOT17-val_half/OCSORT_R2/data"),
 ("mot17", "Deep-OC-SORT"): ("MOT17", "val",      GTM, f"{TRK}/MOT17-val/V9-MOT17-DEEPOCSORT-001__R0/data",  f"{TRK}/MOT17-val/V9-MOT17-DEEPOCSORT-001__R2/data"),
 ("mot17", "Hybrid-SORT"):  ("MOT17", "val",      GTM, f"{TRK}/MOT17-val/V9-MOT17-HYBRIDSORT-002__R0/data", f"{TRK}/MOT17-val/V9-MOT17-HYBRIDSORT-002__R2/data"),
 ("mot20", "Deep-OC-SORT"): ("MOT20", "val",      GTM, f"{TRK}/MOT20-val/V9-MOT20-DEEPOCSORT-001__R0/data", f"{TRK}/MOT20-val/V9-MOT20-DEEPOCSORT-001__R2/data"),
 ("dancetrack", "ByteTrack"):    ("DANCE", "val", GTD, f"{D}/results/trackers/DANCE-val/BYTETRACK_R0/data",  f"{D}/results/trackers/DANCE-val/BYTETRACK_R2_PRIMARY/data"),
 ("dancetrack", "OC-SORT"):      ("DANCE", "val", GTD, f"{D}/results/trackers/DANCE-val/OCSORT_R0/data",     f"{D}/results/trackers/DANCE-val/OCSORT_R2_PRIMARY/data"),
 ("dancetrack", "Deep-OC-SORT"): ("DANCE", "val", GTD, f"{D}/results/trackers/DANCE-val/DEEPOCSORT_R0/data", f"{D}/results/trackers/DANCE-val/DEEPOCSORT_R2_PRIMARY/data"),
 ("dancetrack", "Hybrid-SORT"):  ("DANCE", "val", GTD, f"{D}/results/trackers/DANCE-val/HYBRIDSORT_R0/data", f"{D}/results/trackers/DANCE-val/HYBRIDSORT_R2_PRIMARY/data"),
}


def load_state(d):
    """One evaluated state, keyed by (sequence, frame, track id)."""
    out = {}
    for fn in sorted(os.listdir(d)):
        if not fn.endswith(".txt"):
            continue
        seq = fn[:-4]
        for line in open(os.path.join(d, fn)):
            line = line.strip()
            if not line:
                continue
            f = line.split(",")
            out[(seq, int(float(f[0])), int(float(f[1])))] = line
    return out


def _require_roots():
    missing = [(v, w) for v, w in (
        ("TRACKEVAL_ROOT", "the pinned TrackEval checkout "
                           "(12c8791b303e0a0b50f753af204249e622d0281a)"),
        ("POSTHOC_ROOT", "the frozen MOT17/MOT20 replay results directory"),
        ("DANCE_ROOT", "the frozen DanceTrack controlled-arm directory"),
    ) if not os.environ.get(v)]
    if missing:
        raise SystemExit(
            "Set these before re-scoring:\n"
            + "\n".join(f"  {v} -> {w}" for v, w in missing)
            + "\n\nThe seed mapping itself needs none of them: it is released at\n"
              "  tpami/results/random_control/R1_RANDOM_CONTROL_SEEDS.csv\n"
              "and `seed_for(d)` is importable on its own. See docs/REPRODUCIBILITY.md.")


def admitted_by_seq():
    _require_roots()
    """The frozen per-row admission class of every inserted row, per system."""
    out = collections.defaultdict(dict)
    for x in csv.DictReader(open(f"{P}/A3_primary_replay_rows.csv")):
        k = (x["sequence"], int(float(x["frame"])), int(float(x["track_id"])))
        out[(x["population"], x["pipeline"])][k] = x["class@0.50"]
    for x in csv.DictReader(open(f"{D}/stv/D1B_stv_rows_full.csv")):
        if x["state"] != "R2_PRIMARY":
            continue
        k = (x["sequence"], int(float(x["frame"])), int(float(x["track_id"])))
        out[("dancetrack", x["tracker"])][k] = x["class@0.50"]
    return out


_CLS = None
_W = {}


def classes():
    global _CLS
    if _CLS is None:
        _CLS = admitted_by_seq()
    return _CLS


def init(pop, trk):
    _require_roots()
    bench, split, gt, r0d, r2d = SYS[(pop, trk)]
    r0, r2 = load_state(r0d), load_state(r2d)
    ins = sorted(set(r2) - set(r0))
    cls = classes()[(pop, trk)]
    assert set(cls) == set(ins), f"{pop}/{trk}: class table != inserted set"
    adm = {k for k in ins if cls[k] == "SEMANTICALLY_ADMITTED"}
    # CANONICAL CANDIDATE ORDERING -- load-bearing, do not relax.
    # random.sample() consumes the RNG by position, so the drawn subset depends on
    # the order of the candidate pool as much as on the seed. These keys are built
    # from a set difference, and set iteration order over tuples containing strings
    # moves with PYTHONHASHSEED. Both the pool within each sequence and the order in
    # which sequences are visited are therefore pinned by sorting, never left to
    # whatever order the dict happened to acquire.
    #   pool order within a sequence : ascending (sequence, frame, track_id)
    #   sequence visit order         : ascending sequence name
    per_seq = {}
    for k in ins:
        per_seq.setdefault(k[0], []).append(k)
    for s in per_seq:
        per_seq[s].sort()
    per_seq = {s: per_seq[s] for s in sorted(per_seq)}
    assert all(p == sorted(p) for p in per_seq.values()), "pool not canonically ordered"
    assert list(per_seq) == sorted(per_seq), "sequence visit order not canonical"
    _W.update(dict(r0=set(r0), r2=r2, ins=ins, adm=adm, bench=bench, split=split,
                   gt=gt, per_seq_ins=per_seq,
                   per_seq_n=dict(collections.Counter(k[0] for k in adm))))


def score(keys, r2, bench, split, gt_root, tag):
    """Write one state and score it with the unmodified evaluator, in-process."""
    import numpy as np, trackeval
    tmp = tempfile.mkdtemp(prefix="rc_", dir=os.environ.get("RC_TMPDIR", "/dev/shm"))
    try:
        d = os.path.join(tmp, f"{bench}-{split}", tag, "data")
        os.makedirs(d)
        by = collections.defaultdict(list)
        for k in keys:
            by[k[0]].append(k)
        for seq, ks in by.items():
            ks.sort(key=lambda k: (k[1], k[2]))
            with open(os.path.join(d, seq + ".txt"), "w") as fh:
                for k in ks:
                    fh.write(r2[k] + "\n")
        dc = trackeval.datasets.MotChallenge2DBox.get_default_dataset_config()
        dc.update({"GT_FOLDER": gt_root + "/", "TRACKERS_FOLDER": tmp + "/",
                   "BENCHMARK": bench, "SPLIT_TO_EVAL": split,
                   "TRACKERS_TO_EVAL": [tag], "TRACKER_SUB_FOLDER": "data",
                   "DO_PREPROC": True, "PRINT_CONFIG": False, "SKIP_SPLIT_FOL": False})
        ec = trackeval.Evaluator.get_default_eval_config()
        ec.update({"USE_PARALLEL": False, "PRINT_RESULTS": False, "PRINT_CONFIG": False,
                   "TIME_PROGRESS": False, "OUTPUT_SUMMARY": False,
                   "OUTPUT_EMPTY_CLASSES": False, "OUTPUT_DETAILED": False,
                   "PLOT_CURVES": False, "DISPLAY_LESS_PROGRESS": True})
        mets = [trackeval.metrics.HOTA(), trackeval.metrics.CLEAR(),
                trackeval.metrics.Identity()]
        out, _ = trackeval.Evaluator(ec).evaluate(
            [trackeval.datasets.MotChallenge2DBox(dc)], mets)
        c = out["MotChallenge2DBox"][tag]["COMBINED_SEQ"]["pedestrian"]
        return {"HOTA": 100 * float(np.mean(c["HOTA"]["HOTA"])),
                "DetA": 100 * float(np.mean(c["HOTA"]["DetA"])),
                "AssA": 100 * float(np.mean(c["HOTA"]["AssA"])),
                "IDF1": 100 * float(c["Identity"]["IDF1"]),
                "MOTA": 100 * float(c["CLEAR"]["MOTA"])}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


ORDERING_RULE = ("pool within a sequence: ascending (sequence, frame, track_id); "
                 "sequence visit order: ascending sequence name")


def selected(d):
    """Only the inserted rows control draw d keeps. Pure selection, nothing scored."""
    rng = random.Random(seed_for(d))
    out = []
    for s in sorted(_W["per_seq_ins"]):
        pool = _W["per_seq_ins"][s]
        n = _W["per_seq_n"].get(s, 0)
        if n:
            out.extend(rng.sample(pool, n))
    assert len(out) == len(_W["adm"]), "draw size != admitted size"
    return out


def draw(d):
    """The row set of control draw d. Pure selection: nothing is scored here."""
    rng = random.Random(seed_for(d))          # explicit integer key -- see SEEDING
    keep = set(_W["r0"])
    for s in sorted(_W["per_seq_ins"]):       # canonical visit order -- see init()
        pool = _W["per_seq_ins"][s]
        n = _W["per_seq_n"].get(s, 0)
        if n:
            keep.update(rng.sample(pool, n))
    assert len(keep) == len(_W["r0"]) + len(_W["adm"]), "draw size != R1 size"
    return keep


def one(d):
    return score(draw(d), _W["r2"], _W["bench"], _W["split"], _W["gt"], f"RAND{d:05d}")


if __name__ == "__main__":
    pop, trk = sys.argv[1], sys.argv[2]
    nproc = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    ndraw = int(sys.argv[4]) if len(sys.argv) > 4 else 1000
    if not _SEEDS and sys.version_info[:2] != (3, 8):
        sys.exit(f"{os.path.basename(SEED_CSV)} not found, and the fallback "
                 f"derivation is only valid on CPython 3.8. Ship the seed artifact.")
    missing = [d for d in range(ndraw) if _SEEDS and d not in _SEEDS]
    if missing:
        sys.exit(f"seed artifact covers no key for draw {missing[0]}")
    init(pop, trk)
    with mp.Pool(nproc, initializer=init, initargs=(pop, trk)) as p:
        res = p.map(one, range(ndraw), chunksize=2)
    print(json.dumps({"population": pop, "tracker": trk, "draws": ndraw,
                      "seed_root": SEED, "seeding": "explicit integer MT19937 key",
                      "executed_seed_expression": EXECUTED_SEED_EXPR,
                      "executed_interpreter": "CPython 3.8.10",
                      "interpreter_here": ".".join(str(x) for x in sys.version_info[:3]),
                      "r1_admitted": len(_W["adm"]), "inserted": len(_W["ins"]),
                      "per_seq_n": _W["per_seq_n"], "metrics": res}, indent=1))

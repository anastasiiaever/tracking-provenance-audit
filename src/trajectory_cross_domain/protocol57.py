"""Frozen Record 57 constants. Single source of truth for the implementation.

Every value here is transcribed from
``docs/wacv/plan/57_TRAJECTORY_CROSS_DOMAIN_PROSPECTIVE_PROTOCOL.json``.
Nothing in this module may be changed on the strength of an observed outcome.
"""
from __future__ import annotations

import os

# PATH NORMALISATION FOR RELEASE (no scientific change): the research tree
# hard-coded two absolute dataset locations. They are resolved from the
# environment here so the module is site-independent. Every SHA-256 pin below is
# transcribed verbatim from the frozen record and is unchanged; the audit
# verifies the file it is given against these pins, so relocating the input
# cannot silently change which corpus was read.
#
#   BDD100K_MOT_PARQUET   -> derived BDD100K MOT label table (parquet)
#   MOT17_ZIP             -> official MOT17.zip
#
# See docs/DATASETS.md for how to obtain each corpus.

RECORD = 57
PROTOCOL_COMMIT = "a1cb20abf5ef518bcf714f92908882c62e095c53"
PROTOCOL_TAG = "tpami-v6-trajectory-protocol-20260825"
PROTOCOL_MD_SHA256 = "009ddb32889a1cc03e523f2322dbb88dd4d29a2afe40f62aa02e7e0d8fcbf8a8"
PROTOCOL_JSON_SHA256 = "57f6ace1e563d605a9d8920dcef9f5240c936052bc1a46fe4c75f1cd827e52e8"

# Semantics inherited verbatim from the frozen KITTI protocol.
KITTI_PROTOCOL_COMMIT = "4f106a473b9cfb7966704cf90122fc81de7f2de1"
KITTI_PROTOCOL_SHA256 = "83c7f5c630b3136ef19c38c5f14d1d26e302fa0d2a4b3139ae6b8f90caa8b32f"

# --------------------------------------------------------------------- inputs
BDD_PATH = os.environ.get("BDD100K_MOT_PARQUET", "data/bdd100k_mot/mot_labels.parquet")
BDD_SHA256 = "e296934ebba47f360fb49a61060d5dfc6027f91a8655b96b565ece7ac1599e02"
BDD_SCHEMA = ("name", "videoName", "frameIndex", "id", "category",
              "attributes.crowd", "attributes.occluded", "attributes.truncated",
              "box2d.x1", "box2d.x2", "box2d.y1", "box2d.y2", "haveVideo")
BDD_CATEGORIES = ("pedestrian", "rider", "car", "truck", "bus", "train",
                  "motorcycle", "bicycle")

MOT17_PATH = os.environ.get("MOT17_ZIP", "data/mot17/MOT17.zip")
MOT17_SHA256 = "2058874e3fb7676a89f8d51e03c8b00353a778d31e37218aa3597692e6dbe655"
MOT17_BASE_SEQUENCES = ("MOT17-02", "MOT17-04", "MOT17-05", "MOT17-09",
                        "MOT17-10", "MOT17-11", "MOT17-13")
MOT17_CANONICAL_DETECTOR = "DPM"
MOT17_CANONICAL_DIRS = tuple("%s-%s" % (s, MOT17_CANONICAL_DETECTOR)
                             for s in MOT17_BASE_SEQUENCES)
MOT17_PEDESTRIAN_CLASS = 1
MOT17_REQUIRED_MARK = 1

# ------------------------------------------------------------------- contract
GAP_GRID = (1, 2, 3, 5, 8, 10, 20)
GATE_1R_CLASSES = ("eligible", "leading", "trailing", "no_anchor")
OPERATOR_NAMES = ("linear", "natural_spline", "pchip")

MATERIALITY_CRITERION = 0.10          # ineligible_fraction >= 0.10
BOOTSTRAP_REPLICATES = 10000
BOOTSTRAP_SEED = 20260825
BOOTSTRAP_IS_CONFIDENCE_INTERVAL = False

POPULATION_PRIMARY = "bdd"
POPULATION_SECONDARY = "mot17"
POPULATIONS = (POPULATION_PRIMARY, POPULATION_SECONDARY)

# Intended result root. Nothing is written here during Record 58.
RESULT_ROOT = "results/trajectory_cross_domain_20260825"


class ProtocolViolation(RuntimeError):
    """Raised whenever the frozen Record 57 contract would be broken."""

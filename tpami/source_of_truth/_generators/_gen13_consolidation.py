"""Post-base consolidation. Runs after _gen1.._gen10 and before _gen11/_gen12.

Every edit below was originally applied directly to a generated artifact, which
meant re-running a base generator silently reverted it. That happened once in
this project. All such edits now live here, guarded so the pass is idempotent.
"""
import os, csv
V="<AUDIT_ROOT>/V6_SOURCE_OF_TRUTH"
def rdw(fn):
    p=os.path.join(V,fn); return p, open(p).read()
def put(p,s,fn,what):
    open(p,"w").write(s); print(f"  {fn}: {what}")
def sub(s,a,b,required=True):
    """replace a with b; a no-op if b is already present"""
    if a in s: return s.replace(a,b), True
    if b in s: return s, False
    if required: raise AssertionError(f"anchor missing: {a[:70]!r}")
    return s, False

# ---------------------------------------------------------------- 00_README
p,s=rdw("00_README.md"); ch=[]
s,d=sub(s,"- `06_EVIDENCE_ARCHITECTURE.csv` — the six evidence arms and their type",
          "- `06_EVIDENCE_ARCHITECTURE.csv` — the eight evidence arms and their type"); ch.append(d)
s,d=sub(s,"- `27_V6_BUILD_GUARDRAILS.md` — writing rules for Codex\n",
 "- `27_V6_BUILD_GUARDRAILS.md` — writing rules for Codex\n"
 "- `28`-`30` — writing-style reference, WSOL style observations, and the\n"
 "  unslopping rules. Style only; they carry no scientific authority.\n"
 "- `31_INTERNAL_CONSISTENCY_AUDIT.md`, `32_DUPLICATE_CLAIM_LEDGER.csv` — the\n"
 "  internal-consistency sweep and its claim ledger.\n"
 "- `_generators/` — the scripts that wrote these files, kept for provenance.\n"
 "  `run_all.py` rebuilds the packet from them in order. They are inputs to the\n"
 "  build, not sources of fact.\n"
 "- `V6_SOURCE_OF_TRUTH_MANIFEST.sha256` — hashes of every file above\n"); ch.append(d)
s,d=sub(s,"5. Every numeric claim must cite a row of `05_NUMERIC_LEDGER.csv`.",
 "5. Every numeric claim must cite a row of `05_NUMERIC_LEDGER.csv`.\n"
 "6. If two authoritative artifacts disagree and `01` does not resolve it, write\n"
 "   `[CONTRADICTION]` with both values and both paths, and stop.\n"
 "7. Style is governed by `28`-`30`. Those files may change wording and may never\n"
 "   change a number, a definition, or a caveat."); ch.append(d)
if any(ch): put(p,s,"00_README.md","inventory and rules restored")

# ---------------------------------------------------------- 01_ARTIFACT_PRECEDENCE
p,s=rdw("01_ARTIFACT_PRECEDENCE.md"); ch=[]
s,d=sub(s,"19.046935","19.0469",required=False); ch.append(d)
bib="| bibliography file for the main text | the root `main.bib`, 66 entries, missing `luiten2020trackeval` | `reconcile_20261003/main_v4_docx.bib`, 67 entries, which `\\bibliography{main_v4_docx}` actually resolves to | use the reconcile copy, or add the missing entry to the root copy first |"
anchor="| 12,767 per-row reproduction | Step 9 closing block | Step 9.1 `STEP9_REPORT_CORRECTIONS.md` | population and identities reproduced; no frozen per-row class table exists |"
if bib not in s:
    s,d=sub(s,anchor,anchor+"\n"+bib); ch.append(d)
if any(ch): put(p,s,"01_ARTIFACT_PRECEDENCE.md","bib override and precision restored")

# ------------------------------------------------------------- 03_ALLOWED_CLAIMS
p,s=rdw("03_ALLOWED_CLAIMS.md"); ch=[]
for a,b in (("19.046935","19.0469"),
            ("97.39 to 98.22","97.392 to 98.2151"),
            ("62.04 to 73.54","62.0388 to 73.5409"),
            ("56.84 to 67.47","56.8389 to 67.4668"),
            ("56.839 to 67.467","56.8389 to 67.4668"),
            ("median share of absolute movement 0.181,","median share of absolute movement 0.1812,")):
    s,d=sub(s,a,b,required=False); ch.append(d)
s,d=sub(s,"- AFLink changes the identity of 1,316 rows across 29 remappings and loses one\n  row, from 46,914 to 46,913.",
 "- AFLink changes the identity of 1,316 rows across 29 remappings, reduces the\n"
 "  distinct identity count from 435 to 406, and loses one row, from 46,914 to\n  46,913.",required=False); ch.append(d)
s,d=sub(s,"- No R1 analogue exists for this transition because withholding added rows would\n  change the fit and therefore the surviving coordinates.",
 "- No R1 analogue exists for this transition because withholding added rows would\n"
 "  change the fit and therefore the surviving coordinates. The frozen artifact\n"
 "  records this in its own `nesting_claim` and `stv_state` fields.\n"
 "- The base tracker output was written but not scored, so the AFLink comparison is\n"
 "  structural only.",required=False); ch.append(d)
if any(ch): put(p,s,"03_ALLOWED_CLAIMS.md","identity counts, nesting claim and precision restored")

# --------------------------------------------------- 04_FORBIDDEN_OR_OBSOLETE_CLAIMS
p,s=rdw("04_FORBIDDEN_OR_OBSOLETE_CLAIMS.md"); ch=[]
for a,b in (("19.046935","19.0469"),
            ("62.04 to 73.54","62.0388 to 73.5409"),
            ("1.78 to 2.61","1.7849 to 2.6080"),
            ("median GP share 0.181, max 0.872","median GP share 0.1812, max 0.8722")):
    s,d=sub(s,a,b,required=False); ch.append(d)
old="| S1 exists for StrongSORT++ | PRE, S0, S2 only; no S1, because GSI is not row-additive | frozen `DECOMPOSITION.json` |\n"
new = """| using `S0`, `S1`, `S2` and the frozen `PRE`, `S0`, `S2` interchangeably | the two naming schemes collide; see the naming-collision note below | v5 supplement Sec. S6 against frozen `DECOMPOSITION.json` |
| an R1 analogue exists for the AFLink or GSI stages | withholding added rows changes the fit, so no row-subset intervention exists | frozen `states.py` field `r1_status_for_non_row_additive` |

## Naming collision, StrongSORT++ states

This is a labelling hazard, not a numerical disagreement. The counts agree
exactly between v5 and the frozen artifact.

| v5 supplement Sec. S6 | frozen `DECOMPOSITION.json` | rows | what it is |
|---|---|---|---|
| `S0` | `PRE` | 46,914 | base tracker output |
| `S1` | `S0` | 46,913 | post-AFLink |
| `S2` | `S2` | 50,097 | post-GSI |

v6 must pick one scheme and say which. Recommended: keep the frozen artifact's
`PRE` / `S0` / `S2`, because the artifacts and the released `states.py` use it and
because `S1` invites the reader to expect an R1-style withheld-row state, which
does not exist for this transition. If v6 instead keeps v5's `S0` / `S1` / `S2`,
every cross-reference to an artifact must be relabelled, and Table S6's
`$S_2 - S_1$` row must be read as post-GSI minus post-AFLink in both schemes.

Either way, state explicitly that the base tracker output was written but not
scored, so the AFLink comparison is structural only.
"""
s,d=sub(s,old,new,required=False); ch.append(d)
if any(ch): put(p,s,"04_FORBIDDEN_OR_OBSOLETE_CLAIMS.md","naming collision and precision restored")

# ------------------------------------------------------------- 05_NUMERIC_LEDGER
p=os.path.join(V,"05_NUMERIC_LEDGER.csv")
rows=list(csv.reader(open(p))); hdr,body=rows[0],rows[1:]
FIX={"M20-GSPCT":("19.0469","artifact prints 19.0469; the exact ratio 6631/34814 is 19.0469351%"),
     "DT-RL-ADM-RANGE":("97.392 to 98.2151",None),"DT-RL-NA-RANGE":("62.0388 to 73.5409",None),
     "DT-RL-ADM-BELOW":("1.7849 to 2.6080",None),"GSI-RW-RANGE":("56.8389 to 67.4668",None),
     "GSI-OC-SORT-RWPCT":("67.4668",None),"GSI-Deep-OC-SORT-RWPCT":("61.0163",None),
     "GSI-Hybrid-SORT-RWPCT":("56.8389",None),"GSI-ByteTrack-GPRWPCT":("59.7374",None),
     "GSI-OC-SORT-GPRWPCT":("68.7746",None),"GSI-Deep-OC-SORT-GPRWPCT":("62.4304",None),
     "GSI-Hybrid-SORT-GPRWPCT":("58.2376",None),"D2C-GP-SHARE":("0.1812",None),
     "D2C-GP-SHARE-RANGE":("0.0421 to 0.8722",None)}
for r in body:
    if r[0] in FIX:
        v,note=FIX[r[0]]; r[4]=v
        if note: r[8]=note
ADD=[
 ["SS-IDS-PRE","MOT17","AFLink and GSI","distinct identities in PRE","435","identities","frozen strongsort/DECOMPOSITION.json","CURRENT",""],
 ["SS-IDS-S0","MOT17","AFLink and GSI","distinct identities in S0","406","identities","frozen strongsort/DECOMPOSITION.json","CURRENT",""],
 ["SS-SHARED","MOT17","AFLink and GSI","rows shared between S0 and S2","46913","rows","frozen strongsort/DECOMPOSITION.json","CURRENT",""],
 ["SS-DROP","MOT17","AFLink and GSI","rows dropped by GSI","0","rows","frozen strongsort/DECOMPOSITION.json","CURRENT",""],
 ["M17-CROSS-MARGIN","MOT17","released DTI","|R0 margin| of the 5 crossing cells","0.5104 to 1.4567","metric points","FINAL_unified_pairwise_margins.csv","CURRENT",""],
 ["M17-UNCH-MIN","MOT17","released DTI","smallest |R0 margin| among the 45 unchanged cells","0.1869","metric points","FINAL_unified_pairwise_margins.csv","CURRENT",""],
 ["M17-UNCH-BELOW","MOT17","released DTI","unchanged cells at or below the largest crossing margin","17 of 45","cells","FINAL_unified_pairwise_margins.csv","CURRENT",""],
 ["M17-CROSS-APPEAR","MOT17","released DTI","appearances in crossing cells","Hybrid-SORT 4, Deep-OC-SORT 3, OC-SORT 2, BoT-SORT 1","appearances","FINAL_unified_pairwise_margins.csv","CURRENT",""],
 ["M17-PSIGN-RANGE","MOT17","released DTI","P(sign differs) across the five crossings","0.3585 to 0.5859","frequency","FINAL_unified_pairwise_margins.csv","CURRENT","descriptive, not a p-value"],
 ["DTI-CROSS-MARGIN","DanceTrack","controlled DTI","|R0 margin| of the 7 crossing cells","0.6581 to 2.2203","metric points","FINAL_unified_pairwise_margins.csv","CURRENT",""],
 ["DTI-UNCH-MIN","DanceTrack","controlled DTI","smallest |R0 margin| among the 23 unchanged cells","0.2170","metric points","FINAL_unified_pairwise_margins.csv","CURRENT",""],
 ["DTI-UNCH-BELOW","DanceTrack","controlled DTI","unchanged cells at or below the largest crossing margin","6 of 23","cells","FINAL_unified_pairwise_margins.csv","CURRENT",""],
 ["DTI-CROSS-APPEAR","DanceTrack","controlled DTI","appearances in crossing cells","Hybrid-SORT 5, Deep-OC-SORT 4, OC-SORT 3, ByteTrack 2","appearances","FINAL_unified_pairwise_margins.csv","CURRENT","ByteTrack has the highest non-admission and the fewest appearances"],
 ["GSI-CROSS-APPEAR","DanceTrack","controlled GSI","appearances in crossing cells","Hybrid-SORT 5, Deep-OC-SORT 4, OC-SORT 3, ByteTrack 2","appearances","FINAL_unified_pairwise_margins.csv","CURRENT",""],
 ["GSI-PSIGN-RANGE","DanceTrack","controlled GSI","P(sign differs) across the seven crossings","0.3148 to 0.9365","frequency","FINAL_unified_pairwise_margins.csv","CURRENT","descriptive, not a p-value"],
 ["XARM-CROSS-ID","DanceTrack","DTI against GSI","crossing cells shared between the two operator arms","7 of 7, identical pair-and-metric identities","cells","FINAL_unified_pairwise_margins.csv","CURRENT",""],
 ["DT-RL-NA-ZERO","DanceTrack","row-local support","non-admitted rows with maximum IoU exactly 0 against any scoreable GT","3 to 18 per tracker, 0.0509 to 0.2257 %","rows","D1B.2 D1B2_row_local_support.csv","CURRENT","almost no non-admitted row is geometrically isolated"],
 ["DT-RL-ADM-ZERO","DanceTrack","row-local support","admitted rows with maximum IoU exactly 0","0 for all four trackers","rows","D1B.2 D1B2_row_local_support.csv","CURRENT",""],
 ["DT-ABS-BUCKETS","DanceTrack","row-local support","REFERENCE_ABSENT rows by maximum IoU: at or above the gate / between 0 and the gate / exactly 0","2054 / 1394 / 3","rows","D1B.2 D1B2_reference_absent_local_support.csv","CURRENT","the 3 zero-overlap rows are exactly the 3 with no other identity overlapping"],
 ["DT-ABS-CLASS-GE","DanceTrack","row-local support","TARGET_REFERENCE_ABSENT rows at maxIoU >= 0.5, per tracker","55.6474 to 67.4306","percent","D1B.2 D1B2_row_local_support.csv","CURRENT",""],
 ["D2C-GP-MOVED","DanceTrack","GSI decomposition","metric cells with a non-zero GP delta","20 of 20","cells","D2C D2C_three_state_metrics.csv","CURRENT",""],
 ["DT-PERSIST-NESTING","DanceTrack","controlled DTI","Hybrid-SORT rows REFERENCE_ABSENT at gate 0.70 but not at every gate","1 of 484","rows","D1B_gate_persistence_rows.csv","CURRENT","dancetrack0094 frame 400 track_id 22; the classes are not nested across gates"],
]
have={r[0] for r in body}
body += [r for r in ADD if r[0] not in have]
with open(p,"w",newline="") as f:
    w=csv.writer(f); w.writerow(hdr); w.writerows(body)
print(f"  05_NUMERIC_LEDGER.csv: {len(body)} rows")

# ---------------------------------------------------------------- 10_TABLE_PLAN
p,s=rdw("10_TABLE_PLAN.md"); ch=[]
s,d=sub(s,"### T2. Evidence architecture — NEW in v6\n",
          "### T2. Evidence architecture — NEW in v6, placed in Sec. 3.4\n",required=False); ch.append(d)
s,d=sub(s,"### T7. Operators that admit no row-additive decomposition — REUSE v5 Sec. S6 as a main table",
          "### T7. Operators that admit no row-additive decomposition — Sec. 6, from v5 Sec. S5",required=False); ch.append(d)
s,d=sub(s,"Job: the structural result, promoted from supplement prose because it now carries\ntwo arms, including the boundary case.",
          "Job: the structural result, promoted from supplement prose into its own main-text\nsection because it now carries two arms, including the boundary case.",required=False); ch.append(d)
s,d=sub(s,"""- Percentages carry the precision given in the ledger. Do not round 19.046935 to
  19.05 in the supplement table that is meant to be checkable; the main text may
  use 19.05 if the supplement gives full precision.""",
"""- Percentages carry the precision the artifact prints. The Step 9 tables print
  four decimals, so the MOT20 gate-stable figure is 19.0469 %. Where the main
  text rounds further, the supplement must give both the four-decimal percentage
  and the two counts, 6,631 of 34,814, so a reader can recompute it.""",required=False); ch.append(d)
s,d=sub(s,"the MOT20 row must carry its gate-stable figure, 6,631 and\n19.046935 %",
          "the MOT20 row must carry its gate-stable figure, 6,631 and\n19.0469 %",required=False); ch.append(d)
if any(ch): put(p,s,"10_TABLE_PLAN.md","section pointers and precision rule restored")

# ------------------------------------------------------------ 14_SUPPLEMENT_PLAN
p,s=rdw("14_SUPPLEMENT_PLAN.md"); ch=[]
for a,b in (("19.046935","19.0469"),("1.78 to 2.61","1.7849 to 2.6080"),
            ("58.24 to 68.77","58.2376 to 68.7746"),("median share 0.181,","median share 0.1812,")):
    s,d=sub(s,a,b,required=False); ch.append(d)
if any(ch): put(p,s,"14_SUPPLEMENT_PLAN.md","precision restored")

# --------------------------------------------- 21 / 22 / 24 precision restoration
for fn,subs in (("21_RESULTS_GSI_FACT_PACKET.md",
                   (("56.839 to 67.467","56.8389 to 67.4668"),("| 67.467 |","| 67.4668 |"),
                    ("| 61.016 |","| 61.0163 |"),("| 56.839 |","| 56.8389 |"),
                    ("58.24 to 68.77","58.2376 to 68.7746"),
                    ("median 0.181 and\n  ranges 0.042 to 0.872","median 0.1812 and\n  ranges 0.0421 to 0.8722"))),
                ("22_RESULTS_MOT20_FACT_PACKET.md",(("19.046935","19.0469"),)),
                ("24_LIMITATIONS_FACT_PACKET.md",
                   (("62.04 to 73.54","62.0388 to 73.5409"),("1.78 to 2.61","1.7849 to 2.6080")))):
    p,s=rdw(fn); ch=[]
    for a,b in subs:
        s,d=sub(s,a,b,required=False); ch.append(d)
    if any(ch): put(p,s,fn,"precision restored")

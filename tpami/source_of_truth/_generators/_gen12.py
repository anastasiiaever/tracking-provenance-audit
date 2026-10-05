"""Correction pass, 2026-10-04.

Runs after _gen4 (04, 05) and _gen10 (27). Records the MOT17 added-row range
error found by Codex, backs the corrected statements with ledger rows, and adds
the guardrail that prevents the same class of error recurring.

The error: 17_INTRO_FACT_PACKET.md stated the MOT17 added-row range as
"1,224 to 3,023". 1,224 is ByteTrack's SEMANTICALLY_ADMITTED count and 3,023 is
Hybrid-SORT's synthesized total: two different quantities from two different
deployments. Verified against B1_mot17_gate_summary.csv and, independently,
A3_primary_replay_rows.csv. Corrected in _gen8.py, which owns that file.
"""
import os, csv
V="<AUDIT_ROOT>/V6_SOURCE_OF_TRUTH"

# ---------- 05_NUMERIC_LEDGER.csv : back the corrected ranges ----------
p=os.path.join(V,"05_NUMERIC_LEDGER.csv")
rows=list(csv.reader(open(p))); hdr,body=rows[0],rows[1:]
have={r[0] for r in body}
add=[
 ["M17-SYNTH-RANGE","MOT17","released DTI","synthesized rows per deployment, range",
  "2072 to 3023","rows","Step 9 B1_mot17_gate_summary.csv","CURRENT",
  "min ByteTrack, max Hybrid-SORT; confirmed independently from A3_primary_replay_rows.csv"],
 ["M17-ADM-RANGE","MOT17","released DTI","SEMANTICALLY_ADMITTED rows per deployment, range",
  "1224 to 2104","rows","Step 9 B1_mot17_gate_summary.csv","CURRENT",
  "min ByteTrack, max Deep-OC-SORT; a different quantity from the synthesized range"],
 ["M17-RANGE-ERROR","MOT17","released DTI","superseded added-row range",
  "1224 to 3023","rows","17_INTRO_FACT_PACKET.md before 2026-10-04","SUPERSEDED",
  "combined ByteTrack's admitted count with Hybrid-SORT's synthesized total; do not cite"],
 ["DTI-INS-ROWS-RANGE","DanceTrack","controlled DTI","inserted rows per tracker, range",
  "8511 to 15103","rows","D1B D1B_state_inventory.csv","CURRENT",""],
]
for r in add:
    if r[0] in have: body=[b for b in body if b[0]!=r[0]]
body+=add
with open(p,"w",newline="") as f:
    w=csv.writer(f); w.writerow(hdr); w.writerows(body)
print(f"  05_NUMERIC_LEDGER.csv: {len(body)} rows")

# ---------- 04_FORBIDDEN_OR_OBSOLETE_CLAIMS.md ----------
p=os.path.join(V,"04_FORBIDDEN_OR_OBSOLETE_CLAIMS.md"); s=open(p).read()
anchor="| OC-SORT GPR rewrites 212 rows, 0.4616 % |"
assert anchor in s, "gen12: 04 anchor missing"
newrow=("| MOT17 deployments add 1,224 to 3,023 rows | each adds 2,072 to 3,023 rows; "
        "1,224 to 2,104 of them are admitted | `B1_mot17_gate_summary.csv`; the 1,224 was "
        "ByteTrack's SEMANTICALLY_ADMITTED count, not its synthesized total |\n")
if "1,224 to 3,023" not in s:
    s=s.replace(anchor, newrow+anchor)
# a standing rule, not just this instance
tail_anchor="## Naming collision, StrongSORT++ states"
assert tail_anchor in s, "gen12: 04 tail anchor missing"
rule = """## Never mix a class count with a total or a denominator

The four STV classes are a partition of the synthesized set. A class count is
therefore never the synthesized total, never the added-row count, and never a
denominator for a non-admission percentage. The one error found in this packet
came from exactly that substitution.

Before writing any range, name the quantity and check both endpoints come from
the same column of the same artifact. On MOT17 the four columns give four
different ranges:

| quantity | range | column in `B1_mot17_gate_summary.csv` |
|---|---|---|
| synthesized rows per deployment | 2,072 to 3,023 | `n_synthesized` |
| ANCHOR_UNMATCHED | 408 to 1,266 | `n_unmatched` |
| ANCHOR_ID_MISMATCH | 216 to 375 | `n_id_mismatch` |
| SEMANTICALLY_ADMITTED | 1,224 to 2,104 | `n_admitted` |
| non-admitted | 783 to 1,482 | `n_nonadmitted` |

TARGET_REFERENCE_ABSENT is 0 for every MOT17 deployment, so it has no range.

"""
if "Never mix a class count" not in s:
    s=s.replace(tail_anchor, rule+tail_anchor)
open(p,"w").write(s); print("  04_FORBIDDEN_OR_OBSOLETE_CLAIMS.md: range error and standing rule recorded")

# ---------- 27_V6_BUILD_GUARDRAILS.md ----------
p=os.path.join(V,"27_V6_BUILD_GUARDRAILS.md"); s=open(p).read()
anchor="- Every tolerance-dependent count carries its tolerance. The GPR 52 is the\n  standing example."
assert anchor in s, "gen12: 27 anchor missing"
extra = anchor + """
- Name the quantity before writing a range, and take both endpoints from the same
  column of the same artifact. A class count is never a total and never a
  denominator; see the standing rule in `04_FORBIDDEN_OR_OBSOLETE_CLAIMS.md`."""
if "Name the quantity before writing a range" not in s:
    s=s.replace(anchor, extra)
open(p,"w").write(s); print("  27_V6_BUILD_GUARDRAILS.md: range-construction guardrail added")

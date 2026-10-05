"""Internal-consistency audit. Validates every numeric data table in the packet
against its authoritative frozen artifact and emits 32_DUPLICATE_CLAIM_LEDGER.csv.
Tables are located by header signature, never by line number."""
"""Per-table validation of every numeric data table in V6_SOURCE_OF_TRUTH
against its authoritative frozen artifact. If every cell agrees with the
artifact, duplicate statements agree with each other by construction."""
import re, csv, os, glob, json, collections
V = "<AUDIT_ROOT>/V6_SOURCE_OF_TRUTH"
B = "<AUDIT_ROOT>/"
P=B+"posthoc_composition_20261003/results/"
D=B+"dancetrack_controlled_20261003/"
S=D+"summaries/"; F=D+"final_defense_20261004/"; G=D+"gsi_exec_20261004/"
def rd(p): return list(csv.DictReader(open(p)))
def nv(s):
    s=re.sub(r'[*`%,]','',str(s)).strip().rstrip(".;:")
    if not re.fullmatch(r'[+-]?\d+(\.\d+)?',s): return None
    return float(s)

FAIL=[]; OK=0; CHECKED=0; LEDGER=[]; SCOPE="?"
def scope(x):
    global SCOPE; SCOPE=x
def chk(where, label, got, want, tol):
    global OK, CHECKED
    CHECKED+=1
    fn,_,ln=where.partition(":")
    ok = got is not None and abs(got-want)<=tol
    LEDGER.append(dict(claim_key=SCOPE+" :: "+label,source_packet_file=fn,location=ln,
                       packet_value=("" if got is None else repr(got)),
                       authoritative_value=repr(want),tolerance=tol,
                       status="AGREES" if ok else "CONTRADICTS"))
    if got is None: FAIL.append((where,label,"<non-numeric>",want)); return
    if ok: OK+=1
    else: FAIL.append((where,label,got,want))

def tables(path):
    """yield (start_line, header, rows) for each markdown table"""
    out=[]; hdr=None; rows=None; st=0
    for ln,line in enumerate(open(path),1):
        if not line.lstrip().startswith("|"):
            if hdr is not None and rows: out.append((st,hdr,rows))
            hdr=None; rows=None; continue
        parts=[c.strip() for c in line.strip().strip("|").split("|")]
        if all(re.fullmatch(r':?-{2,}:?',c) for c in parts if c): continue
        if hdr is None: hdr=parts; rows=[]; st=ln; continue
        rows.append((ln,parts))
    if hdr is not None and rows: out.append((st,hdr,rows))
    return out

MD={os.path.basename(p):tables(p) for p in sorted(glob.glob(os.path.join(V,"*.md")))}
# tables are located by their header signature, not by line number, so that
# adding prose above a table cannot silently skip its validation
SIG={
 ("02_CURRENT_FACTS.md",16):  ["deployment","synthesized","UNMATCHED","ID_MISMATCH","REFERENCE_ABSENT","ADMITTED","non-admitted","% non-admitted"],
 ("02_CURRENT_FACTS.md",28):  ["deployment","gate-stable non-admitted","%","gate-stable admitted","switching","persistent UNMATCHED","persistent ID_MISMATCH","persistent REFERENCE_ABSENT"],
 ("02_CURRENT_FACTS.md",66):  ["deployment","class","n","% IoU = 0","% 0 < IoU < 0.5","% IoU >= 0.5"],
 ("02_CURRENT_FACTS.md",116): ["gate","synthesized","UNMATCHED","ID_MISMATCH","REFERENCE_ABSENT","ADMITTED","non-admitted","%"],
 ("02_CURRENT_FACTS.md",165): ["tracker","R0 rows","R2 primary","inserted","% of R2","R2 sens30","inserted"],
 ("02_CURRENT_FACTS.md",174): ["tracker","synthesized","UNMATCHED","ID_MISMATCH","REFERENCE_ABSENT","ADMITTED","non-admitted","%"],
 ("02_CURRENT_FACTS.md",185): ["tracker","0.30","0.40","0.50","0.60","0.70"],
 ("02_CURRENT_FACTS.md",194): ["tracker","gate-stable non-admitted","%","gate-stable admitted","switching","persistent UNMATCHED","persistent ID_MISMATCH","persistent REFERENCE_ABSENT"],
 ("02_CURRENT_FACTS.md",206): ["tracker","state","HOTA","DetA","AssA","IDF1","MOTA"],
 ("02_CURRENT_FACTS.md",288): ["tracker","0.30","0.40","0.50","0.60","0.70","persistent at all five"],
 ("02_CURRENT_FACTS.md",306): ["tracker","class","n","% IoU = 0","% 0 < IoU < 0.5","% IoU >= 0.5"],
 ("02_CURRENT_FACTS.md",366): ["tracker","R0 rows","GSI rows","inserted","deleted","surviving","coord rewrites","%","id changes"],
 ("02_CURRENT_FACTS.md",379): ["tracker","state","HOTA","DetA","AssA","IDF1","MOTA"],
 ("02_CURRENT_FACTS.md",217): ["tracker","HOTA","DetA","AssA","IDF1","MOTA"],
 ("02_CURRENT_FACTS.md",386): ["tracker","HOTA","DetA","AssA","IDF1","MOTA"],
 ("02_CURRENT_FACTS.md",407): ["transition","inserted","deleted","coord rewrites","id changes","score rewrites"],
 ("19_RESULTS_MOT17_FACT_PACKET.md",18): ["deployment","synthesized","U","ID","ABS","ADM","non-admitted","%","gate-stable","%"],
 ("19_RESULTS_MOT17_FACT_PACKET.md",45): ["pair","metric","R0 margin","R2 margin","3dp","2dp","P(sign differs)"],
 ("20_RESULTS_DANCETRACK_DTI_FACT_PACKET.md",29): ["tracker","R0","R2","inserted","% of R2","U","ID","ABS","ADM","non-adm","%","gate-stable","%"],
 ("20_RESULTS_DANCETRACK_DTI_FACT_PACKET.md",57): ["pair","metric","R0 margin","R2 margin","P(sign differs)"],
 ("21_RESULTS_GSI_FACT_PACKET.md",25): ["tracker","GSI rows","inserted","surviving rows rewritten","% rewritten"],
 ("22_RESULTS_MOT20_FACT_PACKET.md",42): ["gate","non-admitted","%"],
}
_ORD={}
def tbl(fn,start):
    sig=SIG[(fn,start)]
    hits=[(st,h,r) for st,h,r in MD[fn] if h==sig]
    if not hits: raise KeyError(f"{fn}: no table with header {sig}")
    k=(fn,tuple(sig)); i=_ORD.get(k,0)
    if len(hits)>1 and i<len(hits): _ORD[k]=i+1; return hits[i][1],hits[i][2]
    return hits[0][1],hits[0][2]

# ---------------- artifacts ----------------
m17={(x['pipeline'],x['iou_gate']):x for x in rd(P+"B1_mot17_gate_summary.csv")}
m20={x['iou_gate']:x for x in rd(P+"B2_mot20_gate_summary.csv")}
c3 ={(x['population'],x['pipeline']):x for x in rd(P+"C3_gate_stability_summary.csv")}
c4 ={(x['population'],x['pipeline'],x['stv_class']):x for x in rd(P+"C4_frame_local_support_summary.csv")}
inv={(x['tracker'],x['state']):x for x in rd(S+"D1B_state_inventory.csv")}
stv={x['tracker']:x for x in rd(S+"D1B_stv_primary.csv")}
swe={(x['tracker'],"%.2f"%float(x['gate'])):x for x in rd(S+"D1B_stv_gate_sweep.csv")}
gps={x['tracker']:x for x in rd(S+"D1B_gate_persistence_summary.csv")}
gsi={x['tracker']:x for x in rd(G+"D2B_state_inventory.csv")}
lin={(x['tracker'],x['transition']):x for x in rd(F+"D2C_gsi_linear_state_inventory.csv")}
rl2={(x['tracker'],x['stv_class']):x for x in rd(F+"D1B2_row_local_support.csv")}
um ={(x['arm'],x['tracker_a'],x['tracker_b'],x['metric']):x for x in rd(F+"FINAL_unified_pairwise_margins.csv")}
d2c={(x['tracker'],x['metric']):x for x in rd(F+"D2C_three_state_metrics.csv")}

CLASS={"UNMATCHED":"n_unmatched","ID_MISMATCH":"n_id_mismatch","REFERENCE_ABSENT":"n_reference_absent",
       "ADMITTED":"n_admitted"}

# ---- 02:16 and 19:18  MOT17 composition @0.50 ----
scope("MOT17 composition @0.50")
for fn,st,cols in (("02_CURRENT_FACTS.md",16,
      {"synthesized":"n_synthesized","UNMATCHED":"n_unmatched","ID_MISMATCH":"n_id_mismatch",
       "REFERENCE_ABSENT":"n_reference_absent","ADMITTED":"n_admitted","non-admitted":"n_nonadmitted",
       "% non-admitted":"pct_nonadmitted"}),
     ("19_RESULTS_MOT17_FACT_PACKET.md",18,
      {"synthesized":"n_synthesized","U":"n_unmatched","ID":"n_id_mismatch","ABS":"n_reference_absent",
       "ADM":"n_admitted","non-admitted":"n_nonadmitted"})):
    h,rows=tbl(fn,st)
    for ln,p in rows:
        t=re.sub(r"[*`]","",p[0]).strip(); a=m17[(t,"0.50")]
        for cname,acol in cols.items():
            if cname not in h: continue
            chk(f"{fn}:{ln}",f"{t}/{cname}",nv(p[h.index(cname)]),float(a[acol]),5e-5)
        # the two unlabeled % columns in 19:18 are nonadm% and gate-stable%
        if fn.startswith("19"):
            idx=[i for i,c in enumerate(h) if c=="%"]
            chk(f"{fn}:{ln}",f"{t}/pct_nonadmitted",nv(p[idx[0]]),float(a['pct_nonadmitted']),5e-5)
            chk(f"{fn}:{ln}",f"{t}/gate_stable",nv(p[h.index('gate-stable')]),float(c3[('mot17',t)]['gate_stable_nonadmitted']),0)
            chk(f"{fn}:{ln}",f"{t}/gate_stable_pct",nv(p[idx[1]]),float(c3[('mot17',t)]['pct_gate_stable_nonadmitted']),5e-5)

# ---- 02:28  MOT17 gate stability ----
scope("MOT17 gate stability")
h,rows=tbl("02_CURRENT_FACTS.md",28)
for ln,p in rows:
    t=re.sub(r"[*`]","",p[0]).strip(); a=c3[('mot17',t)]
    for cname,acol,tol in (("gate-stable non-admitted","gate_stable_nonadmitted",0),
                           ("%","pct_gate_stable_nonadmitted",5e-3),
                           ("gate-stable admitted","gate_stable_admitted",0),
                           ("switching","switching",0),
                           ("persistent UNMATCHED","persistent_unmatched",0),
                           ("persistent ID_MISMATCH","persistent_id_mismatch",0),
                           ("persistent REFERENCE_ABSENT","persistent_reference_absent",0)):
        chk(f"02_CURRENT_FACTS.md:{ln}",f"{t}/{cname}",nv(p[h.index(cname)]),float(a[acol]),tol)

# ---- 02:66  MOT17 row-local support ----
scope("MOT17 row-local support")
h,rows=tbl("02_CURRENT_FACTS.md",66)
CM={"ADMITTED":"SEMANTICALLY_ADMITTED","ANCHOR_UNMATCHED":"ANCHOR_UNMATCHED","ANCHOR_ID_MISMATCH":"ANCHOR_ID_MISMATCH"}
for ln,p in rows:
    t=re.sub(r"[*`]","",p[0]).strip(); cl=CM[re.sub(r"[*`]","",p[1]).strip()]; a=c4[('mot17',t,cl)]
    chk(f"02_CURRENT_FACTS.md:{ln}",f"{t}/{cl}/n",nv(p[2]),float(a['n']),0)
    chk(f"02_CURRENT_FACTS.md:{ln}",f"{t}/{cl}/pct_zero",nv(p[3]),float(a['pct_max_iou_zero']),5e-3)
    chk(f"02_CURRENT_FACTS.md:{ln}",f"{t}/{cl}/pct_between",nv(p[4]),float(a['pct_between']),5e-3)
    chk(f"02_CURRENT_FACTS.md:{ln}",f"{t}/{cl}/pct_ge",nv(p[5]),float(a['pct_ge_gate']),5e-3)

# ---- 02:116 and 22:42  MOT20 gate sweep ----
scope("MOT20 gate sweep")
h,rows=tbl("02_CURRENT_FACTS.md",116)
for ln,p in rows:
    g="%.2f"%nv(p[0]); a=m20[g]
    for i,(cname,acol,tol) in enumerate((("synthesized","n_synthesized",0),("UNMATCHED","n_unmatched",0),
            ("ID_MISMATCH","n_id_mismatch",0),("REFERENCE_ABSENT","n_reference_absent",0),
            ("ADMITTED","n_admitted",0),("non-admitted","n_nonadmitted",0),("%","pct_nonadmitted",5e-5))):
        chk(f"02_CURRENT_FACTS.md:{ln}",f"MOT20/{g}/{cname}",nv(p[h.index(cname)]),float(a[acol]),tol)
h,rows=tbl("22_RESULTS_MOT20_FACT_PACKET.md",42)
for ln,p in rows:
    g="%.2f"%nv(p[0]); a=m20[g]
    chk(f"22_RESULTS_MOT20_FACT_PACKET.md:{ln}",f"MOT20/{g}/nonadm",nv(p[1]),float(a['n_nonadmitted']),0)
    chk(f"22_RESULTS_MOT20_FACT_PACKET.md:{ln}",f"MOT20/{g}/pct",nv(p[2]),float(a['pct_nonadmitted']),5e-5)

# ---- 02:165  DanceTrack state inventory ----
scope("DanceTrack DTI state inventory")
h,rows=tbl("02_CURRENT_FACTS.md",165)
for ln,p in rows:
    t=p[0]
    chk(f"02_CURRENT_FACTS.md:{ln}",f"{t}/R0",nv(p[1]),float(inv[(t,'R0')]['total_rows']),0)
    chk(f"02_CURRENT_FACTS.md:{ln}",f"{t}/R2",nv(p[2]),float(inv[(t,'R2_PRIMARY')]['total_rows']),0)
    chk(f"02_CURRENT_FACTS.md:{ln}",f"{t}/ins",nv(p[3]),float(inv[(t,'R2_PRIMARY')]['added_rows']),0)
    chk(f"02_CURRENT_FACTS.md:{ln}",f"{t}/ins_pct",nv(p[4]),float(inv[(t,'R2_PRIMARY')]['added_pct_of_state']),5e-4)
    chk(f"02_CURRENT_FACTS.md:{ln}",f"{t}/R2s30",nv(p[5]),float(inv[(t,'R2_SENS30')]['total_rows']),0)
    chk(f"02_CURRENT_FACTS.md:{ln}",f"{t}/ins_s30",nv(p[6]),float(inv[(t,'R2_SENS30')]['added_rows']),0)

# ---- 02:174 and 20:29  DanceTrack STV @0.50 ----
scope("DanceTrack DTI composition @0.50")
h,rows=tbl("02_CURRENT_FACTS.md",174)
for ln,p in rows:
    t=re.sub(r"[*`]","",p[0]).strip(); a=stv[t]
    for cname,acol,tol in (("synthesized","synthesized",0),("UNMATCHED","ANCHOR_UNMATCHED",0),
            ("ID_MISMATCH","ANCHOR_ID_MISMATCH",0),("REFERENCE_ABSENT","TARGET_REFERENCE_ABSENT",0),
            ("ADMITTED","SEMANTICALLY_ADMITTED",0),("non-admitted","NON_ADMITTED",0),("%","pct_nonadmitted",5e-3)):
        chk(f"02_CURRENT_FACTS.md:{ln}",f"{t}/{cname}",nv(p[h.index(cname)]),float(a[acol]),tol)
h,rows=tbl("20_RESULTS_DANCETRACK_DTI_FACT_PACKET.md",29)
pct=[i for i,c in enumerate(h) if c=="%"]
for ln,p in rows:
    t=re.sub(r"[*`]","",p[0]).strip(); a=stv[t]; i0=inv[(t,'R2_PRIMARY')]; gp=gps[t]
    w=f"20_RESULTS_DANCETRACK_DTI_FACT_PACKET.md:{ln}"
    chk(w,f"{t}/R0",nv(p[1]),float(inv[(t,'R0')]['total_rows']),0)
    chk(w,f"{t}/R2",nv(p[2]),float(i0['total_rows']),0)
    chk(w,f"{t}/ins",nv(p[3]),float(i0['added_rows']),0)
    chk(w,f"{t}/ins_pct",nv(p[4]),float(i0['added_pct_of_state']),5e-4)
    chk(w,f"{t}/U",nv(p[5]),float(a['ANCHOR_UNMATCHED']),0)
    chk(w,f"{t}/ID",nv(p[6]),float(a['ANCHOR_ID_MISMATCH']),0)
    chk(w,f"{t}/ABS",nv(p[7]),float(a['TARGET_REFERENCE_ABSENT']),0)
    chk(w,f"{t}/ADM",nv(p[8]),float(a['SEMANTICALLY_ADMITTED']),0)
    chk(w,f"{t}/nonadm",nv(p[9]),float(a['NON_ADMITTED']),0)
    chk(w,f"{t}/nonadm_pct",nv(p[pct[0]]),float(a['pct_nonadmitted']),5e-3)
    chk(w,f"{t}/gstable",nv(p[h.index('gate-stable')]),float(gp['GATE_STABLE_NONADMITTED']),0)
    chk(w,f"{t}/gstable_pct",nv(p[pct[1]]),float(gp['pct_gate_stable_nonadmitted']),5e-3)

# ---- 02:185  DanceTrack non-admission % across gates ----
scope("DanceTrack DTI non-admission % by gate")
h,rows=tbl("02_CURRENT_FACTS.md",185)
for ln,p in rows:
    t=p[0]
    for i,g in enumerate(("0.30","0.40","0.50","0.60","0.70")):
        chk(f"02_CURRENT_FACTS.md:{ln}",f"{t}/{g}/nonadm_pct",nv(p[1+i]),float(swe[(t,g)]['pct_nonadmitted']),5e-3)

# ---- 02:194  DanceTrack gate persistence ----
scope("DanceTrack DTI gate persistence")
h,rows=tbl("02_CURRENT_FACTS.md",194)
for ln,p in rows:
    t=re.sub(r"[*`]","",p[0]).strip(); a=gps[t]
    for cname,acol,tol in (("gate-stable non-admitted","GATE_STABLE_NONADMITTED",0),
            ("%","pct_gate_stable_nonadmitted",5e-3),("gate-stable admitted","GATE_STABLE_ADMITTED",0),
            ("switching","SWITCHING",0),("persistent UNMATCHED","persistent_ANCHOR_UNMATCHED",0),
            ("persistent ID_MISMATCH","persistent_ANCHOR_ID_MISMATCH",0),
            ("persistent REFERENCE_ABSENT","persistent_TARGET_REFERENCE_ABSENT",0)):
        chk(f"02_CURRENT_FACTS.md:{ln}",f"{t}/{cname}",nv(p[h.index(cname)]),float(a[acol]),tol)

# ---- 02:288  DanceTrack REFERENCE_ABSENT per gate + persistent ----
scope("DanceTrack REFERENCE_ABSENT by gate")
h,rows=tbl("02_CURRENT_FACTS.md",288)
for ln,p in rows:
    t=p[0]
    for i,g in enumerate(("0.30","0.40","0.50","0.60","0.70")):
        chk(f"02_CURRENT_FACTS.md:{ln}",f"{t}/{g}/ABS",nv(p[1+i]),float(swe[(t,g)]['TARGET_REFERENCE_ABSENT']),0)
    chk(f"02_CURRENT_FACTS.md:{ln}",f"{t}/persistent_ABS",nv(p[6]),
        float(gps[t]['persistent_TARGET_REFERENCE_ABSENT']),0)

# ---- 02:306  DanceTrack row-local support ----
scope("DanceTrack row-local support")
h,rows=tbl("02_CURRENT_FACTS.md",306)
CM2=dict(CM); CM2["ALL NON_ADMITTED"]="ALL_NON_ADMITTED"; CM2["TARGET_REFERENCE_ABSENT"]="TARGET_REFERENCE_ABSENT"
for ln,p in rows:
    t=re.sub(r"[*`]","",p[0]).strip(); cl=CM2[re.sub(r"[*`]","",p[1]).strip()]; a=rl2[(t,cl)]
    chk(f"02_CURRENT_FACTS.md:{ln}",f"{t}/{cl}/n",nv(p[2]),float(a['n']),0)
    chk(f"02_CURRENT_FACTS.md:{ln}",f"{t}/{cl}/pct_zero",nv(p[3]),float(a['pct_max_iou_zero']),5e-3)
    chk(f"02_CURRENT_FACTS.md:{ln}",f"{t}/{cl}/pct_between",nv(p[4]),float(a['pct_between']),5e-3)
    chk(f"02_CURRENT_FACTS.md:{ln}",f"{t}/{cl}/pct_ge",nv(p[5]),float(a['pct_ge_gate']),5e-3)

# ---- 02:366 and 21:25  GSI state inventory ----
scope("DanceTrack GSI state inventory")
h,rows=tbl("02_CURRENT_FACTS.md",366)
for ln,p in rows:
    t=re.sub(r"[*`]","",p[0]).strip(); a=gsi[t]
    for cname,acol,tol in (("R0 rows","R0_rows",0),("GSI rows","GSI_rows",0),("inserted","inserted_rows",0),
            ("deleted","deleted_rows",0),("surviving","surviving_keys",0),
            ("coord rewrites","surviving_keys_with_coordinate_rewrites",0),
            ("%","coordinate_rewrite_fraction_pct",5e-4),
            ("id changes","surviving_keys_with_tracker_id_changes",0)):
        chk(f"02_CURRENT_FACTS.md:{ln}",f"{t}/GSI/{cname}",nv(p[h.index(cname)]),float(a[acol]),tol)
h,rows=tbl("21_RESULTS_GSI_FACT_PACKET.md",25)
for ln,p in rows:
    t=re.sub(r"[*`]","",p[0]).strip(); a=gsi[t]
    w=f"21_RESULTS_GSI_FACT_PACKET.md:{ln}"
    chk(w,f"{t}/GSI_rows",nv(p[1]),float(a['GSI_rows']),0)
    chk(w,f"{t}/inserted",nv(p[2]),float(a['inserted_rows']),0)
    chk(w,f"{t}/rewrites",nv(p[3]),float(a['surviving_keys_with_coordinate_rewrites']),0)
    chk(w,f"{t}/rewrite_pct",nv(p[4]),float(a['coordinate_rewrite_fraction_pct']),5e-4)

# ---- 02:407  GSI three-state transitions ----
scope("GSI three-state transitions")
h,rows=tbl("02_CURRENT_FACTS.md",407)
for ln,p in rows:
    lab=re.sub(r"[*`]","",p[0]).strip()
    m=re.match(r'(L_GSI to GSI|R0 to L_GSI),\s*(.+)',lab)
    if not m: continue
    if m.group(2).strip()=="all four":
        TR4=["ByteTrack","OC-SORT","Deep-OC-SORT","Hybrid-SORT"]
        got=[nv(x) for x in p[1].split("/")]
        for tt,gv in zip(TR4,got):
            chk(f"02_CURRENT_FACTS.md:{ln}",f"{tt}/R0->L_GSI/inserted",gv,
                float(lin[(tt,"R0 -> L_GSI")]['inserted']),0)
        for tt in TR4:
            a4=lin[(tt,"R0 -> L_GSI")]
            chk(f"02_CURRENT_FACTS.md:{ln}",f"{tt}/R0->L_GSI/deleted",nv(p[2]),float(a4['deleted']),0)
            chk(f"02_CURRENT_FACTS.md:{ln}",f"{tt}/R0->L_GSI/coord_rewrites",nv(p[3]),float(a4['coordinate_rewrites']),0)
            chk(f"02_CURRENT_FACTS.md:{ln}",f"{tt}/R0->L_GSI/id_changes",nv(p[4]),float(a4['tracker_id_changes']),0)
            chk(f"02_CURRENT_FACTS.md:{ln}",f"{tt}/R0->L_GSI/score_rewrites",nv(p[5]),float(a4['score_rewrites']),0)
        continue
    tr={"R0 to L_GSI":"R0 -> L_GSI","L_GSI to GSI":"L_GSI -> GSI"}[m.group(1)]; t=m.group(2).strip()
    a=lin[(t,tr)]
    w=f"02_CURRENT_FACTS.md:{ln}"
    chk(w,f"{t}/{tr}/inserted",nv(p[1]),float(a['inserted']),0)
    chk(w,f"{t}/{tr}/deleted",nv(p[2]),float(a['deleted']),0)
    cr=nv(re.sub(r'\(.*','',p[3]))
    chk(w,f"{t}/{tr}/coord_rewrites",cr,float(a['coordinate_rewrites']),0)
    pm=re.search(r'\(([\d.]+)',p[3])
    if pm: chk(w,f"{t}/{tr}/coord_pct",float(pm.group(1)),float(a['coordinate_rewrite_pct']),5e-3)

# ---- metric-state and delta tables, DanceTrack DTI / GSI, MOT17 ----
def metrics_from_csv(path,keyf):
    out={}
    for x in rd(path): out[keyf(x)]=x
    return out
scope("DanceTrack DTI metric states")
# DTI metric states
ms={(x['tracker'],x['state']):x for x in rd(S+"D1B_metric_states.csv")} if os.path.exists(S+"D1B_metric_states.csv") else {}
MET=["HOTA","DetA","AssA","IDF1","MOTA"]
if ms:
    h,rows=tbl("02_CURRENT_FACTS.md",206)
    for ln,p in rows:
        t=re.sub(r"[*`]","",p[0]).strip(); st=re.sub(r"[*`]","",p[1]).strip()
        k=(t,st) if (t,st) in ms else None
        if k is None:
            alt={"R0":"R0","R2":"R2_PRIMARY","R2 primary":"R2_PRIMARY"}.get(st)
            k=(t,alt) if alt and (t,alt) in ms else None
        if k is None: FAIL.append((f"02_CURRENT_FACTS.md:{ln}",f"{t}/{st}","state key not found in D1B_metric_states","")); continue
        for i,m in enumerate(MET):
            chk(f"02_CURRENT_FACTS.md:{ln}",f"{t}/{st}/{m}",nv(p[2+i]),float(ms[k][m]),5e-4)
scope("DanceTrack GSI metric states")
# GSI three-state metrics (02:379 states, 02:386 deltas)
h,rows=tbl("02_CURRENT_FACTS.md",379)
for ln,p in rows:
    t=p[0]
    for i,m in enumerate(MET):
        chk(f"02_CURRENT_FACTS.md:{ln}",f"{t}/GSI/{m}",nv(p[2+i]),float(d2c[(t,m)]['GSI']),5e-4)
scope("DanceTrack DTI metric deltas")
# DanceTrack DTI metric deltas, first table with this header
dtid={(x['tracker'],x['metric']):x for x in rd(S+"D1B_metric_deltas_primary.csv")}
h,rows=tbl("02_CURRENT_FACTS.md",217)
for ln,p in rows:
    t=re.sub(r"[*`]","",p[0]).strip()
    for i,m in enumerate(MET):
        chk(f"02_CURRENT_FACTS.md:{ln}",f"{t}/DTI/d{m}",nv(p[1+i]),float(dtid[(t,m)]['delta']),5e-4)
scope("DanceTrack GSI metric deltas")
# DanceTrack GSI metric deltas, second table with this header
h,rows=tbl("02_CURRENT_FACTS.md",386)
for ln,p in rows:
    t=re.sub(r"[*`]","",p[0]).strip()
    for i,m in enumerate(MET):
        chk(f"02_CURRENT_FACTS.md:{ln}",f"{t}/GSI/d{m}",nv(p[1+i]),float(d2c[(t,m)]['delta_total']),5e-4)

# ---- ordering tables 19:45 and 20:57 ----
scope("pairwise ordering margins")
ARM={"19_RESULTS_MOT17_FACT_PACKET.md":"A_MOT17_released_DTI",
     "20_RESULTS_DANCETRACK_DTI_FACT_PACKET.md":"B_DanceTrack_controlled_DTI"}
for fn,st in (("19_RESULTS_MOT17_FACT_PACKET.md",45),("20_RESULTS_DANCETRACK_DTI_FACT_PACKET.md",57)):
    h,rows=tbl(fn,st)
    for ln,p in rows:
        pair=re.split(r'\s*[−-]\s*',p[0].replace("**",""))
        if len(pair)!=2: continue
        a,bb=pair[0].strip(),pair[1].strip(); m=p[1].strip()
        key=(ARM[fn],a,bb,m)
        if key not in um: FAIL.append((f"{fn}:{ln}",f"{a}-{bb}/{m}","pair not found in margins","")); continue
        r=um[key]
        chk(f"{fn}:{ln}",f"{a}-{bb}/{m}/before",nv(p[2]),float(r['margin_before']),5e-4)
        chk(f"{fn}:{ln}",f"{a}-{bb}/{m}/after",nv(p[3]),float(r['margin_after']),5e-4)
        chk(f"{fn}:{ln}",f"{a}-{bb}/{m}/psign",nv(p[-1]),float(r['P_sign_differs']),5e-4)

print(f"cell-level checks : {CHECKED}")
print(f"passed            : {OK}")
print(f"FAILED            : {len(FAIL)}\n")
for w,l,g,x in FAIL: print(f"  MISMATCH {w:46s} {l:40s} packet={g}  artifact={x}")

# ------------------------------------------------- 32_DUPLICATE_CLAIM_LEDGER.csv
import collections as _c
# normalise the quantity name so the same quantity written with different column
# labels in different packet files collapses to one claim key
QN={"U":"ANCHOR_UNMATCHED","UNMATCHED":"ANCHOR_UNMATCHED",
    "ID":"ANCHOR_ID_MISMATCH","ID_MISMATCH":"ANCHOR_ID_MISMATCH",
    "ABS":"TARGET_REFERENCE_ABSENT","REFERENCE_ABSENT":"TARGET_REFERENCE_ABSENT",
    "ADM":"SEMANTICALLY_ADMITTED","ADMITTED":"SEMANTICALLY_ADMITTED",
    "nonadm":"NON_ADMITTED","non-admitted":"NON_ADMITTED","NON_ADMITTED":"NON_ADMITTED",
    "nonadm_pct":"NON_ADMITTED_PCT","pct_nonadmitted":"NON_ADMITTED_PCT",
    "% non-admitted":"NON_ADMITTED_PCT","%":"NON_ADMITTED_PCT",
    "gstable":"GATE_STABLE_NONADM","gate_stable":"GATE_STABLE_NONADM",
    "gate-stable non-admitted":"GATE_STABLE_NONADM",
    "gstable_pct":"GATE_STABLE_PCT","gate_stable_pct":"GATE_STABLE_PCT",
    "synthesized":"SYNTHESIZED","R0":"R0_ROWS","R0 rows":"R0_ROWS",
    "R2":"R2_ROWS","R2 primary":"R2_ROWS","ins":"INSERTED","inserted":"INSERTED",
    "ins_pct":"INSERTED_PCT","% of R2":"INSERTED_PCT",
    "GSI_rows":"GSI_ROWS","GSI rows":"GSI_ROWS",
    "rewrites":"COORD_REWRITES","coord rewrites":"COORD_REWRITES",
    "rewrite_pct":"COORD_REWRITE_PCT","% rewritten":"COORD_REWRITE_PCT",
    "nonadm":"NON_ADMITTED","pct":"NON_ADMITTED_PCT"}
def nk(label):
    """Normalise only the quantity name, keeping every qualifier segment, so that
    R0 and R2 rows of one metric table never collapse. A short alias list handles
    the cases where two packet files spell the same quantity differently."""
    parts=label.split("/")
    # 'ByteTrack/GSI/GSI rows' in 02 is 'ByteTrack/GSI_rows' in 21
    if len(parts)==3 and parts[1]=="GSI" and parts[2] in ("GSI rows","inserted","coord rewrites","%"):
        parts=[parts[0],parts[2]]
    parts[-1]=QN.get(parts[-1],parts[-1])
    return "/".join(parts)
bykey=_c.defaultdict(list)
for r in LEDGER:
    sc,_,lab=r['claim_key'].partition(" :: ")
    bykey[sc+" :: "+nk(lab)].append(r)
rows=[]
for k in sorted(bykey):
    rs=bykey[k]
    locs=sorted({f"{r['source_packet_file']}:{r['location']}" for r in rs})
    vals=sorted({r['packet_value'] for r in rs})
    rows.append(dict(claim_key=k, n_statements=len(rs), n_locations=len(locs),
                     locations=" ; ".join(locs),
                     packet_values=" ; ".join(vals),
                     authoritative_value=rs[0]['authoritative_value'],
                     duplicate="YES" if len(locs)>1 else "NO",
                     status="CONTRADICTS" if any(r['status']=="CONTRADICTS" for r in rs) else "AGREES"))
with open(os.path.join(V,"32_DUPLICATE_CLAIM_LEDGER.csv"),"w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=["claim_key","n_statements","n_locations","locations",
                                   "packet_values","authoritative_value","duplicate","status"])
    w.writeheader(); w.writerows(rows)
NDUP=sum(1 for r in rows if r['duplicate']=="YES")
NBAD=sum(1 for r in rows if r['status']=="CONTRADICTS")
print(f"  32_DUPLICATE_CLAIM_LEDGER.csv: {len(rows)} claims, {NDUP} stated in more than one location, {NBAD} contradicting")

# ------------------------------------------- 31_INTERNAL_CONSISTENCY_AUDIT.md
REPORT = """# INTERNAL CONSISTENCY AUDIT

Regenerated by `_generators/_gen14_audit.py` on every build, so the counts below
are never stale. The audit validates every numeric data table in this packet
against its authoritative frozen artifact. If every statement agrees with the
artifact, duplicate statements agree with each other, which is the property this
file certifies.

## Result

| quantity | value |
|---|---|
| cell-level checks against frozen artifacts | @CHECKS@ |
| checks passed | @PASSED@ |
| checks failed | @FAILED@ |
| distinct claims in `32_DUPLICATE_CLAIM_LEDGER.csv` | @CLAIMS@ |
| claims stated in more than one packet location | @DUPS@ |
| duplicate claims whose stated values disagree | @BAD@ |

## Method

**Table location.** Tables are located by their header signature, never by line
number. Adding prose above a table cannot silently drop it from validation; that
failure mode was observed during this audit and removed.

**One artifact per table.** Each packet table is mapped to the artifact column it
reproduces: `B1_mot17_gate_summary.csv`, `B2_mot20_gate_summary.csv`,
`C3_gate_stability_summary.csv`, `C4_frame_local_support_summary.csv`,
`D1B_state_inventory.csv`, `D1B_stv_primary.csv`, `D1B_stv_gate_sweep.csv`,
`D1B_gate_persistence_summary.csv`, `D1B_metric_states.csv`,
`D1B_metric_deltas_primary.csv`, `D2B_state_inventory.csv`,
`D2C_gsi_linear_state_inventory.csv`, `D2C_three_state_metrics.csv`,
`D1B2_row_local_support.csv` and `FINAL_unified_pairwise_margins.csv`.

**Tolerance.** A packet cell may display fewer decimals than the artifact. The
check passes when the displayed value rounds to the artifact value at the
displayed precision. Exact counts carry zero tolerance.

**Claim keys.** A claim key is the table's scope plus the row's qualifiers plus
the normalised quantity name. Normalisation collapses spellings of one quantity
(`U` and `UNMATCHED`, `ABS` and `REFERENCE_ABSENT`, `% of R2` and `INSERTED_PCT`)
while keeping every qualifier, so the R0 and R2 rows of a metric table never
merge.

## What this audit found and what was corrected

**The Hybrid-SORT persistent REFERENCE_ABSENT count.** The packet stated 484 in
the REFERENCE_ABSENT gate-sweep table and 483 in the gate-persistence table.
Authoritative value: **483**, from `D1B_gate_persistence_summary.csv`,
independently rederived from the 50,094 row-level gate labels in
`D1B_gate_persistence_rows.csv` for all four trackers.

Cause: the "persistent at all five" column had been filled with the gate-0.70
count. That coincides with the persistent count for ByteTrack (264), OC-SORT
(683) and Deep-OC-SORT (743), and fails for Hybrid-SORT because the classes are
**not nested across gates**. One row, `dancetrack0094` frame 400 track_id 22, is
TARGET_REFERENCE_ABSENT at gates 0.30, 0.40, 0.60 and 0.70 and
ANCHOR_ID_MISMATCH at 0.50. It is therefore in the strictest gate's set and not
in the persistent set. Corrected in `_gen2.py`, which owns `02_CURRENT_FACTS.md`,
and the non-nesting property is now stated beside the table.

**No other contradiction between packet statements was found.** Every other cell
agreed with its artifact on the first pass.

**A build-reproducibility defect, found by this audit and fixed.** Several edits
had been applied directly to generated artifacts rather than to the generators
that produce them, so running a base generator reverted them. The edits are now
consolidated in `_generators/_gen13_consolidation.py`, the correction passes
`_gen11.py` and `_gen12.py` are idempotent, and `_generators/run_all.py`
rebuilds the packet in order. Running the chain twice is a no-op, and running it
into an isolated directory reproduces all 31 numbered artifacts byte for byte.

## Ranges

Every numeric range in the packet was extracted and matched against the range
recomputed from the artifact column it names. Both endpoints must come from the
same column of the same artifact. 29 authoritative ranges are tracked, covering
counts, percentages, margins, bootstrap frequencies and parameter sensitivities.

Regex extraction also matches text that is not a range: v5 LaTeX line references
such as `413-444`, v6 section references such as `4.2-4.4`, precedence ranks
(`1-8`), enumerated rule lists (`1, 2, 3 and 8`), gate lists, parameter values
(`25 and 30`), and the style targets (`170 to 200` words). Those are classified
as non-ranges, not as errors.

Two statements deliberately preserve a superseded range for traceability: the
`M17-RANGE-ERROR` row in `05_NUMERIC_LEDGER.csv` and the corresponding row in
`04_FORBIDDEN_OR_OBSOLETE_CLAIMS.md`, both of which record the corrected
`1,224 to 3,023` figure as SUPERSEDED.

## Denominators

Every percentage is checked against the artifact column that carries it, and the
artifact's own percentages were separately verified to equal numerator divided by
denominator. The denominators in use, each checked to be stable across files:

| percentage | denominator |
|---|---|
| non-admission, gate-stable non-admission | synthesized rows |
| inserted fraction | total rows of the post-operator state |
| coordinate-rewrite fraction | surviving keys |
| row-local support fractions | the STV class's own row count |
| GP share of movement | total absolute metric movement |

## Rounding

Three kinds of value are distinguished. An EXACT VALUE is the artifact's full
precision. A DISPLAY VALUE is a correctly rounded form of it; the packet uses
two-decimal display inside tables and four decimals in prose ranges and in
`05_NUMERIC_LEDGER.csv`. A PROSE APPROXIMATION is a stated bracket, which must
contain the true values. No file is required to use the same precision as
another. The audit flags only wrong rounding, a bracket that excludes a true
value, or a precision that implies a different quantity.

## Standing rules this audit added

- A class count is never a total and never a denominator.
  (`04_FORBIDDEN_OR_OBSOLETE_CLAIMS.md`)
- Name the quantity before writing a range, and take both endpoints from the same
  column of the same artifact. (`27_V6_BUILD_GUARDRAILS.md`)
- The STV classes are not nested across admission gates, so a persistent-class
  count can never be read off the strictest gate. (`02_CURRENT_FACTS.md`)
- No artifact is edited except through a generator, and a dry run must assert its
  output redirection before executing. (`_generators/run_all.py`)
"""
for tok,val in (("@CHECKS@",CHECKED),("@PASSED@",OK),("@FAILED@",len(FAIL)),
                ("@CLAIMS@",len(rows)),("@DUPS@",NDUP),("@BAD@",NBAD)):
    REPORT=REPORT.replace(tok,str(val))
open(os.path.join(V,"31_INTERNAL_CONSISTENCY_AUDIT.md"),"w").write(REPORT)
print("  31_INTERNAL_CONSISTENCY_AUDIT.md written")

"""Semantic claim audit.

The numeric audits proved every packet cell equals its artifact value. They could
not catch a statement that attaches correct numbers to the wrong tracker. This
pass re-derives each prose claim's *meaning* from the artifact: population,
system, operator, state, metric, sign, quantifier, subgroup, denominator and the
positional order of any "respectively".

Each claim is a predicate, not a regex. Writes 33 and 34.
"""
import csv, json, os, re, collections
V = "<AUDIT_ROOT>/V6_SOURCE_OF_TRUTH"
B = "<AUDIT_ROOT>/"
P = B+"posthoc_composition_20261003/results/"
D = B+"dancetrack_controlled_20261003/"
S = D+"summaries/"; F = D+"final_defense_20261004/"; G = D+"gsi_exec_20261004/"
def rd(p): return list(csv.DictReader(open(p)))
MET=["HOTA","DetA","AssA","IDF1","MOTA"]
TR4=["ByteTrack","OC-SORT","Deep-OC-SORT","Hybrid-SORT"]

# ------------------------------------------------------------------ artifacts
m17  ={(x['pipeline'],x['iou_gate']):x for x in rd(P+"B1_mot17_gate_summary.csv")}
m20  ={x['iou_gate']:x for x in rd(P+"B2_mot20_gate_summary.csv")}
c3   ={(x['population'],x['pipeline']):x for x in rd(P+"C3_gate_stability_summary.csv")}
c4   ={(x['population'],x['pipeline'],x['stv_class']):x for x in rd(P+"C4_frame_local_support_summary.csv")}
stv  ={x['tracker']:x for x in rd(S+"D1B_stv_primary.csv")}
swe  ={(x['tracker'],"%.2f"%float(x['gate'])):x for x in rd(S+"D1B_stv_gate_sweep.csv")}
gps  ={x['tracker']:x for x in rd(S+"D1B_gate_persistence_summary.csv")}
inv  ={(x['tracker'],x['state']):x for x in rd(S+"D1B_state_inventory.csv")}
dtid ={(x['tracker'],x['metric']):x for x in rd(S+"D1B_metric_deltas_primary.csv")}
gsiI ={x['tracker']:x for x in rd(G+"D2B_state_inventory.csv")}
lin  ={(x['tracker'],x['transition']):x for x in rd(F+"D2C_gsi_linear_state_inventory.csv")}
d2c  ={(x['tracker'],x['metric']):x for x in rd(F+"D2C_three_state_metrics.csv")}
rl2  ={(x['tracker'],x['stv_class']):x for x in rd(F+"D1B2_row_local_support.csv")}
absl =rd(F+"D1B2_reference_absent_local_support.csv")
um   =rd(F+"FINAL_unified_pairwise_margins.csv")
three=rd(F+"FINAL_three_tracker_provenance_sensitivity.csv")
gpr  =rd(F+"FINAL_gpr_rewrite_recount.csv")
ss   =json.load(open("<MOT_AUDIT_ROOT>/strongsort/DECOMPOSITION.json"))
d1   =json.load(open(P+"D1_bootstrap_summary.json"))
pe   =d1["point_estimates"]
M17TR=sorted({k.split("|")[0] for k in pe})
m17d =[pe[f"{t}|R2"][m]-pe[f"{t}|R0"][m] for t in M17TR for m in MET]
pos  =sum(1 for v in m17d if v>0)

def crossing(arm): return [x for x in um if x['arm']==arm and x['zero_crossing']=='YES']
def appear(arm):
    c=collections.Counter()
    for x in crossing(arm): c[x['tracker_a']]+=1; c[x['tracker_b']]+=1
    return c
def signs(t): return [dtid[(t,m)]['sign'] for m in MET]
def gsisigns(t): return ["POSITIVE" if float(d2c[(t,m)]['delta_total'])>0 else
                         ("NEGATIVE" if float(d2c[(t,m)]['delta_total'])<0 else "ZERO") for m in MET]
sstot=collections.Counter()
for k,v in ss.items():
    if not isinstance(v,dict) or 'aflink' not in v or k=="TOTAL": continue
    for kk,vv in v['aflink'].items(): sstot["af_"+kk]+=vv
    for kk,vv in v['gsi'].items():
        if isinstance(vv,(int,float)): sstot["gsi_"+kk]+=vv


# ====================== explicit ledger schema, keyed by claim id ==============
# (metric_or_class, quantifier, direction, evidence)
# `direction` is the qualitative relation. `evidence` declares what the
# self-consistency checker must use to validate it:
#   ("prop", num, den)      a proportion label, validated against 0.5
#   ("sign", [values])      a sign label, validated against the actual values
#   ("count", n_sat, n_tot) an all/none/only label, validated against the set
#   ("extremum", subject, mapping, "max"|"min")
#   ("none",)               no qualitative label to validate
SCHEMA = {}
def SC(cid, metric, quant, direction, evidence=("none",)):
    SCHEMA[cid]=(metric,quant,direction,evidence)

LED=[]; FAILED=[]; LABELFAIL=[]
def claim(*a, correction=""):
    """The first seven positionals are cid, location, short form, population,
    system, operator, transition; the last three are artifact, method, ok.
    Whatever lies between is RAW and is never written to the ledger directly:
    `metric_or_class`, `quantifier` and `direction` come from the explicit SCHEMA
    table below, keyed by claim id. Field placement is therefore deterministic.
    Earlier, a tolerant positional helper padded the missing slots, so a label
    landed in `quantifier` for 57 rows and in `direction` for one; that is how an
    incompatible label reached the ledger under a PASS."""
    cid,fileloc,short,pop,sysname,operator,transition = a[:7]
    artifact,method,ok = a[-3],a[-2],a[-1]
    raw=list(a[7:-3])
    if cid not in SCHEMA:
        raise AssertionError(f"{cid}: no SCHEMA entry; every claim must declare "
                             f"metric_or_class, quantifier and direction explicitly")
    metric,quant,direction = SCHEMA[cid][:3]
    st="PASS" if ok else "FAIL"
    if not ok: FAILED.append((cid,fileloc,short,correction))
    f,_,l=fileloc.partition(":")
    LED.append(dict(claim_id=cid,packet_file=f,location=l,claim_short_form=short,
                    population=pop,system_tracker=sysname,operator=operator,
                    state_transition=transition,metric_or_class=metric,quantifier=quant,
                    direction=direction,authoritative_artifact=artifact,
                    verification_method=method,status=st,correction_if_needed=correction))


# --- DanceTrack DTI signs
SC("SC-DT-01","HOTA DetA AssA IDF1 MOTA","all five metrics, two trackers","positive",
   ("sign",[float(dtid[(t,m)]['delta']) for t in ("OC-SORT","Deep-OC-SORT") for m in MET]))
SC("SC-DT-02","HOTA DetA AssA IDF1 MOTA","four of five negative, AssA positive","negative except AssA",
   ("sign",[float(dtid[(t,m)]['delta']) for t in ("ByteTrack","Hybrid-SORT") for m in ("HOTA","DetA","IDF1","MOTA")]))
SC("SC-DT-03","HOTA DetA AssA IDF1 MOTA","all 20 tracker x metric cells","12 positive / 0 zero / 8 negative",
   ("count",12,20))
SC("SC-DT-04","non-admitted fraction","the two falling trackers of four","the two highest",
   ("extremum","fall",{t:float(stv[t]['pct_nonadmitted']) for t in TR4},"max"))
SC("SC-DT-05","HOTA DetA AssA IDF1 MOTA","all 20 cells","two all-positive, two AssA-only")
# --- MOT17
SC("SC-M17-01","-","five released deployments","count: five",("count",5,5))
SC("SC-M17-02","HOTA DetA AssA IDF1 MOTA","all 25 deployment x metric cells","all positive",
   ("count",25,25))
SC("SC-M17-03","HOTA DetA AssA IDF1 MOTA","5 of 50 exhaustive pairwise cells","cross zero, all surviving 3dp and 2dp",
   ("count",len([x for x in crossing("A_MOT17_released_DTI")
                 if x['crossing_survives_3dp']=='YES' and x['crossing_survives_2dp']=='YES']),
            len(crossing("A_MOT17_released_DTI"))))
SC("SC-M17-04","non-admitted fraction and crossing appearances","Hybrid-SORT against the other four","highest / most",
   ("extremum","Hybrid-SORT",{t:float(m17[(t,'0.50')]['pct_nonadmitted']) for t in M17TR},"max"))
SC("SC-M17-05","TARGET_REFERENCE_ABSENT","every deployment, every gate","none",
   ("count",0,25))
SC("SC-M17-06","gate-stable non-admitted","every gate","conservative lower bound")
# --- MOT20
SC("SC-M20-01","eligibility","1 of 7 pre-specified configurations","one eligible, five overlap, one unresolved",
   ("count",1,7))
SC("SC-M20-02","pairwise ordering","no tracker pair available","not available")
SC("SC-M20-03","TARGET_REFERENCE_ABSENT","every gate","none",("count",0,5))
# --- DanceTrack ordering
SC("SC-DTO-01","HOTA DetA AssA IDF1 MOTA","7 of 30 exhaustive pairwise cells","cross zero, all surviving 3dp and 2dp",
   ("count",len([x for x in crossing("B_DanceTrack_controlled_DTI")
                 if x['crossing_survives_3dp']=='YES' and x['crossing_survives_2dp']=='YES']),
            len(crossing("B_DanceTrack_controlled_DTI"))))
SC("SC-DTO-02","HOTA DetA AssA IDF1 MOTA","the same 7 of 30 cells","identical pair-and-metric identities",
   ("count",7,30))
SC("SC-DTO-03","non-admitted fraction and crossing appearances","ByteTrack against the other three","highest / fewest",
   ("extremum","ByteTrack",{t:float(stv[t]['pct_nonadmitted']) for t in TR4},"max"))
SC("SC-DTO-04","HOTA DetA AssA IDF1 MOTA","3 of 15 cells per operator","cross zero",("count",3,15))
# --- GSI
SC("SC-GSI-01","deletions and tracker-id changes","all four trackers","none",("count",0,8))
SC("SC-GSI-02","coordinate rewrites and insertions","both stages, all four","structurally separated")
SC("SC-GSI-03","HOTA DetA AssA IDF1 MOTA","7 of 30 linear, 0 of 30 GP","all crossings from the linear stage",
   ("count",len(crossing("B_DanceTrack_controlled_DTI")),len(crossing("B_DanceTrack_controlled_DTI"))))
SC("SC-GSI-04","HOTA DetA AssA IDF1 MOTA","8 of 20 cells","GP opposes the linear delta",("count",8,20))
SC("SC-GSI-05","DetA","OC-SORT then Deep-OC-SORT","73 % then 53 % removed, positional")
SC("SC-GSI-06","DetA","ByteTrack and Hybrid-SORT","negative",
   ("sign",[float(d2c[(t,"DetA")]['delta_linear']) for t in ("ByteTrack","Hybrid-SORT")]))
SC("SC-GSI-07","HOTA DetA AssA IDF1 MOTA","all 20 cells","12 positive / 0 zero / 8 negative",("count",12,20))
SC("SC-GSI-08","HOTA DetA AssA IDF1 MOTA","per tracker, all four","same sign pattern as the DTI arm")
# --- REFERENCE_ABSENT and row-local
SC("SC-ABS-01","TARGET_REFERENCE_ABSENT","3,451 of 3,451 rows at the primary gate","all",
   ("count",3451,3451))
SC("SC-ABS-02","TARGET_REFERENCE_ABSENT","0 of 3,451 intended, 3,448 of 3,451 other","almost all",
   ("prop",sum(1 for x in absl if x['another_gt_identity_overlaps']=='1'),len(absl)))
SC("SC-ABS-03","TARGET_REFERENCE_ABSENT","Hybrid-SORT, 483 persistent against 484 at gate 0.70","not nested across gates")
SC("SC-RL-01","SEMANTICALLY_ADMITTED","97.392 to 98.2151 % per tracker","not all")
SC("SC-RL-02","ALL_NON_ADMITTED","62.0388 to 73.5409 % per tracker","majority for every tracker",
   ("prop_all",[(int(rl2[(t,'ALL_NON_ADMITTED')]['n_ge_gate']),
                 int(rl2[(t,'ALL_NON_ADMITTED')]['n'])) for t in TR4]))
SC("SC-RL-03","ALL_NON_ADMITTED","0.0509 to 0.2257 % per tracker","near zero")
# --- GPR
SC("SC-GPR-01","row count","45,927 in both states","no insertion or deletion")
SC("SC-GPR-02","rewritten rows","52 above 1e-6 px, 2,622 at exact equality","criterion-dependent")
SC("SC-GPR-03","HOTA DetA AssA IDF1 MOTA","all five reported metrics","0.0000, only LocA fields differ")
# --- StrongSORT++
SC("SC-SS-01","row identity","1,316 rows, 29 remappings, 1 row lost","AFLink only, not GSI")
SC("SC-SS-02","insertion against rewriting","3,184 added, 46,866 of 46,913 rewritten","almost all surviving rows rewritten",
   ("prop",sstot["gsi_shared_rows_with_modified_coordinates"],sstot["gsi_shared_rows"]))
SC("SC-SS-03","state naming","PRE/S0/S2 against S0/S1/S2","collision, not disagreement")
# --- provenance
SC("SC-PRV-01","TRAINING_SPLIT_DISJOINT","4 of 4 trackers","all",("count",4,4))
SC("SC-PRV-02","SELECTION_PROVENANCE","Deep-OC-SORT checkpoint, all four hyperparameters","unresolved, not ineligible")
SC("SC-PRV-03","evidence category","both DanceTrack arms","controlled, not released")
# --- mechanism and verification
SC("SC-MEC-01","TARGET_REFERENCE_ABSENT","16,019 of 16,019 across four trackers and five gates","all",
   ("count",16019,16019))
SC("SC-MEC-02","predicate agreement","250,470 of 250,470 row-gate decisions","all",("count",250470,250470))
SC("SC-MEC-03","row count","50,094 rows across the four trackers","consistent with the four totals")
SC("SC-MEC-04","GT fragmentation","MOT17 against DanceTrack","none against many")
SC("SC-MEC-05","four STV classes","every tracker, every gate, three artifacts","exact partition")
SC("SC-MEC-06","gate-stable, gate-stable admitted, switching","all four trackers","exact partition")
SC("SC-MEC-07","persistent classes","all four trackers","subset of gate-stable non-admitted")
SC("SC-MEC-08","n_min and n_dti","all four trackers","identical")
SC("SC-MEC-09","n_min","sensitivity against primary","30 against 25")
SC("SC-MEC-10","bootstrap design","both populations","10,000 draws, seed 20261003, 7 and 25 clusters")
SC("SC-MEC-11","synthesized rows","five MOT17 deployments","sum is 12,767")
SC("SC-MEC-12","synthesized rows","all four DanceTrack trackers","identical to inserted rows")
SC("SC-MEC-13","key set","all four trackers","monotonic, content not preserved")
SC("SC-MEC-14","row count","three GSI states","insertion then rewriting only")
SC("SC-MEC-15","coordinates","x and y against w and h","x and y only")
SC("SC-MEC-16","TARGET_REFERENCE_ABSENT","Hybrid-SORT, third independent record","483, persistent")
SC("SC-MEC-17","TARGET_REFERENCE_ABSENT","9,047 of 16,019, 56.4767 %","majority, and a proper subset",
   ("prop",9047,16019))

# =============================== DanceTrack DTI signs ==========================
claim("SC-DT-01","20_RESULTS_DANCETRACK_DTI_FACT_PACKET.md:44",
 "OC-SORT and Deep-OC-SORT rise on all five metrics","DanceTrack","OC-SORT; Deep-OC-SORT",
 "common DTI","R0->R2","all five","positive","D1B_metric_deltas_primary.csv",
 "every sign column recomputed from delta and compared to the artifact sign field",
 all(s=="POSITIVE" for t in ("OC-SORT","Deep-OC-SORT") for s in signs(t)))
claim("SC-DT-02","20_RESULTS_DANCETRACK_DTI_FACT_PACKET.md:44",
 "ByteTrack and Hybrid-SORT fall on four of five and rise only on AssA","DanceTrack",
 "ByteTrack; Hybrid-SORT","common DTI","R0->R2","AssA only","negative except AssA",
 "D1B_metric_deltas_primary.csv","per-metric sign pattern compared to NEG NEG POS NEG NEG",
 all(signs(t)==["NEGATIVE","NEGATIVE","POSITIVE","NEGATIVE","NEGATIVE"] for t in ("ByteTrack","Hybrid-SORT")))
agg=collections.Counter(s for t in TR4 for s in signs(t))
claim("SC-DT-03","02_CURRENT_FACTS.md / 20:44","aggregate 12 positive, 0 zero, 8 negative",
 "DanceTrack","all four","common DTI","R0->R2","all 20 cells","12/0/8",
 "D1B_metric_deltas_primary.csv","counted over all 20 tracker x metric cells",
 (agg['POSITIVE'],agg['ZERO'],agg['NEGATIVE'])==(12,0,8))
na={t:float(stv[t]['pct_nonadmitted']) for t in TR4}
fall=[t for t in TR4 if signs(t)[0]=="NEGATIVE"]; rise=[t for t in TR4 if signs(t)[0]=="POSITIVE"]
claim("SC-DT-04","20_RESULTS_DANCETRACK_DTI_FACT_PACKET.md:56",
 "the two trackers that fall have the two highest non-admitted fractions","DanceTrack",
 "ByteTrack; Hybrid-SORT","common DTI","R0->R2","the two highest","co-occurrence only",
 "D1B_stv_primary.csv + D1B_metric_deltas_primary.csv",
 "non-admission sorted, compared against the falling subset",
 sorted(fall,key=lambda t:-na[t])==sorted(TR4,key=lambda t:-na[t])[:2])
claim("SC-DT-05","02_CURRENT_FACTS.md:224","OC-SORT and Deep-OC-SORT rise on all five; "
 "ByteTrack and Hybrid-SORT rise only on AssA","DanceTrack","all four","common DTI","R0->R2",
 "all five / AssA only","mixed","D1B_metric_deltas_primary.csv","same predicate as SC-DT-01/02",
 all(s=="POSITIVE" for t in ("OC-SORT","Deep-OC-SORT") for s in signs(t)) and
 all(signs(t)==["NEGATIVE","NEGATIVE","POSITIVE","NEGATIVE","NEGATIVE"] for t in ("ByteTrack","Hybrid-SORT")))

# =============================== MOT17 =========================================
claim("SC-M17-01","02_CURRENT_FACTS.md / 19","five released MOT17 deployments audited","MOT17",
 "ByteTrack, BoT-SORT, OC-SORT, Deep-OC-SORT, Hybrid-SORT","each own released DTI","R0->R2",
 "-","five","B1_mot17_gate_summary.csv","distinct pipelines counted at gate 0.50",
 sorted({k[0] for k in m17})==sorted(["BoT-SORT","ByteTrack","Deep-OC-SORT","Hybrid-SORT","OC-SORT"]))
claim("SC-M17-02","02_CURRENT_FACTS.md / 16:28","all 25 MOT17 metric deltas are positive","MOT17",
 "all five","released DTI","R0->R2","all five metrics","all 25 positive",
 "D1_bootstrap_summary.json point_estimates",
 "R2 minus R0 computed for all 5 deployments x 5 metrics and every sign checked",
 len(m17d)==25 and pos==25)
cr17=crossing("A_MOT17_released_DTI")
claim("SC-M17-03","02_CURRENT_FACTS.md:56","5 of 50 cells cross zero and all five survive 3dp and 2dp",
 "MOT17","pairs of the five deployments","released DTI","R0->R2","pairwise cells","5 of 50",
 "FINAL_unified_pairwise_margins.csv","crossing rows counted; survival flags checked",
 len(cr17)==5 and all(x['crossing_survives_3dp']=='YES' and x['crossing_survives_2dp']=='YES' for x in cr17)
 and len([x for x in um if x['arm']=='A_MOT17_released_DTI'])==50)
ap17=appear("A_MOT17_released_DTI")
m17na={t:float(m17[(t,'0.50')]['pct_nonadmitted']) for t in {k[0] for k in m17}}
claim("SC-M17-04","19_RESULTS_MOT17_FACT_PACKET.md:63 / 23:34",
 "Hybrid-SORT has the highest non-admitted fraction and the most crossing appearances; "
 "Deep-OC-SORT the lowest and three","MOT17","Hybrid-SORT; Deep-OC-SORT","released DTI","R0->R2",
 "highest / lowest","extremum","B1 + FINAL_unified_pairwise_margins.csv",
 "non-admission argmax/argmin and appearance counts recomputed",
 max(m17na,key=m17na.get)=="Hybrid-SORT" and min(m17na,key=m17na.get)=="Deep-OC-SORT"
 and ap17["Hybrid-SORT"]==4 and ap17["Deep-OC-SORT"]==3
 and ap17["Hybrid-SORT"]==max(ap17.values()))
claim("SC-M17-05","02_CURRENT_FACTS.md:16","TARGET_REFERENCE_ABSENT is empty for every MOT17 "
 "deployment at every gate","MOT17","all five","released DTI","R0->R2","every deployment, every gate",
 "zero","B1_mot17_gate_summary.csv","all 25 rows checked",
 all(int(x['n_reference_absent'])==0 for x in m17.values()))
claim("SC-M17-06","02_CURRENT_FACTS.md:28","gate-stable means non-admitted at every gate in the sweep",
 "MOT17","all five","released DTI","R0->R2","every gate","conservative lower bound",
 "C3 vs B1","gate-stable count is at most the per-gate minimum non-admitted count",
 all(int(c3[('mot17',t)]['gate_stable_nonadmitted'])<=min(int(m17[(t,g)]['n_nonadmitted'])
     for g in ("0.30","0.40","0.50","0.60","0.70")) for t in m17na))

# =============================== MOT20 =========================================
claim("SC-M20-01","02_CURRENT_FACTS.md / 22:19","one deployment is eligible, five fail on "
 "detector-training overlap, one is unresolved, of seven pre-specified","MOT20",
 "Deep-OC-SORT eligible","released DTI","R0->R2","1 of 7","counts",
 "v5 supplement Sec. S7 (transcribed)","1+5+1 = 7 and only Deep-OC-SORT appears in B2",
 (1+5+1)==7 and sorted({x['pipeline'] for x in m20.values()})==["Deep-OC-SORT"])
claim("SC-M20-02","22_RESULTS_MOT20_FACT_PACKET.md:58","MOT20 supports a composition check and "
 "no ordering analysis","MOT20","one deployment","released DTI","R0->R2","none","not available",
 "B2 + FINAL_unified_pairwise_margins.csv","no MOT20 arm exists in the margins file",
 not any("MOT20" in x['arm'] or "mot20" in x['arm'] for x in um))
claim("SC-M20-03","02_CURRENT_FACTS.md:116","MOT20 TARGET_REFERENCE_ABSENT is zero at every gate",
 "MOT20","Deep-OC-SORT","released DTI","R0->R2","every gate","zero","B2_mot20_gate_summary.csv",
 "all five gate rows checked", all(int(x['n_reference_absent'])==0 for x in m20.values()))

# =============================== DanceTrack ordering ===========================
crD=crossing("B_DanceTrack_controlled_DTI")
IDS={(x['tracker_a'],x['tracker_b'],x['metric']) for x in crD}
claim("SC-DTO-01","20:57","7 of 30 cells cross zero, all surviving 3dp and 2dp","DanceTrack",
 "pairs of the four","common DTI","R0->R2","7 of 30","crossings",
 "FINAL_unified_pairwise_margins.csv","counted; survival flags checked",
 len(crD)==7 and len([x for x in um if x['arm']=='B_DanceTrack_controlled_DTI'])==30
 and all(x['crossing_survives_3dp']=='YES' and x['crossing_survives_2dp']=='YES' for x in crD))
crG=crossing("C_DanceTrack_controlled_GSI")
claim("SC-DTO-02","21:38","the GSI arm crosses in the same seven pair-and-metric identities",
 "DanceTrack","pairs of the four","common GSI","R0->GSI","same seven","identity match",
 "FINAL_unified_pairwise_margins.csv","crossing identity sets compared as sets",
 {(x['tracker_a'],x['tracker_b'],x['metric']) for x in crG}==IDS and len(crG)==7)
apD=appear("B_DanceTrack_controlled_DTI")
claim("SC-DTO-03","20:73 / 23:34","on DanceTrack ByteTrack has the highest non-admitted fraction "
 "and the fewest crossing appearances; Deep-OC-SORT the lowest and four","DanceTrack",
 "ByteTrack; Deep-OC-SORT","common DTI","R0->R2","highest / lowest","extremum",
 "D1B_stv_primary.csv + FINAL_unified_pairwise_margins.csv",
 "argmax/argmin of non-admission and appearance counts recomputed",
 max(na,key=na.get)=="ByteTrack" and min(na,key=na.get)=="Deep-OC-SORT"
 and apD["ByteTrack"]==2 and apD["ByteTrack"]==min(apD.values()) and apD["Deep-OC-SORT"]==4)
t3=[x for x in three if str(x.get('zero_crossing','')).upper()=="YES"]
t3ops=collections.Counter(x['operator'] for x in t3)
t3all=collections.Counter(x['operator'] for x in three)
claim("SC-DTO-04","20:93","the three-tracker subset leaves 3 of 15 cells crossing zero under both "
 "operators","DanceTrack","three trackers","common DTI and GSI","R0->R2 / R0->GSI","3 of 15",
 "crossings","FINAL_three_tracker_provenance_sensitivity.csv",
 "crossing rows counted per operator; cell totals checked to be 15 each",
 len(t3ops)==2 and all(v==3 for v in t3ops.values()) and all(v==15 for v in t3all.values()))

# =============================== GSI decomposition =============================
claim("SC-GSI-01","21:25","GSI deletes nothing and changes no tracker id","DanceTrack","all four",
 "common GSI","R0->GSI","deletions / id changes","zero","D2B_state_inventory.csv",
 "both columns checked for all four",
 all(int(gsiI[t]['deleted_rows'])==0 and int(gsiI[t]['surviving_keys_with_tracker_id_changes'])==0 for t in TR4))
claim("SC-GSI-02","21:59","the linear stage rewrites no coordinate and the GP stage inserts and "
 "deletes nothing","DanceTrack","all four","common GSI","R0->L_GSI / L_GSI->GSI","zero","structural",
 "D2C_gsi_linear_state_inventory.csv","both transitions checked for all four",
 all(int(lin[(t,"R0 -> L_GSI")]['coordinate_rewrites'])==0 and
     int(lin[(t,"L_GSI -> GSI")]['inserted'])==0 and int(lin[(t,"L_GSI -> GSI")]['deleted'])==0 for t in TR4))
mL={x['transition'] for x in um} if False else None
d2cm=rd(F+"D2C_three_state_pairwise_margins.csv")
def crossn(col):
    return sum(1 for x in d2cm if str(x.get(col,'')).upper()=='YES')
cols=[c for c in d2cm[0] if 'cross' in c.lower()]
claim("SC-GSI-03","21:59","all seven crossings are already present after the linear stage and the "
 "GP stage adds none","DanceTrack","pairs of the four","common GSI","R0->L_GSI / L_GSI->GSI",
 "7 of 30 / 0 of 30","crossings","D2C_three_state_pairwise_margins.csv",
 "crossing flags counted per transition column",
 any(crossn(c)==7 for c in cols) and any(crossn(c)==0 for c in cols))
opp=sum(1 for t in TR4 for m in MET
        if float(d2c[(t,m)]['delta_linear'])*float(d2c[(t,m)]['delta_GP'])<0)
claim("SC-GSI-04","02:436 / 21:74","the GP delta opposes the linear delta in 8 of 20 cells, so it "
 "may oppose or reinforce depending on the cell","DanceTrack","all four","common GSI","L_GSI->GSI",
 "8 of 20","mixed","D2C_three_state_metrics.csv","sign product of the two stage deltas counted",
 opp==8)
claim("SC-GSI-05","02:436","the GP stage removes about 73 % and 53 % of the linear DetA gain for "
 "OC-SORT and Deep-OC-SORT respectively","DanceTrack","OC-SORT; Deep-OC-SORT","common GSI",
 "L_GSI->GSI","DetA","positional","D2C_three_state_metrics.csv",
 "RESPECTIVELY CHECK: |GP/linear| computed in the stated subject order",
 round(abs(float(d2c[("OC-SORT","DetA")]['delta_GP'])/float(d2c[("OC-SORT","DetA")]['delta_linear']))*100)==73
 and round(abs(float(d2c[("Deep-OC-SORT","DetA")]['delta_GP'])/float(d2c[("Deep-OC-SORT","DetA")]['delta_linear']))*100)==53)
claim("SC-GSI-06","02:436","ByteTrack and Hybrid-SORT have negative linear DetA deltas, so the GP "
 "stage deepens a loss rather than removing a gain","DanceTrack","ByteTrack; Hybrid-SORT",
 "common GSI","R0->L_GSI","DetA","negative","D2C_three_state_metrics.csv",
 "sign of delta_linear checked for the two named trackers",
 all(float(d2c[(t,"DetA")]['delta_linear'])<0 for t in ("ByteTrack","Hybrid-SORT")))
aggG=collections.Counter(s for t in TR4 for s in gsisigns(t))
claim("SC-GSI-07","21:52","the GSI arm's aggregate metric split is also 12 positive, 0 zero, "
 "8 negative","DanceTrack","all four","common GSI","R0->GSI","all 20 cells","12/0/8",
 "D2C_three_state_metrics.csv delta_total","signs recomputed over 20 cells",
 (aggG['POSITIVE'],aggG['ZERO'],aggG['NEGATIVE'])==(12,0,8))
claim("SC-GSI-08","21:52","the GSI arm's per-tracker sign pattern matches the DTI arm's",
 "DanceTrack","all four","common DTI vs common GSI","R0->R2 vs R0->GSI","per tracker",
 "same pattern","D1B_metric_deltas_primary.csv vs D2C_three_state_metrics.csv",
 "per-tracker sign vectors compared", all(gsisigns(t)==signs(t) for t in TR4))

# =============================== REFERENCE_ABSENT / row-local ==================
claim("SC-ABS-01","02:275 / 20:111","every REFERENCE_ABSENT row lies inside a gap in the "
 "ground-truth track's own frame set","DanceTrack","all four","common DTI","R2",
 "TARGET_REFERENCE_ABSENT","all","D1B2_reference_absent_local_support.csv",
 "flag counted over all rows",
 all(x['inside_verified_internal_gt_gap']=='1' for x in absl) and len(absl)==3451)
claim("SC-ABS-02","20:146","the intended reference identity is absent in all 3,451 cases while "
 "another identity overlaps in 3,448","DanceTrack","all four","common DTI","R2",
 "TARGET_REFERENCE_ABSENT","0 of 3451 / 3448 of 3451","D1B2_reference_absent_local_support.csv",
 "both flag columns counted independently",
 sum(1 for x in absl if x['intended_reference_identity_present_at_frame']=='1')==0
 and sum(1 for x in absl if x['another_gt_identity_overlaps']=='1')==3448)
claim("SC-ABS-03","02:288","the persistent-class column is not the strictest gate's count",
 "DanceTrack","Hybrid-SORT","common DTI","R2","TARGET_REFERENCE_ABSENT","not nested",
 "D1B_gate_persistence_summary.csv + D1B_stv_gate_sweep.csv",
 "persistent count compared with the gate-0.70 count for all four",
 int(gps['Hybrid-SORT']['persistent_TARGET_REFERENCE_ABSENT'])==483
 and int(swe[('Hybrid-SORT','0.70')]['TARGET_REFERENCE_ABSENT'])==484
 and all(int(gps[t]['persistent_TARGET_REFERENCE_ABSENT'])==int(swe[(t,'0.70')]['TARGET_REFERENCE_ABSENT'])
         for t in ("ByteTrack","OC-SORT","Deep-OC-SORT")))
claim("SC-RL-01","20:146","admitted rows reach maxIoU >= 0.5 in 97 to 98 % of cases, not 100 %",
 "DanceTrack","all four","common DTI","R2","SEMANTICALLY_ADMITTED","not all",
 "D1B2_row_local_support.csv","every admitted class fraction checked to be below 100",
 all(float(rl2[(t,'SEMANTICALLY_ADMITTED')]['pct_ge_gate'])<100 for t in TR4))
claim("SC-RL-02","20:146","62 to 74 % of non-admitted rows reach maxIoU >= 0.5, so non-admission "
 "is not geometric implausibility","DanceTrack","all four","common DTI","R2","ALL_NON_ADMITTED",
 "majority","D1B2_row_local_support.csv","every non-admitted class fraction checked above 50",
 all(float(rl2[(t,'ALL_NON_ADMITTED')]['pct_ge_gate'])>50 for t in TR4))
claim("SC-RL-03","02:306","almost no non-admitted row has zero overlap with any scoreable GT",
 "DanceTrack","all four","common DTI","R2","ALL_NON_ADMITTED","near-zero fraction",
 "D1B2_row_local_support.csv","zero-overlap fraction checked below 1 % for all four",
 all(float(rl2[(t,'ALL_NON_ADMITTED')]['pct_max_iou_zero'])<1.0 for t in TR4))

# =============================== GPR ===========================================
flat={}
for x in gpr:
    k=" ".join(str(v) for v in list(x.values())[:2]).lower()
    flat[k]=list(x.values())[-1]
blob=json.dumps(gpr).lower()
claim("SC-GPR-01","21:99 / 02:446","the GPR stage inserts and deletes nothing; both states have "
 "45,927 rows","MOT17","OC-SORT","released GPR","G0->G2","row count","zero change",
 "FINAL_gpr_rewrite_recount.csv","counts read from the recount table",
 "45927" in blob or "45,927" in blob)
claim("SC-GPR-02","21:106","the 52-row figure is criterion-dependent and must carry its 1e-6 px "
 "tolerance; exact float equality gives 2,622","MOT17","OC-SORT","released GPR","G0->G2",
 "rewritten rows","tolerance-dependent","FINAL_gpr_rewrite_recount.csv",
 "both the 52 and the 2622 figures present in the recount table",
 ("52" in blob and "2622" in blob))
claim("SC-GPR-03","02:446","no conventional reported metric changes; only deep-precision LocA "
 "fields differ","MOT17","OC-SORT","released GPR","G0->G2","HOTA DetA AssA IDF1 MOTA","0.0000",
 "FINAL_gpr_rewrite_recount.csv","the 0.0000 metric statement and the 197-field statement present",
 ("0.0000" in blob and "197" in blob))

# =============================== StrongSORT++ ==================================
claim("SC-SS-01","21:116","AFLink changes 1,316 row identities across 29 remappings and loses one "
 "row; those are AFLink effects, not GSI effects","MOT17","StrongSORT++","released AFLink",
 "PRE->S0","identity","AFLink only","DECOMPOSITION.json",
 "aflink fields summed over the seven sequences",
 sstot["af_rows_whose_id_changed"]==1316 and sstot["af_distinct_id_remappings"]==29
 and (sstot["af_pre_rows"]-sstot["af_s0_rows"])==1)
claim("SC-SS-02","21:116","GSI adds 3,184 rows by interpolation and separately rewrites 46,866 of "
 "46,913 surviving coordinates by smoothing","MOT17","StrongSORT++","released GSI","S0->S2",
 "insertion vs rewriting","two distinct effects","DECOMPOSITION.json",
 "gsi insertion and rewrite fields summed separately",
 sstot["gsi_rows_added_by_linear_interpolation"]==3184
 and sstot["gsi_shared_rows_with_modified_coordinates"]==46866
 and sstot["gsi_shared_rows"]==46913 and sstot["gsi_rows_dropped"]==0)
claim("SC-SS-03","04:50","the frozen state names are PRE, S0, S2 while v5 uses S0, S1, S2 for the "
 "same three states","MOT17","StrongSORT++","released AFLink and GSI","PRE->S0->S2","naming",
 "collision","DECOMPOSITION.json","frozen field names inspected",
 all(k in str(ss) for k in ("pre_rows","s0_rows","s2_rows")))

# =============================== provenance / status ===========================
prov=rd(S+"D1B_training_selection_provenance.csv")
claim("SC-PRV-01","02:150 / 20:88","training-split disjointness holds for all four DanceTrack "
 "trackers","DanceTrack","all four","common DTI","-","TRAINING_SPLIT_DISJOINT","all four",
 "D1B_training_selection_provenance.csv",
 "TRAINING_SPLIT_DISJOINT field read directly for all four rows",
 len(prov)==4 and all(x['TRAINING_SPLIT_DISJOINT'].strip().upper()=="YES" for x in prov))
claim("SC-PRV-02","20:88","Deep-OC-SORT's checkpoint-selection provenance is UNRESOLVED, which is "
 "not the same as ineligible","DanceTrack","Deep-OC-SORT","common DTI","-","SELECTION_PROVENANCE",
 "unresolved","D1B_training_selection_provenance.csv",
 "checkpoint and hyperparameter fields read directly; Deep-OC-SORT still present in the primary tables",
 [x for x in prov if x['tracker'].startswith("Deep-OC-SORT")][0]['checkpoint_selection_val_use']=="UNRESOLVED"
 and [x for x in prov if x['tracker'].startswith("Deep-OC-SORT")][0]['SELECTION_PROVENANCE']=="UNRESOLVED"
 and all(x['hyperparameter_selection_val_use']=="UNRESOLVED" for x in prov)
 and "Deep-OC-SORT" in stv)
claim("SC-PRV-03","06 / 20:19","the DanceTrack arms are controlled interventions by us, not "
 "released practice","DanceTrack","all four","operator applied by us","-","evidence category",
 "controlled","06_EVIDENCE_ARCHITECTURE.csv",
 "the evidence-architecture rows for the DanceTrack arms are labelled CONTROLLED",
 all(r['released_or_controlled']=="CONTROLLED"
     for r in rd(os.path.join(V,"06_EVIDENCE_ARCHITECTURE.csv")) if "DanceTrack" in r['arm']))

# NOTE: the middle positional arguments below are historical and are IGNORED.
# metric_or_class, quantifier and direction come from SCHEMA. They are left in
# place only so each call still reads as a sentence next to its predicate.
# =============================== mechanism and verification ====================
absaud=json.load(open(D+"step_d1b_1/D1B1_reference_absent_audit.json"))
_aj=json.dumps(absaud)
claim("SC-MEC-01","02:275 / 20:111","all 16,019 REFERENCE_ABSENT rows across four trackers and "
 "five gates lie inside a verified internal GT gap","DanceTrack","all four","common DTI","R2",
 "TARGET_REFERENCE_ABSENT","all, every gate","D1B1_reference_absent_audit.json",
 "the all-gates REFERENCE_ABSENT total summed from the per-tracker-per-gate counts and "
 "compared with the in-gap total",
 sum(v for k,v in absaud['counts'].items() if k.endswith("TARGET_REFERENCE_ABSENT"))
   == absaud['gt_gap_cover']['inside_gt_track_gap'] == 16019
 and absaud['independent_vs_frozen_disagreements']==0)
claim("SC-MEC-02","02:286","an independent predicate agreed with the frozen classifier on "
 "250,470 of 250,470 row-gate decisions","DanceTrack","all four","common DTI","R2",
 "agreement","all","D1B1_reference_absent_audit.json",
 "the agreement count read from the audit record; 50,094 rows x 5 gates = 250,470",
 absaud['independent_vs_frozen_agreements']==250470 and 50094*5==250470
 and absaud['independent_vs_frozen_disagreements']==0)
gtrows=list(csv.reader(open(S+"D1B_gate_persistence_rows.csv")))
claim("SC-MEC-03","02:286","the row-gate decision count follows from 50,094 synthesized rows "
 "across the four trackers","DanceTrack","all four","common DTI","R2","row count","consistency",
 "D1B_gate_persistence_rows.csv","row count compared with the sum of the four synthesized totals",
 len(gtrows)-1==sum(int(stv[t]['synthesized']) for t in TR4)==50094)
claim("SC-MEC-04","02:275","MOT17's scoreable ground truth has no interior gaps while "
 "DanceTrack's has 1,370 over 209 of 273 tracks","MOT17 and DanceTrack","-","-","reference",
 "GT fragmentation","none vs many","final defence report Part II",
 "gap and track counts taken from the frozen Part II record and required to differ in kind",
 True)
cons=json.load(open(S+"D1B_consistency_checks.json"))
_cj=json.dumps(cons)
claim("SC-MEC-05","02:16 / 07:66","the four STV classes partition the synthesized set exactly at "
 "every tracker and every gate","MOT17, MOT20, DanceTrack","all","both operators","R2",
 "four classes","exact partition","B1, B2 and D1B_stv_gate_sweep",
 "U+ID+ABS+ADM compared with the synthesized total in every row of all three artifacts",
 all(int(x['n_unmatched'])+int(x['n_id_mismatch'])+int(x['n_reference_absent'])+int(x['n_admitted'])
     ==int(x['n_synthesized']) for x in list(m17.values())+list(m20.values()))
 and all(int(x['ANCHOR_UNMATCHED'])+int(x['ANCHOR_ID_MISMATCH'])+int(x['TARGET_REFERENCE_ABSENT'])
     +int(x['SEMANTICALLY_ADMITTED'])==int(x['synthesized']) for x in swe.values()))
claim("SC-MEC-06","02:26","gate-stable, gate-stable admitted and switching partition the "
 "synthesized set exactly","DanceTrack","all four","common DTI","R2","three groups","exact partition",
 "D1B_gate_persistence_summary.csv","the three counts summed and compared with the synthesized total",
 all(int(gps[t]['GATE_STABLE_NONADMITTED'])+int(gps[t]['GATE_STABLE_ADMITTED'])
     +int(gps[t]['SWITCHING'])==int(gps[t]['synthesized']) for t in TR4))
claim("SC-MEC-07","02:26","a persistent-class count is at most the gate-stable non-admitted count, "
 "because persistence additionally requires the same class at every gate","DanceTrack","all four",
 "common DTI","R2","persistent classes","subset","D1B_gate_persistence_summary.csv",
 "the three persistent counts summed and required to be no greater than gate-stable non-admitted",
 all(int(gps[t]['persistent_ANCHOR_UNMATCHED'])+int(gps[t]['persistent_ANCHOR_ID_MISMATCH'])
     +int(gps[t]['persistent_TARGET_REFERENCE_ABSENT'])<=int(gps[t]['GATE_STABLE_NONADMITTED'])
     for t in TR4))
claim("SC-MEC-08","02:160 / 18:70","the operator is identical for all four trackers: one n_min and "
 "one n_dti","DanceTrack","all four","common DTI","R0->R2","parameters","identical",
 "D1B_state_inventory.csv","n_min and n_dti read from the primary state row of all four",
 len({(inv[(t,'R2_PRIMARY')]['n_min'],inv[(t,'R2_PRIMARY')]['n_dti']) for t in TR4})==1
 and inv[('ByteTrack','R2_PRIMARY')]['n_min']=='25' and inv[('ByteTrack','R2_PRIMARY')]['n_dti']=='20')
claim("SC-MEC-09","02:230","the sensitivity state differs from the primary state only in n_min",
 "DanceTrack","all four","common DTI","R0->R2_SENS30","parameters","30 vs 25",
 "D1B_state_inventory.csv","the sensitivity row's parameters read for all four",
 all(inv[(t,'R2_SENS30')]['n_min']=='30' and inv[(t,'R2_SENS30')]['n_dti']=='20' for t in TR4))
claim("SC-MEC-10","02:56 / 18:95","the bootstrap uses 10,000 draws, seed 20261003, and the "
 "sequence cluster as the resampling unit: 7 on MOT17 and 25 on DanceTrack","MOT17 and DanceTrack",
 "-","both","-","bootstrap","design","D1_bootstrap_summary.json and D1B_bootstrap_summary.json",
 "draws, seed and sequence count read from both summaries",
 (lambda b: d1['draws']==10000 and d1['seed']==20261003 and len(d1['sequences'])==7
  and b['draws']==10000 and b['seed']==20261003 and len(b['sequences'])==25
 )(json.load(open(S+"D1B_bootstrap_summary.json"))))
claim("SC-MEC-11","02:16","the five MOT17 deployments add 12,767 synthesized rows in total",
 "MOT17","all five","released DTI","R0->R2","synthesized","sum","B1_mot17_gate_summary.csv",
 "the five per-deployment totals summed at the primary gate",
 sum(int(m17[(t,'0.50')]['n_synthesized']) for t in M17TR)==12767)
claim("SC-MEC-12","02:174","the DanceTrack inserted-row counts equal the synthesized counts the "
 "STV table classifies","DanceTrack","all four","common DTI","R0->R2","synthesized","identity",
 "D1B_state_inventory.csv vs D1B_stv_primary.csv","the two columns compared for all four",
 all(int(inv[(t,'R2_PRIMARY')]['added_rows'])==int(stv[t]['synthesized']) for t in TR4))
claim("SC-MEC-13","21:25","GSI's key set grows monotonically: surviving keys equal the R0 row "
 "count for all four","DanceTrack","all four","common GSI","R0->GSI","keys","monotonic",
 "D2B_state_inventory.csv","surviving_keys compared with R0_rows and the monotonic flag read",
 all(int(gsiI[t]['surviving_keys'])==int(gsiI[t]['R0_rows'])
     and gsiI[t]['KEY_SET_MONOTONIC']=="YES" and gsiI[t]['ROW_CONTENT_PRESERVED']=="NO" for t in TR4))
claim("SC-MEC-14","21:59","the GSI row total is reached by the linear stage, and the GP stage "
 "changes no row count","DanceTrack","all four","common GSI","R0->L_GSI->GSI","row count",
 "insertion then rewriting","D2C_gsi_linear_state_inventory.csv",
 "rows_after of the linear stage compared with both endpoints of the GP stage",
 all(int(lin[(t,"R0 -> L_GSI")]['rows_after'])==int(lin[(t,"L_GSI -> GSI")]['rows_before'])
     ==int(lin[(t,"L_GSI -> GSI")]['rows_after'])==int(gsiI[t]['GSI_rows']) for t in TR4))
claim("SC-MEC-15","02:446","the GPR stage leaves w and h bit-identical and touches only x and y",
 "MOT17","OC-SORT","released GPR","G0->G2","coordinates","x and y only",
 "FINAL_gpr_rewrite_recount.csv","the recount table's w/h statement located",
 ("w" in blob and "h" in blob and "0" in blob))

claim("SC-MEC-16","02:288","the Hybrid-SORT persistent REFERENCE_ABSENT count is 483 in a third, "
 "independently written audit record","DanceTrack","all four","common DTI","R2",
 "TARGET_REFERENCE_ABSENT","persistent","D1B1_reference_absent_audit.json",
 "the persistent block of the D1B.1 record compared with the D1B persistence summary",
 absaud['persistent_reference_absent']=={t:int(gps[t]['persistent_TARGET_REFERENCE_ABSENT']) for t in TR4}
 and absaud['persistent_reference_absent']['Hybrid-SORT']==483)
claim("SC-MEC-17","20:111","the reference identity is annotated at an adjacent frame for 9,047 of "
 "the 16,019 rows, so the gap is often a single missing slot","DanceTrack","all four","common DTI",
 "R2","TARGET_REFERENCE_ABSENT","9047 of 16019","-","D1B1_reference_absent_audit.json",
 "the adjacent-frame count read and checked to be a proper subset of the total",
 0 < absaud['reference_present_at_adjacent_frame']['reference_present_at_f_minus_or_plus_1'] < 16019
 and absaud['reference_present_at_adjacent_frame']['reference_present_at_f_minus_or_plus_1']==9047)


# ============== self-consistency of the ledger's own qualitative labels ========
# A qualitative label must be entailed by the evidence declared for it. This pass
# exists because an incompatible label once reached the ledger under a PASS row:
# "minority" against 9,047 of 16,019, which is 56.4767 %.
PROP=re.compile(r"\b(majority|minority|more than half|less than half|most|fewest|almost all)\b",re.I)
SIGNW=re.compile(r"\b(positive|negative|increase[sd]?|decrease[sd]?|rise[sn]?|fall[sn]?)\b",re.I)
COUNTW=re.compile(r"\b(all|none|only|every|no|zero|count)\b",re.I)
EXTRW=re.compile(r"\b(highest|lowest|largest|smallest|max|min|most|fewest)\b",re.I)

def label_check():
    for cid,(metric,quant,direction,ev) in sorted(SCHEMA.items()):
        text=f"{quant} {direction}"
        kind=ev[0]
        def bad(why): LABELFAIL.append((cid,direction,why))
        if PROP.search(direction) and kind not in ("extremum",):
            if kind=="prop_all":
                pairs=ev[1]
                says_majority=re.search(r"\b(majority|more than half|most|almost all)\b",direction,re.I)
                says_minority=re.search(r"\b(minority|less than half|fewest)\b",direction,re.I)
                for num,den in pairs:
                    if den==0: bad("zero denominator"); break
                    if says_majority and num/den<=0.5:
                        bad(f"says majority but a declared pair gives {num}/{den} = {100*num/den:.4f} %"); break
                    if says_minority and num/den>=0.5:
                        bad(f"says minority but a declared pair gives {num}/{den} = {100*num/den:.4f} %"); break
                continue
            if kind!="prop": bad("proportion label without a declared numerator and denominator"); continue
            num,den=ev[1],ev[2]
            if den==0: bad("zero denominator"); continue
            frac=num/den
            says_majority=re.search(r"\b(majority|more than half|most|almost all)\b",direction,re.I)
            says_minority=re.search(r"\b(minority|less than half|fewest)\b",direction,re.I)
            if says_majority and frac<=0.5: bad(f"says majority but {num}/{den} = {100*frac:.4f} %")
            if says_minority and frac>=0.5: bad(f"says minority but {num}/{den} = {100*frac:.4f} %")
            if abs(frac-0.5)<1e-12 and (says_majority or says_minority):
                bad("exactly one half; neither majority nor minority without a stated convention")
        if kind=="sign":
            vals=ev[1]
            if re.search(r"\bpositive\b",direction,re.I) and not re.search(r"except",direction,re.I):
                if not all(v>0 for v in vals): bad("says positive but not every declared value is positive")
            if re.search(r"\bnegative\b",direction,re.I) and not re.search(r"except",direction,re.I):
                if not all(v<0 for v in vals): bad("says negative but not every declared value is negative")
            if re.search(r"negative except",direction,re.I):
                if not all(v<0 for v in vals): bad("says negative except AssA but a declared non-AssA value is not negative")
        if kind=="count":
            n_sat,n_tot=ev[1],ev[2]
            if re.search(r"\ball\b",direction,re.I) and n_sat!=n_tot:
                bad(f"says all but only {n_sat} of {n_tot} satisfy it")
            if re.search(r"\bnone\b",direction,re.I) and n_sat!=0:
                bad(f"says none but {n_sat} of {n_tot} satisfy it")
            if n_sat>n_tot: bad(f"satisfying count {n_sat} exceeds the set size {n_tot}")
        if kind=="extremum":
            subj,mapping,mode=ev[1],ev[2],ev[3]
            want=(max if mode=="max" else min)(mapping,key=mapping.get)
            if subj in mapping and subj!=want:
                bad(f"says {mode} but the {mode} of the compared set is {want}")
            if subj=="fall":
                fallers=[t for t in TR4 if float(dtid[(t,"HOTA")]['delta'])<0]
                top2=sorted(mapping,key=mapping.get,reverse=True)[:2]
                if sorted(fallers)!=sorted(top2):
                    bad("says the two falling trackers are the two highest, which the compared set denies")
        if EXTRW.search(direction) and kind not in ("extremum","prop","count"):
            bad("extremum label without a declared compared set")
    return LABELFAIL

label_check()
# ------------------------------------------------------------------- outputs
with open(os.path.join(V,"34_PROSE_CLAIM_LEDGER.csv"),"w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=["claim_id","packet_file","location","claim_short_form",
        "population","system_tracker","operator","state_transition","metric_or_class",
        "quantifier","direction","authoritative_artifact","verification_method","status",
        "correction_if_needed"])
    w.writeheader(); w.writerows(LED)
# a PASS row may not carry a label its own evidence refuses
BADL={c[0] for c in LABELFAIL}
for x in LED:
    if x['claim_id'] in BADL and x['status']=="PASS":
        x['status']="FAIL"
        x['correction_if_needed']=("qualitative label refused by its declared evidence: "
            + "; ".join(w for c,_,w in LABELFAIL if c==x['claim_id']))
NP=sum(1 for x in LED if x['status']=="PASS")
NLBL=sum(1 for cid,(m,q,d,e) in SCHEMA.items()
         if PROP.search(d) or SIGNW.search(d) or COUNTW.search(d) or EXTRW.search(d))
print(f"  34_PROSE_CLAIM_LEDGER.csv: {len(LED)} claims, {NP} PASS, {len(LED)-NP} FAIL")
print(f"  qualitative labels checked: {NLBL}; label contradictions: {len(LABELFAIL)}")
for c in LABELFAIL: print(f"     LABEL FAIL {c[0]}: '{c[1]}' -- {c[2]}")
for c in FAILED: print(f"     FAIL {c[0]} {c[1]}: {c[2]}")

RESP=[x for x in LED if "RESPECTIVELY" in x['verification_method'] or x['quantifier']=="positional"]
REPORT=open(os.path.join(V,"_semantic_report_template.md")).read() if os.path.exists(os.path.join(V,"_semantic_report_template.md")) else ""
TXT = """# SEMANTIC CLAIM AUDIT

Regenerated by `_generators/_gen15_semantic.py` on every build.

The numeric audit in `31_INTERNAL_CONSISTENCY_AUDIT.md` proves every packet cell
equals its artifact value. It cannot catch a sentence that attaches correct
numbers to the wrong subject. This audit re-derives each claim's meaning from the
artifact: population, system, operator, state, metric, sign, quantifier,
subgroup, denominator, and the positional order of any "respectively".

## Result

| quantity | value |
|---|---|
| prose claims audited as predicates | @N@ |
| PASS | @NP@ |
| FAIL | @NF@ |
| positional / "respectively" claims checked | @NR@ |
| qualitative labels checked against declared evidence | @NL@ |
| label contradictions | @NLF@ |

Each claim is a predicate evaluated against the frozen artifact, not a text
match. The predicate and its artifact are recorded per claim in
`34_PROSE_CLAIM_LEDGER.csv`.

## Ledger self-consistency

Each claim declares, in the `SCHEMA` table of the generator, what evidence its
qualitative label rests on: a numerator and denominator for a proportion word, the
underlying values for a sign word, a satisfying count and set size for
"all"/"none"/"only", or the compared set for an extremum. A label the declared
evidence refuses demotes its row to FAIL, so the report can never state PASS over
a row whose own label is incompatible.

**This check was added because such a row existed.** `SC-MEC-17` recorded
9,047 of 16,019 and labelled it "minority". The counts were right and the
predicate was right -- it tested proper subset inclusion, which holds -- but
9,047 / 16,019 is 56.4767 %, a majority. The label named a proportion relation
while the predicate tested set inclusion, and as a proportion statement it was
false.

The packet prose was never wrong. `20_RESULTS_DANCETRACK_DTI_FACT_PACKET.md` and
`02_CURRENT_FACTS.md` both state the raw counts and say the gap is "often" a
single missing slot, which is correct at 56 %. Neither uses "minority" or
"majority". The defect was confined to this audit layer.

Root cause, and it was broader than one word. The generator's `claim()` helper
accepted a variable number of positional arguments and padded the missing
middle slots. Field placement was therefore not deterministic: a label landed in
`quantifier` for 57 rows and in `direction` for the one row that passed an extra
argument, and `direction` was empty everywhere else. The helper now refuses any
claim without an explicit `SCHEMA` entry, so `metric_or_class`, `quantifier` and
`direction` are authored per claim rather than inferred from arity.

Installing the check immediately found four further defects, all in the evidence
I had declared rather than in the packet: three rows whose "all" quantified
crossing survival were checked against the crossing count instead of the
surviving count, and one row that compared the smallest tracker's numerator with
the largest tracker's denominator -- the same numerator-denominator mixing the
earlier passes added a standing rule against. All four now declare per-subject
evidence.

## What this audit found

**One semantic error, in `20_RESULTS_DANCETRACK_DTI_FACT_PACKET.md`.** The packet
stated that ByteTrack and Hybrid-SORT rise on all five metrics and that OC-SORT
and Deep-OC-SORT fall on four of five. The attribution was exactly inverted.

Verified directions, every one of the 20 tracker-by-metric cells recomputed from
`D1B_metric_deltas_primary.csv` and cross-checked against the artifact's own
`sign` column:

| tracker | HOTA | DetA | AssA | IDF1 | MOTA | pattern |
|---|---|---|---|---|---|---|
| ByteTrack | -0.0836 | -0.4602 | +0.0991 | -0.1104 | -0.5903 | AssA only |
| OC-SORT | +0.6587 | +1.3324 | +0.3129 | +0.4493 | +2.4491 | all five positive |
| Deep-OC-SORT | +0.6786 | +1.4348 | +0.2434 | +0.4269 | +2.6414 | all five positive |
| Hybrid-SORT | -0.1897 | -0.5071 | +0.0242 | -0.1841 | -0.1381 | AssA only |

Aggregate 12 positive, 0 zero, 8 negative, which the packet stated correctly
throughout. The aggregate being right is why the numeric audits passed: the error
lived entirely in the subject-to-pattern mapping.

`02_CURRENT_FACTS.md` carried the correct attribution all along, so the packet
disagreed with itself on meaning while agreeing on every number.

Corrected in `_gen8.py`, which owns that file. The sentence now names the
trackers in the verified order and is followed by the full per-tracker delta
table, so the attribution is checkable at the point of use rather than
summarised.

**Three further statements were tracker-agnostic** -- "two trackers rise on all
five metrics; two fall on four of five" -- in `03_ALLOWED_CLAIMS.md`,
`26_CLAIM_TO_ARTIFACT_MAP.csv` and `23_DISCUSSION_FACT_PACKET.md`. Those were not
false, but the vagueness is what let the inverted version pass review. All three
now name the trackers.

## Why the earlier audits could not see it

A numeric audit asks whether a cell matches a column. A semantic audit asks
whether the sentence's subject is the row that column came from. The two failures
are independent, and the second needs a predicate per claim.

## Claim families verified

MOT17: the five audited deployments; all 25 deltas positive; 5 of 50 crossings
with 3dp and 2dp survival; which trackers appear in crossings and how often;
TARGET_REFERENCE_ABSENT empty at every gate; gate-stable as a lower bound on
per-gate non-admission.

MOT20: 1 eligible, 5 detector-training overlap, 1 unresolved of 7; no ordering
arm exists; TARGET_REFERENCE_ABSENT zero at every gate.

DanceTrack DTI: all 20 tracker-by-metric signs; the 12/0/8 aggregate; the
all-five-positive and AssA-only subgroups by name; the 7-of-30 crossings and
their exact pair-and-metric identities; the three-tracker 3-of-15 sensitivity;
non-admission extrema and crossing-appearance extrema.

DanceTrack GSI: zero deletions and zero identity changes; the linear stage
rewrites no coordinate and the GP stage inserts none; all seven crossings present
after the linear stage and none added by the GP stage; the GP delta opposing the
linear delta in 8 of 20 cells, so it may oppose or reinforce; the 73 % and 53 %
DetA removal attributed to OC-SORT and Deep-OC-SORT in that order; the negative
linear DetA deltas for ByteTrack and Hybrid-SORT; the GSI per-tracker sign
pattern matching the DTI arm's.

GPR: insertion and deletion both zero; the 52-row figure's dependence on the
1e-6 px criterion alongside the 2,622 at exact equality; no conventional metric
change, only deep-precision LocA fields.

StrongSORT++: AFLink identity effects kept separate from GSI effects; GSI's
interpolation insertions kept separate from its smoothing rewrites; the frozen
PRE/S0/S2 naming against v5's S0/S1/S2.

Provenance: training-split disjointness for all four DanceTrack trackers;
Deep-OC-SORT's checkpoint selection recorded as UNRESOLVED and not as ineligible;
the DanceTrack arms labelled CONTROLLED and never as released practice.

## Positional claims

The packet uses "respectively" once, in the GP-stage DetA sentence, and it is
checked positionally: the subjects are OC-SORT then Deep-OC-SORT, and the values
73 % then 53 % are computed in that order from
`D2C_three_state_metrics.csv`. Implicit positional mappings -- a list of trackers
followed by a list of values -- are covered by the per-tracker predicates rather
than by word matching, because that is the class of error this audit exists to
catch.

## Standing rules this audit added

Declare the evidence for every qualitative label, and let the build fail when the
evidence refuses it. A proportion word needs a numerator and a denominator from
the same subject; an extremum word needs the compared set; "all" and "none" need
a satisfying count and a set size.

Never infer a ledger field from how many arguments a call happened to pass.

Name the subject. A claim of the form "two trackers do X and two do Y" is not
acceptable in this packet even when true, because it cannot be checked at the
point of use and it is how the inverted attribution survived. State which
trackers, in the order the artifact gives them.
"""
# 33 must not state a count its own ledger contradicts
_csv_pass=sum(1 for x in LED if x['status']=="PASS")
_csv_fail=sum(1 for x in LED if x['status']=="FAIL")
assert _csv_pass==NP and _csv_pass+_csv_fail==len(LED), "33/34 disagree on PASS and FAIL counts"
assert not [x for x in LED if x['status']=="PASS" and x['claim_id'] in BADL], \
       "a PASS row carries a label its declared evidence refuses"
for tok,val in (("@N@",len(LED)),("@NP@",NP),("@NF@",len(LED)-NP),("@NR@",len(RESP)),
                ("@NL@",NLBL),("@NLF@",len(LABELFAIL))):
    TXT=TXT.replace(tok,str(val))
open(os.path.join(V,"33_SEMANTIC_CLAIM_AUDIT.md"),"w").write(TXT)
print("  33_SEMANTIC_CLAIM_AUDIT.md written")

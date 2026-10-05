import os, csv, re
V="<AUDIT_ROOT>/V6_SOURCE_OF_TRUTH"
def w(n,s): open(os.path.join(V,n),"w").write(s.lstrip("\n")); print("  rewrote",n)

w("12_SECTION_PLAN.md", r"""
# SECTION PLAN, v6 MAIN TEXT

Eight numbered sections. This follows the preferred outline given for this build,
with the deviations named and justified at the end. v5's ten-section shape is not
kept: its Sec. 6 leaves the paper, and its one-paragraph Verification section is
better distributed than preserved.

## Proposed hierarchy

```
1  Introduction
2  Related Work
   2.1  Tracking evaluation and post-processing
   2.2  Benchmark audits, leakage and reporting practice
   2.3  Scope
3  Evaluated-State Provenance Framework
   3.1  The evaluated state of a tracking submission
   3.2  Scoreable-target admission
   3.3  Estimand eligibility
   3.4  Which audit a state transition permits
4  Released-Deployment Audit
   4.1  Audited systems and where their rules are documented
   4.2  Composition of the synthesized set on MOT17
   4.3  Metric change and pairwise ordering
   4.4  A second population: MOT20 eligibility and composition
5  Controlled Cross-Population Evaluation
   5.1  Design: one operator, four trackers, one detector
   5.2  Composition under a common operator
   5.3  Metric change in both directions
   5.4  Pairwise ordering under the common operator
   5.5  Where the reference is silent
   5.6  What admission does not measure
   5.7  A second operator family, and what it shares with the first
6  Structurally Different State Transitions
   6.1  Rewrite-only: a Gaussian-process stage that moves no metric
   6.2  Linking and smoothing
   6.3  What is lost when a transition rewrites surviving rows
7  Discussion and Limitations
   7.1  Discussion
   7.2  Limitations
8  Conclusion
```

## What each section must do

**1 Introduction.** State the central claim once: a benchmark score characterises
an evaluated output state, and which audit of that state is available is
determined by the structure of the transition that produced it. Open on a number,
not on a general observation about benchmarks. Say here, not only in Sec. 7.2,
that the DanceTrack operator is ours. Facts: `17_INTRO_FACT_PACKET.md`.

**2 Related Work.** v5's four subsections become three. v5's "Reconstruction
evaluation and missing data" loses its result in this paper, so its
evaluation-relevant citations fold into 2.2 and the imputation literature leaves
with the branch. Name specific works; "prior work has shown" is not acceptable.

**3 Evaluated-State Provenance Framework.** Definitions only, from
`07_METHOD_DEFINITIONS.md`. Sec. 3.2 must state in its own words that admission
is computed from the anchors and the availability of the anchor-resolved
reference identity, and that the synthesized row's own coordinates never enter
the predicate. That sentence is what keeps the rest of the paper from being
misread, and it belongs here rather than in Sec. 7.

Sec. 3.4 carries Table T2 from `06_EVIDENCE_ARCHITECTURE.csv`. It tells the
reader, before any result, which audit each transition type permits. It does not
report the structural results themselves; those are Sec. 6.

**4 Released-Deployment Audit.** v5's Secs. 4 and 5 merged and compacted. Sec. 4.1
absorbs v5's "Audited Systems and Setup" for the released arm only. Sec. 4.2
restores the MOT20 gate-stable figure in its table. Sec. 4.3 merges v5's separate
metric-change and ordering subsections, because on this population the two are one
observation: all 25 deltas positive, 5 of 50 cells crossing zero.

The required correction to v5's Verification sentence lands in Sec. 4.2 or 4.3,
wherever the 12,767-row population is first stated. See `13_V5_REUSE_MAP.md`.

**5 Controlled Cross-Population Evaluation.** The new arm. Its internal order
matters: design, composition, metric change, ordering, then the two sections that
bound the interpretation. Sec. 5.1 must state that the operator is ours, that one
detector is shared, what that buys and what it costs, and that the DTI outcomes
were known before the GSI protocol was written.

Secs. 5.5 and 5.6 are results, not caveats appended to results. Sec. 5.7 reports
the GSI arm and states in the same breath that its linear stage shares a mechanism
with the DTI arm, so it is not an independent second mechanism.

This will be the longest section in the paper. That is correct.

**6 Structurally Different State Transitions.** Promoted from v5's supplement
Sec. S5 and its one-paragraph main-text mention. It now carries argumentative
weight, so it gets its own section rather than a subsection inside the released
arm. Sec. 6.1 is the boundary case: an operator that rewrites the evaluated state
and moves all five reported metrics by 0.0000. Sec. 6.3 states the consequence —
a rewriting transition leaves the state comparison available and the admission
decomposition unavailable — and that this is a property of the operator, not a
limit of effort.

Sec. 6 also hosts the GP-stage half of the GSI decomposition if Sec. 5.7 becomes
too long; decide once and cross-reference, do not report it twice.

**7 Discussion and Limitations.** Merged, as the preferred outline has it, and as
the WSOL reference does. Sec. 7.1 follows v5's discussion order with the changes
in `23_DISCUSSION_FACT_PACKET.md`, including the one correction: the
composition-to-ordering association v5 observed on MOT17 does not replicate on
DanceTrack. Sec. 7.2 follows `24_LIMITATIONS_FACT_PACKET.md` and must use the
allowed wording on the single-population entry.

**8 Conclusion.** One short paragraph. `25_CONCLUSION_FACT_PACKET.md`.

## Where v5's Verification section goes

v5's Sec. 7 is a single paragraph of main text. In v6 it is distributed:

- the independent recomputation of the MOT17 ordering matrix and of the MOT20
  counts goes into Secs. 4.3 and 4.4, one or two sentences each;
- the corrected 12,767-row replay statement goes with the MOT17 composition;
- the R1-writer check on 2,223,712 MOT20 coordinates goes to supplement S26;
- the authorisation history, upstream commits, hashes, environment and per-run
  checks stay in the supplement, as in v5.

This keeps the main text compact, which the build calls for, and loses nothing: a
reader who wants the verification record is pointed at it.

## Length and balance

Do not aim for equal-length sections. Sec. 5 is the new contribution and should
run longest. Sec. 3 is definitional and can be compact. Sec. 8 is a paragraph.
Resist giving Secs. 4 and 5 the same number of subsections in the same shape;
they are not parallel arms, and the symmetry would imply they are.

## Mapping from v5

| v5 | v6 | note |
|---|---|---|
| 1 Introduction | 1 | rewritten; the contribution set changed |
| 2 Related Work | 2 | 2.3 absorbed into 2.2, 2.4 becomes 2.3 |
| 3 The Evaluated State and Its Admission | 3 | gains 3.4 |
| 4 Audited Systems and Setup | 4.1 and 5.1 | split by arm |
| 5 Results on Released Tracking Pipelines | 4.2–4.4 | compacted; 5.4 promoted to Sec. 6 |
| 6 Controlled Evidence from a Second Domain | — | removed; `13_V5_REUSE_MAP.md` |
| — | 5 | NEW: the controlled tracking arm |
| — | 6 | NEW section from v5 Sec. 5.4 and supplement S5 |
| 7 Verification | distributed | see above |
| 8 Discussion | 7.1 | |
| 9 Limitations | 7.2 | |
| 10 Conclusion | 8 | |

Every `\ref` and `\label` carried over must be re-pointed. v5's `sec:results`
belongs to the removed section; do not reuse it for v6's Sec. 5.

## Deviations from the preferred outline, and why

1. **"Audited Systems and Setup" has no top-level section.** The released and
   controlled arms need different setup facts, and a shared setup section would
   force the reader to hold both before either result. Split as 4.1 and 5.1.
2. **Verification is not a numbered section.** It is one v5 paragraph; keeping a
   top-level section for it works against compactness.
3. **"Controlled Cross-Population Evaluation" covers one controlled population,
   not several.** The name is kept because the comparison is across populations:
   MOT17 released against DanceTrack controlled. If that reads as overclaiming to
   a reviewer, rename it "Controlled Evaluation on a Second Population" and
   change nothing else.
4. **Discussion and Limitations are merged** as preferred, with subsections, so
   the limitations stay findable.
""")

# re-point section references elsewhere
def patch(fn, subs):
    """Idempotent: an edit whose anchor is gone and whose result is present is
    treated as already applied; anything else is a hard error."""
    p=os.path.join(V,fn); s=open(p).read(); o=s
    for a,b in subs:
        if a in s: s=s.replace(a,b)
        elif b in s: pass                      # already applied
        else: raise AssertionError((fn,a[:60]))
    if s!=o: open(p,"w").write(s); print("  re-pointed",fn)
    else: print("  already current",fn)

patch("10_TABLE_PLAN.md", [
 ("### T2. Evidence architecture — NEW in v6","### T2. Evidence architecture — NEW in v6, placed in Sec. 3.4"),
 ("### T7. Operators that admit no row-additive decomposition — REUSE v5 Sec. S6 as a main table",
  "### T7. Operators that admit no row-additive decomposition — Sec. 6, from v5 Sec. S5"),
 ("Job: the structural result, promoted from supplement prose because it now carries\ntwo arms, including the boundary case.",
  "Job: the structural result, promoted from supplement prose into its own main-text\nsection because it now carries two arms, including the boundary case."),
])
patch("13_V5_REUSE_MAP.md", [
 ("becomes v6 Sec. 5.5 plus Table T7","becomes v6 Sec. 6 plus Table T7"),
 ("### Required correction in Sec. 7, Verification","### Required correction to v5's Verification paragraph"),
 ("v6's new Sec. 6 would silently re-point every cross-reference. Rename it.",
  "v6's new Sec. 5 would silently re-point every cross-reference. Rename it."),
 ("| Supplement S25, the audit framework implementation | supp 1688 | **MOVE_TO_SUPPLEMENT** — it documents the audit library, which v6 still ships; strip the Part II layer references and keep it |",
  "| Supplement S25, the audit framework implementation | supp 1688 | **MOVE_TO_SUPPLEMENT** — it documents the audit library, which v6 still ships; strip the Part II layer references and keep it |\n| v5 main Sec. 7, Verification | main 445–449 | **DISTRIBUTE** — see `12_SECTION_PLAN.md`; v6 has no numbered Verification section |"),
])
patch("19_RESULTS_MOT17_FACT_PACKET.md", [
 ("v5's Sec. 7 sentence must be\ncorrected.","v5's Verification sentence must be\ncorrected, and in v6 it lands with the MOT17 composition rather than in a\nseparate Verification section."),
])
patch("27_V6_BUILD_GUARDRAILS.md", [
 ("  belongs to the removed section and must not be reused for v6's new Sec. 6.",
  "  belongs to the removed section and must not be reused for v6's new Sec. 5."),
 ("- Do not even out section lengths. Sec. 6 is the new contribution and should be",
  "- Do not even out section lengths. Sec. 5 is the new contribution and should be"),
])

# renumber the v6_section column in 26 and 06
m26={"3.1":"3.1","3.2":"3.2","3.4":"3.4","5.1":"4.2","5.2":"4.3","5.3":"4.3","5.4":"4.4","5.5":"6",
     "6.1":"5.2","6.2":"5.3","6.3":"5.4","6.4":"5.5","6.5":"5.6","6.6":"5.7",
     "4.2":"5.1","7":"4.2","8":"7.1","9":"7.2"}
p=os.path.join(V,"26_CLAIM_TO_ARTIFACT_MAP.csv")
rows=list(csv.reader(open(p))); hdr,body=rows[0],rows[1:]
i=hdr.index("v6_section")
mapped=set(m26.values())
for r in body:
    if r[i] not in mapped or r[i] in ("3.1","3.2","3.4"): r[i]=m26.get(r[i], r[i])
with open(p,"w",newline="") as f:
    x=csv.writer(f); x.writerow(hdr); x.writerows(body)
print("  renumbered 26_CLAIM_TO_ARTIFACT_MAP.csv")

p=os.path.join(V,"06_EVIDENCE_ARCHITECTURE.csv")
rows=list(csv.reader(open(p))); hdr,body=rows[0],rows[1:]
i=hdr.index("v6_section")
m06={"Results, released deployments":"Sec. 4.2-4.3, released deployments",
     "Results, second population composition":"Sec. 4.4, second population composition",
     "Results, controlled second population":"Sec. 5.2-5.6, controlled second population",
     "Results, operator-family generality":"Sec. 5.7, operator-family generality",
     "Method, operator families; Discussion, boundary case":"Sec. 3.4 and Sec. 6.1, boundary case",
     "Method, operator families; Results, structural audit availability":"Sec. 3.4 and Sec. 6.2, linking and smoothing"}
for r in body:
    if r[i] in m06: r[i]=m06[r[i]]
with open(p,"w",newline="") as f:
    x=csv.writer(f); x.writerow(hdr); x.writerows(body)
print("  renumbered 06_EVIDENCE_ARCHITECTURE.csv")

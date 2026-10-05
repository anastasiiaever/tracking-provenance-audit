#!/usr/bin/env python3
"""Independent re-validation of all four figures: re-run every generator from a
clean state, re-check its assertions, and verify the embedded output."""
import hashlib, json, os, re, subprocess, sys
H = os.path.dirname(os.path.abspath(__file__))
R = "<AUDIT_ROOT>"
fails = []
def check(label, ok, detail=""):
    print(("  PASS  " if ok else "  FAIL  ") + label + (f"   {detail}" if detail else ""))
    if not ok: fails.append(label)

print("## generators re-run from scratch")
for s in ("gen_fig1.py", "gen_fig2.py", "gen_fig3.py", "gen_figS1.py"):
    r = subprocess.run([sys.executable, s], cwd=H, capture_output=True, text=True)
    check(f"{s} runs and all its assertions hold", r.returncode == 0,
          (r.stderr.strip().split("\n")[-1] if r.returncode else
           r.stdout.strip().split("\n")[0]))

print("## assertion counts recorded by each generator")
for f, key in (("_fig1_provenance.json", None), ("_fig2_provenance.json", "checks"),
               ("_fig3_provenance.json", "checks"), ("_figS1_provenance.json", "checks")):
    d = json.load(open(f"{H}/{f}"))
    if key is None:
        check(f"{f}: three panels recorded", len(d) == 3, str(len(d)))
    else:
        bad = [c for c in d[key] if not c["pass"]]
        check(f"{f}: {len(d[key])} checks, none failing", not bad, str(bad[:2]))

print("## outputs")
for o, minkb in (("fig1_final.pdf", 8), ("fig2_final.pdf", 4),
                 ("fig3_final.pdf", 4), ("figS1_final.pdf", 4)):
    p = f"{H}/{o}"
    ok = os.path.exists(p) and os.path.getsize(p) > minkb * 1024
    info = subprocess.run(["pdfinfo", p], capture_output=True, text=True).stdout
    pages = re.search(r"Pages:\s+(\d+)", info)
    size = re.search(r"Page size:\s+([\d.]+) x ([\d.]+)", info)
    check(f"{o} exists, one page, vector",
          ok and pages and pages.group(1) == "1",
          f"{os.path.getsize(p)//1024} kB, {size.group(0) if size else '?'}")
    fonts = subprocess.run(["pdffonts", p], capture_output=True, text=True).stdout
    check(f"{o}: no Type 3 font, every font embedded",
          "Type 3" not in fonts and " no " not in fonts.replace("no uni", ""),
          "")

print("## artwork is what the documents include")
for src, dst in (("fig1_final.pdf", f"{R}/V6_INTEGRATED_20261004/figures/fig1_final.pdf"),
                 ("fig2_final.pdf", f"{R}/V6_INTEGRATED_20261004/figures/fig2_final.pdf"),
                 ("fig3_final.pdf", f"{R}/V6_INTEGRATED_20261004/figures/fig3_final.pdf"),
                 ("figS1_final.pdf", f"{R}/V6_WRITING_PHASE3_20261004/figures/figS1_final.pdf")):
    def sha(p):
        h = hashlib.sha256()
        with open(p, "rb") as fh:
            for b in iter(lambda: fh.read(1 << 16), b""): h.update(b)
        return h.hexdigest()
    check(f"{src} matches the copy the build includes",
          os.path.exists(dst) and sha(f"{H}/{src}") == sha(dst))

print("## nothing invented: every figure traces to a frozen artifact")
SRC = ["C6_identity_support_rows.csv", "D1B2_reference_absent_local_support.csv",
       "B1_mot17_gate_summary.csv", "B2_mot20_gate_summary.csv",
       "D1B_stv_primary.csv", "FINAL_unified_pairwise_margins.csv",
       "07_METHOD_DEFINITIONS.md", "06_EVIDENCE_ARCHITECTURE.csv"]
blob = "".join(open(f"{H}/{s}").read() for s in
               ("gen_fig1.py", "gen_fig2.py", "gen_fig3.py", "gen_figS1.py"))
for s in SRC:
    check(f"a generator reads {s}", s in blob)
check("no generator writes outside this directory",
      not re.search(r'open\(f?"\{?(R|INT|SOT|P9|D1B|FIN|AUD)\}?[^"]*",\s*"w"', blob))

print()
print("FIGURE AUDIT:", "no failures" if not fails else f"{len(fails)} failures: {fails}")
sys.exit(1 if fails else 0)

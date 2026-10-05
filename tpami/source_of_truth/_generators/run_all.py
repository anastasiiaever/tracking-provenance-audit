"""Rebuild every V6_SOURCE_OF_TRUTH artifact from its generators, in order.

The build is staged:
  _gen1 .. _gen10            write the base artifacts
  _gen13_consolidation.py    re-applies every edit that was once made directly
                             to a generated file
  _gen11.py                  structural re-pointing to the 8-section plan
  _gen12.py                  the MOT17 added-row-range correction pass
  _gen14_audit.py            validates every table against its artifact and
                             writes 31 and 32
  _gen15_semantic.py         re-derives each prose claim's meaning from the
                             artifact and writes 33 and 34

Running this script end to end must reproduce the packet byte for byte. That is
the fidelity guarantee: no artifact is edited except through a generator.

To test fidelity, redirect V to an isolated directory -- and ASSERT that the
substitution took effect before executing. A dry run whose redirection silently
failed has written into the live directory once in this project.
"""
import subprocess, sys, os
HERE=os.path.dirname(os.path.abspath(__file__))
ORDER=[f"_gen{i}.py" for i in range(1,11)]+["_gen13_consolidation.py","_gen11.py","_gen12.py","_gen14_audit.py","_gen15_semantic.py"]
for g in ORDER:
    p=os.path.join(HERE,g)
    if not os.path.exists(p): print(f"  SKIP   {g} (absent)"); continue
    r=subprocess.run([sys.executable,p],capture_output=True,text=True)
    if r.returncode!=0:
        print(f"  FAIL   {g}\n{r.stdout}\n{r.stderr}"); sys.exit(1)
    print(f"  ok     {g}")
print("build complete")

"""Seeded entry point for the UNMODIFIED upstream OC-SORT GPR transformation.

Corrects the A3 defect where the frozen command invoked
tools/gp_interpolation.py directly and therefore bypassed the validated seeding
wrapper. Upstream source is imported, never edited. Seed and RNG controls are
exactly those exercised by the fresh-process reproducibility preflight.

argv: <oc_sort_repo> <raw_dir> <li_dir> <abs_save_dir> [seed]

SECURITY. The first argument is a path to an upstream repository, and this entry
point EXECUTES code from it: `<oc_sort_repo>/tools/gp_interpolation.py` is loaded
and run as Python, and `<oc_sort_repo>/tools` is prepended to `sys.path`. Pass
only the trusted, pinned OC-SORT checkout named in
`metadata/upstream_pipelines.csv`. Pointing this at an untrusted or unpinned
directory runs arbitrary code with the privileges of the calling process. The
path is deliberately not sanitised here: the audit must execute the upstream
source unmodified, so the trust decision belongs to the caller.
"""
from __future__ import annotations
import importlib.util, os, sys

from .gpr_wrapper import GPR_AUDIT_SEED, seed_all, environment


def main(argv=None) -> int:
    a = (argv if argv is not None else sys.argv[1:])
    repo, raw_dir, li_dir, save_dir = a[0], a[1], a[2], a[3]
    seed = int(a[4]) if len(a) > 4 else GPR_AUDIT_SEED
    for p in (raw_dir, li_dir):
        if not os.path.isdir(p):
            raise SystemExit(f"input directory missing: {p}")
    if not os.path.isabs(save_dir):
        raise SystemExit(f"save_dir must be ABSOLUTE (A3 output-path correction): {save_dir}")
    if os.path.isdir(save_dir) and os.listdir(save_dir):
        raise SystemExit(f"refusing to overwrite non-empty output directory: {save_dir}")
    os.makedirs(save_dir, exist_ok=True)

    src = os.path.join(repo, "tools", "gp_interpolation.py")
    spec = importlib.util.spec_from_file_location("upstream_gp_interpolation", src)
    mod = importlib.util.module_from_spec(spec)
    sys.path.insert(0, os.path.join(repo, "tools"))
    spec.loader.exec_module(mod)                      # upstream source, unmodified

    seed_all(seed)                                    # validated RNG controls
    print(f"[gpr_entry] seed={seed} env={environment()}", flush=True)
    # upstream signature: gp_interpolation(txt_path, save_path, reference_dir, n_min, n_dti)
    mod.gp_interpolation(raw_dir, save_dir, li_dir, n_min=30, n_dti=20)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

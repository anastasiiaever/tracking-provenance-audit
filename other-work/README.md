# Other work: not part of the TPAMI tracking paper

Everything under `other-work/` belongs to a **separate paper** on common-support
and skeleton reconstruction, audited on PoseTrack21, JTA, KITTI, NTU RGB+D and an
object-trajectory population.

It is kept here because it shares this repository's history, and moving it out
would have required rewriting that history. It is **not** part of
*Post-Processing Provenance and the Evaluated State of Tracking Submissions*, and
no claim in that paper rests on anything in this directory.

Its own verification stages still run:

```bash
python other-work/scripts/verify_controlled_arm.py
python other-work/scripts/verify_support_accounting.py
python -m pytest -q other-work/tests/
```

or, together with the tracking stages,

```bash
python scripts/verify_release.py --with-other-work
```

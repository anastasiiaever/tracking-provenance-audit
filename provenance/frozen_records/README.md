# Frozen records

These are the study's own protocol, census, eligibility and result records,
released **verbatim**. Each is byte-identical to the frozen artifact it came
from; `../RELEASE_MANIFEST.json` carries the source SHA-256 for every one.

Two things to know before reading them.

**This is a curated subset.** The study's record set is larger. Released here are
the records that carry scientific content and contain no path, host or address
from the execution environment. Left out are the command, asset and environment
manifests — they are lists of absolute paths on the authors' machine and would
publish infrastructure detail without adding evidence — and the manuscript,
figure and reviewer-response records, which are not scientific artifacts. A
record that names one of the omitted ones is not broken; the reference simply
points outside this release.

**Paths inside them are the research tree's, not this repository's.** These files
were written before the release layout existed. Where a record names a source
module — `stv.py`, `ordering.py`, `guard.py` and the rest — the file is in
`src/tracking_provenance_audit/` here. Where it names `scripts/mot_audit/...` or
`applicability_audit/...`, see `src/`. Where it names `tools/interpolation.py`,
`GSI.py`, `trackeval/...` or a `yolox_*.py` config, it is naming a file in an
**upstream** repository, not in this one.

The records were not rewritten to fix those references. A record whose bytes
changed after freezing is no longer the record that was frozen, and the whole
point of releasing them verbatim is that their digests still check.

## What is here

| record | what it fixes |
|---|---|
| `01_SOURCE_MANIFEST.json`, `01_UNIVERSE_CENSUS.*` | the 24-cell post-processing universe and the upstream commits it was read at |
| `02_PROSPECTIVE_PROTOCOL.*`, `02_PROTOCOL_MANIFEST.json` | the protocol, frozen before any prospective execution |
| `02A_*`, `02B_*` | the two protocol amendments, with what each does and does not license |
| `02_CLI_CONTRACT.md`, `03_EXECUTABLE_IMPLEMENTATION.md`, `02_LITERATURE_AUDIT_SPEC.md` | the executable contract and the literature-audit specification |
| `07_ORDERING_MATRIX.json`, `08_ORDERING_RECOMPUTATION.json` | the ordering result and its independent recomputation |
| `08_INDEPENDENT_RESULT_VERIFICATION.*` | independent verification of the MOT17 arm |
| `09A_MOT20_*` | MOT20 evaluator-native ground-truth semantics and the population manifest specification |
| `10_MOT20_EXECUTION_READINESS.*`, `10A_MOT20_READINESS_CORRECTION.*` | the eligibility ledger and the append-only amendment that raised one cell |
| `11_INVARIANT_MATRIX.json` | the invariants the implementation is required to hold |
| `13_MOT20_DEEP_*` | the executed MOT20 cell: admission result, metric result, arithmetic check |
| `14_MOT20_DEEP_INDEPENDENT_VERIFICATION.*` | independent verification of that result |

`MOT_AUDIT_ADAPTER_SPEC.md` and `MOT_AUDIT_PROTOCOL.md` are the MOT-audit
adapter and protocol specifications. In the research tree they lived under
`protocols/mot_audit/`; only their filenames were prefixed for this release.

## `controlled/`

The controlled arm's own frozen records, released the same way — byte-identical.
PoseTrack21 records 54, 55 and 56; the JTA prospective result (record 51); the
third-family evaluation result (record 45), which carries the noise-sensitivity
grid; and the KITTI hypothesis, descriptive summary and execution log.

The three KITTI records come from a tag other than the primary frozen state,
because that arm was frozen separately and its artifacts are not present at the
primary tag. `../RELEASE_MANIFEST.json` declares both source states under
`source_frozen_state`.

Some of these records mention a matched-predictor 3DPW comparison. That arm is
not part of this release; the records are published byte-identical and are not
edited to remove internal cross-references.

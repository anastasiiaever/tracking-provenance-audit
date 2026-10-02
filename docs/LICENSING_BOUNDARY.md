# Licensing boundary

This repository is released under the **MIT Licence** ([LICENSE](../LICENSE)).
This page records what that licence covers and — just as importantly — what it
does not, and the evidence behind that boundary.

## What MIT covers

Everything published in this repository. `provenance/RELEASE_MANIFEST.json`
classifies each file individually:

| class | files | what it is |
|---|---|---|
| `OWN_CODE` | 51 | the audit implementation, the verification scripts, the tests, the worked example, `conftest.py` |
| `OWN_RECORD` | 63 | the study's own frozen protocol, census, eligibility and result records, plus authored documentation and the frozen config transcriptions |
| `OWN_DERIVED_AGGREGATE` | 29 | tables derived from the study's own frozen results — counts, fractions, metric values, intervals |
| `REFERENCE_ONLY` | 3 | tables that *name* third-party corpora, pipelines and checkpoints without containing any of them |

All four classes are the authors' own work.

## What MIT does not cover

No dataset, checkpoint, tracker implementation or external evaluation tool is
redistributed here, so none of them is licensed by this repository and **no
licence claim is made over any of them**. Each is obtained from its own source
under its own terms:

- corpora — `docs/DATASETS.md` and `metadata/datasets.csv`
- checkpoints and the evaluator — `metadata/external_assets.csv`
- the eight tracker pipelines, with pinned commits — `metadata/upstream_pipelines.csv`

The released tables are aggregate counts, fractions, metric values and
intervals. They contain no image, video, annotation row or personally
identifying material. No corpus content is redistributed here; what each corpus
licence permits remains a matter between you and its distributor.

## How the boundary was established

Three independent checks, all recorded rather than assumed:

- **Provenance.** Every file's origin is in the manifest: byte-identical copies
  of the study's own frozen artifacts, a small number of recorded path
  normalisations, and files authored or derived for this release.
- **Attribution markers.** A search for `copyright`, `(c) 20`, `SPDX`, `adapted
  from`, `based on`, `ported from`, `derived from` and `taken from` across all
  released Python found no third-party attribution. (The word "license" appears
  often in `src/tracking_provenance_audit/` — it is the domain vocabulary: an
  authorization marker *licenses* a run.)
- **Imports.** The released code imports only the standard library plus `numpy`,
  `scipy`, `pytest` and `yaml`. Those are dependencies resolved at
  install time, not vendored code; none of their source is in this tree.

The eight tracker repositories and TrackEval are **read, never included**. The
audit consumes files those tools write; it does not patch, import or wrap them.

## One practical note

`provenance/frozen_records/` is released byte-identical on purpose, and
`provenance/MANIFEST.sha256` asserts it. Adding a licence header to those files
would break those digests and defeat the reason they are published verbatim.
The licence is therefore stated once, in `LICENSE` and in `README.md`, and not
repeated as per-file headers.

## Citation is separate from licence

MIT governs reuse of this repository's contents. It does not remove the citation
obligations that the corpora and the upstream methods carry in their own right.
See `CITATION.cff`.

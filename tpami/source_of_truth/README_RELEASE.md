# Source-of-truth set: two manifests, and why

`V6_SOURCE_OF_TRUTH_MANIFEST.sha256` is the **original** manifest, frozen with the
artifact set. It verifies against the originals on the research host.

`RELEASE_MANIFEST_SANITISED.sha256` is the manifest of the **published copies**.
Use this one here:

```bash
cd tpami/source_of_truth && sha256sum -c RELEASE_MANIFEST_SANITISED.sha256
```

17 of 52 files differ between the two, and all 17 differ for one
reason: they contained absolute paths from the research host, which are not
published. Those path strings were replaced by the placeholders documented in
`../PATHS.md`. No value, no record and no result was altered.

The 17 files are:

- `01_ARTIFACT_PRECEDENCE.md`
- `28_WRITING_STYLE_REFERENCE.md`
- `_generators/_gen1.py`
- `_generators/_gen10.py`
- `_generators/_gen11.py`
- `_generators/_gen12.py`
- `_generators/_gen13_consolidation.py`
- `_generators/_gen14_audit.py`
- `_generators/_gen15_semantic.py`
- `_generators/_gen2.py`
- `_generators/_gen3.py`
- `_generators/_gen4.py`
- `_generators/_gen5.py`
- `_generators/_gen6.py`
- `_generators/_gen7.py`
- `_generators/_gen8.py`
- `_generators/_gen9.py`

Every other file is byte-identical under both manifests, so the original manifest
still verifies for them. Both manifests are shipped so the substitution is
auditable rather than hidden.

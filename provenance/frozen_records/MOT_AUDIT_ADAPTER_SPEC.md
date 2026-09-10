# Generic-artifact adapter specification: MOTChallenge post-processing
Frozen 2026-08-29, before implementation. Scope: software equivalence only.

This specification introduces **no new metric, threshold, admission rule or
matching rule**. Every transformation below already exists in the frozen study
(external MOT freeze `f4084772`, record SHA-256
`ff0ce2a8cd485c5df59fd0b4906d951900ff01b60804af5a64d59a56928497bc`). The goal is
to route the *audit decision* through `applicability_audit` instead of through
the study-specific scripts that originally produced it.

## 1. What is being demonstrated

The frozen scientific outcomes were produced by `scripts/mot_audit/*`. They are
authoritative and are not recomputed, replaced or edited. The adapter must
reproduce the same audit **decisions** from the same immutable inputs, through
the generic core. Metric values remain TrackEval's; the generic core is not a
tracking evaluator and must not compute HOTA/DetA/AssA/IDF1/MOTA.

## 2. Immutable inputs

| input | source | status |
|---|---|---|
| `R0` raw tracker output | `states/<tracker>/R0/<seq>.txt`, mode 444 | read-only |
| `R2` published DTI output | `states/<tracker>/R2/<seq>.txt` | read-only |
| val-half ground truth | `TrackEval/data/gt/mot_challenge/MOT17-val_half/<seq>/gt/gt.txt` | read-only |
| frame convention | rebased `1..N`; identical for R0, R2 and GT | documented |
| DTI parameters | `n_min` 5 (ByteTrack, BoT-SORT) / 30 (OC-SORT); `n_dti` 20 | frozen |
| STV rule | per-frame one-to-one Hungarian on IoU, gate 0.5, against preprocessing-surviving pedestrian GT, frozen once on R0 | frozen |

## 3. Layer mapping onto the generic core

The core's canonical layers are used unchanged.

- **Synthesized row = target.** A row present in `R2` and absent from `R0` under
  the `(frame, tracker_id)` identity.
- **R0 row = anchor.** Rows of the same tracker id present in `R0`.
- **Layer A (structural applicability)** is decided by the core's own
  `segment` + `classify_segment`, i.e. Gate 1R. The DTI family fills interior
  gaps only, so every synthesized row is expected to classify `eligible`; the
  adapter asserts this rather than assuming it.
- **Layer C (metric/reference validity)** carries the study-specific
  **semantic-validity subcheck (STV)**. The adapter computes the four STV
  classes and passes `metric_valid[case_id] = (class == SEMANTICALLY_VALID)`
  into `audit_precomputed_results`. STV is *not* promoted into the core: it is
  study-specific, exactly as the manuscript states.
- **Layer B_m (method support)** is the post-processor's own temporal-support
  contract: a synthesized row is supported iff its gap satisfies
  `1 < gap < n_dti` and its track satisfies `n_frame > n_min`.
- **Layer D** and the admissibility certificate are produced by the core.

## 4. Required outputs

Per tracker: an input certificate over the immutable files (SHA-256, row counts,
duplicate and ordering checks); the synthesized-row identity set; the STV class
per case; the four class counts; the core's admission certificate; and the exact
counts needed to reproduce the frozen ledger.

## 5. Exact equivalence targets

| tracker | unmatched | id mismatch | reference absent | valid | total |
|---|---|---|---|---|---|
| ByteTrack | 604 | 244 | 0 | 1224 | 2072 |
| BoT-SORT | 576 | 227 | 0 | 1287 | 2090 |
| OC-SORT | 408 | 375 | 0 | 1839 | 2622 |

Equivalence is required on **case identities**, not only on counts. No tolerance
is permitted: these are integer identities and must match exactly.

## 6. StrongSORT / GSI adapter

Given immutable `S0` and `S2`, the adapter must classify the transformation by
row provenance and **refuse** the row-subset diagnostic. Expected:
`3184` added rows, `46866 / 46913` pre-existing rows coordinate-modified,
`0` dropped, and

```
ROW_SUBSET_DIAGNOSTIC = NOT_DEFINED
reason = NON_ROW_ADDITIVE_TRANSFORMATION
```

No STV classes are fabricated for GSI and no `R_1` analogue is constructed. The
justification is structural: the smoothing stage refits on the row set, so
deleting a subset of synthesized rows changes the coordinates of surviving rows.

## 7. Prohibitions

No tracker is rerun. No frozen artifact is modified. No existing invariant in
`applicability_audit` is weakened to make MOT fit. If exact equivalence fails,
the correct outcome is a diagnosis of the generic interface, not an adjustment
of the frozen science.

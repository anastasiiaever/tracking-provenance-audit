"""Secondary descriptive materiality classification (protocol Sec. 12).

Frozen: total_nonadmitted_synthesized / total_synthesized >= 0.10.
The R2-denominator companion is ALWAYS emitted alongside.
"""
from __future__ import annotations

THRESHOLD = 0.10
MATERIAL = "STV_COMPOSITION_MATERIAL"
NOT_MATERIAL = "STV_COMPOSITION_NOT_MATERIAL"
UNDEFINED = "UNDEFINED_NO_SYNTHESIZED_ROWS"


def classify(non_admitted: int, synthesized: int, r2_rows: int) -> dict:
    if synthesized == 0:
        return dict(classification=UNDEFINED,
                    fraction_of_synthesized=None,
                    fraction_of_R2_rows=(non_admitted / r2_rows) if r2_rows else None,
                    threshold=THRESHOLD, status="DESCRIPTIVE",
                    note="no synthesized rows; the conditional fraction is undefined")
    frac = non_admitted / synthesized
    return dict(
        classification=MATERIAL if frac >= THRESHOLD else NOT_MATERIAL,
        fraction_of_synthesized=frac,
        fraction_of_R2_rows=(non_admitted / r2_rows) if r2_rows else None,
        threshold=THRESHOLD, status="DESCRIPTIVE",
        note=("secondary descriptive classification; carries no significance or "
              "generalization claim. The R2 fraction is reported so a large "
              "conditional fraction is not read as a submission-wide effect."))

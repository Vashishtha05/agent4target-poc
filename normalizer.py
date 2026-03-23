
from schema import TargetEvidence


def _norm_depmap(raw: float) -> float:
    clamped = max(-1.0, min(0.0, raw))
    return round(abs(clamped), 4)

def _norm_open_targets(raw: float) -> float:
    return round(max(0.0, min(1.0, raw)), 4)

def _norm_literature(raw: float) -> float:
    import math
    if raw <= 0:
        return 0.0
    return round(min(math.log10(raw + 1) / math.log10(1001), 1.0), 4)

SOURCE_NORMALIZERS = {
    "depmap":       _norm_depmap,
    "open_targets": _norm_open_targets,
    "literature":   _norm_literature,
}

DEFAULT_NORMALIZER = lambda raw: round(max(0.0, min(1.0, float(raw))), 4)


def normalize(evidence: TargetEvidence) -> TargetEvidence:
    """
    Normalises every source in source_data to [0.0, 1.0].
    Works for any number of sources — no hardcoded source names.
    """
    for source_name, source_info in evidence.source_data.items():
        if "raw" not in source_info:
            continue
        raw = source_info["raw"]
        normalizer_fn = SOURCE_NORMALIZERS.get(source_name, DEFAULT_NORMALIZER)
        source_info["norm"] = normalizer_fn(raw)
    return evidence

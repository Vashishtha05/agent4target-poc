
from schema import TargetEvidence

TIER_WEIGHTS = {
    "Tclin": 1.0, "Tchem": 0.75, "Tbio": 0.40, "Tdark": 0.10
}

MAX_SOURCE_CONTRIB = 0.3

SOURCE_WEIGHTS = {
    "depmap":       1.0,   # direct cancer essentiality — high relevance
    "open_targets": 0.8,   # disease association — supporting signal
    "literature":   0.6,   # co-mention frequency — weakest signal
    # default for any unlisted source: 1.0
}


def score(evidence: TargetEvidence) -> TargetEvidence:

    tier_score = TIER_WEIGHTS.get(evidence.pharos_tier, 0.1)
    drug_score = min(evidence.drug_count / 20, 0.5)
    ppi_score  = min(evidence.ppi_count  / 500, 0.3)

    pharos_total = tier_score + drug_score + ppi_score  # max = 1.0+0.5+0.3 = 1.8

    source_total = 0.0
    n_sources    = 0

    for source_name, source_info in evidence.source_data.items():
        if "norm" not in source_info:
            continue  # source collected but not yet normalised — skip
        norm_val = source_info["norm"]
        weight   = SOURCE_WEIGHTS.get(source_name, 1.0)
        source_total += min(norm_val * weight, MAX_SOURCE_CONTRIB)
        n_sources += 1

    max_raw = 1.8 + (MAX_SOURCE_CONTRIB * max(n_sources, 1))

    raw = pharos_total + source_total

    if evidence.conflict_severity == "SEVERE":
        raw *= 0.85
    elif evidence.conflict_severity == "MODERATE":
        raw *= 0.92

    evidence.druggability_score = round(raw / max_raw, 3)
    return evidence

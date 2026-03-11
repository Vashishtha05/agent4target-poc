from schema import TargetEvidence

TIER_WEIGHTS = {
    "Tclin": 1.0,    # approved drugs with known mechanism
    "Tchem": 0.75,   # compounds in ChEMBL or DrugCentral
    "Tbio":  0.40,   # biological annotation only
    "Tdark": 0.10    # virtually nothing known
}

def score(evidence: TargetEvidence) -> TargetEvidence:
    """
    Aggregates all normalized signals into one druggability score.
    Max possible raw = 1.0 + 0.5 + 0.3 + 0.3 = 2.1
    """

    tier_score = TIER_WEIGHTS.get(evidence.pharos_tier, 0.1)

    drug_score = min(evidence.drug_count / 10, 0.5)

    ppi_score = min(evidence.ppi_count / 500, 0.3)

    depmap_score = min(evidence.depmap_score_normalized, 0.3)

    # Combine and normalize
    # Max raw = 1.0 + 0.5 + 0.3 + 0.3 = 2.1
    raw = tier_score + drug_score + ppi_score + depmap_score
    evidence.druggability_score = round(raw / 2.1, 3)

    return evidence
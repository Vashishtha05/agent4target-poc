# scorer.py
# Responsible for ONE thing only — compute a druggability score (0.0 → 1.0)
# Scoring logic is directly derived from DrugnomeAI paper findings:
#   - PHAROS tier = strongest categorical signal
#   - Drug count  = top interaction-based predictor
#   - PPI count   = #1 overall predictor (Boruta confirmed)

from schema import TargetEvidence

# Tier weights based on paper's Tclin/Tchem/Tbio/Tdark hierarchy
TIER_WEIGHTS = {
    "Tclin": 1.0,    # Has approved drugs with known mechanism
    "Tchem": 0.75,   # Has compounds in ChEMBL or DrugCentral
    "Tbio":  0.40,   # Has biological annotation but no drugs
    "Tdark": 0.10    # Virtually nothing known
}

def score(evidence: TargetEvidence) -> TargetEvidence:
    """
    Computes druggability score for a gene using 3 signals from the paper.
    Score is normalized to [0.0, 1.0].
    """

    # Signal 1 — Tier (categorical, from PHAROS classification)
    tier_score = TIER_WEIGHTS.get(evidence.pharos_tier, 0.1)

    # Signal 2 — Drug count (capped at 0.5 contribution)
    # Logic: more existing drugs = more validated as druggable
    # Cap prevents one signal dominating for highly-drugged genes
    drug_score = min(evidence.drug_count / 10, 0.5)

    # Signal 3 — PPI count (capped at 0.3 contribution)
    # Logic: paper proved PPI network connectivity = #1 druggability predictor
    # A gene that interacts with many proteins = sits in important pathways
    ppi_score = min(evidence.ppi_count / 500, 0.3)

    # Combine and normalize to [0, 1]
    # Max possible raw score = 1.0 + 0.5 + 0.3 = 1.8
    raw = tier_score + drug_score + ppi_score
    evidence.druggability_score = round(raw / 1.8, 3)

    return evidence
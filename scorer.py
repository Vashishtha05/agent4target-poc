# scorer.py
# V4 — aggregation is now fully generic.
#
# Ziheng's question: "how would the aggregation logic behave as more
# heterogeneous sources are added?"
#
# Answer: the scorer loops over ALL normalised signals in source_data.
# Adding Open Targets, literature, or any new source automatically
# contributes to the score — no changes to this file needed.

from schema import TargetEvidence

TIER_WEIGHTS = {
    "Tclin": 1.0, "Tchem": 0.75, "Tbio": 0.40, "Tdark": 0.10
}

# Maximum contribution any single external source can make.
# Prevents one very strong source from dominating the score.
MAX_SOURCE_CONTRIB = 0.3

# Weights for each source type — controls how much each source counts.
# New sources default to 1.0 (equal weight) unless specified here.
# Tunable as more sources are added and validated.
SOURCE_WEIGHTS = {
    "depmap":       1.0,   # direct cancer essentiality — high relevance
    "open_targets": 0.8,   # disease association — supporting signal
    "literature":   0.6,   # co-mention frequency — weakest signal
    # default for any unlisted source: 1.0
}


def score(evidence: TargetEvidence) -> TargetEvidence:
    # ── PHAROS signals (categorical — handled separately) ─────────────────────
    tier_score = TIER_WEIGHTS.get(evidence.pharos_tier, 0.1)
    drug_score = min(evidence.drug_count / 20, 0.5)
    ppi_score  = min(evidence.ppi_count  / 500, 0.3)

    pharos_total = tier_score + drug_score + ppi_score  # max = 1.0+0.5+0.3 = 1.8

    # ── External source signals (generic loop) ────────────────────────────────
    # For every source that has a normalised value, add its weighted contribution.
    # This loop works for 1 source, 3 sources, or 10 sources identically.
    source_total = 0.0
    n_sources    = 0

    for source_name, source_info in evidence.source_data.items():
        if "norm" not in source_info:
            continue  # source collected but not yet normalised — skip
        norm_val = source_info["norm"]
        weight   = SOURCE_WEIGHTS.get(source_name, 1.0)
        source_total += min(norm_val * weight, MAX_SOURCE_CONTRIB)
        n_sources += 1

    # ── Normalise denominator based on how many sources are present ───────────
    # With 1 source:  max raw = 1.8 + 0.3 = 2.1
    # With 2 sources: max raw = 1.8 + 0.6 = 2.4
    # With 3 sources: max raw = 1.8 + 0.9 = 2.7
    # This keeps the score in [0, 1] regardless of source count.
    max_raw = 1.8 + (MAX_SOURCE_CONTRIB * max(n_sources, 1))

    raw = pharos_total + source_total

    # ── Conflict penalty ──────────────────────────────────────────────────────
    if evidence.conflict_severity == "SEVERE":
        raw *= 0.85
    elif evidence.conflict_severity == "MODERATE":
        raw *= 0.92

    evidence.druggability_score = round(raw / max_raw, 3)
    return evidence

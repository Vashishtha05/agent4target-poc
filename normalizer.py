from schema import TargetEvidence

def normalize(evidence: TargetEvidence) -> TargetEvidence:
    """
    Normalizes DepMap score to 0-1 scale.
    PHAROS signals are handled directly in scorer.py
    """

    if evidence.depmap_score is not None:
        raw = evidence.depmap_score

        # Clamp to expected DepMap range [-2.0, 0.0]
        raw = max(-2.0, min(0.0, raw))

        # Flip and normalize:
        # -2.0 → 1.0  (highly essential for cancer survival → high score)
        #  0.0 → 0.0  (not essential → low score)
        evidence.depmap_score_normalized = round(abs(raw) / 2.0, 4)
    else:
        # Gene not in DepMap — contribute 0 to final score
        evidence.depmap_score_normalized = 0.0

    return evidence
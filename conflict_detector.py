# conflict_detector.py
# V4 — conflict detection works across any sources, not just PHAROS + DepMap.
#
# Ziheng's question: "how should the system handle conflicting signals
# across them [heterogeneous sources]?"
#
# Three conflict types:
#
#   Type 1 — Mechanism conflict (PHAROS-specific)
#     a) Extracellular target — DepMap cannot measure this mechanism
#     b) Approved target but cancer cells don't depend on it (DepMap)
#
#   Type 2 — Cross-source direction conflict (generic — any source pair)
#     Source A says strongly important, Source B says not essential.
#     Detected using DIRECTION not magnitude — prevents flagging genes
#     where both sources agree directionally but differ in scale.
#     Example: OT=0.91 (disease-associated) + DepMap=-0.039 (not essential)
#     → genuinely conflicting: the gene matters clinically but not in vitro.
#
#   Type 3 — Novel opportunity (Tdark + strong DepMap essentiality)
#     Not a conflict — an opportunity flag.

from schema import TargetEvidence

# Secreted/extracellular targets whose approved drugs work outside cancer cells.
EXTRACELLULAR_TARGETS = {
    "TNF", "IL6", "IL1B", "VEGFA", "VEGFB",
    "IL2", "IL17A", "IFNG", "TGFB1",
}

# Cross-source conflict rules.
# Each rule: (source_high, source_low, high_threshold, low_threshold, label)
# A conflict fires when source_high norm > high_threshold
# AND source_low norm < low_threshold simultaneously.
# This catches DIRECTION conflicts, not mere magnitude differences.
CROSS_SOURCE_RULES = [
    # Disease-associated (OT) but not cancer-cell-essential (DepMap)
    # OT > 0.65 means strongly associated with disease
    # DepMap < 0.05 means cancer cells don't depend on it (raw > -0.05)
    ("open_targets", "depmap",  0.65, 0.05,
     "Disease-associated (Open Targets) but not cancer-essential (DepMap)"),

    # Cancer-essential (DepMap) but rarely mentioned in literature
    # Suggests a poorly-studied but functionally important gene
    ("depmap", "literature",    0.50, 0.10,
     "Cancer-essential (DepMap) but sparse literature evidence"),
]


def detect_conflicts(evidence: TargetEvidence) -> TargetEvidence:
    tier = evidence.pharos_tier
    gene = evidence.gene_symbol

    # ── Type 1a: Extracellular/cytokine target ────────────────────────────────
    if tier == "Tclin" and gene in EXTRACELLULAR_TARGETS:
        evidence.conflict_flag     = (
            "MODERATE: Extracellular target — "
            "DepMap cell-autonomous signal does not apply"
        )
        evidence.conflict_severity = "MODERATE"
        return evidence

    # ── Type 1b: Approved target, not cancer-essential ────────────────────────
    if "depmap" in evidence.source_data:
        depmap_raw = evidence.source_data["depmap"]["raw"]
        if tier == "Tclin" and depmap_raw > -0.05:
            evidence.conflict_flag     = (
                f"SEVERE: Approved target but not cancer-essential "
                f"(DepMap={depmap_raw:+.3f})"
            )
            evidence.conflict_severity = "SEVERE"
            return evidence

    # ── Type 2: Cross-source direction conflict ───────────────────────────────
    # Checks every defined source pair — works for 2, 3, or N sources.
    for src_high, src_low, hi_thresh, lo_thresh, label in CROSS_SOURCE_RULES:
        norm_high = evidence.source_data.get(src_high, {}).get("norm")
        norm_low  = evidence.source_data.get(src_low,  {}).get("norm")

        if norm_high is None or norm_low is None:
            continue  # one or both sources not present — skip

        if norm_high > hi_thresh and norm_low < lo_thresh:
            evidence.conflict_flag = (
                f"MODERATE: {label} "
                f"({src_high}={norm_high:.2f}, {src_low}={norm_low:.2f})"
            )
            evidence.conflict_severity = "MODERATE"
            return evidence

    # ── Type 3: Novel opportunity ─────────────────────────────────────────────
    if "depmap" in evidence.source_data:
        depmap_raw = evidence.source_data["depmap"]["raw"]
        if tier == "Tdark" and depmap_raw < -0.5:
            evidence.conflict_flag = (
                f"NOTE: Understudied protein but strongly cancer-essential "
                f"(DepMap={depmap_raw:+.3f}) — potential novel target"
            )
            evidence.conflict_severity = "NOTE"
            return evidence

    # ── No conflict ───────────────────────────────────────────────────────────
    evidence.conflict_flag     = "None (Complementary)"
    evidence.conflict_severity = "NONE"
    return evidence

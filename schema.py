# schema.py
# Defines the structure of evidence collected for a single gene target.
# Think of this as a "form" — every gene gets the same fields filled in.

from dataclasses import dataclass
from typing import Optional

@dataclass
class TargetEvidence:
    # --- Identity ---
    gene_symbol: str           # Short name e.g. "EGFR"
    gene_name: str             # Full name e.g. "Epidermal Growth Factor Receptor"

    # --- Evidence from PHAROS (3 signals paper proved matter most) ---
    pharos_tier: str           # Tclin / Tchem / Tbio / Tdark
                               # Tclin = approved drugs exist (most druggable)
                               # Tdark = virtually unknown (least druggable)

    drug_count: int            # How many drugs already target this gene
    ppi_count: int             # How many proteins this gene interacts with
                               # (Paper's #1 predictor of druggability)

    # --- Computed by scorer ---
    druggability_score: float  # Final score 0.0 → 1.0
    rank: Optional[int] = None # Assigned after all genes are scored
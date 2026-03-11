from dataclasses import dataclass, field
from typing import Optional

@dataclass
class TargetEvidence:
    gene_symbol: str
    gene_name: str

    pharos_tier: str           
    drug_count: int            
    ppi_count: int             

    # --- DepMap signal ---
    depmap_score: Optional[float] = None

    depmap_score_normalized: float = 0.0

    # --- Computed ---
    druggability_score: float = 0.0
    rank: Optional[int] = None
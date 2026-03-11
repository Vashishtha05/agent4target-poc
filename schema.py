from dataclasses import dataclass
from typing import Optional

@dataclass
class TargetEvidence:
    # --- Identity ---
    gene_symbol: str           
    gene_name: str            

    # --- Evidence from PHAROS (3 signals paper proved matter most) ---
    pharos_tier: str          
                               

    drug_count: int           
    ppi_count: int             
                              

    # --- Computed by scorer ---
    druggability_score: float  # Final score 0.0 → 1.0
    rank: Optional[int] = None # Assigned after all genes are scored

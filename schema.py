from dataclasses import dataclass
from typing import Optional

@dataclass
class TargetEvidence:
    
    gene_symbol: str           
    gene_name: str            

    
    pharos_tier: str          
                               

    drug_count: int           
    ppi_count: int             
                              

    # --- Computed by scorer ---
    druggability_score: float  # Final score 0.0 → 1.0
    rank: Optional[int] = None 

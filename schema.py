from dataclasses import dataclass, field
from typing import Optional

@dataclass
class TargetEvidence:
    gene_symbol: str
    gene_name: str

    pharos_tier: str           
    drug_count: int            
    ppi_count: int             

    # Extensible storage for any number of heterogeneous sources
    # Eliminates hardcoded fields so new databases can be added effortlessly.
    source_data: dict = field(default_factory=dict)
    
    # Tracks conflicting signals dynamically
    conflict_flag: str = "None"

    # Type-safe severity — used by scorer instead of string matching.
    # Values: "NONE", "NOTE", "MODERATE", "SEVERE"
    conflict_severity: str = "NONE"

    # --- Computed ---
    druggability_score: float = 0.0
    rank: Optional[int] = None
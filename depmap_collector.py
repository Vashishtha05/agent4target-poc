import pandas as pd
import os
from schema import TargetEvidence

DEPMAP_FILE = "CRISPRGeneEffect.csv"
_depmap_data = None

def _load_depmap() -> pd.DataFrame:
    global _depmap_data
    if _depmap_data is not None:
        return _depmap_data

    if not os.path.exists(DEPMAP_FILE):
        print(f"  [DEPMAP] File not found: {DEPMAP_FILE}")
        return None

    print("  [DEPMAP] Loading dataset (this takes a moment)...")
    df = pd.read_csv(DEPMAP_FILE, index_col=0)
    df.columns = [col.split(" (")[0] for col in df.columns]

    _depmap_data = df
    return _depmap_data

def enrich(evidence: TargetEvidence) -> TargetEvidence:
    df = _load_depmap()
    if df is None:
        return evidence

    gene = evidence.gene_symbol
    if gene not in df.columns:
        return evidence

    # Using median instead of mean to be robust against outlier cell lines
    median_score = df[gene].median()
    
    evidence.source_data["depmap"] = {
        "raw": round(float(median_score), 4)
    }

    return evidence
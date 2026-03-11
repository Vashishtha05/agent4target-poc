import pandas as pd
import os
from schema import TargetEvidence

DEPMAP_FILE = "CRISPRGeneEffect.csv"

# Cache the loaded dataframe so we don't reload for every gene
_depmap_data = None

def _load_depmap() -> pd.DataFrame:
    """
    Loads DepMap CSV once and caches it in memory.
    DepMap format: rows = cell lines, columns = genes (e.g. "EGFR (1956)")
    """
    global _depmap_data

    if _depmap_data is not None:
        return _depmap_data

    if not os.path.exists(DEPMAP_FILE):
        print(f"  [DEPMAP] File not found: {DEPMAP_FILE}")
        print(f"  [DEPMAP] Download from: https://depmap.org/portal/download/all/")
        return None

    print("  [DEPMAP] Loading dataset (this takes a moment)...")
    df = pd.read_csv(DEPMAP_FILE, index_col=0)

    df.columns = [col.split(" (")[0] for col in df.columns]

    _depmap_data = df
    print(f"  [DEPMAP] Loaded. {df.shape[0]} cell lines, {df.shape[1]} genes.")
    return _depmap_data


def enrich(evidence: TargetEvidence) -> TargetEvidence:
    """
    Adds DepMap dependency score to an existing TargetEvidence object.
    Called after pharos_collector.collect() fills the PHAROS fields.
    Returns same object with depmap_score filled in.
    """
    df = _load_depmap()

    if df is None:
        # DepMap file not available — skip silently
        return evidence

    gene = evidence.gene_symbol

    if gene not in df.columns:
        print(f"  [DEPMAP] '{gene}' not found in dataset.")
        evidence.depmap_score = None
        return evidence

    # Mean dependency score across all cancer cell lines
    mean_score = df[gene].mean()
    evidence.depmap_score = round(float(mean_score), 4)

    return evidence
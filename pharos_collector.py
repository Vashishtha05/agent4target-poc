import requests
from schema import TargetEvidence

PHAROS_API = "https://pharos-api.ncats.io/graphql"

QUERY = """
query fetchTarget($sym: String!) {
  target(q: {sym: $sym}) {
    name
    sym
    tdl
    ligandCounts {
      name
      value
    }
    ppiCounts {
      name
      value
    }
  }
}
"""

def _extract_count(counts: list, preferred_name: str) -> int:
    if not counts:
        return 0
    for item in counts:
        if item.get("name", "").lower() == preferred_name.lower():
            return item.get("value", 0) or 0
    return max((item.get("value", 0) or 0) for item in counts)

def collect(gene_symbol: str) -> TargetEvidence:
    """
    Fetches PHAROS evidence for a single gene.
    Returns TargetEvidence with PHAROS fields filled.
    DepMap fields left as None — filled by depmap_collector.
    """
    try:
        response = requests.post(
            PHAROS_API,
            json={
                "query": QUERY,
                "variables": {"sym": gene_symbol}
            },
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()

        target = data.get("data", {}).get("target")
        if not target:
            print(f"  [PHAROS] '{gene_symbol}' not found. Skipping.")
            return None

        ligand_counts = target.get("ligandCounts") or []
        ppi_counts    = target.get("ppiCounts") or []

        return TargetEvidence(
            gene_symbol = target["sym"],
            gene_name   = target["name"],
            pharos_tier = target["tdl"],
            drug_count  = _extract_count(ligand_counts, "drug"),
            ppi_count   = _extract_count(ppi_counts, "Total"),
        )

    except requests.exceptions.RequestException as e:
        print(f"  [PHAROS ERROR] '{gene_symbol}': {e}")
        return None
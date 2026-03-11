# pipeline.py
# The main entry point. Runs the full collect → score → rank pipeline.
# This is what Ziheng's "structured pipeline" looks like in code.

from collector import collect
from scorer import score

# Test genes — mix of well-known druggable (Tclin) and less studied targets
# Chosen to demonstrate score spread across tiers
GENES = ["EGFR", "BRAF", "TP53", "TNF", "IL6", "VEGFA", "BRCA1"]

def run_pipeline(genes: list) -> list:
    """
    Full pipeline:
      1. Collect — fetch evidence from PHAROS for each gene
      2. Score   — compute druggability score per gene
      3. Rank    — sort by score descending
    """
    results = []

    print("\n Collecting evidence from PHAROS...")
    print("-" * 40)

    for gene in genes:
        print(f"  Fetching: {gene}")

        # Step 1 — Collect
        evidence = collect(gene)
        if evidence is None:
            continue

        # Step 2 — Score
        evidence = score(evidence)
        results.append(evidence)

    # Step 3 — Rank
    results.sort(key=lambda x: x.druggability_score, reverse=True)
    for i, r in enumerate(results, 1):
        r.rank = i

    return results


def print_results(results: list):
    """Prints ranked results as a clean table."""

    if not results:
        print("\nNo results available. All fetches failed or returned no data.\n")
        return

    print("\n RANKED DRUGGABILITY SCORES")
    print("=" * 65)
    print(f"{'Rank':<6} {'Gene':<10} {'Tier':<8} {'Drugs':<8} {'PPI':<8} {'Score':<8}")
    print("-" * 65)

    for r in results:
        print(
            f"{r.rank:<6} "
            f"{r.gene_symbol:<10} "
            f"{r.pharos_tier:<8} "
            f"{r.drug_count:<8} "
            f"{r.ppi_count:<8} "
            f"{r.druggability_score:<8}"
        )

    print("=" * 65)
    print(f"\n Top target: {results[0].gene_symbol} "
          f"(Score: {results[0].druggability_score})\n")


if __name__ == "__main__":
    results = run_pipeline(GENES)
    print_results(results)
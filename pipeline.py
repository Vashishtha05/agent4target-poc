# pipeline.py
# Main entry point. Runs the full pipeline:
# Collect (PHAROS) → Enrich (DepMap) → Normalize → Score → Rank

from pharos_collector import collect
from depmap_collector import enrich
from normalizer import normalize
from scorer import score

GENES = ["EGFR", "BRAF", "TP53", "TNF", "IL6", "VEGFA", "BRCA1"]

def run_pipeline(genes: list) -> list:
    results = []

    print("\n Running Agent4Target Pipeline")
    print("=" * 50)

    for gene in genes:
        print(f"\n Processing: {gene}")

        # Step 1 — Collect from PHAROS
        print(f"  Fetching PHAROS...")
        evidence = collect(gene)
        if evidence is None:
            continue

        # Step 2 — Enrich with DepMap
        print(f"  Fetching DepMap...")
        evidence = enrich(evidence)

        # Step 3 — Normalize signals
        evidence = normalize(evidence)

        # Step 4 — Score
        evidence = score(evidence)
        results.append(evidence)

    # Step 5 — Rank
    results.sort(key=lambda x: x.druggability_score, reverse=True)
    for i, r in enumerate(results, 1):
        r.rank = i

    return results


def print_results(results: list):
    if not results:
        print("\n No results returned.\n")
        return

    print("\n\n FINAL RANKED DRUGGABILITY SCORES")
    print("=" * 80)
    print(f"{'Rank':<6} {'Gene':<10} {'Tier':<8} {'Drugs':<8} "
          f"{'PPI':<8} {'DepMap':<10} {'Score':<8}")
    print("-" * 80)

    for r in results:
        depmap_display = (
            f"{r.depmap_score:.3f}"
            if r.depmap_score is not None
            else "N/A"
        )
        print(
            f"{r.rank:<6} "
            f"{r.gene_symbol:<10} "
            f"{r.pharos_tier:<8} "
            f"{r.drug_count:<8} "
            f"{r.ppi_count:<8} "
            f"{depmap_display:<10} "
            f"{r.druggability_score:<8}"
        )

    print("=" * 80)
    print(f"\n Top target: {results[0].gene_symbol} "
          f"(Score: {results[0].druggability_score})")
    print(f" DepMap most dependent: "
          f"{min(results, key=lambda x: x.depmap_score or 0).gene_symbol}\n")


if __name__ == "__main__":
    results = run_pipeline(GENES)
    print_results(results)
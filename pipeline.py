from pharos_collector import collect
from depmap_collector import enrich
from normalizer import normalize
from conflict_detector import detect_conflicts
from scorer import score

GENES = ["EGFR", "BRAF", "TP53", "TNF", "IL6", "VEGFA", "BRCA1"]

def run_pipeline(genes: list) -> list:
    results = []
    print("\n Running Agent4Target Pipeline (Extensible & Conflict-Aware)")
    print("=" * 75)

    for gene in genes:
        print(f" Processing: {gene}")
        evidence = collect(gene)
        if evidence is None:
            continue

        try:
            evidence = enrich(evidence)
            evidence = normalize(evidence)
            evidence = detect_conflicts(evidence)
            evidence = score(evidence)
        except Exception as e:
            print(f"  [ERROR] {gene}: {e}")
            continue
        
        results.append(evidence)

    results.sort(key=lambda x: x.druggability_score, reverse=True)
    for i, r in enumerate(results, 1):
        r.rank = i

    return results

def print_results(results: list):
    if not results:
        print("\n No results returned.\n")
        return

    print("\n\n FINAL RANKED DRUGGABILITY SCORES")
    print("=" * 115)
    print(f"{'Rank':<5} {'Gene':<8} {'Tier':<7} {'Score':<7} {'Conflict Status'}")
    print("-" * 115)

    for r in results:
        print(f"{r.rank:<5} {r.gene_symbol:<8} {r.pharos_tier:<7} {r.druggability_score:<7} {r.conflict_flag}")
    print("=" * 115)

if __name__ == "__main__":
    results = run_pipeline(GENES)
    print_results(results)
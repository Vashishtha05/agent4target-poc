# Agent4Target — Evidence Aggregation POC

A proof-of-concept pipeline for drug target prioritisation using multiple biomedical evidence sources. Built iteratively as part of a GSoC 2026 proposal for the [Agent4Target project](https://ucsc-ospo.github.io/project/osre26/uci/agent4target/) (UC OSPO / UC Irvine).

---

## What This Does

Takes a list of gene names and ranks them by druggability score using evidence from multiple biomedical databases. Each source is an independent collector module. The normalizer, scorer, and conflict detector all work generically — adding a new source requires writing one new collector file and one line in the normalizer. Nothing else changes..

```
PHAROS Collector ──→ ┐
                     ├──→ Normalizer ──→ Conflict Detector ──→ Scorer ──→ Ranked Output
DepMap Collector ──→ ┘
```

---

## Sample Output (V4 — Real Run, 1186 Cell Lines)

```
Rank  Gene     Tier    Score   Conflict Status
─────────────────────────────────────────────────────────────────────────────────────
1     EGFR     Tclin   0.920   None (Complementary)
2     BRAF     Tclin   0.803   None (Complementary)
3     VEGFA    Tclin   0.718   MODERATE: Extracellular target — DepMap cell-autonomous signal does not apply
4     TNF      Tclin   0.711   MODERATE: Extracellular target — DepMap cell-autonomous signal does not apply
5     BRCA1    Tchem   0.643   None (Complementary)
6     IL6      Tclin   0.613   MODERATE: Extracellular target — DepMap cell-autonomous signal does not apply
7     TP53     Tchem   0.500   None (Complementary)
```

---

## V4 — What Changed From V2

**V2** collected PHAROS + DepMap and scored them with a fixed formula. Adding a new source required editing the scorer by hand.

**V4** answers two questions Ziheng raised after reviewing V2:

### 1. How does the aggregation handle more heterogeneous sources?

The scorer now loops over every source in `source_data` automatically:

```python
# scorer.py — works for 2 sources, 3 sources, or 10
for source_name, source_info in evidence.source_data.items():
    if "norm" not in source_info:
        continue
    weight = SOURCE_WEIGHTS.get(source_name, 1.0)
    source_total += min(source_info["norm"] * weight, MAX_SOURCE_CONTRIB)
```

The normalizer maps each source to [0, 1] using a per-source rule:

```python
# normalizer.py — add one line per new source
SOURCE_NORMALIZERS = {
    "depmap":       _norm_depmap,        # clamp [-1, 0] → [0, 1]
    "open_targets": _norm_open_targets,  # already [0, 1] — pass through
    "literature":   _norm_literature,    # log-scale, cap at 1000 publications
}
```

Adding Open Targets as a third source: write `open_targets_collector.py`, add one entry to `SOURCE_NORMALIZERS`, add one line to `pipeline.py`. `scorer.py`, `schema.py`, `conflict_detector.py` — untouched.

### 2. How does the system handle conflicting signals?

The conflict detector distinguishes three biologically grounded cases:

**Type 1 — Extracellular/mechanism conflict**
An approved drug exists (Tclin) but the gene product is secreted — cancer cells don't depend on it in a cell-autonomous way. DepMap measures knockout in isolated cell lines and cannot capture extracellular mechanisms. TNF, VEGFA, and IL6 all fall here. Flagged MODERATE.

**Type 2 — Cross-source direction conflict (generic)**
Two sources measuring overlapping biology give opposite signals. Defined as a rule table — adding a new source pair takes one line:

```python
# conflict_detector.py
CROSS_SOURCE_RULES = [
    # Disease-associated but not cancer-cell-essential
    ("open_targets", "depmap", 0.65, 0.05,
     "Disease-associated (Open Targets) but not cancer-essential (DepMap)"),

    # Cancer-essential but poorly studied in literature
    ("depmap", "literature", 0.50, 0.10,
     "Cancer-essential (DepMap) but sparse literature evidence"),
]
```

**Type 3 — Novel opportunity**
Understudied protein (Tdark) but strongly cancer-essential (DepMap < −0.5). Not a conflict — flagged as a potential target opportunity.

---

## Key Findings

**Adding DepMap broke a four-way tie.** EGFR, BRAF, TNF, and VEGFA were all scoring 1.0 on PHAROS tier alone. DepMap separated them.

**BRCA1 ranks above TP53.** BRCA1 has a DepMap median of −0.420 across 1186 cancer cell lines — moderately essential. TP53 sits at +0.201 — cancer cells do not depend on it because most lines have already lost TP53 function. A purely literature-based ranking would place TP53 higher due to its 1985 protein interactions. DepMap corrects this.

**Extracellular targets are flagged.** TNF, VEGFA, and IL6 all have approved drugs but DepMap scores near zero. Their drugs work via immune or vascular mechanisms, not by killing cancer cells directly. The conflict detector catches all three consistently.

**Median not mean.** DepMap uses median dependency across cell lines. Mean was being pulled down by outlier cell lines with extreme dependency. EGFR mean = −0.241, median = −0.133.

---

## Scoring Logic

```
Score = (pharos_signals + Σ source_contributions) / max_raw
```

`max_raw` scales with the number of sources present, keeping the score in [0, 1] regardless of how many sources are added.

**PHAROS signals:**

| Signal | Max Contribution | Notes |
|---|---|---|
| PHAROS tier | 1.0 | Strongest categorical druggability signal |
| Drug count | 0.5 | Capped at 20 drugs to differentiate highly targeted genes |
| PPI count | 0.3 | Network centrality — capped to prevent undruggable hub proteins (e.g. TP53) from scoring high |

**External sources (generic — any source contributes automatically once normalised):**

| Source | Weight | Normalisation |
|---|---|---|
| DepMap | 1.0 | Clamp [−1, 0] → [0, 1] |
| Open Targets | 0.8 | Already [0, 1] — pass through |
| Literature | 0.6 | Log-scale, cap at 1000 publications |

**Conflict penalties:**

| Severity | Multiplier |
|---|---|
| SEVERE | × 0.85 |
| MODERATE | × 0.92 |

---

## PHAROS Tiers

| Tier | Meaning | Weight |
|---|---|---|
| Tclin | Approved drugs with known mechanism | 1.0 |
| Tchem | Compounds in ChEMBL or DrugCentral | 0.75 |
| Tbio | Biological annotation only, no drugs | 0.40 |
| Tdark | Virtually nothing known | 0.10 |

---

## Project Structure

```
agent4target-poc/
├── schema.py              # TargetEvidence dataclass — source_data dict is N-source extensible
├── pharos_collector.py    # PHAROS GraphQL API — tier, drug count, PPI count
├── depmap_collector.py    # DepMap CRISPR CSV — median dependency across 1186 cell lines
├── normalizer.py          # Per-source normalisation rules — add one line per new source
├── conflict_detector.py   # Biologically grounded conflict detection — CROSS_SOURCE_RULES table
├── scorer.py              # Generic aggregation loop — works for any number of sources
├── pipeline.py            # collect → normalise → detect → score → rank
└── CRISPRGeneEffect.csv   # DepMap 25Q3 snapshot (not tracked in git — ~500MB)
```

---

## Adding a New Evidence Source

To add Open Targets as a third source:

**1. Write the collector** (`open_targets_collector.py`, ~40 lines):
```python
def enrich(evidence: TargetEvidence) -> TargetEvidence:
    score = fetch_ot_score(evidence.gene_symbol)
    evidence.source_data["open_targets"] = {"raw": score}
    return evidence
```

**2. Register the normaliser** (one line in `normalizer.py`):
```python
"open_targets": _norm_open_targets,
```

**3. Add to pipeline** (one line in `pipeline.py`):
```python
evidence = ot_collector.enrich(evidence)
```

`scorer.py`, `schema.py`, `conflict_detector.py` — untouched.

---

## Setup

```bash
pip install requests pandas

# Download DepMap 25Q3 CRISPR gene effect file:
# https://depmap.org/portal/download/all/ → CRISPRGeneEffect.csv

python pipeline.py
```

---

## Mentor Exchange

Built iteratively based on feedback from Ziheng Duan (UC Irvine):

- **V1** — PHAROS only. Ziheng suggested adding DepMap and confirmed modular collector/scorer architecture.
- **V2** — Added DepMap. Ziheng confirmed local snapshot for reproducibility and noted: *"It would be interesting to see how easily additional sources can be plugged in."*
- **V4** — Generic aggregation and conflict detection across N sources. Adding a new source now requires one new file and two lines.

---

## Inspiration

Scoring logic and source selection derived from:
*DrugnomeAI is an ensemble machine-learning framework for predicting druggability of candidate drug targets.* Communications Biology, 2022.
https://doi.org/10.1038/s42003-022-04245-4

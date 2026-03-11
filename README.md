# Agent4Target — Evidence Aggregation POC

A proof-of-concept pipeline for drug target scoring using multiple biomedical evidence sources. Built as part of a GSoC 2026 proposal for the [Agent4Target project](https://ucsc-ospo.github.io/project/osre26/uci/agent4target/) (UC OSPO / UC Irvine).

---

## What This Does

Takes a list of gene names and ranks them by druggability score using two evidence sources:

- **PHAROS** — NIH database classifying every human gene by druggability tier
- **DepMap** — Broad Institute CRISPR dataset showing cancer cell gene dependencies

```
PHAROS Collector ──→ ┐
                     ├──→ Normalizer ──→ Scorer ──→ Ranked Output
DepMap Collector ──→ ┘
```

Each source is a separate collector module. Adding a new source (e.g. Open Targets) requires only writing a new collector — the normalizer, scorer, and pipeline don't change.

---

## Sample Output 
<img width="600" height="273" alt="image" src="https://github.com/user-attachments/assets/f7ee8acd-ed30-429e-b4b2-0796138e80b6" />
---

## What I Noticed

Adding DepMap differentiated genes that PHAROS alone couldn't 
separate — EGFR, BRAF, TNF and VEGFA were all scoring 1.0 
before DepMap was added.

Most interesting: BRCA1 moved above TP53 once DepMap was 
factored in. BRCA1 has a mean dependency score of -0.444 
across cancer cell lines while TP53 sits at +0.373.

---

## Scoring Logic

Each gene is scored on 4 signals derived from the DrugnomeAI paper's Boruta feature analysis:

| Signal | Source | Max Contribution | Reasoning |
|---|---|---|---|
| PHAROS tier | PHAROS | 1.0 | Strongest categorical druggability signal |
| Drug count | PHAROS | 0.5 | Validated therapeutic precedent |
| PPI count | PHAROS | 0.3 | #1 network predictor (paper confirmed) |
| Dependency | DepMap | 0.3 | Functional cancer evidence |

```
Score = (tier + drug + ppi + depmap) / 2.1
```

---

## PHAROS Tiers Explained

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
├── schema.py              # TargetEvidence dataclass — shared data structure
├── pharos_collector.py    # Fetches evidence from PHAROS GraphQL API (live)
├── depmap_collector.py    # Reads DepMap CRISPR CSV (local snapshot)
├── normalizer.py          # Converts raw signals to 0-1 scale
├── scorer.py              # Aggregates normalized signals into final score
├── pipeline.py            # Main entry point — runs full collect→score→rank
└── CRISPRGeneEffect.csv   # DepMap dataset (not tracked in git)
```

Each file has one responsibility. Adding a new evidence source = add one new collector file. Nothing else changes.

---

## Setup

```bash
# Install dependencies
pip install requests pandas

# Add DepMap dataset (not included due to file size)
# Download CRISPRGeneEffect.csv from:
# https://depmap.org/portal/download/all/ → DepMap Public 25Q3

# Run pipeline
python pipeline.py
```

---

## Notes

Kept collector and scorer as separate modules so adding a new 
source means writing one new file.

DepMap is loaded from a local file rather than a live API for 
reproducibility — same input should always give same output.

---

## Inspiration

Scoring logic and architecture derived from:
*DrugnomeAI is an ensemble machine-learning framework for predicting druggability of candidate drug targets.* Communications Biology, 2022.
https://doi.org/10.1038/s42003-022-04245-4


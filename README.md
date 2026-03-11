# Agent4Target — Minimal Evidence Aggregation POC

A proof-of-concept pipeline for drug target scoring using PHAROS
as the evidence source. Built as part of GSoC 2026 proposal for
the Agent4Target project (UC OSPO / UC Irvine).

## Pipeline

```
Collect (PHAROS API) → Score (3 signals) → Rank (0.0 → 1.0)
```

## Evidence Schema

Each gene is represented by 3 fields derived from DrugnomeAI
paper's Boruta feature analysis:

- PHAROS tier (Tclin/Tchem/Tbio/Tdark)
- Drug interaction count
- Protein-protein interaction count

## Run

```bash
pip install requests
python pipeline.py
```
## Sample Output 
<img width="763" height="470" alt="image" src="https://github.com/user-attachments/assets/69affb8e-1f0c-49a4-937a-c74ed82eff51" />

## Inspiration

Scoring logic derived from:

> DrugnomeAI: An ensemble ML framework for predicting druggability
> of candidate drug targets. Raies et al., Communications Biology 2022.

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
<img width="695" height="552" alt="image" src="https://github.com/user-attachments/assets/17a07c60-3b2f-4f0b-a5c8-399f74aedebf" />


## Inspiration

Scoring logic derived from:

DrugnomeAI: An ensemble ML framework for predicting druggability of candidate drug targets.

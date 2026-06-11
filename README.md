# wsi-registry

Lightweight registry for tracking WSI collections, cohort metadata, and split lineage. Designed for computational pathology workflows that need reproducible data bookkeeping without a heavy database.

## Features

- `SlideRecord` — per-slide metadata: slide ID, cohort, label, institution (TSS), split assignment
- `SlideRegistry` — in-memory registry backed by a Parquet/CSV manifest; add, query, export
- `SplitLineage` — record which freeze hash each split was generated from; prevent silent re-runs
- `CohortSummary` — per-cohort label counts, institution distribution, split balance check

## Install

```bash
pip install wsi-registry
```

## Usage

```python
from wsi_registry import SlideRegistry, SplitLineage

reg = SlideRegistry.from_csv("manifest.csv")
train_slides = reg.query(split="train", cohort="BRCA")

lineage = SplitLineage("splits/split_metadata.json")
lineage.verify(freeze_hash="abc123def456")
```

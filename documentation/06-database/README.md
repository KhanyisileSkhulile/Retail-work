# M07-01 — Define Database Entities and Data Requirements

## Purpose
Logical database schema for Retail-X-AI, based on:
- `dataset/raw/retail_store_inventory.csv` (73,100 rows × 15 columns)
- M02-04 Data Dictionary
- M02-05 Forecasting target & leakage risks

## Contents
| File | Description |
|------|-------------|
| `README.md` | This file |
| `erd_diagram.png` | Entity-Relationship Diagram (exported from dbdiagram.io) |
| `schema.sql` | CREATE TABLE statements + constraints + indexes |
| `data_requirements.md` | Full data requirements specification |
| `sample_queries.sql` | 8 analytical queries demonstrating usability |

## Entities Identified (6)
| # | Entity | Rows | Purpose |
|---|--------|------|---------|
| 1 | Category | 5 | Product groups |
| 2 | Region | 4 | Geographic territories |
| 3 | Store | 5 | Retail locations |
| 4 | Product | 20 | Products sold |
| 5 | Date_Dim | 731 | Daily calendar dimension |
| 6 | Inventory_Record | 73,100 | Daily fact table |

## Dependency Status
| Task | Status | Impact |
|------|--------|--------|
| M02-04 — Data Dictionary |  Read | Types, ranges, quality issues confirmed |
| M02-05 — Forecasting target & leakage |  Read | Target column identified |
| M04-01 — AI model design |  Pending | §3.7 feature refinement deferred |

## Known Data Quality Issues
- `Demand Forecast` contains **673 negative values** (min = -9.99).
  Must be cleaned to `>= 0` before ingestion. Enforced by CHECK constraint.
- Dataset is **synthetic** (Kaggle source, see `dataset/raw/DATASET-SOURCE.md`).
- `Holiday/Promotion` is the same column as `Promotion` in the Kaggle source.

## Assignee
@KhanyisileSkhulile614

## Status
-  Entities identified
-  ERD drawn (to be exported)
-  Schema written
-  Data requirements documented
-  Sample queries added
-  PR merged
  Issue #33 closed

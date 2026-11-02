# M16-04 - Deployment Validation Results

**Date:** 2 November 2026
**Issue:** #86
**Branch:** feature/M16-04-validate-deployment
**Environment:** Windows, Python 3.11.9, Streamlit 1.63.0
**Deployment:** Local Streamlit

## 1. Application startup
The application started successfully using:
`python -m streamlit run app.py`

Local URL: http://localhost:8501

## 2. Manual page validation

| Page | Result |
|---|---|
| Dashboard | PASS |
| Sales Analysis | PASS |
| AI Forecasting | PASS |
| Smart Restocking | PASS |
| Inventory Alerts | PASS |
| AI Chatbot | PASS |
| Model Performance | PASS |

## 3. Store filter validation

S004 and S005 were tested. All Stores reset was also tested successfully.

Dashboard, Sales Analysis, AI Forecasting, Smart Restocking and Inventory Alerts responded to the selected store.

**Limitation:** Model Performance did not respond to the global store filter. Its metrics remained unchanged.

## 4. Chatbot validation

The chatbot processed the question:
"What should S004 reorder?"

It returned five historical reorder recommendations dated 1 January 2024. No purchase order was created. These are historical advisory results, not live purchasing instructions.

## 5. Automated test results

| Test group | Passed | Skipped |
|---|---:|---:|
| Restocking integration | 2 | 0 |
| M15-06 integration | 4 | 0 |
| M15-06 performance | 3 | 0 |
| Dashboard functional | 2 | 0 |
| Database service | 5 | 0 |
| Chatbot tests | 55 | 1 |
| M15-03 AI validation | 6 | 0 |
| Reorder recommendations | 8 | 0 |
| Restocking scenarios | 9 | 0 |
| Stockout detection | 14 | 0 |
| **Total** | **108** | **1** |

The chatbot tests also reported 37 passing subtests.

### Test collection limitation

The full `python -m pytest -q` run encountered three import collection errors caused by conflicting module names for `recommendations`.

All affected test groups passed when executed individually. The combined collection conflict remains unresolved.

## 6. Database validation

The database test initially exposed a duplicate SQL statement in `database/sqlite_schema.sql`.

The duplicate line was removed. The database tests passed again: **5 passed**.

## 7. AI output audit

The saved AI output audit returned **PASS_WITH_WARNINGS**.

Schema, numeric, date, forecast metric, key alignment and metadata checks passed.

Warnings:
- 100% of historical reorder records were classified as REORDER_NOW.
- 100% of historical stockout records were classified as STOCKOUT_RISK.

These historical outputs require review before operational use.

## 8. Application and dependency checks

| Check | Result |
|---|---|
| Python compilation of app.py | PASS |
| pip check | PASS - no broken requirements |
| Streamlit startup | PASS |
| Seven browser pages | PASS |
| Database tests after correction | PASS |
| Git diff whitespace check | PASS |

Streamlit displayed `use_container_width` deprecation warnings. They did not prevent the application from loading.

## 9. Deployment scope and limitations

This validation covers local Windows deployment only. No cloud or production deployment was tested.

Other limitations:
- Model Performance does not respond to the global store filter.
- Historical AI recommendation distributions require review.
- Combined pytest collection has an import conflict.
- Streamlit displays deprecation warnings.

## 10. Conclusion

The application launched successfully and all seven pages were manually validated.

A total of 108 automated tests passed, one was skipped, and 37 chatbot subtests passed across individually executed test groups.

The database schema issue was corrected and its tests passed again.

Local deployment validation is complete, subject to the limitations documented above.

**Issue:** M16-04 (#86)
**Status:** Evidence prepared for review.

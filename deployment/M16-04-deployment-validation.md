# M16-04 - Deployment Validation Evidence

**Issue:** #86
**Milestone:** M16 - Deployment
**Date:** 2 November 2026
**Assignee:** Thabang14

## Work completed

The Retail-X-AI application was successfully launched and tested in a local Windows environment.

All seven Streamlit application pages were manually inspected. The global store filter was tested using S004, S005 and All Stores.

The chatbot successfully processed a test question and returned historical reorder recommendations.

## Automated verification

- 108 automated tests passed across individually executed test groups.
- 1 test was skipped.
- 37 chatbot subtests passed.
- 5 database tests passed after correcting the SQL schema.
- Application compilation passed.
- Python dependency consistency check passed.

## Findings and limitations

- Model Performance does not respond to the global store filter.
- The combined pytest collection encounters conflicting recommendations imports.
- Historical reorder and stockout outputs both have 100% concentration in one status, requiring further operational review.
- Streamlit displays use_container_width deprecation warnings.
- Cloud and production deployment were not tested.

## Detailed results

See:

`testing/results/M16-04-deployment-validation-results.md`

## Outcome

Local deployment validation completed successfully, with the identified limitations documented.

**Evidence status:** Prepared for review.

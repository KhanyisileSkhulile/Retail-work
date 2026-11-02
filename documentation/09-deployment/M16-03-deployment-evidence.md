# M16-03 Deployment Documentation Evidence

## 1. Task information

- Milestone: M16-03
- GitHub issue: #85
- Task: Document deployment process
- Repository: Retail-X-AI / Retail-work
- Evidence folder: documentation/09-deployment/

## 2. Documentation delivered

The technical deployment guide is available at:

`deployment/documentation/M16-03-deployment-guide.md`

The guide covers:

- Environment prerequisites.
- Repository setup.
- Python virtual environment creation and activation.
- Dependency installation.
- Required application data files.
- SQLite database initialization.
- Streamlit application startup.
- Deployment verification.
- Troubleshooting.
- Application updates.
- Security considerations.
- Deployment limitations.

## 3. Verified development environment

| Check | Verified result |
|---|---|
| Python | 3.11.9 |
| Streamlit | 1.63.0 |
| Virtual environment | Active (.venv) |
| Application syntax | py_compile completed successfully |
| Dependency consistency | No broken requirements found |

## 4. Application and data inspection

The repository contains the following application and data files:

- app.py
- requirements.txt
- retail_store_inventory.csv
- retailai_forecasts.csv
- retailai_model_evaluation.csv
- retailai_restocking_recommendations.csv
- retailai_inventory_alerts.csv
- database/retail_inventory.db
- database/sqlite_schema.sql
- dataset/raw/retail_store_inventory.csv

The Streamlit dashboard loads its CSV files relative to the project root.

The backend database service uses `dataset/raw/retail_store_inventory.csv` as its default import source and `database/sqlite_schema.sql` as its schema.

## 5. SQLite database evidence

The existing SQLite database was inspected in read-only mode.

Tables found:

- import_metadata
- inventory_records

The inventory_records table contained:

**73,100 inventory records.**

The database service provides a database initialization function. Inspection confirmed that the Streamlit entry point does not automatically invoke this function. Database initialization is therefore documented as a separate setup step.

## 6. Deployment process documented

The documented local deployment process consists of:

1. Preparing the Python environment.
2. Installing dependencies from requirements.txt.
3. Confirming the dashboard data files are available.
4. Initializing SQLite when backend database functionality is required.
5. Starting the dashboard using Streamlit.
6. Verifying application and data availability.

The dashboard CSV data path and backend SQLite data path are documented separately.

## 7. Verification scope and limitations

The following checks were completed:

- Python version checked.
- Streamlit version checked.
- Application syntax compilation completed.
- Python dependency consistency checked.
- Existing SQLite database inspected.
- Database tables identified.
- Inventory record count retrieved.

These checks establish the local environment and database state. They do not establish that every dashboard page, a complete live dashboard session, or a production deployment has been successfully tested.

No configured cloud hosting provider, production domain, SSL setup, container deployment or automated production release pipeline was established during this task.

Further deployment validation is part of the subsequent deployment validation task.

## 8. Conclusion

The M16-03 deployment process has been documented based on the repository structure and verified local environment.

The technical deployment guide is provided separately under `deployment/documentation/`.

This evidence records the checks performed and distinguishes verified results from deployment activities that have not yet been tested.

# Retail-X-AI Deployment Guide

## 1. Purpose

This guide explains how to install, configure and run Retail-X-AI locally on Windows using Python, Streamlit, CSV files and SQLite.

It documents local deployment only. Cloud or production hosting has not been established.

## 2. Prerequisites

- Windows 10 or Windows 11.
- Python 3.11.x.
- Git.
- PowerShell.
- Internet access for installing dependencies.

Verified development environment:
- Python 3.11.9
- Streamlit 1.63.0

## 3. Obtain the project

Clone the repository using `git clone https://github.com/Retail-X-AI/Retail-work.git`, then navigate into the `Retail-work` directory.

## 4. Python virtual environment

For a fresh installation, create an environment using `py -3.11 -m venv .venv`.

Activate it using `.\.venv\Scripts\Activate.ps1`.

For an existing installation, activate the existing environment instead. Do not create another environment unnecessarily.

If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` and activate the environment again.

## 5. Install dependencies

With the virtual environment activated, run:

- `python -m pip install --upgrade pip`
- `python -m pip install -r requirements.txt`
- `python -m pip check`

A successful dependency check reports: `No broken requirements found.`

## 6. Application data files

The Streamlit dashboard loads CSV files relative to the project root.

The primary inventory file is:
- `retail_store_inventory.csv`

Supporting dashboard files:
- `retailai_forecasts.csv`
- `retailai_model_evaluation.csv`
- `retailai_restocking_recommendations.csv`
- `retailai_inventory_alerts.csv`

The backend database service uses a separate default dataset:
- `dataset/raw/retail_store_inventory.csv`

Ensure the required files are present before running the relevant application features.

## 7. SQLite database setup

The database service uses:
- `database/retail_inventory.db`
- `database/sqlite_schema.sql`
- `dataset/raw/retail_store_inventory.csv`

Starting Streamlit does not automatically initialize the SQLite database.

To initialize the database and import the default dataset, run this from the project root:

`python application/backend/database/service.py`

The service applies the schema, validates the source data and imports inventory records. It also stores import metadata and can reuse an unchanged dataset.

Back up the database before operations that may replace existing inventory records.

## 8. Start the application

From the project root, with the virtual environment activated, run:

`python -m streamlit run app.py`

Open the application in a browser at:

`http://localhost:8501`

To stop the application, return to PowerShell and press `Ctrl+C`.

## 9. Deployment verification

After starting the application:

1. Confirm Streamlit starts without a Python traceback.
2. Open the local application address.
3. Confirm the dashboard loads.
4. Check that inventory data is displayed.
5. Check forecast, evaluation, recommendation and alert sections where supporting files are available.
6. If backend database functionality is required, confirm database initialization and inventory records.

Useful verification commands:

- `python --version`
- `python -m streamlit --version`
- `python -m pip check`
- `python -m py_compile app.py`

## 10. Troubleshooting

### Streamlit is not recognized

Ensure the virtual environment is activated and run:

`python -m streamlit run app.py`

### Missing inventory CSV

Check that `retail_store_inventory.csv` exists in the project root and that PowerShell is currently in the project root directory.

### Missing Python dependencies

Run:

`python -m pip install -r requirements.txt`

### Database or schema errors

Check that these files exist:

- `database/sqlite_schema.sql`
- `dataset/raw/retail_store_inventory.csv`

Review the error reported by the database service.

### Port 8501 is already in use

Run:

`python -m streamlit run app.py --server.port 8502`

Then open `http://localhost:8502`.

## 11. Updating the application

Back up important local data and the SQLite database before updating.

Fetch repository changes:

`git pull`

Install updated dependencies:

`python -m pip install -r requirements.txt`

Repeat the verification checks and restart the application.

## 12. Security considerations

- Do not commit passwords, API keys or tokens.
- Restrict access to the host machine and its data files.
- Back up important database and dataset files.
- Review Streamlit network settings before exposing the application to other users.
- Do not treat historical-data recommendations as live stock levels or real-time purchasing instructions.

## 13. Deployment limitations

This guide covers local Windows deployment using Python, Streamlit, CSV files and SQLite.

The repository inspection did not establish a configured cloud hosting provider, production domain, SSL configuration, container deployment or automated production release pipeline.

These require separate implementation and validation before production deployment can be claimed.

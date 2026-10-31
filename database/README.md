# Database

This directory contains the database schemas, queries, migrations, seed data, and documentation for Retail-X-AI.

## Database integration

The application database service uses SQLite to store and query retail inventory records.

### Important files

- `schema.sql` — Existing PostgreSQL schema.
- `sqlite_schema.sql` — SQLite schema used by the Python database service.
- `../application/backend/database/service.py` — Initializes the database, validates the CSV dataset, imports inventory records, and provides inventory summary functions.
- `retail_inventory.db` — Generated local SQLite database, excluded from Git.

### Requirements

- Python 3.11 or a compatible Python version.
- pandas installed in the active Python environment.
- `retail_store_inventory.csv` in the repository root.

### Initialize the database

From the repository root, run:

    python ".\application\backend\database\service.py"

The service initializes the schema and imports the inventory dataset when necessary. It checks the source CSV checksum and stored record count to avoid unnecessarily reimporting unchanged data.

The current dataset contains 73,100 inventory records.

### Verify the database

Run the following command from the repository root:

    python -c "import sqlite3; c=sqlite3.connect('database/retail_inventory.db'); print('Integrity:', c.execute('PRAGMA integrity_check').fetchone()[0]); print('Records:', c.execute('SELECT COUNT(*) FROM inventory_records').fetchone()[0]); c.close()"

A successful integrity check returns `ok`. The record count should be 73,100 for the current dataset.

### Inventory summary

The service provides `get_inventory_summary()` to return the number of inventory records, distinct stores, distinct products, and distinct categories.

### Git and generated files

Commit the database schema, service code, and documentation. Do not commit the generated SQLite database, which is excluded by the root `.gitignore`.

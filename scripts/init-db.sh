#!/bin/bash
set -e

DB_PATH="db/neurolearn.db"
SCHEMA="db/schema.sql"
SAMPLE="db/sample_data.sql"

echo "Initializing SQLite database at $DB_PATH..."

sqlite3 "$DB_PATH" < "$SCHEMA"
sqlite3 "$DB_PATH" < "$SAMPLE"

echo "Database initialized with schema and sample data."
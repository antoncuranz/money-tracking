#!/bin/bash
echo "creating db dump..."
pg_dump --dbname=money-tracking --format=p --inserts --clean --if-exists --file=./money-tracking.sql --username=postgres --host=localhost --port=5432

echo "starting postgres database..."
docker run --rm -d -e POSTGRES_PASSWORD=postgres -p 5433:5432 postgres

sleep 3

echo "restoring db dump..."
PGPASSWORD=postgres psql --file=./money-tracking.sql --username=postgres --host=localhost --port=5433 postgres

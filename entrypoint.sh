#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "Running alembic check"
python3 -m alembic --version

# Run Django management commands
echo "Running upgrades..."
python3 -m alembic upgrade head

echo "Starting FastAPI server..."
uvicorn main:app --host 0.0.0.0 --port 8000 --ssl-keyfile /app/key.pem --ssl-certfile /app/cert.pem --reload
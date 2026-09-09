#!/usr/bin/env bash
set -e

echo "==================================================="
echo "   THERMALIS-X: SIH Problem Statement 26162"
echo "   Industrial Thermal Intelligence and GIS Console"
echo "==================================================="

export PYTHONPATH="."

echo ""
echo "[1/3] Running Database Seeder..."
python scripts/seed_database.py

echo ""
echo "[2/3] Verifying System Acceptance Tests..."
python scripts/run_acceptance_tests.py

echo ""
echo "[3/3] Launching FastAPI ASGI Server and GIS Console..."
echo "Open your browser at: http://localhost:8000"
echo "API Documentation at: http://localhost:8000/docs"
echo "Documentation Hub at: http://localhost:8000/docs-portal/index.html"
echo ""

python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload

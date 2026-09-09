#!/usr/bin/env bash
set -e

echo "================================================================"
echo "      THERMALIS-X: INDUSTRIAL THERMAL INTELLIGENCE CONSOLE"
echo "      Smart India Hackathon Problem Statement 26162"
echo "================================================================"

export PYTHONPATH="."

if [ ! -f "thermalis.db" ]; then
    echo ""
    echo "[1/3] Initializing and seeding database..."
    python scripts/seed_database.py
else
    echo ""
    echo "[1/3] Verified thermalis.db."
fi

echo ""
echo "[2/3] Verifying Acceptance Tests..."
python scripts/run_acceptance_tests.py

echo ""
echo "[3/3] Launching FastAPI ASGI Server & GIS Console..."
echo "Console URL:       http://localhost:8000"
echo "Doc Portal:        http://localhost:8000/docs-portal/index.html"
echo "Interactive API:   http://localhost:8000/docs"
echo ""

if which xdg-open > /dev/null; then
    xdg-open "http://localhost:8000" &
elif which open > /dev/null; then
    open "http://localhost:8000" &
fi

python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload

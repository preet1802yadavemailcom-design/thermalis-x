@echo off
TITLE THERMALIS-X Launcher - SIH Problem Statement 26162
COLOR 0B
echo ================================================================
echo       THERMALIS-X: INDUSTRIAL THERMAL INTELLIGENCE CONSOLE
echo       Smart India Hackathon Problem Statement 26162
echo ================================================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    COLOR 0C
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python 3.10+ and add it to your system PATH.
    pause
    exit /b 1
)

set PYTHONPATH=.

if not exist "thermalis.db" (
    echo [1/3] Database not found. Initializing and seeding thermalis.db...
    python scripts\seed_database.py
) else (
    echo [1/3] Database verified: thermalis.db
)

echo [2/3] Verifying acceptance criteria...
python scripts\run_acceptance_tests.py
if errorlevel 1 (
    COLOR 0C
    echo [WARNING] Acceptance tests reported issues. Proceeding to launch...
)

echo.
echo [3/3] Launching FastAPI ASGI Server ^& GIS Console...
echo Console URL:          http://localhost:8000
echo Documentation Portal: http://localhost:8000/docs-portal/index.html
echo Interactive API:      http://localhost:8000/docs
echo.

start http://localhost:8000
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload

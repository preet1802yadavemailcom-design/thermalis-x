# THERMALIS-X 1-Click PowerShell Launcher
$Host.UI.RawUI.WindowTitle = "THERMALIS-X Console Launcher"
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "      THERMALIS-X: INDUSTRIAL THERMAL INTELLIGENCE CONSOLE" -ForegroundColor Yellow
Write-Host "      Smart India Hackathon Problem Statement 26162" -ForegroundColor White
Write-Host "================================================================" -ForegroundColor Cyan

$env:PYTHONPATH="."

if (-not (Test-Path "thermalis.db")) {
    Write-Host "`n[1/3] Initializing and seeding database..." -ForegroundColor Green
    python scripts/seed_database.py
} else {
    Write-Host "`n[1/3] Verified thermalis.db." -ForegroundColor Green
}

Write-Host "`n[2/3] Verifying Acceptance Tests..." -ForegroundColor Green
python scripts/run_acceptance_tests.py

Write-Host "`n[3/3] Launching FastAPI ASGI Server & GIS Console..." -ForegroundColor Green
Write-Host "Console URL:       http://localhost:8000" -ForegroundColor Yellow
Write-Host "Doc Portal:        http://localhost:8000/docs-portal/index.html" -ForegroundColor Yellow
Write-Host "Interactive API:   http://localhost:8000/docs`n" -ForegroundColor Yellow

Start-Process "http://localhost:8000"
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload

# THERMALIS-X Windows Demo Launcher
$Host.UI.RawUI.WindowTitle = "THERMALIS-X Console Launcher"
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "   THERMALIS-X: SIH Problem Statement 26162" -ForegroundColor Yellow
Write-Host "   Industrial Thermal Intelligence and GIS Console" -ForegroundColor White
Write-Host "===================================================" -ForegroundColor Cyan

$env:PYTHONPATH="."

Write-Host "`n[1/3] Running Database Seeder..." -ForegroundColor Green
python scripts/seed_database.py

Write-Host "`n[2/3] Verifying System Acceptance Tests..." -ForegroundColor Green
python scripts/run_acceptance_tests.py

Write-Host "`n[3/3] Launching FastAPI ASGI Server and GIS Console..." -ForegroundColor Green
Write-Host "Open your browser at: http://localhost:8000" -ForegroundColor Yellow
Write-Host "API Documentation at: http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host "Documentation Hub at: http://localhost:8000/docs-portal/index.html`n" -ForegroundColor Yellow

python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload

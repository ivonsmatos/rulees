$Root = Split-Path -Parent $PSScriptRoot
Write-Host "RuleEs dev helper"
Write-Host "Backend:  cd $Root\backend; .\.venv\Scripts\Activate.ps1; uvicorn app.main:app --reload --host 127.0.0.1 --port 8001"
Write-Host "Frontend: cd $Root\frontend; npm run dev -- --host 127.0.0.1 --port 5173"

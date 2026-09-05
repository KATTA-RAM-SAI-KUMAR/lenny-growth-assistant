@echo off
echo ===============================================================================
echo Starting The Lenny Growth Assistant (Local Dev Mode)
echo ===============================================================================

echo 1. Launching Backend server on http://localhost:8000 ...
start "Lenny Backend" cmd /k "cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

timeout /t 2 >nul

echo 2. Launching Frontend dev server on http://localhost:3000 ...
start "Lenny Frontend" cmd /k "cd frontend && npm run dev"

echo ===============================================================================
echo Services launched!
echo - Frontend: http://localhost:3000
echo - Backend API Docs: http://localhost:8000/docs
echo - Health Probe: http://localhost:8000/api/health
echo ===============================================================================

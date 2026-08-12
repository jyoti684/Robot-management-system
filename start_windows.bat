@echo off
setlocal
where docker >nul 2>nul
if errorlevel 1 (
  echo Docker was not found. Install Docker Desktop and try again.
  pause
  exit /b 1
)
if not exist .env copy .env.example .env >nul
echo Starting Robot Management System...
docker compose up --build
endlocal

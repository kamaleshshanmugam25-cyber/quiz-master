@echo off
title QuizProject Launcher
echo ========================================================
echo          STARTING QUIZPROJECT APPLICATION
echo ========================================================
echo.

echo 1. Checking Memurai / Redis Service...
sc query Memurai | find "RUNNING" >nul
if %ERRORLEVEL% EQU 0 (
    echo    [OK] Memurai is running on port 6379.
) else (
    echo    [INFO] Starting Memurai service...
    net start Memurai >nul 2>&1
)

echo.
echo 2. Launching Backend Server on port 8001...
start "QuizProject Backend" cmd /k "cd /d C:\A2757\QuizProject\backend && C:\A2757\QuizProject\backend\venv\Scripts\daphne.exe -b 127.0.0.1 -p 8001 backend.asgi:application"

echo.
echo 3. Launching Frontend Server on port 3000...
start "QuizProject Frontend" cmd /k "cd /d C:\A2757\QuizProject\frontend && npm start"

echo.
echo ========================================================
echo App running!
echo - Host Dashboard:    http://localhost:3000/
echo - Player Join:       http://localhost:3000/join
echo ========================================================
echo You can minimize this window.
timeout /t 5 >nul

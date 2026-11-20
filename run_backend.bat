@echo off
title QuizProject - Backend (Daphne ASGI Port 8001)
echo Starting QuizProject Daphne ASGI Server on port 8001...
cd /d "C:\A2757\QuizProject\backend"
"C:\A2757\QuizProject\backend\venv\Scripts\daphne.exe" -b 127.0.0.1 -p 8001 backend.asgi:application
pause

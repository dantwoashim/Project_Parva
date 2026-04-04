@echo off
if "%PARVA_SERVE_FRONTEND%"=="" set PARVA_SERVE_FRONTEND=true
if "%PARVA_ENV%"=="" set PARVA_ENV=development
if "%PARVA_RATE_LIMIT_BACKEND%"=="" set PARVA_RATE_LIMIT_BACKEND=memory
set PYTHONPATH=backend
py -3.11 -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --app-dir backend

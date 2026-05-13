@echo off
if "%PARVA_SERVE_FRONTEND%"=="" set PARVA_SERVE_FRONTEND=true
if "%PARVA_ENV%"=="" set PARVA_ENV=development
if "%PARVA_RATE_LIMIT_BACKEND%"=="" set PARVA_RATE_LIMIT_BACKEND=memory
if "%PARVA_PYTHON%"=="" set PARVA_PYTHON=python
set PYTHONPATH=backend
"%PARVA_PYTHON%" -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --app-dir backend

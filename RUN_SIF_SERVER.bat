@echo off
setlocal
cd /d "%~dp0"
title SIF SERVER - DO NOT CLOSE
set "PY=%~dp0backend\.venv\Scripts\python.exe"
if not exist "%PY%" (
  echo ERROR: Python environment not found.
  echo Please run START_SIF.bat first.
  pause
  exit /b 1
)
echo ============================================
echo SIF SERVER - DO NOT CLOSE
echo Folder: %CD%
echo Port: 8017
echo ============================================
echo.
"%PY%" -m uvicorn backend.main:app --host 127.0.0.1 --port 8017
set "RC=%ERRORLEVEL%"
echo.
echo ============================================
echo SERVER STOPPED. Exit code: %RC%
echo ============================================
pause
exit /b %RC%

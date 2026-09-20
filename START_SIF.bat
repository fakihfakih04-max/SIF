@echo off
setlocal
cd /d "%~dp0"
set PORT=8045

echo ============================================
echo SIF Mobile ^& Computer - PHASE 49
echo Folder: %CD%
echo Port: %PORT%
echo ============================================

for /f "tokens=5" %%P in ('netstat -ano ^| findstr ":%PORT%" ^| findstr "LISTENING"') do taskkill /PID %%P /F >nul 2>&1

if not exist "backend\.venv\Scripts\python.exe" py -3 -m venv backend\.venv
call backend\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt

start "SIF SERVER - DO NOT CLOSE" cmd /k "cd /d "%CD%" && backend\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port %PORT%"

echo Waiting for SIF server...
for /l %%N in (1,1,30) do (
  powershell -NoProfile -Command "try { (Invoke-WebRequest -UseBasicParsing http://127.0.0.1:%PORT%/api/health -TimeoutSec 1).StatusCode } catch { 0 }" | findstr /x "200" >nul && goto READY
  timeout /t 1 /nobreak >nul
)
echo SERVER DID NOT START. Check SIF SERVER window.
pause
exit /b 1

:READY
start "" "http://127.0.0.1:%PORT%/?v=49"
endlocal

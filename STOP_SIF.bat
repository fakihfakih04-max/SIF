@echo off
for /f "tokens=5" %%P in ('netstat -ano ^| findstr ":8017" ^| findstr "LISTENING"') do taskkill /PID %%P /F >nul 2>&1
echo SIF server stopped.
pause

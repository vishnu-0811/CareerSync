@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo Virtual environment not ready. Run setup.bat first.
  exit /b 1
)

REM Prevent broken UI from stale Streamlit processes left on port 8501.
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8501" ^| findstr "LISTENING"') do (
  taskkill /F /PID %%a >nul 2>&1
)

echo Starting CareerSync...
".venv\Scripts\python.exe" -m streamlit run main.py
endlocal

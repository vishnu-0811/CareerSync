@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo Creating virtual environment...
  py -3.13 -m venv .venv
  if errorlevel 1 (
    echo Failed to create .venv. Make sure Python 3.13 is installed.
    exit /b 1
  )
)

echo Installing dependencies into .venv (one-time / when requirements change)...
".venv\Scripts\python.exe" -m pip install --upgrade pip
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
  echo Dependency install failed.
  exit /b 1
)

echo.
echo Setup complete. Use run.bat to start the app.
endlocal

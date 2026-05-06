@echo off
setlocal

where py >nul 2>nul
if errorlevel 1 (
  echo Python launcher ^(`py`^) was not found.
  echo Install Python from python.org and enable "Add python.exe to PATH".
  exit /b 1
)

echo Installing ffetch for the current user...
py -m pip install --user .
if errorlevel 1 (
  echo Installation failed.
  exit /b 1
)

for /f "usebackq delims=" %%I in (`py -c "import os, sysconfig; print(sysconfig.get_path('scripts', scheme=f'{os.name}_user'))"`) do set "SCRIPTS_DIR=%%I"

echo.
echo Installed. The command should now be available as:
echo   ffetch
echo.
echo If Windows still says "ffetch is not recognized", add this folder to PATH:
echo   %SCRIPTS_DIR%

where ffetch >nul 2>nul
if errorlevel 1 (
  echo.
  echo PATH does not currently include the Scripts folder in this shell.
  exit /b 0
)

echo PATH looks good. You can now run `ffetch` from any drive.

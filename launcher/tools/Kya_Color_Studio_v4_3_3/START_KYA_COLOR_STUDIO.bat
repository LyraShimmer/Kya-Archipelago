@echo off
setlocal
cd /d "%~dp0"
title Kya Color Studio
where py >nul 2>nul
if not errorlevel 1 (
  set "PYTHON=py -3"
  goto :found
)
where python >nul 2>nul
if not errorlevel 1 (
  set "PYTHON=python"
  goto :found
)
echo Python 3 was not found. Install Python 3 with Add to PATH enabled.
pause
exit /b 1
:found
%PYTHON% -c "import PIL" >nul 2>nul
if errorlevel 1 (
  echo Installing Pillow, required for the color editor...
  %PYTHON% -m pip install Pillow
  if errorlevel 1 (
    echo Could not install Pillow. Check Python and your connection.
    pause
    exit /b 1
  )
)
%PYTHON% "%~dp0Kya_Color_Studio.py"
if errorlevel 1 (
  echo The editor could not start. See errors above.
  pause
)

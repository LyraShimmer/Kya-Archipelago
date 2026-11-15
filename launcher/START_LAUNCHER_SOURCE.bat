@echo off
cd /d "%~dp0"
py -3 -c "import PIL" >nul 2>&1
if errorlevel 1 (
  echo Pillow is required. Attempting to install it...
  py -3 -m pip install pillow
  if errorlevel 1 goto fail
)
py -3 "Kya_Archipelago_Launcher.py"
if errorlevel 1 goto fail
exit /b 0
:fail
echo Could not start the Python source-mode launcher. Check Python and Pillow.
pause
exit /b 1

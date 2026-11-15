@echo off
setlocal
cd /d "%~dp0"
echo Building Kya Archipelago v9.0.1 RC2 Launcher source (Windows)
py -3 -m pip install pyinstaller pillow websocket-client certifi
if errorlevel 1 goto fail
py -3 -m PyInstaller --noconfirm --clean KyaMemoryCore.spec
if errorlevel 1 goto fail
py -3 -m PyInstaller --noconfirm --clean KyaArchipelagoLauncher.spec
if errorlevel 1 goto fail
echo.
echo Built EXE(s) under launcher\dist. Copy the ENTIRE launcher\data folder
 echo beside the executable, keeping original SSL fixes/resources intact.
 echo PCSX2 + PINE test required; do not publish without testing.
pause
exit /b 0
:fail
echo Build failed. See error messages above.
pause
exit /b 1

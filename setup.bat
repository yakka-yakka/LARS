:: setup.bat
@echo off
title LARS - Setup & Management
setlocal
cd /d "%~dp0"

:menu
cls
echo ==============================================
echo        LARS - MANAGEMENT
echo ==============================================
echo.
echo 1) Install / Repair the Suite
echo 2) Uninstall entirely
echo 3) Exit
echo.
set /p choice="Please select an option (1-3): "

if "%choice%"=="1" goto install
if "%choice%"=="2" goto uninstall
if "%choice%"=="3" exit
goto menu

:install
echo.
echo [+] Checking environment...

if exist "python_env\python.exe" goto skip_python
echo [!] Setting up local Python environment (this may take a minute)...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$ErrorActionPreference = 'Stop'; Write-Host 'Downloading Python...'; Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.8/python-3.11.8-embed-amd64.zip' -OutFile 'python.zip'; Expand-Archive -Path 'python.zip' -DestinationPath 'python_env' -Force; Remove-Item 'python.zip'; $pth = Get-ChildItem -Path 'python_env' -Filter 'python*._pth' | Select-Object -First 1; (Get-Content $pth.FullName) -replace '#import site', 'import site' | Set-Content $pth.FullName; Write-Host 'Downloading pip...'; Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile 'python_env\get-pip.py'; & 'python_env\python.exe' 'python_env\get-pip.py'; & 'python_env\python.exe' -m pip install -r requirements.txt"
:skip_python

if exist "ahk_env\AutoHotkey64.exe" goto skip_ahk
echo [!] Setting up local AutoHotkey environment...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$ErrorActionPreference = 'Stop'; Write-Host 'Downloading AHK...'; Invoke-WebRequest -Uri 'https://www.autohotkey.com/download/ahk-v2.zip' -OutFile 'ahk.zip'; Expand-Archive -Path 'ahk.zip' -DestinationPath 'ahk_env' -Force; Remove-Item 'ahk.zip'"
:skip_ahk

echo.
echo [+] Registering LARS Watcher to run silently on startup...
echo Set WshShell = CreateObject("WScript.Shell") > "run_hidden.vbs"
echo WshShell.Run chr(34) ^& "%~dp0python_env\pythonw.exe" ^& chr(34) ^& " " ^& chr(34) ^& "%~dp0watcher.py" ^& chr(34), 0, False >> "run_hidden.vbs"

:: Register script in Current User Startup Registry
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "LARS_Watcher" /t REG_SZ /d "\"wscript.exe\" \"%~dp0run_hidden.vbs\"" /f >nul 2>&1

echo.
echo [+] Starting the Watcher Service now...
wscript.exe "run_hidden.vbs"

echo.
echo [+] Done! Installation complete. The service is running in the background.
echo [+] It will silently launch whenever it detects Arma Reforger.
pause
goto menu

:uninstall
echo.
set /p confirm="Are you sure you want to completely uninstall? y/n: "
if /i not "%confirm%"=="y" goto menu

echo.
echo [+] Stopping background services...
powershell -NoProfile -Command "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match 'watcher\.py|main\.py' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }" >nul 2>&1

echo [+] Removing Startup Registrations...
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "LARS_Watcher" /f >nul 2>&1
schtasks /Delete /TN "LARS_Watcher" /F >nul 2>&1

echo [+] Cleaning up environment files...
if exist "run_hidden.vbs" del /f /q "run_hidden.vbs"
if exist "python_env" rmdir /s /q "python_env"
if exist "ahk_env" rmdir /s /q "ahk_env"

echo.
echo [+] Uninstall Complete. Background services are stopped and local environments are wiped.
pause
goto menu

@echo off

REM Check for clean parameter
set CLEAN_ENV=%1
if "%CLEAN_ENV%"=="" set CLEAN_ENV=ask

REM Jump to main script, skip subroutine definitions
goto :main

REM ===== SUBROUTINES =====
:cleanup_vbox_vm
rem parameters are passed via %~1
if "%~1"=="" goto :cleanup_vbox_vm_end
where VBoxManage >nul 2>&1
if %ERRORLEVEL% neq 0 goto :cleanup_vbox_vm_end
for /f "usebackq tokens=*" %%G in (`VBoxManage list vms ^| findstr /i "\"%~1\""`) do (
    echo Found existing VirtualBox VM named '%~1'. Attempting to power off and remove it to avoid conflicts...
    VBoxManage controlvm "%~1" poweroff >nul 2>&1 || echo Poweroff attempt failed or VM not running
    VBoxManage unregistervm "%~1" --delete >nul 2>&1 && echo Removed existing VM '%~1' || echo Warning: failed to unregister VM '%~1' (it may be locked or in use)
)
:cleanup_vbox_vm_end
goto :eof

REM ===== MAIN SCRIPT =====
:main

call :cleanup_vbox_vm "open-net-dns-server"
echo ========================================
echo.
echo This script will launch all three VMs in the correct order:
echo 1. DNS Server (192.168.10.1)
echo 2. Agent (DHCP)
echo 3. Detective (DHCP)
echo.

REM Handle cleanup based on parameter
if "%CLEAN_ENV%"=="clean" (
    echo Cleaning up existing lab VMs...
    cd DNS
    vagrant destroy -f >nul 2>&1
    cd ..\Agent
    vagrant destroy -f >nul 2>&1
    cd ..\Detective
    vagrant destroy -f >nul 2>&1
    cd ..
    echo Cleanup complete. Starting fresh lab setup...
    echo.
) else if "%CLEAN_ENV%"=="noclean" (
    echo Skipping cleanup - using existing VMs if available...
    echo.
) else (
    echo Do you want to clean up existing lab VMs? (This will destroy any existing VMs)
    echo   y = Yes, clean up existing VMs (fresh start)
    echo   n = No, keep existing VMs
    choice /c yn /n /m "Choice [y/n]: "
    if errorlevel 2 (
        echo Skipping cleanup - using existing VMs if available...
        echo.
    ) else (
        echo Cleaning up existing lab VMs...
        cd DNS
        vagrant destroy -f >nul 2>&1
        cd ..\Agent
        vagrant destroy -f >nul 2>&1
        cd ..\Detective
        vagrant destroy -f >nul 2>&1
        cd ..
        echo Cleanup complete. Starting fresh lab setup...
        echo.
    )
)

pause

echo.
echo ========================================
echo  Step 1: Starting DNS Server...
echo ========================================
cd DNS
echo Current directory: %CD%
vagrant up
if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to start DNS Server
    pause
    exit /b 1
)
echo DNS Server started successfully!

echo.
echo Reloading DNS Server to initialize DNS-DHCP services...
echo Attempting to fix read-only file system issue first...
vagrant ssh -c "sudo mount -o remount,rw / 2>/dev/null || echo 'Filesystem remount skipped'"
vagrant reload
if %ERRORLEVEL% neq 0 (
    echo WARNING: Failed to reload DNS Server (this may be normal for some VMs)
    echo Attempting to continue without reload...
    echo Checking if DNS services are already running...
    vagrant ssh -c "sudo systemctl status dnsmasq 2>/dev/null || echo 'DNS service check completed'"
    echo Continuing with lab setup...
) else (
    echo DNS Server reloaded and services initialized!
)
echo.

echo ========================================
echo  Step 2: Starting Agent VM...
echo ========================================
cd ..\Agent
echo Current directory: %CD%
call :cleanup_vbox_vm "agent-vm"
vagrant up
if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to start Agent VM
    pause
    exit /b 1
)
echo Agent VM started successfully!
echo.

echo ========================================
echo  Step 3: Starting Detective VM...
echo ========================================
cd ..\Detective
echo Current directory: %CD%
call :cleanup_vbox_vm "detective-vm"
vagrant up
if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to start Detective VM
    pause
    exit /b 1
)
echo Detective VM started successfully!
echo.

cd ..
echo ========================================
echo  Lab Setup Complete!
echo ========================================
echo.
echo All VMs are now running:
echo - DNS Server: 192.168.10.1
echo - Agent: Check IP with 'vagrant ssh' then 'ip addr'
echo - Detective: Check IP with 'vagrant ssh' then 'ip addr'
echo.
echo To connect to a VM:
echo   cd [VM_folder] ^&^& vagrant ssh
echo.
echo To stop all VMs:
echo   .\shutdown-lab.bat
echo.
echo Usage examples:
echo   .\launch-lab.bat         (ask about cleanup)
echo   .\launch-lab.bat clean   (clean existing VMs)
echo   .\launch-lab.bat noclean (keep existing VMs)
echo.
pause
@echo off
echo ========================================
echo  Open Network Security Lab Launcher
echo ========================================
echo.
echo This script will launch all three VMs in the correct order:
echo 1. DNS Server (192.168.10.1)
echo 2. Agent (DHCP)
echo 3. Detective (DHCP)
echo.
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

echo ========================================
echo  Step 2: Starting Agent VM...
echo ========================================
cd ..\Agent
echo Current directory: %CD%
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
pause
@echo off
echo ========================================
echo  Open Network Security Lab Shutdown
echo ========================================
echo.
echo This script will shutdown all three VMs:
echo 1. Detective
echo 2. Agent  
echo 3. DNS Server
echo.
pause

echo.
echo ========================================
echo  Step 1: Shutting down Detective VM...
echo ========================================
cd Detective
echo Current directory: %CD%
vagrant halt
if %ERRORLEVEL% neq 0 (
    echo WARNING: Failed to gracefully shutdown Detective VM, forcing shutdown...
    vagrant destroy -f
)
echo Detective VM shutdown complete!
echo.

echo ========================================
echo  Step 2: Shutting down Agent VM...
echo ========================================
cd ..\Agent
echo Current directory: %CD%
vagrant halt
if %ERRORLEVEL% neq 0 (
    echo WARNING: Failed to gracefully shutdown Agent VM, forcing shutdown...
    vagrant destroy -f
)
echo Agent VM shutdown complete!
echo.

echo ========================================
echo  Step 3: Shutting down DNS Server...
echo ========================================
cd ..\DNS
echo Current directory: %CD%
vagrant halt
if %ERRORLEVEL% neq 0 (
    echo WARNING: Failed to gracefully shutdown DNS Server, forcing shutdown...
    vagrant destroy -f
)
echo DNS Server shutdown complete!
echo.

cd ..
echo ========================================
echo  Lab Shutdown Complete!
echo ========================================
echo.
echo All VMs have been shutdown.
echo.
echo To restart the lab:
echo   .\launch-lab.bat
echo.
echo To completely destroy all VMs (free up disk space):
echo   vagrant destroy -f (in each VM folder: DNS, Agent, Detective)
echo.
pause
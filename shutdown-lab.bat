@echo off
echo ========================================
echo  Shutting Down Lab VMs
echo ========================================
echo.

echo Stopping Detective VM...
cd Detective
vagrant halt
echo.

echo Stopping Agent VM...
cd ..\Agent
vagrant halt
echo.

echo Stopping DNS Server...
cd ..\DNS
vagrant halt
echo.

cd ..
echo ========================================
echo  All VMs Stopped
echo ========================================
pause
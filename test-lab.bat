@echo off
rem test-lab.bat - Windows equivalent of test-lab.sh
setlocal

rem Determine script directory
set "ROOT_DIR=%~dp0"

echo Testing lab connectivity: Agent -> DNS (192.168.10.1)

rem Check that vagrant is available
vagrant --version >nul 2>&1
if errorlevel 1 (
  echo Vagrant not found in PATH. Please install Vagrant and ensure it is on PATH.
  exit /b 1
)

goto :main

:: run_check <vm_path> <name>
:run_check
set "VM_PATH=%~1"
set "VM_NAME=%~2"
echo.
echo == %VM_NAME% ==
pushd "%VM_PATH%" >nul 2>&1 || (
  echo Cannot change directory to %VM_PATH%
  goto :eof
)

echo IP addresses (internal interface enp0s8):
vagrant ssh -c "ip -4 addr show enp0s8 | sed -n 's/.*inet \([0-9.]*\/.*\).*/\1/p' || ip -4 addr show | sed -n 's/.*inet \([0-9.]*\/.*\).*/\1/p'"

echo Ping DNS (192.168.10.1):
vagrant ssh -c "ping -c 4 192.168.10.1" || echo Ping command failed or returned non-zero status

popd >nul 2>&1
goto :eof

:main
call :run_check "%ROOT_DIR%Agent" "Agent"

echo.
echo Test complete.
endlocal

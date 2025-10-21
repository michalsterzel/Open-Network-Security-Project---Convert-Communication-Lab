@echo off
echo ========================================
echo  Open Network Security Lab Prerequisites
echo ========================================
echo.
echo This script will check and install:
echo - Vagrant
echo - VirtualBox
echo - Ansible (optional: required if you provision from the host)
echo.
echo Note: You may need to run this as Administrator
echo.
pause

echo Checking if Vagrant is installed...
vagrant --version >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo ✓ Vagrant is already installed
    vagrant --version
) else (
    echo ✗ Vagrant not found
    echo.
    echo Installing Vagrant...
    echo Please download and install Vagrant from: https://www.vagrantup.com/downloads
    echo After installation, restart this script.
    echo.
    start https://www.vagrantup.com/downloads
    pause
    exit /b 1
)

echo.
echo Checking if VirtualBox is installed...
where VBoxManage >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo ✓ VirtualBox is already installed
    VBoxManage --version
) else (
    echo ✗ VirtualBox not found
    echo.
    echo Installing VirtualBox...
    echo Please download and install VirtualBox from: https://www.virtualbox.org/wiki/Downloads
    echo After installation, restart this script.
    echo.
    start https://www.virtualbox.org/wiki/Downloads
    pause
    exit /b 1
)

echo.
echo Checking if Ansible is installed...
where ansible >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo ✓ Ansible is already installed
    ansible --version 2>nul
) else (
    echo ✗ Ansible not found
    echo Note: On Windows you can install Ansible via WSL, pip inside a Python virtualenv, or by using Chocolatey/WSL. See: https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html
)

echo.
echo ========================================
echo  Prerequisites Check Complete!
echo ========================================
echo.
echo ✓ Vagrant is installed
echo ✓ VirtualBox is installed
echo.
if %ERRORLEVEL% equ 0 (
    echo If you plan to run Ansible from this host, please install Ansible as noted above.
)
echo.
echo You can now run the lab launcher:
echo   .\launch-lab.bat
echo.
pause
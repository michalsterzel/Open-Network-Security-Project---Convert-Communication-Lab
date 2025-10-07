#!/bin/bash

# Check for clean parameter
CLEAN_ENV=${1:-ask}

echo "========================================"
echo " Open Network Security Lab Launcher"
echo "========================================"
echo
echo "This script will launch all three VMs in the correct order:"
echo "1. DNS Server (192.168.10.1)"
echo "2. Agent (DHCP)"
echo "3. Detective (DHCP)"
echo

# Handle cleanup based on parameter
if [ "$CLEAN_ENV" = "clean" ]; then
    echo "Cleaning up existing lab VMs..."
    cd DNS && vagrant destroy -f >/dev/null 2>&1
    cd ../Agent && vagrant destroy -f >/dev/null 2>&1
    cd ../Detective && vagrant destroy -f >/dev/null 2>&1
    cd ..
    echo "Cleanup complete. Starting fresh lab setup..."
    echo
elif [ "$CLEAN_ENV" = "noclean" ]; then
    echo "Skipping cleanup - using existing VMs if available..."
    echo
else
    echo "Do you want to clean up existing lab VMs? (This will destroy any existing VMs)"
    echo "  y = Yes, clean up existing VMs (fresh start)"
    echo "  n = No, keep existing VMs"
    read -p "Choice [y/n]: " choice
    case "$choice" in
        y|Y)
            echo "Cleaning up existing lab VMs..."
            cd DNS && vagrant destroy -f >/dev/null 2>&1
            cd ../Agent && vagrant destroy -f >/dev/null 2>&1
            cd ../Detective && vagrant destroy -f >/dev/null 2>&1
            cd ..
            echo "Cleanup complete. Starting fresh lab setup..."
            echo
            ;;
        n|N)
            echo "Skipping cleanup - using existing VMs if available..."
            echo
            ;;
        *)
            echo "Invalid choice. Skipping cleanup..."
            echo
            ;;
    esac
fi

read -p "Press Enter to continue..."

echo
echo "========================================"
echo " Step 1: Starting DNS Server..."
echo "========================================"
cd DNS
echo "Current directory: $(pwd)"
vagrant up
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to start DNS Server"
    exit 1
fi
echo "DNS Server started successfully!"

echo
echo "Reloading DNS Server to initialize DNS-DHCP services..."
echo "Attempting to fix read-only file system issue first..."
vagrant ssh -c "sudo mount -o remount,rw / 2>/dev/null || echo 'Filesystem remount skipped'"
vagrant reload
if [ $? -ne 0 ]; then
    echo "WARNING: Failed to reload DNS Server (this may be normal for some VMs)"
    echo "Attempting to continue without reload..."
    echo "Checking if DNS services are already running..."
    vagrant ssh -c "sudo systemctl status dnsmasq 2>/dev/null || echo 'DNS service check completed'"
    echo "Continuing with lab setup..."
else
    echo "DNS Server reloaded and services initialized!"
fi
echo

echo "========================================"
echo " Step 2: Starting Agent VM..."
echo "========================================"
cd ../Agent
echo "Current directory: $(pwd)"
vagrant up
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to start Agent VM"
    exit 1
fi
echo "Agent VM started successfully!"
echo

echo "========================================"
echo " Step 3: Starting Detective VM..."
echo "========================================"
cd ../Detective
echo "Current directory: $(pwd)"
vagrant up
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to start Detective VM"
    exit 1
fi
echo "Detective VM started successfully!"
echo

cd ..
echo "========================================"
echo " Lab Setup Complete!"
echo "========================================"
echo
echo "All VMs are now running:"
echo "- DNS Server: 192.168.10.1"
echo "- Agent: Check IP with 'vagrant ssh' then 'ip addr'"
echo "- Detective: Check IP with 'vagrant ssh' then 'ip addr'"
echo
echo "To connect to a VM:"
echo "  cd [VM_folder] && vagrant ssh"
echo
echo "To stop all VMs:"
echo "  ./shutdown-lab.sh"
echo
echo "Usage examples:"
echo "  ./launch-lab.sh         (ask about cleanup)"
echo "  ./launch-lab.sh clean   (clean existing VMs)"
echo "  ./launch-lab.sh noclean (keep existing VMs)"
echo
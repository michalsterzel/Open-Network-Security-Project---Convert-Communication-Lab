#!/bin/bash

echo "========================================"
echo " Open Network Security Lab Shutdown"
echo "========================================"
echo
echo "This script will shutdown all three VMs:"
echo "1. Detective"
echo "2. Agent"
echo "3. DNS Server"
echo
read -p "Press Enter to continue..."

echo
echo "========================================"
echo " Step 1: Shutting down Detective VM..."
echo "========================================"
cd Detective
echo "Current directory: $(pwd)"
vagrant halt
if [ $? -ne 0 ]; then
    echo "WARNING: Failed to gracefully shutdown Detective VM, forcing shutdown..."
    vagrant destroy -f
fi
echo "Detective VM shutdown complete!"
echo

echo "========================================"
echo " Step 2: Shutting down Agent VM..."
echo "========================================"
cd ../Agent
echo "Current directory: $(pwd)"
vagrant halt
if [ $? -ne 0 ]; then
    echo "WARNING: Failed to gracefully shutdown Agent VM, forcing shutdown..."
    vagrant destroy -f
fi
echo "Agent VM shutdown complete!"
echo

echo "========================================"
echo " Step 3: Shutting down DNS Server..."
echo "========================================"
cd ../DNS
echo "Current directory: $(pwd)"
vagrant halt
if [ $? -ne 0 ]; then
    echo "WARNING: Failed to gracefully shutdown DNS Server, forcing shutdown..."
    vagrant destroy -f
fi
echo "DNS Server shutdown complete!"
echo

cd ..
echo "========================================"
echo " Lab Shutdown Complete!"
echo "========================================"
echo
echo "All VMs have been shutdown."
echo
echo "To restart the lab:"
echo "  ./launch-lab.sh"
echo
echo "To completely destroy all VMs (free up disk space):"
echo "  vagrant destroy -f (in each VM folder: DNS, Agent, Detective)"
echo
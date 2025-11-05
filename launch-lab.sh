#!/bin/bash

# Check for clean parameter
CLEAN_ENV=${1:-ask}

echo "========================================"
echo " Open Network Security Lab Launcher"
echo "========================================"
echo
echo "This script will launch the lab VMs in the correct order:"
echo "1. DNS Server (192.168.10.1)"
echo "2. Agent (DHCP)"
echo

# Handle cleanup based on parameter
if [ "$CLEAN_ENV" = "clean" ]; then
    echo "Cleaning up existing lab VMs..."
    cd DNS && vagrant destroy -f >/dev/null 2>&1
    cd ../Agent && vagrant destroy -f >/dev/null 2>&1
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

# Helper: if a VirtualBox VM with given name exists, try to power it off and unregister it
cleanup_vbox_vm() {
    local vm_name="$1"
    if ! command -v VBoxManage >/dev/null 2>&1; then
        return 0
    fi
    # look for exact name match in VBoxManage list
    if VBoxManage list vms | grep -q "\"${vm_name}\""; then
        echo "Found existing VirtualBox VM named '${vm_name}'. Attempting to power off and remove it to avoid conflicts..."
        # Best-effort poweroff, ignore errors
        VBoxManage controlvm "${vm_name}" poweroff 2>/dev/null || true
        # Unregister and delete files; ignore errors but report
        if VBoxManage unregistervm "${vm_name}" --delete 2>/dev/null; then
            echo "Removed existing VM '${vm_name}'."
        else
            echo "Warning: failed to unregister VM '${vm_name}' (it may be locked or in use)."
            echo "You may need to stop VirtualBox or remove the VM manually: VBoxManage unregistervm \"${vm_name}\" --delete"
        fi
    fi
}

# Try to cleanup any stale VMs that would conflict
cleanup_vbox_vm "open-net-dns-server"
vagrant up
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to start DNS Server"
    exit 1
fi
echo "DNS Server started successfully!"


echo "========================================"
echo " Step 2: Starting Agent VM..."
echo "========================================"
cd ../Agent
echo "Current directory: $(pwd)"
cleanup_vbox_vm "agent-vm"
vagrant up
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to start Agent VM"
    exit 1
fi
echo "Agent VM started successfully!"
echo

cd ..
echo "========================================"
echo " Lab Setup Complete!"
echo "========================================"
echo
echo "All VMs are now running:"
echo "- DNS Server: 192.168.10.1"
echo "- Agent: Check IP with 'vagrant ssh' then 'ip addr'"
echo
echo "To connect to a VM:"
echo "  cd [VM_folder] && vagrant ssh"
echo
echo "To test the setup:"
echo "  ./test-lab.sh"
echo
echo "To stop all VMs:"
echo "  ./shutdown-lab.sh"
echo
echo "Usage examples:"
echo "  ./launch-lab.sh         (ask about cleanup)"
echo "  ./launch-lab.sh clean   (clean existing VMs)"
echo "  ./launch-lab.sh noclean (keep existing VMs)"
echo
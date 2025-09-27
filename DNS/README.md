# Vagrant DNS Lab Setup

## Prerequisites
- Vagrant installed
- VirtualBox installed

## Quick Setup

Run the appropriate setup script for your operating system:

### Windows
```batch
dns-setup-windows.bat
```

### Linux/macOS
```bash
chmod +x dns-setup-linux.sh
./dns-setup-linux.sh
```

These scripts will automatically:
- Initialize Vagrant
- Configure Kali Linux as the base OS
- Set up VirtualBox with 4GB RAM and 2 CPU cores
- Enable GUI mode
- Start the VM

## Connecting to the VM
After the setup completes, connect using:
```bash
vagrant ssh
```

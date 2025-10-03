# Vagrant Detective Lab Setup

## Prerequisites
- Vagrant installed
- VirtualBox installed
- DNS Server VM running (from DNS folder)

## Quick Setup

Run the appropriate setup script for your operating system:

### Windows
```batch
detective-setup-windows.bat
```

### Linux/macOS
```bash
chmod +x detective-setup-linux.sh
./detective-setup-linux.sh
```

These scripts will automatically:
- Remove any existing Vagrantfile
- Create a new Vagrantfile with Detective configuration
- Use the `open_network_security/detective` box
- Connect to the internal network (`labnet`)
- Get IP via DHCP from DNS server
- Configure 2GB RAM and 2 CPU cores
- Install network testing tools
- Configure DNS to use the DNS server (192.168.10.1)
- Start the VM

## Network Configuration
- **Network**: Internal network `labnet`
- **IP Assignment**: DHCP (192.168.10.3-192.168.10.100)
- **DNS Server**: 192.168.10.1
- **VM Name**: detective-vm

## Connecting to the VM
After the setup completes, connect using:
```bash
vagrant ssh
```
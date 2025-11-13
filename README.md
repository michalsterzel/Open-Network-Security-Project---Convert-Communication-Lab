# Open Network Security Lab

A complete DNS security lab environment with virtual machines for learning and testing DNS security concepts.

## Quick Start

1. **Install Prerequisites**
   ```bash
   # Run the installation script to install Vagrant and VirtualBox
   ./install-prerequisites.bat    # Windows
   ./install-prerequisites.sh     # Linux/macOS
   ```

2. **Launch All VMs**
   ```bash
   # Start all VMs in the correct order
   ./launch-lab.bat               # Windows
   ./launch-lab.sh                # Linux/macOS
   
   # Or with cleanup options
   ./launch-lab.bat clean         # Windows - force clean start
   ./launch-lab.bat noclean       # Windows - keep existing VMs
   ./launch-lab.sh clean          # Linux/macOS - force clean start
   ./launch-lab.sh noclean        # Linux/macOS - keep existing VMs
   ```

3. **Shutdown All VMs**
   ```bash
   # Gracefully shutdown all VMs in reverse order
   ./shutdown-lab.bat             # Windows
   ./shutdown-lab.sh              # Linux/macOS
   ```

4. **Manual Setup (Alternative)**
   ```bash
   # Start VMs individually in order
   cd DNS && vagrant up && vagrant reload  # Reload needed for DNS-DHCP
   cd ../Agent && vagrant up
   ```

## Lab Components

| VM | Role | Base Box | IP Address | Resources |
|---|---|---|---|---|
| **DNS Server** | DNS server with DHCP | `bento/ubuntu-22.04` | 192.168.10.1 (static) | 4GB RAM, 2 CPUs |
| **Agent** | Agent machine for testing | `bento/ubuntu-22.04` | DHCP (192.168.10.3+) | 2GB RAM, 2 CPUs |

## Network Architecture

All VMs are connected to an isolated internal network (`labnet`) for secure testing:
- DNS Server provides DNS services and DHCP (192.168.10.3-192.168.10.100 range)
- Agent gets IP address via DHCP
- All communication stays within the isolated network

**Note**: The DNS server requires a reload after initial startup to properly initialize the DNS-DHCP services. The launch script handles this automatically.

## Usage

### Lab Management
- **Start Lab**: `./launch-lab.bat` (Windows) or `./launch-lab.sh` (Linux/macOS)
- **Stop Lab**: `./shutdown-lab.bat` (Windows) or `./shutdown-lab.sh` (Linux/macOS)

### Individual VM Management
- **Connect to VMs**: `vagrant ssh` (from each VM's folder)
- **Stop VMs**: `vagrant halt` (from each VM's folder)
- **Destroy VMs**: `vagrant destroy` (from each VM's folder)

## Prerequisites

- Vagrant 2.0+
- VirtualBox 6.0+
- 8GB+ RAM recommended
- 20GB+ free disk space

**Note on Ansible**: The lab uses `ansible_local` on Windows (Ansible runs inside each VM) and host-based Ansible on Linux/macOS. On Windows, Ansible is automatically installed inside the VMs—no host installation needed.

## Quick test

After the lab is up you can quickly verify internal networking using the helper script `test-lab.sh` or `test-lab.bat` located at the repository root.

What it checks:
- Prints the DHCP-assigned internal IP for the `Agent` VM
- Pings the DNS server at `192.168.10.1` from the Agent VM to confirm connectivity

Run it like this:

```bash
chmod +x test-lab.sh
./test-lab.sh                    # Linux/macOS
.\test-lab.bat                   # Windows
```

# Code
The code for the lab is available in the `src` folder with its relative README.
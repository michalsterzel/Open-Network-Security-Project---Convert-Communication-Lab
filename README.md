# Open Network Security Lab

A complete DNS security lab environment with three virtual machines for learning and testing DNS security concepts.

## Quick Start

1. **Install Prerequisites**
   ```bash
   # Run the installation script to install Vagrant and VirtualBox
   ./install-prerequisites.bat    # Windows
   ./install-prerequisites.sh     # Linux/macOS
   ```

2. **Launch All VMs**
   ```bash
   # Start all three VMs in the correct order
   ./launch-lab.bat               # Windows
   ./launch-lab.sh                # Linux/macOS
   ```

3. **Manual Setup (Alternative)**
   ```bash
   # Start VMs individually in order
   cd DNS && vagrant up
   cd ../Agent && vagrant up
   cd ../Detective && vagrant up
   ```

## Lab Components

| VM | Role | IP Address | Resources |
|---|---|---|---|
| **DNS Server** | DNS server with security monitoring | 192.168.10.1 (static) | 4GB RAM, 2 CPUs |
| **Agent** | Client machine for testing | DHCP (192.168.10.x) | 2GB RAM, 2 CPUs |
| **Detective** | Security analysis workstation | DHCP (192.168.10.x) | 2GB RAM, 2 CPUs |

## Network Architecture

All VMs are connected to an isolated internal network (`labnet`) for secure testing:
- DNS Server provides DNS services and DHCP
- Agent and Detective get IP addresses via DHCP
- All communication stays within the isolated network

## Usage

- **Connect to VMs**: `vagrant ssh` (from each VM's folder)
- **Stop VMs**: `vagrant halt` (from each VM's folder)
- **Destroy VMs**: `vagrant destroy` (from each VM's folder)

## Prerequisites

- Vagrant 2.0+
- VirtualBox 6.0+
- 8GB+ RAM recommended
- 20GB+ free disk space
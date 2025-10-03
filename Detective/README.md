# Detective Lab

## Prerequisites
- Vagrant installed
- VirtualBox installed
- DNS Server VM running (from DNS folder)

## Quick Setup

```bash
vagrant up
```

## VM Configuration
- **OS**: Detective (open_network_security/detective v0.1.0)
- **Memory**: 2GB
- **CPUs**: 2 cores
- **Network**: Internal network (DHCP on labnet)
- **GUI**: Enabled

## Connecting to the VM
```bash
vagrant ssh
```
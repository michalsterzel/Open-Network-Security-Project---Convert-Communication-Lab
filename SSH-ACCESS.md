# SSH Access Guide

## Automatic SSH Access
With the updated configuration, you can now connect to VMs without GUI prompts:

### Connect to VMs:
```bash
# DNS Server
cd DNS && vagrant ssh

# Agent
cd Agent && vagrant ssh  

# Detective
cd Detective && vagrant ssh
```

### VM Network Access:
```bash
# From host machine, after VMs are running:
ssh vagrant@192.168.10.1  # DNS Server (if SSH is enabled on internal network)
# Agent and Detective IPs: Check with 'ip addr' inside VMs
```

### Enable GUI (if needed):
Change `vb.gui = false` to `vb.gui = true` in any Vagrantfile
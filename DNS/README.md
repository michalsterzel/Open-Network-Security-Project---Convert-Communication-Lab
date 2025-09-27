# Vagrant DNS Lab Setup

## Prerequisites
- Vagrant installed
- VirtualBox installed

## Quick Setup

### 1. Configure Vagrant Box
```powershell
vagrant init
(Get-Content Vagrantfile) -replace 'config.vm.box = "base"', 'config.vm.box = "kalilinux/rolling"' | Set-Content Vagrantfile
```

### 2. Configure VirtualBox Provider
```powershell
# Uncomment the VirtualBox provider section
(Get-Content Vagrantfile) -replace '  # config.vm.provider "virtualbox" do \|vb\|', '  config.vm.provider "virtualbox" do |vb|' | Set-Content Vagrantfile

# Uncomment and enable GUI
(Get-Content Vagrantfile) -replace '  #   vb.gui = true', '    vb.gui = true' | Set-Content Vagrantfile

# Uncomment and set memory to 4GB
(Get-Content Vagrantfile) -replace '  #   vb.memory = "1024"', '    vb.memory = "4096"' | Set-Content Vagrantfile

# Add CPU configuration
(Get-Content Vagrantfile) -replace '    vb.memory = "4096"', "    vb.memory = `"4096`"`r`n    vb.cpus = 2" | Set-Content Vagrantfile

# Uncomment the end statement
(Get-Content Vagrantfile) -replace '  # end', '  end' | Set-Content Vagrantfile
```

### 3. Start VM
```powershell
vagrant up
vagrant ssh
```

## VM Configuration
- **OS**: Kali Linux Rolling
- **Memory**: 4GB
- **CPUs**: 2 cores  
- **GUI**: Enabled

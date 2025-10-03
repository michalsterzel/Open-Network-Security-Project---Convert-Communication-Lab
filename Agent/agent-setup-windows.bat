@echo off
echo Setting up Vagrant Agent Lab...
echo.

REM Remove existing Vagrantfile if it exists
echo Step 1: Cleaning up existing Vagrantfile...
if exist "Vagrantfile" (
    echo Removing existing Vagrantfile...
    del "Vagrantfile"
) else (
    echo No existing Vagrantfile found.
)

REM Create Agent Vagrantfile with custom configuration
echo Step 2: Creating Agent Vagrantfile...
powershell -Command "@'
# -*- mode: ruby -*-
# vi: set ft=ruby :

# Agent VM Configuration
# This VM connects to the internal network of the DNS server
Vagrant.configure(\"2\") do |config|
  # Base box for the agent
  config.vm.box = \"open_network_security/agent\"

  # Disable default synced folder for better isolation
  config.vm.synced_folder \".\", \"/vagrant\", disabled: true

  # Connect to the same internal network as the DNS server
  # This will put the agent on the same network as the DNS server (192.168.10.1)
  # The agent will get an IP from the DHCP server (192.168.10.3-192.168.10.100)
  config.vm.network \"private_network\", 
                    type: \"dhcp\", 
                    virtualbox__intnet: \"labnet\"

  # Alternative: Assign a static IP if you prefer (uncomment the line below and comment the DHCP line above)
  # config.vm.network \"private_network\", ip: \"192.168.10.10\", virtualbox__intnet: \"labnet\"

  # VirtualBox provider configuration
  config.vm.provider \"virtualbox\" do |vb|
    # Display the VirtualBox GUI when booting the machine
    vb.gui = true
    
    # Customize the amount of memory on the VM
    vb.memory = \"2048\"
    
    # Set the number of CPUs on the VM
    vb.cpus = 2
    
    # Set VM name
    vb.name = \"agent-vm\"
  end

  # Provisioning script to configure the agent
  config.vm.provision \"shell\", inline: <<-SHELL
    # Update system
    apt-get update
    
    # Install useful tools for network testing and debugging
    apt-get install -y net-tools dnsutils curl wget nmap

    # Configure DNS to use our DNS server
    # This will be set automatically via DHCP, but we can verify/override if needed
    echo \"nameserver 192.168.10.1\" > /etc/resolv.conf
    echo \"search local\" >> /etc/resolv.conf
    
    # Prevent NetworkManager from overriding resolv.conf
    chattr +i /etc/resolv.conf
    
    # Display network configuration
    echo \"=== Network Configuration ===\"
    ip addr show
    echo \"=== DNS Configuration ===\"
    cat /etc/resolv.conf
    echo \"=== Testing DNS Resolution ===\"
    nslookup google.com 192.168.10.1 || echo \"DNS server not yet available\"
    
    echo \"Agent VM setup complete!\"
  SHELL
end
'@ | Out-File -FilePath 'Vagrantfile' -Encoding UTF8"

echo.
echo Configuration complete! Starting VM...
vagrant up

echo.
echo Setup finished! VM is now running.
echo To connect to the VM, run: vagrant ssh
pause
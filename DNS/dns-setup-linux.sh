#!/bin/bash

echo "Setting up Vagrant DNS Lab..."
echo

# Remove existing Vagrantfile if it exists
echo "Step 1: Cleaning up existing Vagrantfile..."
if [ -f "Vagrantfile" ]; then
    echo "Removing existing Vagrantfile..."
    rm "Vagrantfile"
else
    echo "No existing Vagrantfile found."
fi

# Initialize Vagrant
echo "Step 2: Initializing Vagrant..."
vagrant init

# Configure Vagrant box
echo "Step 3: Setting DNS Server box..."
sed -i 's/config.vm.box = "base"/config.vm.box = "open_network_security\/dns_server"/' Vagrantfile

# Set box version
echo "Step 4: Setting box version..."
sed -i '/config.vm.box = "open_network_security\/dns_server"/a\  config.vm.box_version = "1.0.0"' Vagrantfile

# Configure VirtualBox Provider
echo "Step 5: Configuring VirtualBox provider..."
sed -i 's/  # config.vm.provider "virtualbox" do |vb|/  config.vm.provider "virtualbox" do |vb|/' Vagrantfile

echo "Step 6: Enabling GUI..."
sed -i 's/  #   vb.gui = true/    vb.gui = true/' Vagrantfile

echo "Step 7: Setting memory to 4GB..."
sed -i 's/  #   vb.memory = "1024"/    vb.memory = "4096"/' Vagrantfile

echo "Step 8: Adding CPU configuration..."
sed -i 's/    vb.memory = "4096"/    vb.memory = "4096"\n    vb.cpus = 2/' Vagrantfile

echo "Step 9: Fixing end statement..."
sed -i 's/  # end/  end/' Vagrantfile

echo
echo "Configuration complete! Starting VM..."
vagrant up

echo
echo "Setup finished! VM is now running."
echo "To connect to the VM, run: vagrant ssh"
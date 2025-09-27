#!/bin/bash

echo "Setting up Vagrant DNS Lab..."
echo

# Initialize Vagrant
echo "Step 1: Initializing Vagrant..."
vagrant init

# Configure Vagrant box
echo "Step 2: Setting Kali Linux box..."
sed -i 's/config.vm.box = "base"/config.vm.box = "kalilinux\/rolling"/' Vagrantfile

# Configure VirtualBox Provider
echo "Step 3: Configuring VirtualBox provider..."
sed -i 's/  # config.vm.provider "virtualbox" do |vb|/  config.vm.provider "virtualbox" do |vb|/' Vagrantfile

echo "Step 4: Enabling GUI..."
sed -i 's/  #   vb.gui = true/    vb.gui = true/' Vagrantfile

echo "Step 5: Setting memory to 4GB..."
sed -i 's/  #   vb.memory = "1024"/    vb.memory = "4096"/' Vagrantfile

echo "Step 6: Adding CPU configuration..."
sed -i 's/    vb.memory = "4096"/    vb.memory = "4096"\n    vb.cpus = 2/' Vagrantfile

echo "Step 7: Fixing end statement..."
sed -i 's/  # end/  end/' Vagrantfile

echo
echo "Configuration complete! Starting VM..."
vagrant up

echo
echo "Setup finished! VM is now running."
echo "To connect to the VM, run: vagrant ssh"
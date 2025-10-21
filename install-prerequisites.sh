#!/bin/bash

echo "========================================"
echo " Open Network Security Lab Prerequisites"
echo "========================================"
echo
echo "This script will check and install:"
echo "- Vagrant"
echo "- VirtualBox"
echo "- Ansible (optional: required if you provision from the host)"
echo
echo "Note: You may need to run this with sudo"
echo
read -p "Press Enter to continue..."

# Function to install on Ubuntu/Debian
install_ubuntu() {
    echo "Installing for Ubuntu/Debian..."
    
    # Update package list
    sudo apt-get update
    
    # Install VirtualBox
    if ! command -v VBoxManage &> /dev/null; then
        echo "Installing VirtualBox..."
        sudo apt-get install -y virtualbox virtualbox-ext-pack
    fi
    
    # Install Vagrant
    if ! command -v vagrant &> /dev/null; then
        echo "Installing Vagrant..."
        wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
        echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
        sudo apt-get update && sudo apt-get install -y vagrant
    fi

    # Install Ansible (host provisioning support)
    if ! command -v ansible &> /dev/null; then
        echo "Installing Ansible..."
        sudo apt-get install -y ansible
    fi
}

# Function to install on CentOS/RHEL/Fedora
install_rhel() {
    echo "Installing for CentOS/RHEL/Fedora..."
    
    # Install VirtualBox
    if ! command -v VBoxManage &> /dev/null; then
        echo "Installing VirtualBox..."
        sudo dnf install -y VirtualBox
    fi
    
    # Install Vagrant
    if ! command -v vagrant &> /dev/null; then
        echo "Installing Vagrant..."
        sudo dnf install -y dnf-plugins-core
        sudo dnf config-manager --add-repo https://rpm.releases.hashicorp.com/RHEL/hashicorp.repo
        sudo dnf install -y vagrant
    fi

    # Install Ansible
    if ! command -v ansible &> /dev/null; then
        echo "Installing Ansible..."
        sudo dnf install -y ansible
    fi
}

# Function to install on macOS
install_macos() {
    echo "Installing for macOS..."
    
    # Check if Homebrew is installed
    if ! command -v brew &> /dev/null; then
        echo "Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    
    # Install VirtualBox
    if ! command -v VBoxManage &> /dev/null; then
        echo "Installing VirtualBox..."
        brew install --cask virtualbox
    fi
    
    # Install Vagrant
    if ! command -v vagrant &> /dev/null; then
        echo "Installing Vagrant..."
        brew install --cask vagrant
    fi

    # Install Ansible
    if ! command -v ansible &> /dev/null; then
        echo "Installing Ansible..."
        brew install ansible
    fi
}

echo "Checking if Vagrant is installed..."
if command -v vagrant &> /dev/null; then
    echo "✓ Vagrant is already installed"
    vagrant --version
else
    echo "✗ Vagrant not found"
fi

echo
echo "Checking if VirtualBox is installed..."
if command -v VBoxManage &> /dev/null; then
    echo "✓ VirtualBox is already installed"
    VBoxManage --version
else
    echo "✗ VirtualBox not found"
fi

echo
echo "Checking if Ansible is installed..."
if command -v ansible &> /dev/null; then
    echo "✓ Ansible is already installed"
    ansible --version | head -n1
else
    echo "✗ Ansible not found"
fi

# If both are installed, exit
if command -v vagrant &> /dev/null && command -v VBoxManage &> /dev/null && command -v ansible &> /dev/null; then
    echo
    echo "========================================"
    echo " Prerequisites Check Complete!"
    echo "========================================"
    echo
    echo "✓ Vagrant is installed"
    echo "✓ VirtualBox is installed"
    echo "✓ Ansible is installed"
    echo
    echo "You can now run the lab launcher:"
    echo "  ./launch-lab.sh"
    echo
    exit 0
fi

echo
echo "Installing missing prerequisites..."

# Detect OS and install accordingly
if [[ "$OSTYPE" == "darwin"* ]]; then
    install_macos
elif [[ -f /etc/debian_version ]]; then
    install_ubuntu
elif [[ -f /etc/redhat-release ]]; then
    install_rhel
else
    echo "Unsupported operating system. Please install Vagrant and VirtualBox manually:"
    echo "- Vagrant: https://www.vagrantup.com/downloads"
    echo "- VirtualBox: https://www.virtualbox.org/wiki/Downloads"
    exit 1
fi

echo
echo "========================================"
echo " Installation Complete!"
echo "========================================"
echo
echo "You can now run the lab launcher:"
echo "  ./launch-lab.sh"
echo
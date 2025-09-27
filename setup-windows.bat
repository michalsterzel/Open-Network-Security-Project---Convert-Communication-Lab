@echo off
echo Setting up Vagrant DNS Lab...
echo.

REM Initialize Vagrant
echo Step 1: Initializing Vagrant...
vagrant init

REM Configure Vagrant box
echo Step 2: Setting Kali Linux box...
powershell -Command "(Get-Content Vagrantfile) -replace 'config.vm.box = \"base\"', 'config.vm.box = \"kalilinux/rolling\"' | Set-Content Vagrantfile"

REM Configure VirtualBox Provider
echo Step 3: Configuring VirtualBox provider...
powershell -Command "(Get-Content Vagrantfile) -replace '  # config.vm.provider \"virtualbox\" do \\|vb\\|', '  config.vm.provider \"virtualbox\" do |vb|' | Set-Content Vagrantfile"

echo Step 4: Enabling GUI...
powershell -Command "(Get-Content Vagrantfile) -replace '  #   vb.gui = true', '    vb.gui = true' | Set-Content Vagrantfile"

echo Step 5: Setting memory to 4GB...
powershell -Command "(Get-Content Vagrantfile) -replace '  #   vb.memory = \"1024\"', '    vb.memory = \"4096\"' | Set-Content Vagrantfile"

echo Step 6: Adding CPU configuration...
powershell -Command "(Get-Content Vagrantfile) -replace '    vb.memory = \"4096\"', \"    vb.memory = `\"4096`\"`r`n    vb.cpus = 2\" | Set-Content Vagrantfile"

echo Step 7: Fixing end statement...
powershell -Command "(Get-Content Vagrantfile) -replace '  # end', '  end' | Set-Content Vagrantfile"

echo.
echo Configuration complete! Starting VM...
vagrant up

echo.
echo Setup finished! VM is now running.
echo To connect to the VM, run: vagrant ssh
pause
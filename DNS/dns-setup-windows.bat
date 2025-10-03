@echo off
echo Setting up Vagrant DNS Lab...
echo.

REM Remove existing Vagrantfile if it exists
echo Step 1: Cleaning up existing Vagrantfile...
if exist "Vagrantfile" (
    echo Removing existing Vagrantfile...
    del "Vagrantfile"
) else (
    echo No existing Vagrantfile found.
)

REM Initialize Vagrant
echo Step 2: Initializing Vagrant...
vagrant init

REM Configure Vagrant box
echo Step 3: Setting DNS Server box...
powershell -Command "(Get-Content Vagrantfile) -replace 'config.vm.box = \"base\"', 'config.vm.box = \"open_network_security/dns_server\"' | Set-Content Vagrantfile"

REM Set box version
echo Step 4: Setting box version...
powershell -Command "$content = Get-Content Vagrantfile; $index = 0; $newContent = @(); foreach($line in $content) { if($line -match 'config.vm.box = \"open_network_security/dns_server\"') { $newContent += $line; $newContent += '  config.vm.box_version = \"1.0.0\"' } else { $newContent += $line } }; $newContent | Set-Content Vagrantfile"

REM Configure internal network
echo Step 5: Configuring internal network...
powershell -Command "$content = Get-Content Vagrantfile; $index = 0; $newContent = @(); foreach($line in $content) { if($line -match 'config.vm.box_version = \"1.0.0\"') { $newContent += $line; $newContent += ''; $newContent += '  # Set up Internal Network for isolated VM-to-VM communication (VirtualBox specific)'; $newContent += '  # Assign a static IP address for this VM on the internal network'; $newContent += '  config.vm.network \"private_network\", ip: \"192.168.10.1\", virtualbox__intnet: \"labnet\"' } else { $newContent += $line } }; $newContent | Set-Content Vagrantfile"

REM Configure VirtualBox Provider - Use simpler approach
echo Step 6: Configuring VirtualBox provider...
powershell -Command "$content = Get-Content Vagrantfile; $content = $content -replace '  # config.vm.provider \"virtualbox\" do \|vb\|', '  config.vm.provider \"virtualbox\" do |vb|'; $content = $content -replace '  #   vb.gui = true', '    vb.gui = true'; $content = $content -replace '  #   vb.memory = \"1024\"', '    vb.memory = \"4096\"'; $content = $content -replace '  # end', '  end'; $content | Set-Content Vagrantfile"

echo Step 7: Adding CPU configuration...
powershell -Command "$content = Get-Content Vagrantfile; $index = 0; $newContent = @(); foreach($line in $content) { if($line -match 'vb.memory = \"4096\"') { $newContent += $line; $newContent += '    vb.cpus = 2' } else { $newContent += $line } }; $newContent | Set-Content Vagrantfile"

echo.
echo Configuration complete! Starting VM...
vagrant up

echo.
echo Setup finished! VM is now running.
echo To connect to the VM, run: vagrant ssh
pause
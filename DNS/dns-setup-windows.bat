@echo off
echo Setting up Vagrant DNS Lab...
echo.

REM Initialize Vagrant
echo Step 1: Initializing Vagrant...
vagrant init

REM Configure Vagrant box
echo Step 2: Setting Kali Linux box...
powershell -Command "(Get-Content Vagrantfile) -replace 'config.vm.box = \"base\"', 'config.vm.box = \"kalilinux/rolling\"' | Set-Content Vagrantfile"

REM Configure VirtualBox Provider - Use simpler approach
echo Step 3: Configuring VirtualBox provider...
powershell -Command "$content = Get-Content Vagrantfile; $content = $content -replace '  # config.vm.provider \"virtualbox\" do \|vb\|', '  config.vm.provider \"virtualbox\" do |vb|'; $content = $content -replace '  #   vb.gui = true', '    vb.gui = true'; $content = $content -replace '  #   vb.memory = \"1024\"', '    vb.memory = \"4096\"'; $content = $content -replace '  # end', '  end'; $content | Set-Content Vagrantfile"

echo Step 4: Adding CPU configuration...
powershell -Command "$content = Get-Content Vagrantfile; $index = 0; $newContent = @(); foreach($line in $content) { if($line -match 'vb.memory = \"4096\"') { $newContent += $line; $newContent += '    vb.cpus = 2' } else { $newContent += $line } }; $newContent | Set-Content Vagrantfile"

echo.
echo Configuration complete! Starting VM...
vagrant up

echo.
echo Setup finished! VM is now running.
echo To connect to the VM, run: vagrant ssh
pause
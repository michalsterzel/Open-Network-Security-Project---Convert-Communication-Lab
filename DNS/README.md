Step 1:
(Get-Content Vagrantfile) -replace 'config.vm.box = "base"', 'config.vm.box = "kalilinux/rolling"' | Set-Content Vagrantfile

Step 2:
(Get-Content Vagrantfile) -replace '  # vb.memory = "1024"', '  vb.memory = "4096"' | Set-Content Vagrantfile
(Get-Content Vagrantfile) -replace '  # vb.cpus = 2', '  vb.cpus = 4' | Set-Content Vagrantfile


Step 3:
Uncomment the VirtualBox provider section in Vagrantfile:
Modify the amount of memory for the VM to 4 GB (4096 MB):
(Get-Content Vagrantfile) -replace 'vb.memory = "1024"', 'vb.memory = "4096"' | Set-Content Vagrantfile

This command updates the VM memory setting in the Vagrantfile to 4096 MB (4 GB).

Set the number of CPUs for the VM to 2:
(Get-Content Vagrantfile) -replace 'vb.cpus = [0-9]+', 'vb.cpus = 2' | Set-Content Vagrantfile

This command sets the VM CPUs to 2 in the Vagrantfile.
(Get-Content Vagrantfile) | ForEach-Object {
	if ($_ -match '^\s*#\s?config\.vm\.provider "virtualbox" do \|vb\|' -or
		$_ -match '^\s*#\s{3}# Display the VirtualBox GUI when booting the machine' -or
		$_ -match '^\s*#\s{3}vb\.gui = true' -or
		$_ -match '^\s*#\s*$' -or
		$_ -match '^\s*#\s{3}# Customize the amount of memory on the VM:' -or
		$_ -match '^\s*#\s{3}vb\.memory = "1024"' -or
		$_ -match '^\s*#\s{3}end') {
		$_ -replace '^\s*#\s?', ''
	} else {
		$_
	}
} | Set-Content Vagrantfile

This command will only uncomment the lines in the VirtualBox provider section.

Uncomment the 'end' clause in Vagrantfile:
(Get-Content Vagrantfile) -replace '^\s*#\s*end', 'end' | Set-Content Vagrantfile

This command will uncomment any line that starts with '# end'.





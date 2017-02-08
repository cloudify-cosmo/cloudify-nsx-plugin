<#
.SYNOPSIS
  Example how to run Platformtest of Cloudify NSX plugin on powershell

.DESCRIPTION
  The script run set of tests covering common NSX plugin features.

  Before run the script next programs and components should be installed
  1. python 2.7.9
  2. VCForPython27.msi (http://aka.ms/vcpython27)
#>


Add-Type -AssemblyName System.IO.Compression.FileSystem

# Create work directory and set it as current
$dir= Get-Location
$wd = New-Item -ItemType directory -Path ($dir.Path + "\platform_Test")
Set-Location -Path $wd

# Download vsphere-plugin and NSX-plugin
(New-Object System.Net.WebClient).DownloadFile("https://github.com/cloudify-cosmo/cloudify-vsphere-plugin/archive/2.1.0.zip", "$wd\2.1.0.zip")
(New-Object System.Net.WebClient).DownloadFile("https://github.com/cloudify-cosmo/cloudify-nsx-plugin/archive/master.zip", "$wd\master.zip")

# Unzip plugins
[System.IO.Compression.ZipFile]::ExtractToDirectory("$wd\2.1.0.zip", $wd)
[System.IO.Compression.ZipFile]::ExtractToDirectory("$wd\master.zip", $wd)

# Create python virtual env and activate it
virtualenv .
.\Scripts\activate

# Install CFY CLI
Invoke-WebRequest -Uri "http://gigaspaces-repository-eu.s3.amazonaws.com/org/cloudify3/get-cloudify.py" -OutFile "get-cloudify.py"
python get-cloudify.py --version 3.4.0 --upgrade

# Install plugins localy
pip install -e .\cloudify-nsx-plugin-master\
pip install -r .\cloudify-nsx-plugin-master\test-requirements.txt
pip install -e .\cloudify-vsphere-plugin-2.1.0\
pip install -r .\cloudify-vsphere-plugin-2.1.0\test-requirements.txt

# inputs for platform tests
#NSX
$env:NSX_IP="<nsx_ip>"
$env:NSX_USER="<nsx_user>"
$env:NSX_PASSWORD="<nsx_password>"
#VCENTER
$env:VCENTER_HOST="<vcenter_host>"
$env:VCENTER_PORT="443"
$env:VCENTER_USERNAME="<vcenter_username>"
$env:VCENTER_PASSWORD="<vcenter_password>"
#optional
$env:VCENTER_DATACENTER_NAME="<vcenter_datacenter_name>"
$env:VCENTER_RESOURCE_POOL_NAME="<vcenter_resource_pool>"
$env:VCENTER_AUTO_PLACEMENT="true" # if cluster is used set true
#prefixes
$env:NODE_NAME_PREFIX="<PREFIX>"

nosetests -v --with-coverage --cover-package=cloudify_nsx cloudify-nsx-plugin-master/tests/platformtests/ cloudify-nsx-plugin-master/tests/unittests/

deactivate
cd ..
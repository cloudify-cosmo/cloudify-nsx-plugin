# cloudify-nsx-plugin
Cloudify Network Virtualization with VMware (NSX) plugin

# Check platform example
```

# get plugin codebase
git clone https://github.com/cloudify-cosmo/cloudify-nsx-plugin.git

# install plugin localy
pip install -e cloudify-nsx-plugin/
pip install -r cloudify-nsx-plugin/test-requirements.txt

# inputs for platform tests
export NSX_IP="<nsx_ip>"
export NSX_USER="<nsx_user>"
export NSX_PASSWORD="<nsx_password>"
export NODE_NAME_PREFIX="<some_free_prefix_for_objects>"
export VSPHERE_USERNAME=<vsphere username>
export VSPHERE_PASSWORD=<vsphere password>
export VSPHERE_HOST=<vsphere host IP>
export VSPHERE_PORT=443
export VSPHERE_DATACENTER_NAME=<Datacenter name>
export VSPHERE_RESOURCE_POOL_NAME=<Resource pool name>
export VSPHERE_AUTO_PLACEMENT=true
export VSPHERE_CENTOS_NAME=<VM name>
export VSPHERE_CENTOS_IMAGE=<Template name>
export VSPHERE_CENTOS_AGENT_INSTALL_METHOD=none
export VSPHERE_AGENT_USER=<cloudify agent user>
export VSPHERE_AGENT_KEY=<SSH private key file>
export NAME_OF_TAG=<name of security tag>
export POLICY_NAME=<security policy name>
export SECURITY_GROUP_NAME=<security group name>
export NESTED_SECURITY_GROUP_NAME=<nested security group name>
export PREFIX=<prefix>

# cleanup previous results
rm .coverage -rf

# check state
nosetests -v --with-coverage --cover-package=cloudify_nsx cloudify-nsx-plugin/tests/platformtests/ cloudify-nsx-plugin/tests/unittests/

```
# Check total coverage and full functionality
```

# get plugin codebase
git clone https://github.com/cloudify-cosmo/cloudify-nsx-plugin.git
git clone https://github.com/cloudify-cosmo/cloudify-vsphere-plugin.git

# install plugin localy
pip install -e cloudify-nsx-plugin/
pip install -r cloudify-nsx-plugin/test-requirements.txt

cd cloudify-vsphere-plugin/ && git checkout 2.3.0-m1 && cd ..
pip install -e cloudify-vsphere-plugin/
pip install -r cloudify-vsphere-plugin/test-requirements.txt

# inputs for platform tests
# NSX
export NSX_IP="<nsx_ip>"
export NSX_USER="<nsx_user>"
export NSX_PASSWORD="<nsx_password>"
# VCENTER
export VCENTER_IP="<vcenter_ip>"
export VCENTER_USER="<vcenter_user>"
export VCENTER_PASSWORD="<vcenter_password>"
# optional
export VCENTER_DATASTORE="<vcenter_datastore>"
export VCENTER_DATACENTER="<vcenter_datacenter>"
export VCENTER_TEMPLATE="<vcenter_linux_template>"
export VCENTER_CLUSTER="<vcenter_cluster>"
export VCENTER_RESOURCE_POOL="<vcenter_resource_pool>"
# prefixes
export NODE_NAME_PREFIX="<some_free_prefix_for_objects>"

# cleanup previous results
rm .coverage -rf

# check state
nosetests -v --with-coverage --cover-package=cloudify_nsx cloudify-nsx-plugin/tests/

```

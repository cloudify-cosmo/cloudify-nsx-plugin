# cloudify-nsx-plugin
Cloudify Network Virtualization with VMware (NSX) plugin

# Check platform example
```

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

# get plugin codebase
git clone https://github.com/cloudify-cosmo/cloudify-nsx-plugin.git

# install plugin localy
pip install -e cloudify-nsx-plugin/
pip install -r cloudify-nsx-plugin/test-requirements.txt

# cleanup previous results
rm .coverage -rf

# check state
nosetests -v --with-coverage --cover-package=cloudify_nsx cloudify-nsx-plugin/tests/

```

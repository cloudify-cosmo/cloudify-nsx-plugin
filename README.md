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

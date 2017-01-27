# cloudify-nsx-plugin
Cloudify Network Virtualization with VMware (NSX) plugin

# Check platform example
```

export NSX_IP="<nsx_ip>"
export NSX_USER="<nsx_user>"
export NSX_PASSWORD="<nsx_password>"
export NODE_NAME_PREFIX="<some_free_prefix_for_objects>"

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

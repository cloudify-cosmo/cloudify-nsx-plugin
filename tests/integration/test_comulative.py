########
# Copyright (c) 2017 GigaSpaces Technologies Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
#    * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    * See the License for the specific language governing permissions and
#    * limitations under the License.

# Stdlib imports
import os

# Third party imports
import unittest
import pytest

# Cloudify imports
from cloudify.workflows import local
from cloudify_cli import constants as cli_constants


class ComulativeTest(unittest.TestCase):

    def setUp(self):
        super(ComulativeTest, self).setUp()
        self.comulative_env = None
        self.ext_inputs = {
            # prefix for run
            'node_name_prefix': os.environ.get('NODE_NAME_PREFIX', ""),
            # nsx inputs
            'nsx_ip': os.environ.get('NSX_IP'),
            'nsx_user': os.environ.get('NSX_USER'),
            'nsx_password': os.environ.get('NSX_PASSWORD'),
            # vcenter inputs
            'vcenter_ip': os.environ.get('VCENTER_IP'),
            'vcenter_user': os.environ.get('VCENTER_USER'),
            'vcenter_password': os.environ.get('VCENTER_PASSWORD')
        }

        if (
            not self.ext_inputs['nsx_ip'] or
            not self.ext_inputs['nsx_ip'] or
            not self.ext_inputs['nsx_password']
        ):
                self.skipTest("You dont have credentials for nsx")

        if (
            not self.ext_inputs['vcenter_ip'] or
            not self.ext_inputs['vcenter_ip'] or
            not self.ext_inputs['vcenter_password']
        ):
                self.skipTest("You dont have credentials for vcenter")

        blueprints_path = os.path.split(os.path.abspath(__file__))[0]
        self.blueprints_path = os.path.join(
            blueprints_path,
            'resources'
        )

    def tearDown(self):
        if self.comulative_env:
            try:
                self.comulative_env.execute(
                    'uninstall',
                    task_retries=50,
                    task_retry_interval=3,
                )
            except Exception as ex:
                print str(ex)
        super(ComulativeTest, self).tearDown()

    def _common_run(self, name, inputs):
        # set blueprint name
        blueprint = os.path.join(
            self.blueprints_path,
            name
        )

        # cfy local init
        self.comulative_env = local.init_env(
            blueprint,
            inputs=inputs,
            name=self._testMethodName,
            ignored_modules=cli_constants.IGNORED_LOCAL_WORKFLOW_MODULES)

        # cfy local execute -w install
        self.comulative_env.execute(
            'install',
            task_retries=50,
            task_retry_interval=3,
        )

        # cfy local execute -w uninstall
        self.comulative_env.execute(
            'uninstall',
            task_retries=50,
            task_retry_interval=3,
        )

        self.comulative_env = None

    @pytest.mark.external
    def test_securitytag(self):
        """Dry run: Check security tag functionality"""
        inputs = {k: self.ext_inputs[k] for k in self.ext_inputs}

        if os.environ.get('VCENTER_DATASTORE'):
            inputs['vcenter_datastore'] = os.environ.get('VCENTER_DATASTORE')
        if os.environ.get('VCENTER_DATACENTER'):
            inputs['vcenter_datacenter'] = os.environ.get('VCENTER_DATACENTER')
        if os.environ.get('VCENTER_TEMPLATE'):
            inputs['template_name'] = os.environ.get('VCENTER_TEMPLATE')

        self._common_run('security_functionality.yaml', inputs)

    @pytest.mark.external
    def test_dlr(self):
        """Dry run: Check dlr functionality"""
        inputs = {k: self.ext_inputs[k] for k in self.ext_inputs}

        if os.environ.get('VCENTER_CLUSTER'):
            inputs['vcenter_cluster'] = os.environ.get('VCENTER_CLUSTER')
        if os.environ.get('VCENTER_DATASTORE'):
            inputs['vcenter_datastore'] = os.environ.get('VCENTER_DATASTORE')
        if os.environ.get('VCENTER_DATACENTER'):
            inputs['vcenter_datacenter'] = os.environ.get('VCENTER_DATACENTER')
        if os.environ.get('VCENTER_RESOURCE_POOL'):
            inputs['vcenter_resource_pool'] = os.environ.get(
                'VCENTER_RESOURCE_POOL'
            )
        if os.environ.get('VCENTER_TEMPLATE'):
            inputs['template_name'] = os.environ.get('VCENTER_TEMPLATE')

        self._common_run('dlr_functionality.yaml', inputs)

    @pytest.mark.external
    def test_dlr_bgp(self):
        """Dry run: Check dlr with bgp routing functionality"""
        inputs = {k: self.ext_inputs[k] for k in self.ext_inputs}

        if os.environ.get('VCENTER_CLUSTER'):
            inputs['vcenter_cluster'] = os.environ.get('VCENTER_CLUSTER')
        if os.environ.get('VCENTER_DATASTORE'):
            inputs['vcenter_datastore'] = os.environ.get('VCENTER_DATASTORE')
        if os.environ.get('VCENTER_DATACENTER'):
            inputs['vcenter_datacenter'] = os.environ.get('VCENTER_DATACENTER')
        if os.environ.get('VCENTER_RESOURCE_POOL'):
            inputs['vcenter_resource_pool'] = os.environ.get(
                'VCENTER_RESOURCE_POOL'
            )

        self._common_run('dlr_with_bgp_functionality.yaml', inputs)

    @pytest.mark.external
    def test_esg(self):
        """Dry run: Check edge gateway functionality"""
        inputs = {k: self.ext_inputs[k] for k in self.ext_inputs}

        if os.environ.get('VCENTER_CLUSTER'):
            inputs['vcenter_cluster'] = os.environ.get('VCENTER_CLUSTER')
        if os.environ.get('VCENTER_DATASTORE'):
            inputs['vcenter_datastore'] = os.environ.get('VCENTER_DATASTORE')
        if os.environ.get('VCENTER_DATACENTER'):
            inputs['vcenter_datacenter'] = os.environ.get('VCENTER_DATACENTER')
        if os.environ.get('VCENTER_RESOURCE_POOL'):
            inputs['vcenter_resource_pool'] = os.environ.get(
                'VCENTER_RESOURCE_POOL'
            )

        self._common_run('esg_functionality.yaml', inputs)

    @pytest.mark.external
    def test_esg_ospf(self):
        """Dry run: Check edge gateway with ospf routing functionality"""
        inputs = {k: self.ext_inputs[k] for k in self.ext_inputs}

        if os.environ.get('VCENTER_CLUSTER'):
            inputs['vcenter_cluster'] = os.environ.get('VCENTER_CLUSTER')
        if os.environ.get('VCENTER_DATASTORE'):
            inputs['vcenter_datastore'] = os.environ.get('VCENTER_DATASTORE')
        if os.environ.get('VCENTER_DATACENTER'):
            inputs['vcenter_datacenter'] = os.environ.get('VCENTER_DATACENTER')
        if os.environ.get('VCENTER_RESOURCE_POOL'):
            inputs['vcenter_resource_pool'] = os.environ.get(
                'VCENTER_RESOURCE_POOL'
            )

        self._common_run('esg_with_ospf_functionality.yaml', inputs)


if __name__ == '__main__':
    unittest.main()

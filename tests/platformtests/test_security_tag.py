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
import mock

# Cloudify imports
from cloudify.workflows import local
from cloudify_cli import constants as cli_constants
import cloudify_nsx.library.nsx_security_tag as nsx_security_tag
import cloudify_nsx.library.nsx_security_group as nsx_security_group
import cloudify_nsx.library.nsx_security_policy as nsx_security_policy
import cloudify_nsx.library.nsx_common as common
from cloudify import mocks as cfy_mocks
from cloudify.state import current_ctx


class SecurityTagTest(unittest.TestCase):

    def setUp(self):
        super(SecurityTagTest, self).setUp()
        self.ext_inputs = {
            'node_name_prefix': os.environ.get('NODE_NAME_PREFIX'),
            'nsx_ip': os.environ.get('NSX_IP'),
            'nsx_user': os.environ.get('NSX_USER'),
            'nsx_password': os.environ.get('NSX_PASSWORD'),
        }

        blueprints_path = os.path.split(os.path.abspath(__file__))[0]
        self.blueprints_path = os.path.join(
            blueprints_path,
            'resources'
        )

        self.fake_ctx = cfy_mocks.MockCloudifyContext()
        instance = mock.Mock()
        instance.runtime_properties = {}
        self.fake_ctx._instance = instance
        node = mock.Mock()
        self.fake_ctx._node = node
        node.properties = {}
        node.runtime_properties = {}
        current_ctx.set(self.fake_ctx)

        # credentials
        self.client_session = common.nsx_login({
            'nsx_auth': {
                'username': self.ext_inputs['nsx_user'],
                'password': self.ext_inputs['nsx_password'],
                'host': self.ext_inputs['nsx_ip']
            }
        })

    def tearDown(self):
        current_ctx.clear()

    def test_securitytag(self):
        """Deploying security tag minimal test"""

        # set blueprint name
        blueprint = os.path.join(
            self.blueprints_path,
            'security_tag.yaml'
        )

        # check prexist of security tag
        resource_id, _ = nsx_security_tag.get_tag(
            self.client_session,
            self.ext_inputs['node_name_prefix'] + "secret_tag"
        )

        self.assertTrue(resource_id is None)

        # cfy local init
        self.security_tag_env = local.init_env(
            blueprint,
            inputs=self.ext_inputs,
            name=self._testMethodName,
            ignored_modules=cli_constants.IGNORED_LOCAL_WORKFLOW_MODULES)

        # cfy local execute -w install
        self.security_tag_env.execute(
            'install',
            task_retries=50,
            task_retry_interval=3,
        )

        # check security tag properties
        resource_id, info = nsx_security_tag.get_tag(
            self.client_session,
            self.ext_inputs['node_name_prefix'] + "secret_tag"
        )

        self.assertTrue(resource_id is not None)
        self.assertTrue(info is not None)

        self.assertEqual(
            info['name'], self.ext_inputs['node_name_prefix'] + "secret_tag"
        )
        self.assertEqual(info['description'], "What can i say?")

        # cfy local execute -w uninstall
        self.security_tag_env.execute(
            'uninstall',
            task_retries=50,
            task_retry_interval=3,
        )

        # must be deleted
        resource_id, _ = nsx_security_tag.get_tag(
            self.client_session,
            self.ext_inputs['node_name_prefix'] + "secret_tag"
        )

        self.assertTrue(resource_id is None)


    def test_yet_another_security_tag(self):
        """Yet another deploying security tag minimal test"""

        # Define inputs related to this function
        local_inputs = {
            'nsx_ip': os.environ.get('NSX_IP'),
            'nsx_user': os.environ.get('NSX_USER'),
            'nsx_password': os.environ.get('NSX_PASSWORD'),
            'vsphere_username': str(os.environ.get('VSPHERE_USERNAME')),
            'vsphere_password': str(os.environ.get('VSPHERE_PASSWORD')),
            'vsphere_host': str(os.environ.get('VSPHERE_HOST')),
            'vsphere_port': str(os.environ.get('VSPHERE_PORT')),
            'vsphere_datacenter_name': str(os.environ.get('VSPHERE_DATACENTER_NAME')),
            'vsphere_resource_pool_name': str(os.environ.get('VSPHERE_RESOURCE_POOL_NAME')),
            'vsphere_auto_placement': str(os.environ.get('VSPHERE_AUTO_PLACEMENT')),
            'vsphere_centos_name': str(os.environ.get('VSPHERE_CENTOS_NAME')),
            'vsphere_centos_image': str(os.environ.get('VSPHERE_CENTOS_IMAGE')),
            'vsphere_centos_agent_install_method': str(os.environ.get('VSPHERE_CENTOS_AGENT_INSTALL_METHOD')),
            'vsphere_agent_user': str(os.environ.get('VSPHERE_AGENT_USER')),
            'vsphere_agent_key': str(os.environ.get('VSPHERE_AGENT_KEY')),
            'name_of_tag': str(os.environ.get('NAME_OF_TAG')),
            'prefix': str(os.environ.get('PREFIX')),
        }

        # set blueprint name
        blueprint = os.path.join(
            self.blueprints_path,
            'security_tag/blueprint.yaml'
        )

        # check prexist of security tag
        resource_id, _ = nsx_security_tag.get_tag(
            self.client_session,
            local_inputs['prefix'] + local_inputs['name_of_tag']
        )

        self.assertTrue(resource_id is None)

        # cfy local init
        self.security_tag_env = local.init_env(
            blueprint,
            inputs=local_inputs,
            name=self._testMethodName,
            ignored_modules=cli_constants.IGNORED_LOCAL_WORKFLOW_MODULES)

        # cfy local execute -w install
        self.security_tag_env.execute(
            'install',
            task_retries=4,
            task_retry_interval=3,
        )

        # check security tag properties
        resource_id, info = nsx_security_tag.get_tag(
            self.client_session,
            local_inputs['prefix'] + local_inputs['name_of_tag']
        )

        self.assertTrue(resource_id is not None)
        self.assertTrue(info is not None)

        self.assertEqual(
            info['name'], local_inputs['prefix'] + local_inputs['name_of_tag']
        )
        self.assertEqual(info['description'], "Example security tag which will be assigned to example VM")

        # cfy local execute -w uninstall
        self.security_tag_env.execute(
            'uninstall',
            task_retries=50,
            task_retry_interval=3,
        )

        # must be deleted
        resource_id, _ = nsx_security_tag.get_tag(
            self.client_session,
            local_inputs['prefix'] + local_inputs['name_of_tag']
        )

        self.assertTrue(resource_id is None)


    def test_security_group(self):
        """Deploying security group minimal test"""

        # Define inputs related to this function
        local_inputs = {
            'nsx_ip': os.environ.get('NSX_IP'),
            'nsx_user': os.environ.get('NSX_USER'),
            'nsx_password': os.environ.get('NSX_PASSWORD'),
            'security_group_name': os.environ.get('SECURITY_GROUP_NAME'),
            'nested_security_group_name': os.environ.get('NESTED_SECURITY_GROUP_NAME'),
            'prefix': str(os.environ.get('PREFIX')),
        }

        # set blueprint name
        blueprint = os.path.join(
            self.blueprints_path,
            'security_groups/blueprint.yaml'
        )

        # check prexist of security groups
        resource_id = nsx_security_group.get_group(
            self.client_session,
            'globalroot-0',
            local_inputs['prefix'] + local_inputs['security_group_name']
        )

        self.assertTrue(resource_id is None)

        resource_id = nsx_security_group.get_group(
            self.client_session,
            'globalroot-0',
            local_inputs['prefix'] + local_inputs['nested_security_group_name']
        )

        self.assertTrue(resource_id is None)

        # cfy local init
        self.security_group_env = local.init_env(
            blueprint,
            inputs=local_inputs,
            name=self._testMethodName,
            ignored_modules=cli_constants.IGNORED_LOCAL_WORKFLOW_MODULES)

        # cfy local execute -w install
        self.security_group_env.execute(
            'install',
            task_retries=4,
            task_retry_interval=3,
        )

        # check security groups properties
        resource_id = nsx_security_group.get_group(
            self.client_session,
            'globalroot-0',
            local_inputs['prefix'] + local_inputs['security_group_name']
        )

        self.assertTrue(resource_id is not None)

        resource_id = nsx_security_group.get_group(
            self.client_session,
            'globalroot-0',
            local_inputs['prefix'] + local_inputs['nested_security_group_name']
        )

        self.assertTrue(resource_id is not None)

        # cfy local execute -w uninstall
        self.security_group_env.execute(
            'uninstall',
            task_retries=50,
            task_retry_interval=3,
        )

        # must be deleted
        resource_id = nsx_security_group.get_group(
            self.client_session,
            'globalroot-0',
            local_inputs['prefix'] + local_inputs['security_group_name']
        )

        self.assertTrue(resource_id is None)

        resource_id = nsx_security_group.get_group(
            self.client_session,
            'globalroot-0',
            local_inputs['prefix'] + local_inputs['nested_security_group_name']
        )

        self.assertTrue(resource_id is None)

    def test_security_policy(self):
        """Deploying security policy minimal test"""

        # Define inputs related to this function
        local_inputs = {
            'nsx_ip': os.environ.get('NSX_IP'),
            'nsx_user': os.environ.get('NSX_USER'),
            'nsx_password': os.environ.get('NSX_PASSWORD'),
            'policy_name': os.environ.get('POLICY_NAME'),
            'prefix': str(os.environ.get('PREFIX')),
        }

        # set blueprint name
        blueprint = os.path.join(
            self.blueprints_path,
            'security_policy/blueprint.yaml'
        )

        # check prexist of security policy
        resource_id, policy = nsx_security_policy.get_policy(
            self.client_session,
            local_inputs['prefix'] + local_inputs['policy_name']
        )

        self.assertTrue(resource_id is None)

        # cfy local init
        self.security_group_env = local.init_env(
            blueprint,
            inputs=local_inputs,
            name=self._testMethodName,
            ignored_modules=cli_constants.IGNORED_LOCAL_WORKFLOW_MODULES)

        # cfy local execute -w install
        self.security_group_env.execute(
            'install',
            task_retries=4,
            task_retry_interval=3,
        )

        # check security policy properties
        resource_id, policy = nsx_security_policy.get_policy(
            self.client_session,
            local_inputs['prefix'] + local_inputs['policy_name']
        )

        self.assertTrue(resource_id is not None)
        self.assertTrue(policy is not None)

        # cfy local execute -w uninstall
        self.security_group_env.execute(
            'uninstall',
            task_retries=50,
            task_retry_interval=3,
        )

        # must be deleted
        resource_id, policy = nsx_security_policy.get_policy(
            self.client_session,
            local_inputs['prefix'] + local_inputs['policy_name']
        )

        self.assertTrue(resource_id is None)


    def test_security_policy_bind(self):
        """Bind security policy to security group minimal test"""

        # Define inputs related to this function
        local_inputs = {
            'nsx_ip': os.environ.get('NSX_IP'),
            'nsx_user': os.environ.get('NSX_USER'),
            'nsx_password': os.environ.get('NSX_PASSWORD'),
            'security_group_name': os.environ.get('SECURITY_GROUP_NAME'),
            'policy_name': os.environ.get('POLICY_NAME'),
            'prefix': str(os.environ.get('PREFIX')),
        }

        # set blueprint name
        blueprint = os.path.join(
            self.blueprints_path,
            'bind_policy_group/blueprint.yaml'
        )

        # check prexist of security policy
        resource_id, policy = nsx_security_policy.get_policy(
            self.client_session,
            local_inputs['prefix'] + local_inputs['policy_name']
        )

        self.assertTrue(resource_id is None)

        # check prexist of security group
        resource_id = nsx_security_group.get_group(
            self.client_session,
            'globalroot-0',
            local_inputs['prefix'] + local_inputs['security_group_name']
        )

        self.assertTrue(resource_id is None)

        # cfy local init
        self.security_group_env = local.init_env(
            blueprint,
            inputs=local_inputs,
            name=self._testMethodName,
            ignored_modules=cli_constants.IGNORED_LOCAL_WORKFLOW_MODULES)

        # cfy local execute -w install
        self.security_group_env.execute(
            'install',
            task_retries=4,
            task_retry_interval=3,
        )

        # check security policy properties
        resource_id, policy = nsx_security_policy.get_policy(
            self.client_session,
            local_inputs['prefix'] + local_inputs['policy_name']
        )

        self.assertTrue(resource_id is not None)
        self.assertTrue(policy is not None)

        # check security group
        resource_id = nsx_security_group.get_group(
            self.client_session,
            'globalroot-0',
            local_inputs['prefix'] + local_inputs['security_group_name']
        )

        self.assertTrue(resource_id is not None)

        # cfy local execute -w uninstall
        self.security_group_env.execute(
            'uninstall',
            task_retries=50,
            task_retry_interval=3,
        )

        # must be deleted
        resource_id, policy = nsx_security_policy.get_policy(
            self.client_session,
            local_inputs['prefix'] + local_inputs['policy_name']
        )

        self.assertTrue(resource_id is None)

        resource_id = nsx_security_group.get_group(
            self.client_session,
            'globalroot-0',
            local_inputs['prefix'] + local_inputs['security_group_name']
        )

        self.assertTrue(resource_id is None)

if __name__ == '__main__':
    unittest.main()

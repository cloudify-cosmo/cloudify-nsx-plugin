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
        super(SecurityTagTest, self).tearDown()

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


if __name__ == '__main__':
    unittest.main()

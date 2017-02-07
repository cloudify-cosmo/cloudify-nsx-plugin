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
import cloudify_nsx.library.nsx_common as common
from cloudify import mocks as cfy_mocks
from cloudify.state import current_ctx


class BaseTest(unittest.TestCase):

    def setUp(self):
        super(BaseTest, self).setUp()
        self.local_env = None
        self.ext_inputs = {
            # prefix for run
            'node_name_prefix': os.environ.get('NODE_NAME_PREFIX', ""),
            # nsx inputs
            'nsx_ip': os.environ.get('NSX_IP'),
            'nsx_user': os.environ.get('NSX_USER'),
            'nsx_password': os.environ.get('NSX_PASSWORD'),
        }

        if (
            not self.ext_inputs['nsx_ip'] or
            not self.ext_inputs['nsx_ip'] or
            not self.ext_inputs['nsx_password']
        ):
                self.skipTest("You dont have credentials for nsx")

        blueprints_path = os.path.split(os.path.abspath(__file__))[0]
        self.blueprints_path = os.path.join(
            blueprints_path,
            'resources'
        )

        self._regen_ctx()

        # credentials
        self.client_session = common.nsx_login({
            'nsx_auth': {
                'username': self.ext_inputs['nsx_user'],
                'password': self.ext_inputs['nsx_password'],
                'host': self.ext_inputs['nsx_ip']
            }
        })

    def _regen_ctx(self):
        self.fake_ctx = cfy_mocks.MockCloudifyContext()
        instance = mock.Mock()
        instance.runtime_properties = {}
        self.fake_ctx._instance = instance
        node = mock.Mock()
        self.fake_ctx._node = node
        node.properties = {}
        node.runtime_properties = {}
        current_ctx.set(self.fake_ctx)

    def tearDown(self):
        current_ctx.clear()
        if self.local_env:
            try:
                self.local_env.execute(
                    'uninstall',
                    task_retries=50,
                    task_retry_interval=3,
                )
            except Exception as ex:
                print str(ex)
        super(BaseTest, self).tearDown()

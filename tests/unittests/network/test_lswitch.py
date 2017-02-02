# Copyright (c) 2015 GigaSpaces Technologies Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import unittest
import mock
import pytest
import cloudify_nsx.network.lswitch as lswitch
from cloudify import mocks as cfy_mocks
from cloudify.state import current_ctx


class LswitchTest(unittest.TestCase):

    def setUp(self):
        super(LswitchTest, self).setUp()
        self._regen_ctx()

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
        super(LswitchTest, self).tearDown()

    @pytest.mark.internal
    @pytest.mark.unit
    def test_install(self):
        """Check create logical swicth"""
        self.fake_ctx.instance.runtime_properties['resource_id'] = "some_id"
        fake_client = mock.Mock()
        fake_get_logical_switch = mock.MagicMock(return_value={
            'vdsContextWithBacking': {
                'backingValue': "some_port_id"
            }
        })

        with mock.patch(
            'cloudify_nsx.library.nsx_common.NsxClient',
            mock.MagicMock(return_value=fake_client)
        ):
            with mock.patch(
                'cloudify_nsx.library.nsx_lswitch.get_logical_switch',
                fake_get_logical_switch
            ):
                lswitch.create(ctx=self.fake_ctx,
                               switch={"name": "name",
                                       "transport_zone": "transport_zone"},
                               nsx_auth={'username': 'username',
                                         'password': 'password',
                                         'host': 'host'})
        fake_get_logical_switch.assert_called_with(
            fake_client, 'some_id'
        )
        self.assertEqual(
            self.fake_ctx.instance.runtime_properties['vsphere_network_id'],
            "some_port_id"
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_uninstall(self):
        """Check delete logical switch"""
        self.fake_ctx.instance.runtime_properties['resource_id'] = None
        lswitch.delete(ctx=self.fake_ctx,
                       switch={})


if __name__ == '__main__':
    unittest.main()

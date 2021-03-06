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
import cloudify_nsx.network.dlr as dlr
from cloudify import mocks as cfy_mocks
from cloudify.state import current_ctx


class DlrTest(unittest.TestCase):

    def setUp(self):
        super(DlrTest, self).setUp()
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
        super(DlrTest, self).tearDown()

    @pytest.mark.internal
    @pytest.mark.unit
    def test_install(self):
        """Check create dlr"""
        self.fake_ctx.instance.runtime_properties['resource_id'] = "some_id"
        fake_client = mock.Mock()
        fake_dlr_esg = mock.Mock()
        fake_dlr_esg.update_common_edges = mock.MagicMock()
        fake_dlr_esg.get_uplink_vnic = mock.MagicMock(return_value='vnic_id')
        props_update = mock.MagicMock(return_value={"esg": "struct"})
        with mock.patch(
            'cloudify_nsx.library.nsx_common.' +
            'possibly_assign_vm_creation_props',
            props_update
        ):
            with mock.patch(
                'cloudify_nsx.library.nsx_common.NsxClient',
                mock.MagicMock(return_value=fake_client)
            ):
                with mock.patch(
                    'cloudify_nsx.network.dlr.nsx_dlr',
                    fake_dlr_esg
                ):
                    dlr.create(ctx=self.fake_ctx,
                               router={"name": "name",
                                       "dlr_pwd": "dlr_pwd",
                                       "ha_ls_id": "ha_ls_id",
                                       "uplink_ls_id": "uplink_ls_id",
                                       "uplink_ip": "uplink_ip",
                                       "uplink_subnet": "uplink_subnet",
                                       "uplink_dgw": "uplink_dgw"},
                               nsx_auth={'username': 'username',
                                         'password': 'password',
                                         'host': 'host'})

        fake_dlr_esg.get_uplink_vnic.assert_called_with(
            fake_client, 'some_id', 'uplink_ls_id'
        )
        fake_dlr_esg.update_common_edges.assert_called_with(
            fake_client, 'some_id', {
                'nsx_auth': {
                    'username': 'username',
                    'host': 'host',
                    'password': 'password'
                },
                'router': {
                    'dlr_pwd': 'dlr_pwd',
                    'name': 'name',
                    'ha_ls_id': 'ha_ls_id',
                    'uplink_ip': 'uplink_ip',
                    'uplink_dgw': 'uplink_dgw',
                    'uplink_subnet': 'uplink_subnet',
                    'uplink_ls_id': 'uplink_ls_id'
                },
                'ctx': self.fake_ctx
            }, False
        )
        self.assertEqual(
            self.fake_ctx.instance.runtime_properties['router']['uplink_vnic'],
            'vnic_id'
        )


if __name__ == '__main__':
    unittest.main()

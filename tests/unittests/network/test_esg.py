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
import cloudify_nsx.network.esg as esg
from cloudify import mocks as cfy_mocks
from cloudify.state import current_ctx


class EsgTest(unittest.TestCase):

    def setUp(self):
        super(EsgTest, self).setUp()
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
        super(EsgTest, self).tearDown()

    @pytest.mark.internal
    @pytest.mark.unit
    def test_install(self):
        """Check create esg"""
        self.fake_ctx.instance.runtime_properties['resource_id'] = "some_id"
        fake_client = mock.Mock()
        fake_dlr_esg = mock.Mock()
        fake_dlr_esg.update_common_edges = mock.MagicMock()
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
                    'cloudify_nsx.network.esg.nsx_dlr',
                    fake_dlr_esg
                ):
                    esg.create(ctx=self.fake_ctx,
                               edge={"name": "name",
                                     "esg_pwd": "esg_pwd",
                                     "default_pg": "default_pg"},
                               nsx_auth={'username': 'username',
                                         'password': 'password',
                                         'host': 'host'})
        fake_dlr_esg.update_common_edges.assert_called_with(
            fake_client, 'some_id', {
                'nsx_auth': {
                    'username': 'username',
                    'host': 'host',
                    'password': 'password'
                },
                'edge': {
                    'esg_pwd': 'esg_pwd',
                    'name': 'name',
                    'default_pg': 'default_pg'
                },
                'ctx': self.fake_ctx
            }, True
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_uninstall(self):
        """Check delete esg"""
        # not fully created
        self.fake_ctx.instance.runtime_properties['resource_id'] = None
        esg.delete(ctx=self.fake_ctx,
                   edge={})
        self.assertEqual(self.fake_ctx.instance.runtime_properties, {})

        # check use existed
        self._regen_ctx()
        self.fake_ctx.instance.runtime_properties['resource_id'] = 'some_id'
        self.fake_ctx.node.properties['use_external_resource'] = True
        esg.delete(ctx=self.fake_ctx,
                   edge={})
        self.assertEqual(self.fake_ctx.instance.runtime_properties, {})


if __name__ == '__main__':
    unittest.main()

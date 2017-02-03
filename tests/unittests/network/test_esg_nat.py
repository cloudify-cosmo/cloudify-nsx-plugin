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
import cloudify_nsx.network.esg_nat as esg_nat
from cloudify import mocks as cfy_mocks
from cloudify.state import current_ctx


class EsgNatTest(unittest.TestCase):

    def setUp(self):
        super(EsgNatTest, self).setUp()
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
        super(EsgNatTest, self).tearDown()

    @pytest.mark.internal
    @pytest.mark.unit
    def test_install(self):
        """Check create esg nat rule"""
        self.fake_ctx.instance.runtime_properties['resource_id'] = "some_id"

        esg_nat.create(ctx=self.fake_ctx,
                       rule={"esg_id": "esg_id",
                             "action": "action",
                             "originalAddress": "originalAddress",
                             "translatedAddress": "translatedAddress"})

        # without resource_id
        self._regen_ctx()
        fake_client = mock.Mock()
        fake_nsx_nat = mock.Mock()
        fake_nsx_nat.add_nat_rule = mock.MagicMock(
            return_value="some_id"
        )
        with mock.patch(
            'cloudify_nsx.library.nsx_common.NsxClient',
            mock.MagicMock(return_value=fake_client)
        ):
            with mock.patch(
                'cloudify_nsx.network.esg_nat.nsx_nat',
                fake_nsx_nat
            ):
                esg_nat.create(ctx=self.fake_ctx,
                               rule={"esg_id": "esg_id",
                                     "action": "action",
                                     "originalAddress": "originalAddress",
                                     "translatedAddress": "translatedAddress"},
                               nsx_auth={'username': 'username',
                                         'password': 'password',
                                         'host': 'host'})
        fake_nsx_nat.add_nat_rule.assert_called_with(
            fake_client, 'esg_id', 'action', 'originalAddress',
            'translatedAddress', None, None, False, True, None, 'any',
            'any', 'any'
        )
        self.assertEqual(
            self.fake_ctx.instance.runtime_properties['resource_id'],
            "some_id"
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_uninstall(self):
        """Check delete esg nat rule"""
        # not fully created
        self.fake_ctx.instance.runtime_properties['resource_id'] = None
        esg_nat.delete(ctx=self.fake_ctx,
                       rule={})
        self.assertEqual(self.fake_ctx.instance.runtime_properties, {})

        # check use existed
        self._regen_ctx()
        self.fake_ctx.instance.runtime_properties['resource_id'] = 'some_id'
        self.fake_ctx.node.properties['use_external_resource'] = True
        esg_nat.delete(ctx=self.fake_ctx,
                       rule={})
        self.assertEqual(self.fake_ctx.instance.runtime_properties, {})


if __name__ == '__main__':
    unittest.main()

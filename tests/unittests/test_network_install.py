# Copyright (c) 2017 GigaSpaces Technologies Ltd. All rights reserved
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
import library.test_nsx_base as test_nsx_base
import pytest
import mock
import cloudify_nsx.network.esg_nat as esg_nat
import cloudify_nsx.network.relay as relay
import cloudify_nsx.network.routing_ip_prefix as routing_ip_prefix
import cloudify_nsx.network.routing_redistribution as routing_redistribution
from cloudify.state import current_ctx


class NetworkInstallTest(test_nsx_base.NSXBaseTest):

    def setUp(self):
        super(NetworkInstallTest, self).setUp()
        self._regen_ctx()

    def tearDown(self):
        current_ctx.clear()
        super(NetworkInstallTest, self).tearDown()

    @pytest.mark.internal
    @pytest.mark.unit
    def test_esg_nat_install(self):
        """Check create esg nat rule"""
        self._common_install(
            "some_id", esg_nat.create,
            {
                'rule': {
                    "esg_id": "esg_id",
                    "action": "action",
                    "originalAddress": "originalAddress",
                    "translatedAddress": "translatedAddress"
                }
            }
        )

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
    def test_dhcp_relay_install(self):
        """Check create dhcp relay(dlr)"""
        self._common_install(
            "some_id", relay.create,
            {
                'relay': {
                    "dlr_id": "dlr_id"
                }
            }
        )

        # without resource_id
        self._regen_ctx()
        fake_client = mock.Mock()
        fake_dlr_esg = mock.Mock()
        fake_dlr_esg.update_dhcp_relay = mock.MagicMock()
        with mock.patch(
            'cloudify_nsx.library.nsx_common.NsxClient',
            mock.MagicMock(return_value=fake_client)
        ):
            with mock.patch(
                'cloudify_nsx.network.relay.cfy_dlr',
                fake_dlr_esg
            ):
                relay.create(
                    ctx=self.fake_ctx,
                    relay={
                        "dlr_id": "dlr_id"
                    },
                    nsx_auth={
                        'username': 'username',
                        'password': 'password',
                        'host': 'host'
                    }
                )

        fake_dlr_esg.update_dhcp_relay.assert_called_with(
            fake_client, 'dlr_id', {}, {}
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_routing_ip_install(self):
        """Check create routing ip prefix"""
        self._common_install(
            "some_id", routing_ip_prefix.create,
            {
                'prefix': {
                    "dlr_id": "dlr_id",
                    "name": "name",
                    "ipAddress": "ipAddress"
                }
            }
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_routing_redistribution_install(self):
        """Check create routing redistribution rule"""
        self._common_install(
            "some_id", routing_redistribution.create,
            {
                'rule': {
                    "action": "deny",
                    "type": "bgp",
                    "dlr_id": "dlr_id"
                }
            }
        )


if __name__ == '__main__':
    unittest.main()

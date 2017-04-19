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
import copy
import cloudify_nsx.network.esg_firewall as esg_firewall
import cloudify_nsx.network.esg_interface as esg_interface
import cloudify_nsx.network.esg_nat as esg_nat
import cloudify_nsx.network.dlr_interface as dlr_interface
import cloudify_nsx.network.lswitch as lswitch
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
    def test_esg_firewall_install(self):
        """Check create esg firewall rule"""
        # everything by default
        self._common_install_create(
            "esg_id|id", esg_firewall.create,
            {"rule": {"esg_id": "esg_id", "action": "deny"}},
            create_args=['firewallRules'],
            create_kwargs={
                "request_body_dict": {
                    'firewallRules': {
                        'firewallRule': {
                            'direction': None,
                            'name': None,
                            'application': None,
                            'loggingEnabled': 'false',
                            'matchTranslated': 'false',
                            'destination': None,
                            'enabled': 'true',
                            'source': None,
                            'action': 'deny'
                        }
                    }
                },
                "uri_parameters": {'edgeId': 'esg_id'}
            },
            create_response=test_nsx_base.SUCCESS_RESPONSE_ID
        )

        # Additional values(non default)
        self._common_install_create(
            "other_esg_id|id", esg_firewall.create,
            {"rule": {
                "esg_id": "other_esg_id",
                "action": "accept",
                'loggingEnabled': True,
                'matchTranslated': True,
                'enabled': False,
                'ruleTag': 42,
                'description': 'Some Rule',
                'source': 'any',
                'direction': 'in',
                'destination': '8.8.8.8',
                'name': 'rule'
            }},
            create_args=['firewallRules'],
            create_kwargs={
                "request_body_dict": {
                    'firewallRules': {
                        'firewallRule': {
                            'direction': 'in',
                            'name': 'rule',
                            'application': None,
                            'loggingEnabled': 'true',
                            'matchTranslated': 'true',
                            'destination': '8.8.8.8',
                            'enabled': 'false',
                            'source': 'any',
                            'action': 'accept',
                            'ruleTag': '42',
                            'description': 'Some Rule'
                        }
                    }
                },
                "uri_parameters": {'edgeId': 'other_esg_id'}
            },
            create_response=test_nsx_base.SUCCESS_RESPONSE_ID
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_esg_interface_install(self):
        """Check create esg interface"""
        self._common_install_extract_or_read_and_update(
            'id|esg_id',
            esg_interface.create,
            {'interface': {
                "esg_id": "esg_id",
                "ifindex": "id",
                "portgroup_id": "portgroup_id"
            }},
            read_args=['vnic'],
            read_kwargs={'uri_parameters': {'index': 'id', 'edgeId': 'esg_id'}},
            read_response={
                'status': 204,
                'body': test_nsx_base.EDGE_INTERFACE_BEFORE
            },
            update_args=['vnic'],
            update_kwargs={
                'request_body_dict': test_nsx_base.EDGE_INTERFACE_AFTER,
                'uri_parameters': {'index': 'id', 'edgeId': 'esg_id'}
            },
            update_response=test_nsx_base.SUCCESS_RESPONSE
        )

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
        fake_client, _, kwargs = self._kwargs_regen_client(
            None, {
                'rule': {
                    "esg_id": "esg_id",
                    "action": "action",
                    "originalAddress": "originalAddress",
                    "translatedAddress": "translatedAddress"
                }
            }
        )

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
                esg_nat.create(**kwargs)
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
    def test_dlr_interface_install(self):
        """Check create dlr interface"""
        self.fake_ctx.instance.runtime_properties['resource_id'] = "some_id"
        dlr_interface.create(
            ctx=self.fake_ctx,
            interface={
                "dlr_id": "dlr_id",
                "interface_ls_id": "interface_ls_id",
                "interface_ip": "interface_ip",
                "interface_subnet": "interface_subnet"
            }
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_lswitch_install(self):
        """Check create logical swicth"""
        fake_client, _, kwargs = self._kwargs_regen_client(
            "id", {
                "switch": {
                    "name": "name",
                    "transport_zone": "transport_zone"
                }
            }
        )

        fake_client.read = mock.Mock(
            return_value=copy.deepcopy({
                'status': 204,
                'body': test_nsx_base.LSWITCH
            })
        )

        with mock.patch(
            'cloudify_nsx.library.nsx_common.NsxClient',
            mock.MagicMock(return_value=fake_client)
        ):
            lswitch.create(**kwargs)
        self.assertEqual(
            self.fake_ctx.instance.runtime_properties['vsphere_network_id'],
            "some_port_id"
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
        fake_client, _, kwargs = self._kwargs_regen_client(
            None, {
                'relay': {
                    "dlr_id": "dlr_id"
                }
            }
        )

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
                relay.create(**kwargs)

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

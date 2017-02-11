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
import cloudify_nsx.network.dlr_bgp_neighbour as dlr_bgp_neighbour
import cloudify_nsx.network.bgp_neighbour_filter as bgp_neighbour_filter
import cloudify_nsx.network.esg_firewall as esg_firewall
import cloudify_nsx.network.lswitch as lswitch
import cloudify_nsx.network.esg_nat as esg_nat
from cloudify.state import current_ctx


class NetworkUninstallTest(test_nsx_base.NSXBaseTest):

    def setUp(self):
        super(NetworkUninstallTest, self).setUp()
        self._regen_ctx()

    def tearDown(self):
        current_ctx.clear()
        super(NetworkUninstallTest, self).tearDown()

    @pytest.mark.internal
    @pytest.mark.unit
    def test_bgp_neighbour_uninstall(self):
        """Check remove dlr bgp neighbour"""
        self._common_uninstall_read_update(
            'esg_id|ip|remoteAS|protocolIp|forwardingIp',
            dlr_bgp_neighbour.delete,
            {},
            read_args=['routingBGP'],
            read_kwargs={'uri_parameters': {'edgeId': 'esg_id'}},
            read_response={
                'body': {
                    'bgp': {
                        'bgpNeighbours': {
                            'bgpNeighbour': [{
                                'ipAddress': 'ip',
                                'remoteAS': 'remoteAS',
                                'forwardingAddress': 'forwardingIp',
                                'protocolAddress': 'protocolIp',
                                'bgpFilters': {
                                    'bgpFilter': {
                                        'network': 'net',
                                        'action': 'action',
                                        'ipPrefixGe': 'ipPrefixGe',
                                        'ipPrefixLe': 'ipPrefixLe',
                                        'direction': 'direction'
                                    }
                                }
                            }, {
                                'ipAddress': 'other_ip',
                                'remoteAS': 'other_remoteAS',
                                'forwardingAddress': 'other_forwardingIp',
                                'protocolAddress': 'other_protocolIp',
                                'bgpFilters': {}
                            }]
                        }
                    }
                },
                'status': 204
            },
            update_args=['routingBGP'],
            update_kwargs={
                'request_body_dict': {
                    'bgp': {
                        'bgpNeighbours': {
                            'bgpNeighbour': [{
                                'forwardingAddress': 'other_forwardingIp',
                                'protocolAddress': 'other_protocolIp',
                                'ipAddress': 'other_ip',
                                'bgpFilters': {},
                                'remoteAS': 'other_remoteAS'
                            }]
                        }
                    }
                },
                'uri_parameters': {'edgeId': 'esg_id'}
            }
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_bgp_neighbour_filter_uninstall(self):
        """Check delete bgp neighbour filter"""
        self._common_uninstall_read_update(
            'net|esg_id|ip|remoteAS|protocolIp|forwardingIp',
            bgp_neighbour_filter.delete,
            {},
            read_args=['routingBGP'],
            read_kwargs={'uri_parameters': {'edgeId': 'esg_id'}},
            read_response={
                'body': {
                    'bgp': {
                        'bgpNeighbours': {
                            'bgpNeighbour': [{
                                'ipAddress': 'ip',
                                'remoteAS': 'remoteAS',
                                'forwardingAddress': 'forwardingIp',
                                'protocolAddress': 'protocolIp',
                                'bgpFilters': {
                                    'bgpFilter': {
                                        'network': 'net',
                                        'action': 'action',
                                        'ipPrefixGe': 'ipPrefixGe',
                                        'ipPrefixLe': 'ipPrefixLe',
                                        'direction': 'direction'
                                    }
                                }
                            }, {
                                'ipAddress': 'other_ip',
                                'remoteAS': 'other_remoteAS',
                                'forwardingAddress': 'other_forwardingIp',
                                'protocolAddress': 'other_protocolIp',
                                'bgpFilters': {}
                            }]
                        }
                    }
                },
                'status': 204
            },
            update_args=['routingBGP'],
            update_kwargs={
                'request_body_dict': {
                    'bgp': {
                        'bgpNeighbours': {
                            'bgpNeighbour': [{
                                'forwardingAddress': 'forwardingIp',
                                'protocolAddress': 'protocolIp',
                                'ipAddress': 'ip',
                                'bgpFilters': {
                                    'bgpFilter': []
                                },
                                'remoteAS': 'remoteAS'
                            }, {
                                'forwardingAddress': 'other_forwardingIp',
                                'protocolAddress': 'other_protocolIp',
                                'ipAddress': 'other_ip',
                                'bgpFilters': {},
                                'remoteAS': 'other_remoteAS'
                            }]
                        }
                    }
                },
                'uri_parameters': {'edgeId': 'esg_id'}
            }
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_firewall_rule_uninstall(self):
        """Check delete esg firewall rule"""
        self._common_uninstall_delete(
            'id', esg_firewall.delete,
            {'rule': {
                'esg_id': 'esg_id'
            }},
            ['firewallRule'], {
                'uri_parameters': {'edgeId': 'esg_id', 'ruleId': 'id'}
            }
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_lswith_uninstall(self):
        """Check delete for logical switch"""
        self._common_uninstall_delete(
            'id', lswitch.delete,
            {'switch': {}},
            ['logicalSwitch'], {
                'uri_parameters': {'virtualWireID': 'id'}
            },
            additional_params=['vsphere_network_id']
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_esg_nat_uninstall(self):
        """Check delete esg nat rule"""
        self._common_uninstall_delete(
            'id', esg_nat.delete,
            {'rule': {
                'esg_id': 'esg_id'
            }},
            ['edgeNatRule'], {
                'uri_parameters': {'edgeId': 'esg_id', 'ruleID': 'id'}
            }
        )


if __name__ == '__main__':
    unittest.main()

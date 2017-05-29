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
import cloudify_nsx.network.dlr as dlr
import cloudify_nsx.network.dlr_bgp_neighbour as dlr_bgp_neighbour
import cloudify_nsx.network.dlr_dgw as dlr_dgw
import cloudify_nsx.network.dlr_interface as dlr_interface
import cloudify_nsx.network.bgp_neighbour_filter as bgp_neighbour_filter
import cloudify_nsx.network.dhcp_bind as dhcp_bind
import cloudify_nsx.network.dhcp_pool as dhcp_pool
import cloudify_nsx.network.esg_firewall as esg_firewall
import cloudify_nsx.network.lswitch as lswitch
import cloudify_nsx.network.esg as esg
import cloudify_nsx.network.esg_gateway as esg_gateway
import cloudify_nsx.network.esg_interface as esg_interface
import cloudify_nsx.network.esg_nat as esg_nat
import cloudify_nsx.network.esg_route as esg_route
import cloudify_nsx.network.ospf_area as ospf_area
import cloudify_nsx.network.ospf_interface as ospf_interface
import cloudify_nsx.network.relay as relay
import cloudify_nsx.network.routing_ip_prefix as routing_ip_prefix
import cloudify_nsx.network.routing_redistribution as routing_redistribution
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
    def test_dlr_uninstall(self):
        """Check delete dlr"""
        self._common_uninstall_delete(
            'dlr_id', dlr.delete,
            {'router': {}},
            delete_args=['nsxEdge'],
            delete_kwargs={
                'uri_parameters': {'edgeId': 'dlr_id'}
            }
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_dlr_dgw_uninstall(self):
        """Check delete dlr dgw"""
        self._common_uninstall_delete(
            'dlr_id', dlr_dgw.delete,
            {'gateway': {}},
            delete_args=['routingConfig'],
            delete_kwargs={
                'uri_parameters': {'edgeId': 'dlr_id'}
            }
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_dlr_interface_uninstall(self):
        """Check delete dlr interface"""
        self._common_uninstall_delete(
            'id|dlr_id',
            dlr_interface.delete,
            {},
            delete_args=['interfaces'],
            delete_kwargs={
                'uri_parameters': {'edgeId': 'dlr_id'},
                'query_parameters_dict': {'index': 'id'}
            }
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_dhcp_bind_uninstall(self):
        """Check remove binding rule vm to dhcp ip"""
        self._common_uninstall_delete(
            'esg_id|bind_id', dhcp_bind.delete,
            {'bind': {}},
            delete_args=['dhcpStaticBindingID'],
            delete_kwargs={
                'uri_parameters': {'edgeId': 'esg_id', 'bindingID': 'bind_id'}
            }
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_dhcp_pool_uninstall(self):
        """Check delete dhcp pool"""
        self._common_uninstall_delete(
            'esg_id|pool_id', dhcp_pool.delete,
            {'pool': {}},
            delete_args=['dhcpPoolID'],
            delete_kwargs={
                'uri_parameters': {'edgeId': 'esg_id', 'poolID': 'pool_id'}
            }
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_esg_uninstall(self):
        """Check delete esg"""
        self._common_uninstall_delete(
            'esg_id', esg.delete,
            {'edge': {}},
            delete_args=['nsxEdge'],
            delete_kwargs={
                'uri_parameters': {'edgeId': 'esg_id'}
            }
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_esg_firewall_rule_uninstall(self):
        """Check delete esg firewall rule"""
        self._common_uninstall_delete(
            'esg_id|id', esg_firewall.delete,
            {'rule': {
                'esg_id': 'esg_id'
            }},
            ['firewallRule'], {
                'uri_parameters': {'edgeId': 'esg_id', 'ruleId': 'id'}
            },
            additional_params=['rule_id']
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_lswitch_uninstall(self):
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
    def test_esg_gateway_uninstall(self):
        """Check delete esg gateway"""
        self._common_uninstall_external_and_unintialized(
            'esg_id|ip', esg_gateway.delete,
            {'gateway': {}}
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_esg_interface_uninstall(self):
        """Check delete esg interface"""
        self._common_uninstall_read_update(
            'id|esg_id',
            esg_interface.delete,
            {},
            read_args=['vnic'], read_kwargs={
                'uri_parameters': {'index': 'id', 'edgeId': 'esg_id'}
            },
            read_response={
                'body': test_nsx_base.EDGE_INTERFACE_AFTER,
                'status': 204
            },
            update_args=['vnic'],
            update_kwargs={
                'request_body_dict': test_nsx_base.EDGE_INTERFACE_BEFORE,
                'uri_parameters': {'index': 'id', 'edgeId': 'esg_id'}
            }
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_esg_nat_uninstall(self):
        """Check delete esg nat rule"""
        self._common_uninstall_delete(
            'esg_id|id', esg_nat.delete,
            {'rule': {
                'esg_id': 'esg_id'
            }},
            ['edgeNatRule'], {
                'uri_parameters': {'edgeId': 'esg_id', 'ruleID': 'id'}
            }
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_esg_route_uninstall(self):
        """Check delete esg route"""
        self._common_uninstall_external_and_unintialized(
            'esg_id|rule_id|next_hop', esg_route.delete,
            {'route': {}}
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_ospf_area_uninstall(self):
        """Check delete ospf area"""
        self._common_uninstall_external_and_unintialized(
            'some_id', ospf_area.delete,
            {'area': {}}
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_ospf_interface_uninstall(self):
        """Check delete ospf interface"""
        self._common_uninstall_external_and_unintialized(
            'some_id', ospf_interface.delete,
            {'interface': {}}
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_relay_uninstall(self):
        """Check delete dhcop relay(dlr)"""
        self._common_uninstall_delete(
            "dlr_id", relay.delete,
            {'relay': {"dlr_id": "dlr_id"}},
            ['dhcpRelay'],
            {'uri_parameters': {'edgeId': 'dlr_id'}}
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_routing_ip_prefix_uninstall(self):
        """Check delete routing ip prefix"""
        self._common_uninstall_external_and_unintialized(
            'some_id', routing_ip_prefix.delete,
            {'prefix': {}}
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_routing_redistribution_uninstall(self):
        """Check delete routing redistribution rule"""
        self._common_uninstall_external_and_unintialized(
            'some_id', routing_redistribution.delete,
            {'rule': {}}
        )


if __name__ == '__main__':
    unittest.main()

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
import cloudify_nsx.network.dhcp_bind as dhcp_bind
import cloudify_nsx.network.dhcp_pool as dhcp_pool
import cloudify_nsx.network.dlr_dgw as dlr_dgw
import cloudify_nsx.network.bgp_neighbour_filter as bgp_neighbour_filter
import cloudify_nsx.network.esg_firewall as esg_firewall
import cloudify_nsx.network.esg_gateway as esg_gateway
import cloudify_nsx.network.esg_interface as esg_interface
import cloudify_nsx.network.esg_nat as esg_nat
import cloudify_nsx.network.dlr_bgp_neighbour as dlr_bgp_neighbour
import cloudify_nsx.network.dlr_interface as dlr_interface
import cloudify_nsx.network.lswitch as lswitch
import cloudify_nsx.network.ospf_area as ospf_area
import cloudify_nsx.network.ospf_interface as ospf_interface
import cloudify_nsx.network.esg_route as esg_route
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
            read_args=['vnic'], read_kwargs={
                'uri_parameters': {'index': 'id', 'edgeId': 'esg_id'}
            },
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
    def test_esg_interface_install_all_fields(self):
        """Check create esg interface"""
        self._common_install_extract_or_read_and_update(
            'id|esg_id',
            esg_interface.create,
            {'interface': {
                "esg_id": "esg_id",
                "ifindex": "id",
                "name": "name",
                "netmask": "255.255.255.0",
                "ipaddr": "192.168.3.127",
                "secondary_ips": "192.168.3.128",
                'prefixlen': "24",
                'enable_send_redirects': 'true',
                'is_connected': 'true',
                'enable_proxy_arp': 'true',
                "portgroup_id": "portgroup_id"
            }},
            read_args=['vnic'], read_kwargs={
                'uri_parameters': {'index': 'id', 'edgeId': 'esg_id'}
            },
            read_response={
                'status': 204,
                'body': test_nsx_base.EDGE_INTERFACE_BEFORE
            },
            update_args=['vnic'],
            update_kwargs={
                'request_body_dict': {
                    'vnic': {
                        'portgroupId': 'portgroup_id',
                        'portgroupName': None,
                        'type': 'internal',
                        'enableProxyArp': 'true',
                        'name': 'name',
                        'addressGroups': {
                            'addressGroup': {
                                'secondaryAddresses': {
                                    'ipAddress': '192.168.3.128'
                                },
                                'primaryAddress': '192.168.3.127',
                                'subnetMask': '255.255.255.0',
                                'subnetPrefixLength': '24'
                            }
                        },
                        'isConnected': 'true',
                        'enableSendRedirects': 'true',
                        'mtu': 1500
                    }
                },
                'uri_parameters': {'index': 'id', 'edgeId': 'esg_id'}
            },
            update_response=test_nsx_base.SUCCESS_RESPONSE
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_esg_nat_install(self):
        """Check create esg nat rule"""
        self._common_install_extract_or_read_and_update(
            'esg_id|id', esg_nat.create,
            {'rule': {
                "esg_id": "esg_id",
                "action": "action",
                "originalAddress": "originalAddress",
                "translatedAddress": "translatedAddress"
            }},
            extract_args=['edgeNatRules', 'create'], extract_kwargs={},
            extract_response={
                'natRules': {
                    'natRule': {}
                }
            },
            create_args=['edgeNatRules'],
            create_kwargs={
                'uri_parameters': {'edgeId': "esg_id"},
                'request_body_dict': test_nsx_base.ESG_NAT_AFTER
            },
            create_response=test_nsx_base.SUCCESS_RESPONSE_ID
        )

        self._common_install_extract_or_read_and_update(
            'esg_id|id', esg_nat.create,
            {'rule': {
                "esg_id": "esg_id",
                "action": "action",
                "originalAddress": "originalAddress",
                "translatedAddress": "translatedAddress",
                "description": "3",
                'vnic': '1',
                'ruleTag': '2',
                "loggingEnabled": 'true',
                'enabled': 'false'
            }},
            extract_args=['edgeNatRules', 'create'], extract_kwargs={},
            extract_response={
                'natRules': {
                    'natRule': {}
                }
            },
            create_args=['edgeNatRules'],
            create_kwargs={
                'uri_parameters': {'edgeId': "esg_id"},
                'request_body_dict': {
                    'natRules': {
                        'natRule': {
                            'translatedPort': 'any',
                            'action': 'action',
                            'originalAddress': 'originalAddress',
                            'translatedAddress': 'translatedAddress',
                            'vnic': '1',
                            'ruleTag': '2',
                            'description': '3',
                            'enabled': 'false',
                            'protocol': 'any',
                            'originalPort': 'any',
                            'loggingEnabled': 'true'
                        }
                    }
                }
            },
            create_response=test_nsx_base.SUCCESS_RESPONSE_ID
        )

    @pytest.mark.unit
    def test_dlr_bgp_neighbour_dlr_install(self):
        """Check define dlr bgp neighbour"""
        self._common_use_existing_without_run(
            'some_id',
            dlr_bgp_neighbour.create_dlr,
            {'neighbour': {"dlr_id": "dlr_id",
                           "ipAddress": "ipAddress",
                           'remoteAS': 'remoteAS',
                           'protocolAddress': 'protocolAddress',
                           'forwardingAddress': 'forwardingAddress'}})

        self._common_install_extract_or_read_and_update(
            'dlr_id|ip|remoteAS|protocolIp|forwardingIp',
            dlr_bgp_neighbour.create_dlr,
            {'neighbour': {"dlr_id": "dlr_id",
                           "ipAddress": "ip",
                           'remoteAS': 'remoteAS',
                           'forwardingAddress': 'forwardingIp',
                           'protocolAddress': 'protocolIp'}},
            read_args=['routingBGP'],
            read_kwargs={'uri_parameters': {'edgeId': 'dlr_id'}},
            read_response={
                'body': test_nsx_base.DLR_BGP_NEIGHBOUR_BEFORE,
                'status': 204
            },
            update_args=['routingBGP'],
            update_kwargs={
                'request_body_dict': test_nsx_base.DLR_BGP_NEIGHBOUR_AFTER,
                'uri_parameters': {'edgeId': 'dlr_id'}
            },
            update_response=test_nsx_base.SUCCESS_RESPONSE_ID
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_dlr_bgp_neighbour_esg_install(self):
        """Check define esg bgp neighbour"""
        self._common_use_existing_without_run(
            'esg_id|ip|remoteAS||',
            dlr_bgp_neighbour.create_esg,
            {'neighbour': {"dlr_id": "dlr_id",
                           "ipAddress": "ipAddress",
                           'remoteAS': 'remoteAS'}})

        self._common_install_extract_or_read_and_update(
            'esg_id|ip|remoteAS||',
            dlr_bgp_neighbour.create_esg,
            {'neighbour': {"dlr_id": "esg_id",
                           "ipAddress": "ip",
                           'remoteAS': 'remoteAS'}},
            read_args=['routingBGP'],
            read_kwargs={'uri_parameters': {'edgeId': 'esg_id'}},
            read_response={
                'body': test_nsx_base.EDGE_BGP_NEIGHBOUR_BEFORE,
                'status': 204
            },
            update_args=['routingBGP'],
            update_kwargs={
                'request_body_dict': test_nsx_base.EDGE_BGP_NEIGHBOUR_AFTER,
                'uri_parameters': {'edgeId': 'esg_id'}
            },
            update_response=test_nsx_base.SUCCESS_RESPONSE_ID
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_dlr_dgw_install(self):
        """Check create dlr dgw"""
        self._common_install_extract_or_read_and_update(
            'dlr_id', dlr_dgw.create,
            {'gateway': {"dlr_id": "dlr_id", "address": "address"}},
            extract_args=['routingConfig', 'update'], extract_kwargs={},
            extract_response=test_nsx_base.ROUTING_CONFIG_UPDATE_EXTRACT,
            update_args=['routingConfig'],
            update_kwargs={
                'uri_parameters': {'edgeId': "dlr_id"},
                'request_body_dict': {
                    'routing': test_nsx_base.EDG_STATIC_ROUTING_GATEWAY_AFTER
                }
            },
            update_response=test_nsx_base.SUCCESS_RESPONSE_ID
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_dhcp_pool_install(self):
        """Check create dhcp pool"""
        self._common_use_existing_without_run(
            'some_id', dhcp_pool.create,
            {'pool': {'esg_id': 'esg_id',
                      'ip_range': 'ip_range'}})

        self._common_install_create(
            'esg_id|id', dhcp_pool.create,
            {'pool': {'esg_id': 'esg_id',
                      'ip_range': '192.168.5.128-192.168.5.250',
                      'default_gateway': '192.168.5.1',
                      'subnet_mask': '255.255.255.0',
                      'domain_name': 'internal.test',
                      'dns_server_1': '8.8.8.8',
                      'dns_server_2': '192.168.5.1',
                      'lease_time': 'infinite',
                      'auto_dns': 'true'}},
            create_args=['dhcpPool'],
            create_kwargs={
                'request_body_dict': {
                    'ipPool': {
                        'domainName': 'internal.test',
                        'leaseTime': 'infinite',
                        'primaryNameServer': '8.8.8.8',
                        'secondaryNameServer': '192.168.5.1',
                        'autoConfigureDNS': 'true',
                        'subnetMask': '255.255.255.0',
                        'ipRange': '192.168.5.128-192.168.5.250',
                        'defaultGateway': '192.168.5.1'
                    }
                },
                'uri_parameters': {'edgeId': 'esg_id'}
            },
            create_response=test_nsx_base.SUCCESS_RESPONSE_ID
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_dhcp_bind_install(self):
        """Check insert binding rule to dhcp ip"""
        self._common_use_existing_without_run(
            "some_id", dhcp_bind.create,
            {'bind': {"esg_id": "esg_id",
                      "hostname": "hostname",
                      "ip": "ip"}})

        self._common_install(
            "some_id", dhcp_bind.create,
            {'bind': {"esg_id": "esg_id",
                      "hostname": "hostname",
                      "ip": "ip"}})

    @pytest.mark.internal
    @pytest.mark.unit
    def test_dhcp_bind_install_mac(self):
        """Check insert binding rule to dhcp ip"""
        self._common_install_create(
            'esg_id|id', dhcp_bind.create,
            {'bind': {'esg_id': 'esg_id',
                      'mac': '11:22:33:44:55:66',
                      'hostname': 'secret.server',
                      'ip': '192.168.5.251',
                      'default_gateway': '192.168.5.1',
                      'subnet_mask': '255.255.255.0',
                      'domain_name': 'secret.internal.test',
                      'dns_server_1': '8.8.8.8',
                      'dns_server_2': '192.168.5.1',
                      'lease_time': 'infinite',
                      'auto_dns': 'true'}},
            create_args=['dhcpStaticBinding'],
            create_kwargs={
                'request_body_dict': {
                    'staticBinding': {
                        'subnetMask': '255.255.255.0',
                        'domainName': 'secret.internal.test',
                        'primaryNameServer': '8.8.8.8',
                        'macAddress': '11:22:33:44:55:66',
                        'leaseTime': 'infinite',
                        'secondaryNameServer': '192.168.5.1',
                        'hostname': 'secret.server',
                        'defaultGateway': '192.168.5.1',
                        'ipAddress': '192.168.5.251',
                        'autoConfigureDNS': 'true'
                    }
                },
                'uri_parameters': {'edgeId': 'esg_id'}
            },
            create_response=test_nsx_base.SUCCESS_RESPONSE_ID
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_dhcp_bind_install_vm(self):
        """Check insert binding rule to dhcp ip"""
        self._common_install_create(
            'esg_id|id', dhcp_bind.create,
            {'bind': {'esg_id': 'esg_id',
                      'vm_id': 'vm_id',
                      'vnic_id': 'vnic_id',
                      'hostname': 'secret.server',
                      'ip': '192.168.5.251',
                      'default_gateway': '192.168.5.1',
                      'subnet_mask': '255.255.255.0',
                      'domain_name': 'secret.internal.test',
                      'dns_server_1': '8.8.8.8',
                      'dns_server_2': '192.168.5.1',
                      'lease_time': 'infinite',
                      'auto_dns': 'true'}},
            create_args=['dhcpStaticBinding'],
            create_kwargs={
                'request_body_dict': {
                    'staticBinding': {
                        'subnetMask': '255.255.255.0',
                        'domainName': 'secret.internal.test',
                        'primaryNameServer': '8.8.8.8',
                        'vnicId': 'vnic_id',
                        'vmId': 'vm_id',
                        'secondaryNameServer': '192.168.5.1',
                        'hostname': 'secret.server',
                        'ipAddress': '192.168.5.251',
                        'defaultGateway': '192.168.5.1',
                        'leaseTime': 'infinite',
                        'autoConfigureDNS': 'true'
                    }
                },
                'uri_parameters': {'edgeId': 'esg_id'}
            },
            create_response=test_nsx_base.SUCCESS_RESPONSE_ID
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_bgp_neighbour_filter_install(self):
        """Check create bgp_neighbour_filter"""
        self._common_use_existing_without_run(
            'net|esg_id|ip|remoteAS|protocolIp|forwardingIp',
            bgp_neighbour_filter.create,
            {'filter': {
                "neighbour_id": "neighbour_id",
                "action": "deny",
                "direction": "in",
                "network": "network"}})

        self._common_install_extract_or_read_and_update(
            'net|esg_id|ip|remoteAS|protocolIp|forwardingIp',
            bgp_neighbour_filter.create,
            {'filter': {
                "neighbour_id": "esg_id|ip|remoteAS|protocolIp|forwardingIp",
                "action": "deny",
                "direction": "in",
                "network": "net",
                "ipPrefixGe": "ipPrefixGe",
                "ipPrefixLe": "ipPrefixLe"
            }},
            # read
            read_args=['routingBGP'],
            read_kwargs={'uri_parameters': {'edgeId': 'esg_id'}},
            read_response={
                'body': test_nsx_base.DLR_BGP_NEIGHBOUR_WITH_FILTER_BEFORE,
                'status': 204
            },
            # update
            update_args=['routingBGP'],
            update_kwargs={
                'request_body_dict':
                    test_nsx_base.DLR_BGP_NEIGHBOUR_WITH_FILTER_AFTER,
                'uri_parameters': {'edgeId': 'esg_id'}
            },
            update_response=test_nsx_base.SUCCESS_RESPONSE_ID
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_dlr_interface_install(self):
        """Check create dlr interface"""
        self._common_use_existing_without_run(
            'id|dlr_id',
            dlr_interface.create,
            {'interface': {
                "dlr_id": "dlr_id",
                "interface_ls_id": "interface_ls_id",
                "interface_ip": "interface_ip",
                "interface_subnet": "interface_subnet"
            }})

        self._common_install_extract_or_read_and_update(
            'id|dlr_id',
            dlr_interface.create,
            {'interface': {
                "dlr_id": "dlr_id",
                "interface_ls_id": "interface_ls_id",
                "interface_ip": "interface_ip",
                "interface_subnet": "interface_subnet"
            }},
            extract_args=['interfaces', 'create'], extract_kwargs={},
            extract_response={
                'interfaces': {
                    'interface': {
                        'addressGroups': {
                            'addressGroup': {
                                'primaryAddress': {
                                }
                            }
                        }
                    }
                }
            },
            create_args=['interfaces'],
            create_kwargs={
                'query_parameters_dict': {'action': 'patch'},
                'request_body_dict': test_nsx_base.DLR_INTERFACE_CREATE,
                'uri_parameters': {'edgeId': 'dlr_id'}
            },
            create_response={
                'status': 204,
                'body': test_nsx_base.DLR_INTERFACE_CREATE_RESPONSE
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
    def test_esg_route_install(self):
        """Check create esg route"""
        self._common_install_extract_or_read_and_update(
            "esg_id|network|192.168.3.10", esg_route.create,
            {'route': {"esg_id": "esg_id", "network": "network",
                       "next_hop": "192.168.3.10"}},
            # read
            read_args=['routingConfigStatic'],
            read_kwargs={'uri_parameters': {'edgeId': "esg_id"}},
            read_response={
                'status': 204,
                'body': test_nsx_base.EDG_STATIC_ROUTING_BEFORE
            },
            # update
            update_args=['routingConfigStatic'],
            update_kwargs={
                'uri_parameters': {'edgeId': "esg_id"},
                'request_body_dict': {
                    'staticRouting': {
                        'staticRoutes': {
                            'route': [{
                                'description': None,
                                'network': 'network',
                                'mtu': '1500',
                                'vnic': None,
                                'nextHop': "192.168.3.10",
                                'adminDistance': '1'
                            }]
                        },
                        'defaultRoute': {
                            'vnic': None,
                            'gatewayAddress': 'address',
                            'description': None,
                            'mtu': None
                        }
                    }
                }
            },
            update_response=test_nsx_base.SUCCESS_RESPONSE_ID
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_esg_gateway_install(self):
        """Check create esg gateway"""
        self._common_install_extract_or_read_and_update(
            "esg_id|dgw_ip", esg_gateway.create,
            {"gateway": {"esg_id": "esg_id", "dgw_ip": "dgw_ip"}},
            # read
            read_args=['routingConfigStatic'],
            read_kwargs={'uri_parameters': {'edgeId': "esg_id"}},
            read_response={
                'status': 204,
                'body': test_nsx_base.EDG_STATIC_ROUTING_BEFORE
            },
            # update
            update_args=['routingConfigStatic'],
            update_kwargs={
                'uri_parameters': {'edgeId': "esg_id"},
                'request_body_dict': {
                    'staticRouting': {
                        'staticRoutes': {},
                        'defaultRoute': {
                            'mtu': '1500',
                            'vnic': None,
                            'adminDistance': '1',
                            'gatewayAddress': 'dgw_ip'
                        }
                    }
                }
            },
            update_response=test_nsx_base.SUCCESS_RESPONSE_ID
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_ospf_interface_install(self):
        """Check create ospf interface"""
        self._common_install(
            "some_id", ospf_interface.create,
            {'interface': {"dlr_id": "dlr_id",
                           "areaId": "areaId",
                           "vnic": "vnic"}})

    @pytest.mark.internal
    @pytest.mark.unit
    def test_ospf_area_install(self):
        """Check create ospf area"""
        self._common_install(
            "some_id", ospf_area.create,
            {"area": {"dlr_id": "dlr_id",
                      "areaId": "areaId",
                      "type": "nssa"}})

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

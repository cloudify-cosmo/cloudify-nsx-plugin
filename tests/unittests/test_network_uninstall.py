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
import test_base
import pytest
import cloudify_nsx.network.esg_firewall as esg_firewall
import cloudify_nsx.network.lswitch as lswitch
import cloudify_nsx.network.esg_nat as esg_nat
from cloudify.state import current_ctx


class NetworkTest(test_base.BaseTest):

    def setUp(self):
        super(NetworkTest, self).setUp()
        self._regen_ctx()

    def tearDown(self):
        current_ctx.clear()
        super(NetworkTest, self).tearDown()

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

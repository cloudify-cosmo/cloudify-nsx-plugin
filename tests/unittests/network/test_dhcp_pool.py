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
import cloudify_nsx.network.dhcp_pool as dhcp_pool
from cloudify import mocks as cfy_mocks
from cloudify.state import current_ctx


class DhcpPoolTest(unittest.TestCase):

    def setUp(self):
        super(DhcpPoolTest, self).setUp()
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
        super(DhcpPoolTest, self).tearDown()

    @pytest.mark.internal
    @pytest.mark.unit
    def test_install(self):
        """Check create dhcp pool"""
        self.fake_ctx.instance.runtime_properties['resource_id'] = "some_id"
        dhcp_pool.create(ctx=self.fake_ctx,
                         pool={"esg_id": "esg_id",
                               "ip_range": "ip_range"})

    @pytest.mark.internal
    @pytest.mark.unit
    def test_uninstall(self):
        """Check delete dhcp pool"""
        self.fake_ctx.instance.runtime_properties['resource_id'] = None
        dhcp_pool.delete(ctx=self.fake_ctx,
                         pool={})


if __name__ == '__main__':
    unittest.main()

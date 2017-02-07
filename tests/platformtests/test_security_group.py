########
# Copyright (c) 2017 GigaSpaces Technologies Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
#    * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    * See the License for the specific language governing permissions and
#    * limitations under the License.

# Stdlib imports
import os

# Third party imports
import unittest
import pytest

# Cloudify imports
import test_base
from cloudify.workflows import local
from cloudify_cli import constants as cli_constants
import cloudify_nsx.library.nsx_security_group as nsx_security_group


class SecurityGroupTest(test_base.BaseTest):

    @pytest.mark.external
    def test_security_group(self):
        """Platform check: security group"""
        inputs = {k: self.ext_inputs[k] for k in self.ext_inputs}

        # Define inputs related to this function
        inputs['security_group_name'] = os.environ.get(
            'SECURITY_GROUP_NAME', "security_group_name"
        )
        inputs['nested_security_group_name'] = os.environ.get(
            'NESTED_SECURITY_GROUP_NAME', "nested_security_group_name"
        )

        # set blueprint name
        blueprint = os.path.join(
            self.blueprints_path,
            'security_groups.yaml'
        )

        # check prexist of security groups
        resource_id, _ = nsx_security_group.get_group(
            self.client_session,
            'globalroot-0',
            inputs['node_name_prefix'] + inputs['security_group_name']
        )

        self.assertTrue(resource_id is None)

        resource_id, _ = nsx_security_group.get_group(
            self.client_session,
            'globalroot-0',
            inputs['node_name_prefix'] + inputs['nested_security_group_name']
        )

        self.assertTrue(resource_id is None)

        # cfy local init
        self.local_env = local.init_env(
            blueprint,
            inputs=inputs,
            name=self._testMethodName,
            ignored_modules=cli_constants.IGNORED_LOCAL_WORKFLOW_MODULES)

        # cfy local execute -w install
        self.local_env.execute(
            'install',
            task_retries=4,
            task_retry_interval=3,
        )

        # check security groups properties
        resource_id, main_properties = nsx_security_group.get_group(
            self.client_session,
            'globalroot-0',
            inputs['node_name_prefix'] + inputs['security_group_name']
        )

        self.assertTrue(resource_id is not None)

        nested_resource_id, nested_properties = nsx_security_group.get_group(
            self.client_session,
            'globalroot-0',
            inputs['node_name_prefix'] + inputs['nested_security_group_name']
        )
        self.assertTrue(nested_resource_id is not None)

        self.assertEqual(
            main_properties['member']['name'],
            inputs['node_name_prefix'] + inputs['nested_security_group_name']
        )

        self.assertEqual(
            main_properties['member']['objectId'],
            nested_resource_id
        )

        self.assertFalse(nested_properties.get('member'))

        # cfy local execute -w uninstall
        self.local_env.execute(
            'uninstall',
            task_retries=50,
            task_retry_interval=3,
        )

        # must be deleted
        resource_id, _ = nsx_security_group.get_group(
            self.client_session,
            'globalroot-0',
            inputs['node_name_prefix'] + inputs['security_group_name']
        )

        self.assertTrue(resource_id is None)

        resource_id, _ = nsx_security_group.get_group(
            self.client_session,
            'globalroot-0',
            inputs['node_name_prefix'] + inputs['nested_security_group_name']
        )

        self.assertTrue(resource_id is None)


if __name__ == '__main__':
    unittest.main()

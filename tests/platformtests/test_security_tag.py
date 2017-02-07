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
import cloudify_nsx.library.nsx_security_tag as nsx_security_tag
import cloudify_nsx.library.nsx_security_group as nsx_security_group
import cloudify_nsx.library.nsx_security_policy as nsx_security_policy


class SecurityTagTest(test_base.BaseTest):

    @pytest.mark.external
    def test_security_tag(self):
        """Platform check: security tag"""

        # set blueprint name
        blueprint = os.path.join(
            self.blueprints_path,
            'security_tag.yaml'
        )

        # check prexist of security tag
        resource_id, _ = nsx_security_tag.get_tag(
            self.client_session,
            self.ext_inputs['node_name_prefix'] + "secret_tag"
        )

        self.assertTrue(resource_id is None)

        # cfy local init
        self.local_env = local.init_env(
            blueprint,
            inputs=self.ext_inputs,
            name=self._testMethodName,
            ignored_modules=cli_constants.IGNORED_LOCAL_WORKFLOW_MODULES)

        # cfy local execute -w install
        self.local_env.execute(
            'install',
            task_retries=50,
            task_retry_interval=3,
        )

        # check security tag properties
        resource_id, info = nsx_security_tag.get_tag(
            self.client_session,
            self.ext_inputs['node_name_prefix'] + "secret_tag"
        )

        self.assertTrue(resource_id is not None)
        self.assertTrue(info is not None)

        self.assertEqual(
            info['name'], self.ext_inputs['node_name_prefix'] + "secret_tag"
        )
        self.assertEqual(info['description'], "What can i say?")

        # cfy local execute -w uninstall
        self.local_env.execute(
            'uninstall',
            task_retries=50,
            task_retry_interval=3,
        )

        # must be deleted
        resource_id, _ = nsx_security_tag.get_tag(
            self.client_session,
            self.ext_inputs['node_name_prefix'] + "secret_tag"
        )

        self.assertTrue(resource_id is None)

        self.local_env = None

    @pytest.mark.external
    def test_security_tag_vm_bind(self):
        """Platform check: bind security tag to vm"""
        inputs = {k: self.ext_inputs[k] for k in self.ext_inputs}

        # Define inputs related to this function
        inputs.update({
            'name_of_tag': str(os.environ.get('NAME_OF_TAG', 'tag_name')),
            # vcenter inputs
            'vcenter_ip': os.environ.get('VCENTER_IP'),
            'vcenter_user': os.environ.get('VCENTER_USER'),
            'vcenter_password': os.environ.get('VCENTER_PASSWORD'),
        })

        # update custom params
        if os.environ.get('VCENTER_PORT'):
            inputs['vcenter_port'] = str(os.environ.get(
                'VCENTER_PORT'
            ))
        # update custom params
        if os.environ.get('VCENTER_DATACENTER'):
            inputs['vcenter_datacenter'] = os.environ.get(
                'VCENTER_DATACENTER'
            )
        if os.environ.get('VCENTER_RESOURCE_POOL'):
            inputs['vcenter_resource_pool'] = os.environ.get(
                'VCENTER_RESOURCE_POOL'
            )
        if os.environ.get('VCENTER_TEMPLATE'):
            inputs['template_name'] = os.environ.get('VCENTER_TEMPLATE')

        if (
            not inputs['vcenter_ip'] or
            not inputs['vcenter_ip'] or
            not inputs['vcenter_password']
        ):
                self.skipTest("You dont have credentials for vcenter")

        # set blueprint name
        blueprint = os.path.join(
            self.blueprints_path,
            'security_tag_vm.yaml'
        )

        # check prexist of security tag
        resource_id, _ = nsx_security_tag.get_tag(
            self.client_session,
            inputs['node_name_prefix'] + inputs['name_of_tag']
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

        # check security tag properties
        resource_id, info = nsx_security_tag.get_tag(
            self.client_session,
            inputs['node_name_prefix'] + inputs['name_of_tag']
        )

        self.assertTrue(resource_id is not None)
        self.assertTrue(info is not None)

        self.assertEqual(
            info['name'],
            inputs['node_name_prefix'] + inputs['name_of_tag']
        )
        self.assertEqual(
            info['description'],
            "Example security tag which will be assigned to example VM"
        )

        # cfy local execute -w uninstall
        self.local_env.execute(
            'uninstall',
            task_retries=50,
            task_retry_interval=3,
        )

        # must be deleted
        resource_id, _ = nsx_security_tag.get_tag(
            self.client_session,
            inputs['node_name_prefix'] + inputs['name_of_tag']
        )

        self.assertTrue(resource_id is None)

    @pytest.mark.external
    def test_security_policy(self):
        """Platform check: security policy"""
        inputs = {k: self.ext_inputs[k] for k in self.ext_inputs}

        # Define inputs related to this function
        inputs['policy_name'] = os.environ.get(
            'POLICY_NAME', 'policy_name'
        )

        # set blueprint name
        blueprint = os.path.join(
            self.blueprints_path,
            'security_policy.yaml'
        )

        # check prexist of security policy
        resource_id, policy = nsx_security_policy.get_policy(
            self.client_session,
            inputs['node_name_prefix'] + inputs['policy_name']
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

        # check security policy properties
        resource_id, policy = nsx_security_policy.get_policy(
            self.client_session,
            inputs['node_name_prefix'] + inputs['policy_name']
        )

        self.assertTrue(resource_id is not None)
        self.assertTrue(policy is not None)

        # cfy local execute -w uninstall
        self.local_env.execute(
            'uninstall',
            task_retries=50,
            task_retry_interval=3,
        )

        # must be deleted
        resource_id, policy = nsx_security_policy.get_policy(
            self.client_session,
            inputs['node_name_prefix'] + inputs['policy_name']
        )

        self.assertTrue(resource_id is None)

    @pytest.mark.external
    def test_security_policy_bind(self):
        """Platform check: bind security policy to security group"""
        inputs = {k: self.ext_inputs[k] for k in self.ext_inputs}

        # Define inputs related to this function
        inputs['security_group_name'] = os.environ.get(
            'SECURITY_GROUP_NAME', "security_group_name"
        )
        inputs['policy_name'] = os.environ.get(
            'POLICY_NAME', 'policy_name'
        )

        # set blueprint name
        blueprint = os.path.join(
            self.blueprints_path,
            'bind_policy_group.yaml'
        )

        # check prexist of security policy
        resource_id, policy = nsx_security_policy.get_policy(
            self.client_session,
            inputs['node_name_prefix'] + inputs['policy_name']
        )

        self.assertTrue(resource_id is None)

        # check prexist of security group
        resource_id, _ = nsx_security_group.get_group(
            self.client_session,
            'globalroot-0',
            inputs['node_name_prefix'] + inputs['security_group_name']
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

        # check security policy properties
        resource_id, policy = nsx_security_policy.get_policy(
            self.client_session,
            inputs['node_name_prefix'] + inputs['policy_name']
        )

        self.assertTrue(resource_id is not None)
        self.assertTrue(policy is not None)

        # check security group
        resource_id, _ = nsx_security_group.get_group(
            self.client_session,
            'globalroot-0',
            inputs['node_name_prefix'] + inputs['security_group_name']
        )

        self.assertTrue(resource_id is not None)

        # cfy local execute -w uninstall
        self.local_env.execute(
            'uninstall',
            task_retries=50,
            task_retry_interval=3,
        )

        # must be deleted
        resource_id, policy = nsx_security_policy.get_policy(
            self.client_session,
            inputs['node_name_prefix'] + inputs['policy_name']
        )

        self.assertTrue(resource_id is None)

        resource_id, _ = nsx_security_group.get_group(
            self.client_session,
            'globalroot-0',
            inputs['node_name_prefix'] + inputs['security_group_name']
        )

        self.assertTrue(resource_id is None)


if __name__ == '__main__':
    unittest.main()

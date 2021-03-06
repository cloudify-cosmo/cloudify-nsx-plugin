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
import cloudify_nsx.security.group as group
import cloudify_nsx.security.group_dynamic_member as group_dynamic_member
import cloudify_nsx.security.group_exclude_member as group_exclude_member
import cloudify_nsx.security.group_member as group_member
import cloudify_nsx.security.policy as policy
import cloudify_nsx.security.policy_group_bind as policy_group_bind
import cloudify_nsx.security.policy_section as policy_section
import cloudify_nsx.security.tag as tag
import cloudify_nsx.security.tag_vm as tag_vm
from cloudify.state import current_ctx


class SecurityUninstallTest(test_nsx_base.NSXBaseTest):

    def setUp(self):
        super(SecurityUninstallTest, self).setUp()
        self._regen_ctx()

    def tearDown(self):
        current_ctx.clear()
        super(SecurityUninstallTest, self).tearDown()

    @pytest.mark.internal
    @pytest.mark.unit
    def test_group_uninstall(self):
        """Check delete for security group"""
        self._common_uninstall_delete(
            'id', group.delete,
            {"group": {"name": "name"}},
            ['secGroupObject'], {
                'query_parameters_dict': {'force': 'true'},
                'uri_parameters': {'objectId': 'id'}
            }
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_group_dynamic_member_uninstall(self):
        """Check cleanup dynamic member in security group"""
        self._common_uninstall_read_update(
            'id', group_dynamic_member.delete,
            {"dynamic_member": {
                "dynamic_set": "dynamic_set",
                "security_group_id": "security_group_id"
            }},
            read_args=['secGroupObject'],
            read_kwargs={'uri_parameters': {'objectId': 'id'}},
            read_response={
                'body': {
                    'securitygroup': {
                        'dynamicMemberDefinition': {
                            'dynamicSet': {}
                        }
                    }
                },
                'status': 204
            },
            update_args=['secGroupBulk'],
            update_kwargs={
                'request_body_dict': {
                    'securitygroup': {
                        'dynamicMemberDefinition': {}
                    }
                },
                'uri_parameters': {'scopeId': 'id'}
            }
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_group_exclude_member_uninstall(self):
        """Check remove member from exclude list in security group"""
        self._common_uninstall_read_update(
            'security_group_id|member_id', group_exclude_member.delete,
            {"group_exclude_member": {
                "objectId": "objectId",
                "security_group_id": "security_group_id"
            }},
            read_args=['secGroupObject'],
            read_kwargs={'uri_parameters': {'objectId': 'security_group_id'}},
            read_response={
                'body': test_nsx_base.SEC_GROUP_EXCLUDE_AFTER,
                'status': 204
            },
            update_args=['secGroupObject'],
            update_kwargs={
                'request_body_dict': test_nsx_base.SEC_GROUP_EXCLUDE_BEFORE,
                'uri_parameters': {'objectId': 'security_group_id'}
            }
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_group_member_uninstall(self):
        """Check remove member from include list in security group"""
        self._common_uninstall_delete(
            'id|di', group_member.delete,
            {"group_member": {
                "objectId": "objectId",
                "security_group_id": "security_group_id"
            }},
            ['secGroupMember'], {
                'uri_parameters': {'memberMoref': 'di', 'objectId': 'id'}
            }
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_policy_uninstall(self):
        """Check delete for security policy"""
        self._common_uninstall_delete(
            'id', policy.delete,
            {"policy": {
                "name": "name",
                "description": "description",
                "precedence": "precedence"
            }},
            ['securityPolicyID'], {
                'query_parameters_dict': {'force': 'true'},
                'uri_parameters': {'ID': 'id'}
            }
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_policy_group_bind_uninstall(self):
        """Check unbind security group from security policy"""
        self._common_uninstall_read_update(
            'security_group_id|security_policy_id', policy_group_bind.delete,
            {"policy_group_bind": {
                "security_policy_id": "security_policy_id",
                "security_group_id": "security_group_id"
            }},
            read_args=['securityPolicyID'],
            read_kwargs={'uri_parameters': {'ID': 'security_policy_id'}},
            read_response={
                'body': test_nsx_base.SEC_GROUP_POLICY_BIND_AFTER,
                'status': 204
            },
            update_args=['securityPolicyID'],
            update_kwargs={
                'uri_parameters': {'ID': 'security_policy_id'},
                'request_body_dict': test_nsx_base.SEC_GROUP_POLICY_BIND_BEFORE
            }
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_policy_group_bind_uninstall_by_relationship(self):
        """Check unbind security policy from group by relationship"""
        self._common_run_relationship_read_update(
            policy_group_bind.unlink,
            {'resource_id': 'security_policy_id'},
            {'resource_id': 'security_group_id'},
            read_args=['securityPolicyID'],
            read_kwargs={'uri_parameters': {'ID': 'security_policy_id'}},
            read_response={
                'body': test_nsx_base.SEC_GROUP_POLICY_BIND_AFTER,
                'status': 204
            },
            update_args=['securityPolicyID'],
            update_kwargs={
                'uri_parameters': {'ID': 'security_policy_id'},
                'request_body_dict': test_nsx_base.SEC_GROUP_POLICY_BIND_BEFORE
            },
            update_response=test_nsx_base.SUCCESS_RESPONSE
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_policy_section_uninstall(self):
        """Check cleanup security policy section"""
        self._common_uninstall_read_update(
            'category|security_policy_id', policy_section.delete,
            {"policy_section": {
                "category": "category",
                "action": "action",
                "security_policy_id": "security_policy_id"
            }},
            read_args=['securityPolicyID'],
            read_kwargs={'uri_parameters': {'ID': 'security_policy_id'}},
            read_response={
                'body': test_nsx_base.SEC_POLICY_SECTION_AFTER,
                'status': 204
            },
            update_args=['securityPolicyID'],
            update_kwargs={
                'request_body_dict': test_nsx_base.SEC_POLICY_SECTION_BEFORE,
                'uri_parameters': {'ID': 'security_policy_id'}
            }
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_tag_uninstall(self):
        """Check delete security tag"""
        self._common_uninstall_delete(
            'id', tag.delete,
            {"tag": {"name": "name", "description": "description"}},
            ['securityTagID'], {'uri_parameters': {'tagId': 'id'}}
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_tag_vm_uninstall(self):
        """Check unbind security tag from vm"""
        self._common_uninstall_delete(
            'ab|cd', tag_vm.delete,
            {"vm_tag": {"vm_id": "vm_id", "tag_id": "tag_id"}},
            ['securityTagVM'],
            {'uri_parameters': {'tagId': 'ab', 'vmMoid': 'cd'}},
            read_args=['securityTagVMsList'],
            read_kwargs={"uri_parameters": {'tagId': 'ab'}},
            read_response={
                'body': {
                    'basicinfolist': {
                        'basicinfo': {
                            'objectId': 'cd'
                        }
                    }
                },
                'status': 204
            }
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_tag_vm_uninstall_by_relationship(self):
        """Check unbind security tag from vm by relationship"""
        self._common_run_relationship_read_update(
            tag_vm.unlink,
            {'vsphere_server_id': 'vm_id'}, {'resource_id': 'ab'},
            read_args=['securityTagVMsList'],
            read_kwargs={"uri_parameters": {'tagId': 'ab'}},
            read_response={
                'body': {},
                'status': 204
            }
        )


if __name__ == '__main__':
    unittest.main()

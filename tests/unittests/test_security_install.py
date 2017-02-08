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
import pytest
import test_base
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


class SecurityInstallTest(test_base.BaseTest):

    def setUp(self):
        super(SecurityInstallTest, self).setUp()
        self._regen_ctx()

    def tearDown(self):
        current_ctx.clear()
        super(SecurityInstallTest, self).tearDown()

    @pytest.mark.internal
    @pytest.mark.unit
    def test_group_install(self):
        """Check create for security group"""
        self._common_install_read_and_create(
            'id', group.create,
            {'group': {"name": "name"}},
            read_args=['secGroupScope'],
            read_kwargs={'uri_parameters': {'scopeId': 'globalroot-0'}},
            read_responce={
                'status': 204,
                'body': {
                    'list': {
                        'securitygroup': {
                            'name': 'name',
                            'objectId': 'id'
                        }
                    }
                }
            },
            create_args=['secGroupBulk'],
            create_kwargs={
                'request_body_dict': {
                    'securitygroup': {
                        'member': None,
                        'excludeMember': None,
                        'name': 'name',
                        'dynamicMemberDefinition': None
                    }
                },
                'uri_parameters': {'scopeId': 'globalroot-0'}
            },
            create_responce={
                'status': 204,
                'objectId': 'id'
            }
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_group_dynamic_member_install(self):
        """Check update dynamic member in security group"""
        self._common_install(
            "some_id", group_dynamic_member.create,
            {'dynamic_member': {
                "dynamic_set": "dynamic_set",
                "security_group_id": "security_group_id"
            }}
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_group_exclude_member_install(self):
        """Check insert member to exclude list in security group"""
        self._common_install(
            "some_id", group_exclude_member.create,
            {'group_exclude_member': {
                "objectId": "objectId",
                "security_group_id": "security_group_id"
            }}
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_group_member_install(self):
        """Check insert member to include list in security group"""
        self._common_install(
            "some_id", group_member.create,
            {'group_member': {
                "objectId": "objectId",
                "security_group_id": "security_group_id"
            }}
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_policy_install(self):
        """Check create for security policy"""
        self._common_install_read_and_create(
            'id', policy.create,
            {'policy': {
                "name": "name",
                "description": "description",
                "precedence": "precedence"
            }},
            read_args=['securityPolicyID'],
            read_kwargs={'uri_parameters': {'ID': 'all'}},
            read_responce={
                'status': 204,
                'body': {
                    'securityPolicies': {
                        'securityPolicy': {
                            'name': 'name',
                            'objectId': 'id',
                            'description': 'description',
                            'precedence': 'precedence',
                            'parent': None,
                            'securityGroupBinding': None,
                            'actionsByCategory': None
                        }
                    }
                }
            },
            create_args=['securityPolicy'],
            create_kwargs={
                'request_body_dict': {
                    'securityPolicy': {
                        'name': 'name',
                        'parent': None,
                        'precedence': 'precedence',
                        'actionsByCategory': None,
                        'securityGroupBinding': None,
                        'description': 'description'
                    }
                }
            },
            create_responce={
                'status': 204,
                'objectId': 'id'
            },
            recheck_runtime={
                'policy': {
                    'actionsByCategory': None,
                    'description': 'description',
                    'name': 'name',
                    'parent': None,
                    'precedence': 'precedence',
                    'securityGroupBinding': None
                }
            }
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_policy_group_bind_install(self):
        """Check bind security group to security policy"""
        self._common_install(
            "some_id", policy_group_bind.create,
            {'policy_group_bind': {
                "security_policy_id": "security_policy_id",
                "security_group_id": "security_group_id"
            }}
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_policy_section_install(self):
        """Check replace security policy section"""
        self._common_install(
            "some_id", policy_section.create,
            {'policy_section': {
                "category": "category",
                "action": "action",
                "security_policy_id": "security_policy_id"
            }}
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_tag_install(self):
        """Check create security tag"""
        self._common_install_read_and_create(
            'id', tag.create,
            {'tag': {
                "name": "name", "description": "description"
            }},
            read_args=['securityTag'],
            read_kwargs={},
            read_responce={
                'status': 204,
                'body': {
                    'securityTags': {
                        'securityTag': {
                            'name': 'name',
                            'objectId': 'id'
                        }
                    }
                }
            },
            create_args=['securityTag'],
            create_kwargs={
                'request_body_dict': {
                    'securityTag': {
                        'name': 'name',
                        'description': 'description'
                    }
                }
            },
            create_responce={
                'status': 204,
                'objectId': 'id'
            }
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_tag_vm_install(self):
        """Check bind security tag to vm"""
        self._common_install(
            "some_id", tag_vm.create,
            {'vm_tag': {
                "vm_id": "vm_id", "tag_id": "tag_id"
            }}
        )


if __name__ == '__main__':
    unittest.main()

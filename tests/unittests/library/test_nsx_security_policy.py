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
import pytest
import test_nsx_base
import cloudify_nsx.library.nsx_security_policy as nsx_security_policy
from cloudify import exceptions as cfy_exc


class NsxSecurityPolicyTest(test_nsx_base.NSXBaseTest):

    @pytest.mark.internal
    @pytest.mark.unit
    def test_add_policy_group_bind_insert(self):
        """Check nsx_security_policy.add_policy_group_bind func: insert"""
        client_session = self._prepare_check(read={
            'status': 204,
            'body': {
                'securityPolicy': {
                    'securityGroupBinding': [{
                        'objectId': 'other'
                    }],
                    'name': 'name'
                }
            }
        })

        self.assertEqual(
            nsx_security_policy.add_policy_group_bind(
                client_session, 'security_policy_id', 'security_group_id'
            ),
            "security_group_id|security_policy_id"
        )

        client_session.read.assert_called_with(
            'securityPolicyID', uri_parameters={'ID': 'security_policy_id'}
        )

        client_session.update.assert_called_with(
            'securityPolicyID',
            request_body_dict={
                'securityPolicy': {
                    'securityGroupBinding': [{
                        'objectId': 'other'
                    }, {
                        'objectId': 'security_group_id'
                    }],
                    'name': 'name'
                }
            },
            uri_parameters={'ID': 'security_policy_id'}
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_add_policy_group_bind_existing(self):
        """Check nsx_security_policy.add_policy_group_bind func existing"""
        client_session = self._prepare_check(read={
            'status': 204,
            'body': {
                'securityPolicy': {
                    'securityGroupBinding': [{
                        'objectId': 'other'
                    }],
                    'name': 'name'
                }
            }
        })

        with self.assertRaises(cfy_exc.NonRecoverableError) as error:
            nsx_security_policy.add_policy_group_bind(
                client_session, 'security_policy_id', 'other'
            )
        self.assertEqual(
            str(error.exception),
            "Group other already exists in name policy"
        )

        client_session.read.assert_called_with(
            'securityPolicyID', uri_parameters={'ID': 'security_policy_id'}
        )

        client_session.update.assert_not_called()

    @pytest.mark.internal
    @pytest.mark.unit
    def test_del_policy_group_bind_existing(self):
        """Check nsx_security_policy.del_policy_group_bind func: existing"""
        client_session = self._prepare_check(read={
            'status': 204,
            'body': {
                'securityPolicy': {
                    'securityGroupBinding': [{
                        'objectId': 'other'
                    }, {
                        'objectId': 'security_group_id'
                    }],
                    'name': 'name'
                }
            }
        })

        nsx_security_policy.del_policy_group_bind(
            client_session, "security_group_id|security_policy_id"
        )

        client_session.read.assert_called_with(
            'securityPolicyID', uri_parameters={'ID': 'security_policy_id'}
        )

        client_session.update.assert_called_with(
            'securityPolicyID',
            request_body_dict={
                'securityPolicy': {
                    'securityGroupBinding': [{
                        'objectId': 'other'
                    }],
                    'name': 'name'
                }
            },
            uri_parameters={'ID': 'security_policy_id'}
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_del_policy_group_bind_unexisting(self):
        """Check nsx_security_policy.del_policy_group_bind func: unexisting"""
        client_session = self._prepare_check(read={
            'status': 204,
            'body': {
                'securityPolicy': {
                    'securityGroupBinding': [{
                        'objectId': 'other'
                    }, {
                        'objectId': 'security_group_id'
                    }],
                    'name': 'name'
                }
            }
        })

        nsx_security_policy.del_policy_group_bind(
            client_session, "security_id|security_policy_id"
        )

        client_session.read.assert_called_with(
            'securityPolicyID', uri_parameters={'ID': 'security_policy_id'}
        )

        client_session.update.assert_not_called()

    @pytest.mark.internal
    @pytest.mark.unit
    def test_add_policy_section_insert(self):
        """Check nsx_security_policy.add_policy_section func: positive"""
        client_session = self._prepare_check(read={
            'status': 204,
            'body': {
                'securityPolicy': {
                    'actionsByCategory': [{
                        "category": "other_category",
                        "action": "other_action"
                    }]
                }
            }
        })

        self.assertEqual(
            nsx_security_policy.add_policy_section(
                client_session, 'security_policy_id', 'category', "action"
            ),
            "category|security_policy_id"
        )

        client_session.read.assert_called_with(
            'securityPolicyID', uri_parameters={'ID': 'security_policy_id'}
        )

        client_session.update.assert_called_with(
            'securityPolicyID',
            request_body_dict={
                'securityPolicy': {
                    'actionsByCategory': [{
                        "category": "other_category",
                        "action": "other_action"
                    }, {
                        "category": "category",
                        "action": "action"
                    }]
                }
            },
            uri_parameters={'ID': 'security_policy_id'}
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_add_policy_section_overwrite(self):
        """Check nsx_security_policy.add_policy_section func: overwrite"""
        client_session = self._prepare_check(read={
            'status': 204,
            'body': {
                'securityPolicy': {
                    'actionsByCategory': [{
                        "category": "other_category",
                        "action": "other_action"
                    }]
                }
            }
        })

        self.assertEqual(
            nsx_security_policy.add_policy_section(
                client_session, 'security_policy_id', 'other_category',
                "action"
            ),
            "other_category|security_policy_id"
        )

        client_session.read.assert_called_with(
            'securityPolicyID', uri_parameters={'ID': 'security_policy_id'}
        )

        client_session.update.assert_called_with(
            'securityPolicyID',
            request_body_dict={
                'securityPolicy': {
                    'actionsByCategory': [{
                        "category": "other_category",
                        "action": "action"
                    }]
                }
            },
            uri_parameters={'ID': 'security_policy_id'}
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_del_policy_section_existing(self):
        """Check nsx_security_policy.del_policy_section func existing"""

        # delete existed
        client_session = self._prepare_check(read={
            'status': 204,
            'body': {
                'securityPolicy': {
                    'actionsByCategory': [{
                        "category": "other_category",
                        "action": "other_action"
                    }, {
                        "category": "category",
                        "action": "action"
                    }]
                }
            }
        })

        nsx_security_policy.del_policy_section(
            client_session, "category|security_policy_id"
        )

        client_session.read.assert_called_with(
            'securityPolicyID', uri_parameters={'ID': 'security_policy_id'}
        )

        client_session.update.assert_called_with(
            'securityPolicyID',
            request_body_dict={
                'securityPolicy': {
                    'actionsByCategory': [{
                        "category": "other_category",
                        "action": "other_action"
                    }]
                }
            },
            uri_parameters={'ID': 'security_policy_id'}
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_del_policy_section_unexisting(self):
        """Check nsx_security_policy.del_policy_section func: unexisting"""

        # delete existed
        client_session = self._prepare_check(read={
            'status': 204,
            'body': {
                'securityPolicy': {
                    'actionsByCategory': [{
                        "category": "other_category",
                        "action": "other_action"
                    }, {
                        "category": "category",
                        "action": "action"
                    }]
                }
            }
        })

        nsx_security_policy.del_policy_section(
            client_session, "unknown|security_policy_id"
        )

        client_session.read.assert_called_with(
            'securityPolicyID', uri_parameters={'ID': 'security_policy_id'}
        )

        client_session.update.assert_not_called()


if __name__ == '__main__':
    unittest.main()

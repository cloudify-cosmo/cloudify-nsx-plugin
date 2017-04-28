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
        read_response = {
            'status': 204,
            'body': test_nsx_base.SEC_GROUP_POLICY_BIND_BEFORE
        }
        client_session = self._create_fake_cs_result()
        self._update_fake_cs_result(
            client_session,
            read_response=read_response,
            update_response=test_nsx_base.SUCCESS_RESPONSE
        )

        self.assertEqual(
            nsx_security_policy.add_policy_group_bind(
                client_session, 'security_policy_id', 'security_group_id'
            ),
            "security_group_id|security_policy_id"
        )
        self._check_fake_cs_result(
            client_session,
            # read
            read_response=read_response,
            read_args=['securityPolicyID'],
            read_kwargs={'uri_parameters': {'ID': 'security_policy_id'}},
            # update
            update_response=test_nsx_base.SUCCESS_RESPONSE,
            update_args=['securityPolicyID'],
            update_kwargs={
                'request_body_dict': test_nsx_base.SEC_GROUP_POLICY_BIND_AFTER,
                'uri_parameters': {'ID': 'security_policy_id'}
            }
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_add_policy_group_bind_existing(self):
        """Check nsx_security_policy.add_policy_group_bind func existing"""
        read_response = {
            'status': 204,
            'body': test_nsx_base.SEC_GROUP_POLICY_BIND_BEFORE
        }

        client_session = self._create_fake_cs_result()
        self._update_fake_cs_result(
            client_session,
            read_response=read_response
        )

        with self.assertRaises(cfy_exc.NonRecoverableError) as error:
            nsx_security_policy.add_policy_group_bind(
                client_session, 'security_policy_id', 'other'
            )
        self.assertEqual(
            str(error.exception),
            "Group other already exists in name policy"
        )

        self._check_fake_cs_result(
            client_session,
            # read
            read_response=read_response,
            read_args=['securityPolicyID'],
            read_kwargs={'uri_parameters': {'ID': 'security_policy_id'}},
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_del_policy_group_bind_existing(self):
        """Check nsx_security_policy.del_policy_group_bind func: existing"""
        read_response = {
            'status': 204,
            'body': test_nsx_base.SEC_GROUP_POLICY_BIND_AFTER
        }
        client_session = self._create_fake_cs_result()
        self._update_fake_cs_result(
            client_session,
            read_response=read_response,
            update_response=test_nsx_base.SUCCESS_RESPONSE
        )

        nsx_security_policy.del_policy_group_bind(
            client_session, "security_group_id|security_policy_id"
        )

        self._check_fake_cs_result(
            client_session,
            # read
            read_response=read_response,
            read_args=['securityPolicyID'],
            read_kwargs={'uri_parameters': {'ID': 'security_policy_id'}},
            # update
            update_response=test_nsx_base.SUCCESS_RESPONSE,
            update_args=['securityPolicyID'],
            update_kwargs={
                'uri_parameters': {'ID': 'security_policy_id'},
                'request_body_dict': test_nsx_base.SEC_GROUP_POLICY_BIND_BEFORE
            }
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_del_policy_group_bind_unexisting(self):
        """Check nsx_security_policy.del_policy_group_bind func: unexisting"""
        read_response = {
            'status': 204,
            'body': test_nsx_base.SEC_GROUP_POLICY_BIND_AFTER
        }
        client_session = self._create_fake_cs_result()
        self._update_fake_cs_result(
            client_session,
            read_response=read_response
        )

        nsx_security_policy.del_policy_group_bind(
            client_session, "security_id|security_policy_id"
        )

        self._check_fake_cs_result(
            client_session,
            # read
            read_response=read_response,
            read_args=['securityPolicyID'],
            read_kwargs={'uri_parameters': {'ID': 'security_policy_id'}},
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_add_policy_section_insert(self):
        """Check nsx_security_policy.add_policy_section func: insert"""
        read_response = {
            'status': 204,
            'body': test_nsx_base.SEC_POLICY_SECTION_BEFORE
        }
        client_session = self._create_fake_cs_result()
        self._update_fake_cs_result(
            client_session,
            read_response=read_response,
            update_response=test_nsx_base.SUCCESS_RESPONSE
        )

        self.assertEqual(
            nsx_security_policy.add_policy_section(
                client_session, 'security_policy_id', 'category', "action"
            ),
            "category|security_policy_id"
        )

        self._check_fake_cs_result(
            client_session,
            # read
            read_response=read_response,
            read_args=['securityPolicyID'],
            read_kwargs={'uri_parameters': {'ID': 'security_policy_id'}},
            # update
            update_response=test_nsx_base.SUCCESS_RESPONSE,
            update_args=['securityPolicyID'],
            update_kwargs={
                'request_body_dict': test_nsx_base.SEC_POLICY_SECTION_AFTER,
                'uri_parameters': {'ID': 'security_policy_id'}
            }
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_add_policy_section_overwrite(self):
        """Check nsx_security_policy.add_policy_section func: overwrite"""
        read_response = {
            'status': 204,
            'body': test_nsx_base.SEC_POLICY_SECTION_BEFORE
        }

        client_session = self._create_fake_cs_result()
        self._update_fake_cs_result(
            client_session,
            read_response=read_response,
            update_response=test_nsx_base.SUCCESS_RESPONSE
        )

        self.assertEqual(
            nsx_security_policy.add_policy_section(
                client_session, 'security_policy_id', 'other_category',
                "action"
            ),
            "other_category|security_policy_id"
        )

        self._check_fake_cs_result(
            client_session,
            # read
            read_response=read_response,
            read_args=['securityPolicyID'],
            read_kwargs={'uri_parameters': {'ID': 'security_policy_id'}},
            # update
            update_response=test_nsx_base.SUCCESS_RESPONSE,
            update_args=['securityPolicyID'],
            update_kwargs={
                'uri_parameters': {'ID': 'security_policy_id'},
                'request_body_dict': test_nsx_base.SEC_POLICY_SECTION_OVERWRITE
            }
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_del_policy_section_existing(self):
        """Check nsx_security_policy.del_policy_section func existing"""
        read_response = {
            'status': 204,
            'body': test_nsx_base.SEC_POLICY_SECTION_AFTER
        }

        # delete existed
        client_session = self._create_fake_cs_result()
        self._update_fake_cs_result(
            client_session,
            read_response=read_response,
            update_response=test_nsx_base.SUCCESS_RESPONSE
        )

        nsx_security_policy.del_policy_section(
            client_session, "category|security_policy_id"
        )

        self._check_fake_cs_result(
            client_session,
            # read
            read_response=read_response,
            read_args=['securityPolicyID'],
            read_kwargs={'uri_parameters': {'ID': 'security_policy_id'}},
            # update
            update_response=test_nsx_base.SUCCESS_RESPONSE,
            update_args=['securityPolicyID'],
            update_kwargs={
                'request_body_dict': test_nsx_base.SEC_POLICY_SECTION_BEFORE,
                'uri_parameters': {'ID': 'security_policy_id'}
            }
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_del_policy_section_unexisting(self):
        """Check nsx_security_policy.del_policy_section func: unexisting"""

        read_response = {
            'status': 204,
            'body': test_nsx_base.SEC_POLICY_SECTION_AFTER
        }

        # delete existed
        client_session = self._create_fake_cs_result()
        self._update_fake_cs_result(
            client_session,
            read_response=read_response
        )

        nsx_security_policy.del_policy_section(
            client_session, "unknown|security_policy_id"
        )

        self._check_fake_cs_result(
            client_session,
            # read
            read_response=read_response,
            read_args=['securityPolicyID'],
            read_kwargs={'uri_parameters': {'ID': 'security_policy_id'}}
        )


if __name__ == '__main__':
    unittest.main()

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
import test_nsx_base
import cloudify_nsx.library.nsx_security_group as nsx_security_group
from cloudify import exceptions as cfy_exc


class NsxSecurityGroupTest(test_nsx_base.NSXBaseTest):

    @pytest.mark.internal
    @pytest.mark.unit
    def test_add_group_exclude_member_insert(self):
        """Check nsx_security_group.add_group_exclude_member func insert"""
        read_response = {
            'status': 204,
            'body': test_nsx_base.SEC_GROUP_EXCLUDE_BEFORE
        }
        client_session = self._create_fake_cs_result()
        self._update_fake_cs_result(
            client_session,
            read_response=read_response,
            update_response=test_nsx_base.SUCCESS_RESPONSE
        )

        self.assertEqual(
            nsx_security_group.add_group_exclude_member(
                client_session, 'security_group_id', 'member_id'
            ),
            "security_group_id|member_id"
        )

        self._check_fake_cs_result(
            client_session,
            # read
            read_response=read_response,
            read_args=['secGroupObject'],
            read_kwargs={'uri_parameters': {'objectId': 'security_group_id'}},
            # update
            update_response=test_nsx_base.SUCCESS_RESPONSE,
            update_args=['secGroupObject'],
            update_kwargs={
                'request_body_dict': test_nsx_base.SEC_GROUP_EXCLUDE_AFTER,
                'uri_parameters': {'objectId': 'security_group_id'}
            }
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_add_group_exclude_member_existing(self):
        """Check nsx_security_group.add_group_exclude_member func existing"""
        read_response = {
            'status': 204,
            'body': test_nsx_base.SEC_GROUP_EXCLUDE_BEFORE
        }
        client_session = self._create_fake_cs_result()
        self._update_fake_cs_result(
            client_session,
            read_response=read_response
        )

        with self.assertRaises(cfy_exc.NonRecoverableError) as error:
            nsx_security_group.add_group_exclude_member(
                client_session, 'security_group_id', 'other_objectId'
            )

        self.assertEqual(
            str(error.exception),
            "Member other_objectId already exists in some_name group"
        )
        self._check_fake_cs_result(
            client_session,
            # read
            read_response=read_response,
            read_args=['secGroupObject'],
            read_kwargs={'uri_parameters': {'objectId': 'security_group_id'}},
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_del_group_exclude_member_existing(self):
        """Check nsx_security_group.del_group_exclude_member func existing"""
        read_response = {
            'status': 204,
            'body': test_nsx_base.SEC_GROUP_EXCLUDE_AFTER
        }
        client_session = self._create_fake_cs_result()
        self._update_fake_cs_result(
            client_session,
            read_response=read_response,
            update_response=test_nsx_base.SUCCESS_RESPONSE
        )

        nsx_security_group.del_group_exclude_member(
            client_session, "security_group_id|member_id"
        )

        self._check_fake_cs_result(
            client_session,
            # read
            read_response=read_response,
            read_args=['secGroupObject'],
            read_kwargs={'uri_parameters': {'objectId': 'security_group_id'}},
            # update
            update_response=test_nsx_base.SUCCESS_RESPONSE,
            update_args=['secGroupObject'],
            update_kwargs={
                'request_body_dict': test_nsx_base.SEC_GROUP_EXCLUDE_BEFORE,
                'uri_parameters': {'objectId': 'security_group_id'}
            }
        )

    @pytest.mark.internal
    @pytest.mark.unit
    def test_del_group_exclude_member_unexisting(self):
        """Check nsx_security_group.del_group_exclude_member func unexisting"""
        read_response = {
            'status': 204,
            'body': test_nsx_base.SEC_GROUP_EXCLUDE_AFTER
        }
        client_session = self._create_fake_cs_result()
        self._update_fake_cs_result(
            client_session,
            read_response=read_response
        )

        nsx_security_group.del_group_exclude_member(
            client_session, "security_group_id|unknown"
        )

        self._check_fake_cs_result(
            client_session,
            # read
            read_response=read_response,
            read_args=['secGroupObject'],
            read_kwargs={'uri_parameters': {'objectId': 'security_group_id'}}
        )


if __name__ == '__main__':
    unittest.main()

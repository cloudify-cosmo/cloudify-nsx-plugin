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
import cloudify_nsx.library.nsx_security_group as nsx_security_group
from cloudify import exceptions as cfy_exc


class NsxSecurityGroupTest(unittest.TestCase):

    @pytest.mark.internal
    @pytest.mark.unit
    def test_add_group_exclude_member(self):
        """Check nsx_security_group.add_group_exclude_member func"""
        def prepere_check():
            client_session = mock.Mock()
            client_session.read = mock.Mock(
                return_value={
                    'status': 204,
                    'body': {
                        'securitygroup': {
                            'excludeMember': [{
                                "objectId": "other_objectId",
                            }],
                            'name': 'some_name'
                        }
                    }
                }
            )

            client_session.update = mock.Mock(
                return_value={
                    'status': 204
                }
            )

            return client_session

        # common add
        client_session = prepere_check()

        self.assertEqual(
            nsx_security_group.add_group_exclude_member(
                client_session, 'security_group_id', 'member_id'
            ),
            "security_group_id|member_id"
        )

        client_session.read.assert_called_with(
            'secGroupObject', uri_parameters={'objectId': 'security_group_id'}
        )

        client_session.update.assert_called_with(
            'secGroupObject',
            request_body_dict={
                'securitygroup': {
                    'excludeMember': [{
                        'objectId': 'other_objectId'
                    }, {
                        'objectId': 'member_id'
                    }],
                    'name': 'some_name'
                }
            },
            uri_parameters={'objectId': 'security_group_id'}
        )

        # issue with add
        client_session = prepere_check()

        with self.assertRaises(cfy_exc.NonRecoverableError):
            nsx_security_group.add_group_exclude_member(
                client_session, 'security_group_id', 'other_objectId'
            )

        client_session.read.assert_called_with(
            'secGroupObject', uri_parameters={'objectId': 'security_group_id'}
        )

        client_session.update.assert_not_called()

    @pytest.mark.internal
    @pytest.mark.unit
    def test_del_group_exclude_member(self):
        """Check nsx_security_group.del_group_exclude_member func"""
        def prepere_check():
            client_session = mock.Mock()
            client_session.read = mock.Mock(
                return_value={
                    'status': 204,
                    'body': {
                        'securitygroup': {
                            'excludeMember': [{
                                'objectId': 'member_id'
                            }, {
                                'objectId': 'objectOtherId'
                            }],
                            'name': 'some_name'
                        }
                    }
                }
            )

            client_session.update = mock.Mock(
                return_value={
                    'status': 204
                }
            )

            return client_session

        # delete existed
        client_session = prepere_check()

        nsx_security_group.del_group_exclude_member(
            client_session, "security_group_id|member_id"
        )

        client_session.read.assert_called_with(
            'secGroupObject', uri_parameters={'objectId': 'security_group_id'}
        )

        client_session.update.assert_called_with(
            'secGroupObject',
            request_body_dict={
                'securitygroup': {
                    'excludeMember': [{
                        'objectId': 'objectOtherId'
                    }],
                    'name': 'some_name'
                }
            },
            uri_parameters={'objectId': 'security_group_id'}
        )

        # delete unexisted
        client_session = prepere_check()

        nsx_security_group.del_group_exclude_member(
            client_session, "security_group_id|other_member_id"
        )

        client_session.read.assert_called_with(
            'secGroupObject', uri_parameters={'objectId': 'security_group_id'}
        )

        client_session.update.assert_not_called()


if __name__ == '__main__':
    unittest.main()

# Copyright (c) 2016 GigaSpaces Technologies Ltd. All rights reserved
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
import nsx_common as common


def get(client_session, scopeId, name):
    raw_result = client_session.read('secGroupScope',
                                     uri_parameters={'scopeId': scopeId})

    common.check_raw_result(raw_result)

    if not 'list' in raw_result['body']:
        return None

    groups = raw_result['body']['list'].get('securitygroup')

    if isinstance(groups, dict):
        groups = [groups]

    for group in groups:
        if group.get('name') == name:
            return group.get('objectId')

    return None


def add_group(client_session, scopeId, name, member, excludeMember,
              dynamicMemberDefinition):

    security_group = {
        'securitygroup': {
            'name': name,
            'member': member,
            'excludeMember': excludeMember,
            'dynamicMemberDefinition': dynamicMemberDefinition
        }
    }

    raw_result = client_session.create(
        'secGroupBulk', uri_parameters={'scopeId': scopeId},
        request_body_dict=security_group
    )

    common.check_raw_result(raw_result)

    return raw_result['objectId']


def del_group(client_session, resource_id):

    client_session.delete('secGroupObject',
                          uri_parameters={'objectId': resource_id},
                          query_parameters_dict={'force': 'true'})

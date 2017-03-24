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
from cloudify import exceptions as cfy_exc


def get_group(client_session, scopeId, name):
    return common.nsx_search(
        client_session, 'body/list/securitygroup', name,
        'secGroupScope', uri_parameters={'scopeId': scopeId}
    )


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


def add_group_exclude_member(client_session, security_group_id, member_id):
    security_group = common.nsx_read(
        client_session, 'body',
        'secGroupObject', uri_parameters={'objectId': security_group_id}
    )

    excludeMembers = common.nsx_struct_get_list(
        security_group, 'securitygroup/excludeMember'
    )

    for member in excludeMembers:
        if member.get("objectId") == member_id:
            raise cfy_exc.NonRecoverableError(
                "Member %s already exists in %s group" % (
                    member_id, security_group['securitygroup'].get(
                        'name', '*unknown*'
                    )
                )
            )

    excludeMembers.append({"objectId": member_id})

    raw_result = client_session.update(
        'secGroupObject', uri_parameters={'objectId': security_group_id},
        request_body_dict=security_group
    )

    common.check_raw_result(raw_result)

    return "%s|%s" % (security_group_id, member_id)


def add_group_member(client_session, security_group_id, member_id):

    raw_result = client_session.update(
        'secGroupMember', uri_parameters={
            'objectId': security_group_id,
            'memberMoref': member_id}
    )

    common.check_raw_result(raw_result)

    return "%s|%s" % (security_group_id, member_id)


def set_dynamic_member(client_session, security_group_id, dynamic_set):

    security_group = common.nsx_read(
        client_session, 'body',
        'secGroupObject', uri_parameters={'objectId': security_group_id}
    )
    # fully overwrite previous state
    security_group['securitygroup']['dynamicMemberDefinition'] = {
        'dynamicSet': dynamic_set
    }

    # it is not error!
    # We need to use bulk to update dynamic members
    # with use security_group_id as scope
    raw_result = client_session.update(
        'secGroupBulk', uri_parameters={'scopeId': security_group_id},
        request_body_dict=security_group
    )

    common.check_raw_result(raw_result)

    return security_group_id


def del_dynamic_member(client_session, security_group_id):
    security_group = common.nsx_read(
        client_session, 'body',
        'secGroupObject', uri_parameters={'objectId': security_group_id}
    )
    security_group['securitygroup']['dynamicMemberDefinition'] = {}

    # it is not error!
    # We need to use bulk to update dynamic members
    # with use security_group_id as scope
    raw_result = client_session.update(
        'secGroupBulk', uri_parameters={'scopeId': security_group_id},
        request_body_dict=security_group
    )

    common.check_raw_result(raw_result)


def del_group_member(client_session, resource_id):
    try:
        security_group_id, member_id = resource_id.split("|")
    except Exception as ex:
        raise cfy_exc.NonRecoverableError(
            'Unexpected error retrieving resource ID: %s' % str(ex)
        )

    raw_result = client_session.delete(
        'secGroupMember', uri_parameters={
            'objectId': security_group_id,
            'memberMoref': member_id}
    )

    common.check_raw_result(raw_result)


def del_group_exclude_member(client_session, resource_id):
    try:
        security_group_id, member_id = resource_id.split("|")
    except Exception as ex:
        raise cfy_exc.NonRecoverableError(
            'Unexpected error retrieving resource ID: %s' % str(ex)
        )

    security_group = common.nsx_read(
        client_session, 'body',
        'secGroupObject', uri_parameters={'objectId': security_group_id}
    )

    excludeMembers = common.nsx_struct_get_list(
        security_group, 'securitygroup/excludeMember'
    )

    for member in excludeMembers:
        if member.get("objectId") == member_id:
            excludeMembers.remove(member)
            break
    else:
        return

    raw_result = client_session.update(
        'secGroupObject', uri_parameters={'objectId': security_group_id},
        request_body_dict=security_group
    )

    common.check_raw_result(raw_result)


def del_group(client_session, resource_id):

    client_session.delete('secGroupObject',
                          uri_parameters={'objectId': resource_id},
                          query_parameters_dict={'force': 'true'})

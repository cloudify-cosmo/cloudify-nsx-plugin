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


def get_policy(client_session, name):
    raw_result = client_session.read('securityPolicyID',
                                     uri_parameters={'ID': "all"})

    common.check_raw_result(raw_result)

    if 'securityPolicies' not in raw_result['body']:
        return None

    policies = raw_result['body']['securityPolicies'].get('securityPolicy')

    if isinstance(policies, dict):
        policies = [policies]

    for policy in policies:
        if policy.get('name') == name:
            return policy.get('objectId')

    return None


def get_group(client_session, scopeId, name):
    raw_result = client_session.read('secGroupScope',
                                     uri_parameters={'scopeId': scopeId})

    common.check_raw_result(raw_result)

    if 'list' not in raw_result['body']:
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


def add_group_exclude_member(client_session, security_group_id, member_id):
    raw_result = client_session.read(
        'secGroupObject', uri_parameters={'objectId': security_group_id}
    )

    common.check_raw_result(raw_result)

    security_group = raw_result['body']

    if 'excludeMember' not in security_group['securitygroup']:
        security_group['securitygroup']['excludeMember'] = []

    excludeMembers = security_group['securitygroup']['excludeMember']
    if isinstance(excludeMembers, dict):
        excludeMembers = [excludeMembers]

    for member in excludeMembers:
        if member.get("objectId") == member_id:
            raise cfy_exc.NonRecoverableError(
                "You already have such member in security group."
            )

    excludeMembers.append({"objectId": member_id})

    security_group['securitygroup']['excludeMember'] = excludeMembers

    raw_result = client_session.update(
        'secGroupObject', uri_parameters={'objectId': security_group_id},
        request_body_dict=security_group
    )

    common.check_raw_result(raw_result)

    return "%s|%s" % (security_group_id, member_id)


def add_group_member(client_session, security_group_id, member_id):

    raw_result = client_session.read(
        'secGroupObject', uri_parameters={'objectId': security_group_id}
    )

    common.check_raw_result(raw_result)

    security_group = raw_result['body']

    if 'member' not in security_group['securitygroup']:
        security_group['securitygroup']['member'] = []

    members = security_group['securitygroup']['member']
    if isinstance(members, dict):
        members = [members]

    for member in members:
        if member.get("objectId") == member_id:
            raise cfy_exc.NonRecoverableError(
                "You already have such member in security group."
            )

    members.append({"objectId": member_id})

    security_group['securitygroup']['member'] = members

    raw_result = client_session.update(
        'secGroupObject', uri_parameters={'objectId': security_group_id},
        request_body_dict=security_group
    )

    common.check_raw_result(raw_result)

    return "%s|%s" % (security_group_id, member_id)


def del_group_member(client_session, resource_id):
    security_group_id, member_id = resource_id.split("|")

    raw_result = client_session.read(
        'secGroupObject', uri_parameters={'objectId': security_group_id}
    )

    common.check_raw_result(raw_result)

    security_group = raw_result['body']

    if 'member' not in security_group['securitygroup']:
        return

    members = security_group['securitygroup']['member']
    if isinstance(members, dict):
        members = [members]

    for member in members:
        if member.get("objectId") == member_id:
            members.remove(member)
            break

    security_group['securitygroup']['member'] = members

    raw_result = client_session.update(
        'secGroupObject', uri_parameters={'objectId': security_group_id},
        request_body_dict=security_group
    )

    common.check_raw_result(raw_result)


def del_group_exclude_member(client_session, resource_id):
    security_group_id, member_id = resource_id.split("|")

    raw_result = client_session.read(
        'secGroupObject', uri_parameters={'objectId': security_group_id}
    )

    common.check_raw_result(raw_result)

    security_group = raw_result['body']

    if 'excludeMember' not in security_group['securitygroup']:
        return

    excludeMembers = security_group['securitygroup']['excludeMember']
    if isinstance(excludeMembers, dict):
        excludeMembers = [excludeMembers]

    for member in excludeMembers:
        if member.get("objectId") == member_id:
            excludeMembers.remove(member)
            break

    security_group['securitygroup']['member'] = excludeMembers

    raw_result = client_session.update(
        'secGroupObject', uri_parameters={'objectId': security_group_id},
        request_body_dict=security_group
    )

    common.check_raw_result(raw_result)


def add_policy(client_session, name, description, precedence, parent,
               securityGroupBinding, actionsByCategory):

    security_policy = {
        'securityPolicy': {
            "name": name,
            "description": description,
            "precedence": precedence,
            "parent": parent,
            "securityGroupBinding": securityGroupBinding,
            "actionsByCategory": actionsByCategory
        }
    }

    raw_result = client_session.create(
        'securityPolicy', request_body_dict=security_policy
    )

    common.check_raw_result(raw_result)

    return raw_result['objectId']


def del_group(client_session, resource_id):

    client_session.delete('secGroupObject',
                          uri_parameters={'objectId': resource_id},
                          query_parameters_dict={'force': 'true'})


def del_policy(client_session, resource_id):

    client_session.delete('securityPolicyID',
                          uri_parameters={'ID': resource_id},
                          query_parameters_dict={'force': 'true'})

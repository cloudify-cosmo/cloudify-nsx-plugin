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
    return common.nsx_search(
        client_session, 'body/securityPolicies/securityPolicy', name,
        'securityPolicyID', uri_parameters={'ID': "all"}
    )


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


def add_policy_group_bind(client_session, security_policy_id,
                          security_group_id):

    security_policy = common.nsx_read(
        client_session, 'body',
        'securityPolicyID', uri_parameters={'ID': security_policy_id}
    )

    bindings = common.nsx_struct_get_list(
        security_policy, 'securityPolicy/securityGroupBinding'
    )

    for bind in bindings:
        if bind.get('objectId') == security_group_id:
            raise cfy_exc.NonRecoverableError(
                "Group %s already exists in %s policy" % (
                    security_group_id,
                    security_policy['securityPolicy'].get(
                        'name', '*unknown*'
                    )
                )
            )

    bindings.append({'objectId': security_group_id})

    raw_result = client_session.update(
        'securityPolicyID', uri_parameters={'ID': security_policy_id},
        request_body_dict=security_policy
    )

    common.check_raw_result(raw_result)

    return "%s|%s" % (security_group_id, security_policy_id)


def add_policy_section(client_session, security_policy_id, category, action):
    security_policy = common.nsx_read(
        client_session, 'body',
        'securityPolicyID', uri_parameters={'ID': security_policy_id}
    )

    actionsByCategory = common.nsx_struct_get_list(
        security_policy, 'securityPolicy/actionsByCategory'
    )

    for actions in actionsByCategory:
        if actions.get('category') == category:
            actions['action'] = action
            break
    else:
        actionsByCategory.append({
            'category': category,
            'action': action
        })

    raw_result = client_session.update(
        'securityPolicyID', uri_parameters={'ID': security_policy_id},
        request_body_dict=security_policy
    )

    common.check_raw_result(raw_result)

    return "%s|%s" % (category, security_policy_id)


def del_policy_section(client_session, resource_id):
    try:
        category, security_policy_id = resource_id.split("|")
    except Exception as ex:
        raise cfy_exc.NonRecoverableError(
            'Unexpected error retrieving resource ID: %s' % str(ex)
        )

    security_policy = common.nsx_read(
        client_session, 'body',
        'securityPolicyID', uri_parameters={'ID': security_policy_id}
    )

    actionsByCategory = common.nsx_struct_get_list(
        security_policy, 'securityPolicy/actionsByCategory'
    )

    for actions in actionsByCategory:
        if actions.get('category') == category:
            actionsByCategory.remove(actions)
            break
    else:
        return

    raw_result = client_session.update(
        'securityPolicyID', uri_parameters={'ID': security_policy_id},
        request_body_dict=security_policy
    )

    common.check_raw_result(raw_result)


def del_policy_group_bind(client_session, resource_id):
    try:
        security_group_id, security_policy_id = resource_id.split("|")
    except Exception as ex:
        raise cfy_exc.NonRecoverableError(
            'Unexpected error retrieving resource ID: %s' % str(ex)
        )

    security_policy = common.nsx_read(
        client_session, 'body',
        'securityPolicyID', uri_parameters={'ID': security_policy_id}
    )

    bindings = common.nsx_struct_get_list(
        security_policy, 'securityPolicy/securityGroupBinding'
    )

    for bind in bindings:
        if bind.get('objectId') == security_group_id:
            bindings.remove(bind)
            break
    else:
        return

    raw_result = client_session.update(
        'securityPolicyID', uri_parameters={'ID': security_policy_id},
        request_body_dict=security_policy
    )

    common.check_raw_result(raw_result)


def del_policy(client_session, resource_id):

    client_session.delete('securityPolicyID',
                          uri_parameters={'ID': resource_id},
                          query_parameters_dict={'force': 'true'})

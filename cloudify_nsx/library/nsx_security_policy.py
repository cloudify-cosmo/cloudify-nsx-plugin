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
        return None, None

    policies = raw_result['body']['securityPolicies'].get('securityPolicy', [])

    if not policies:
        return None, None

    if isinstance(policies, dict):
        policies = [policies]

    for policy in policies:
        if policy.get('name') == name:
            return policy.get('objectId'), policy

    return None, None


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

    raw_result = client_session.read(
        'securityPolicyID', uri_parameters={'ID': security_policy_id}
    )

    common.check_raw_result(raw_result)

    security_policy = raw_result['body']

    bindings = security_policy['securityPolicy'].get(
        'securityGroupBinding', []
    )

    if isinstance(bindings, dict):
        bindings = [bindings]

    for bind in bindings:
        if bind.get('objectId') == security_group_id:
            raise cfy_exc.NonRecoverableError(
                "You already have such group in security policy."
            )

    bindings.append({'objectId': security_group_id})

    security_policy['securityPolicy']['securityGroupBinding'] = bindings

    raw_result = client_session.update(
        'securityPolicyID', uri_parameters={'ID': security_policy_id},
        request_body_dict=security_policy
    )

    common.check_raw_result(raw_result)

    return "%s|%s" % (security_group_id, security_policy_id)


def del_policy_group_bind(client_session, resource_id):

    security_group_id, security_policy_id = resource_id.split("|")

    raw_result = client_session.read(
        'securityPolicyID', uri_parameters={'ID': security_policy_id}
    )

    common.check_raw_result(raw_result)

    security_policy = raw_result['body']

    bindings = security_policy['securityPolicy'].get(
        'securityGroupBinding', []
    )

    if isinstance(bindings, dict):
        bindings = [bindings]

    found = True
    for bind in bindings:
        if bind.get('objectId') == security_group_id:
            bindings.remove(bind)
            found = True
            break

    if not found:
        return

    security_policy['securityPolicy']['securityGroupBinding'] = bindings

    raw_result = client_session.update(
        'securityPolicyID', uri_parameters={'ID': security_policy_id},
        request_body_dict=security_policy
    )

    common.check_raw_result(raw_result)


def del_policy(client_session, resource_id):

    client_session.delete('securityPolicyID',
                          uri_parameters={'ID': resource_id},
                          query_parameters_dict={'force': 'true'})

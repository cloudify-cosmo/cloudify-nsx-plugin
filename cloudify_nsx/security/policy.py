########
# Copyright (c) 2016 GigaSpaces Technologies Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
#    * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    * See the License for the specific language governing permissions and
#    * limitations under the License.
from cloudify import ctx
from cloudify.decorators import operation
import cloudify_nsx.library.nsx_security_policy as nsx_security_policy
import cloudify_nsx.library.nsx_common as common
from cloudify import exceptions as cfy_exc


def _update_policy(exist_policy):
    """update policy info by existed policy"""
    for i in ['description', 'precedence', 'parent',
              'securityGroupBinding', 'actionsByCategory']:
        ctx.instance.runtime_properties['policy'][i] = exist_policy.get(i)


@operation
def create(**kwargs):
    validation_rules = {
        "name": {
            "required": True
        },
        "description": {
            "set_none": True
        },
        "precedence": {
            "type": "string",
            "required": True
        },
        "parent": {
            "set_none": True
        },
        "securityGroupBinding": {
            "set_none": True
        },
        "actionsByCategory": {
            "set_none": True
        }
    }

    use_existing, policy = common.get_properties_and_validate(
        'policy', kwargs, validation_rules
    )

    resource_id = ctx.instance.runtime_properties.get('resource_id')
    if resource_id:
        ctx.logger.info("Reused %s" % resource_id)
        return

    # credentials
    client_session = common.nsx_login(kwargs)

    if not resource_id:
        resource_id, exist_policy = nsx_security_policy.get_policy(
            client_session,
            policy['name']
        )

        if use_existing and resource_id:
            ctx.instance.runtime_properties['resource_id'] = resource_id
            _update_policy(exist_policy)
            ctx.logger.info("Used existed %s" % resource_id)
        elif resource_id:
            raise cfy_exc.NonRecoverableError(
                "Security policy '%s' already exists" % policy['name']
            )
        elif use_existing:
            raise cfy_exc.NonRecoverableError(
                "Security policy '%s' does not exist" % policy['name']
            )

    if not resource_id:
        resource_id = nsx_security_policy.add_policy(
            client_session,
            policy['name'],
            policy['description'],
            policy['precedence'],
            policy['parent'],
            policy['securityGroupBinding'],
            policy['actionsByCategory']
        )

        ctx.instance.runtime_properties['resource_id'] = resource_id
        ctx.logger.info("created %s" % resource_id)


@operation
def delete(**kwargs):
    common.delete_object(
        nsx_security_policy.del_policy, 'policy',
        kwargs
    )

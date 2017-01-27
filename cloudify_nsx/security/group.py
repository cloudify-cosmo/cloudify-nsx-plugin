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
import cloudify_nsx.library.nsx_security_group as nsx_security_group
import cloudify_nsx.library.nsx_common as common
from cloudify import exceptions as cfy_exc


@operation
def create(**kwargs):

    validation_rules = {
        "scopeId": {
            "default": "globalroot-0",
            "required": True
        },
        "name": {
            "required": True
        },
        "member": {
            "set_none": True
        },
        "excludeMember": {
            "set_none": True
        },
        "dynamicMemberDefinition": {
            "set_none": True
        }
    }

    use_existing, group = common.get_properties_and_validate(
        'group', kwargs, validation_rules
    )

    resource_id = ctx.instance.runtime_properties.get('resource_id')
    if resource_id:
        ctx.logger.info("Reused %s" % resource_id)
        return

    # credentials
    client_session = common.nsx_login(kwargs)

    if not resource_id:
        resource_id = nsx_security_group.get_group(client_session,
                                                   group['scopeId'],
                                                   group['name'])

        if use_existing and resource_id:
            ctx.instance.runtime_properties['resource_id'] = resource_id
            ctx.logger.info("Used existed %s" % resource_id)
        elif resource_id:
            raise cfy_exc.NonRecoverableError(
                "Security group '%s' already exists" % group['name']
            )

    if not resource_id:
        resource_id = nsx_security_group.add_group(
            client_session,
            group['scopeId'],
            group['name'],
            group['member'],
            group['excludeMember'],
            group['dynamicMemberDefinition']
        )

        ctx.instance.runtime_properties['resource_id'] = resource_id
        ctx.logger.info("created %s" % resource_id)


@operation
def delete(**kwargs):
    use_existing, group = common.get_properties('group', kwargs)

    if use_existing:
        ctx.logger.info("Used existed")
        return

    resource_id = ctx.instance.runtime_properties.get('resource_id')
    if not resource_id:
        ctx.logger.info("Not fully created, skip")
        return

    # credentials
    client_session = common.nsx_login(kwargs)

    nsx_security_group.del_group(
        client_session,
        resource_id
    )

    ctx.logger.info("delete %s" % resource_id)

    common.remove_properties('group')

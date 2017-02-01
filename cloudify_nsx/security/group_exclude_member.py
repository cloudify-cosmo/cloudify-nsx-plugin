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
from cloudify import exceptions as cfy_exc
import cloudify_nsx.library.nsx_security_group as nsx_security_group
import cloudify_nsx.library.nsx_common as common


@operation
def create(**kwargs):

    validate_rules = {
        "security_group_id": {
            "required": True
        },
        # member id
        "objectId": {
            "required": True
        }
    }

    use_existing, group_exclude_member = common.get_properties_and_validate(
        'group_exclude_member', kwargs, validate_rules
    )

    resource_id = ctx.instance.runtime_properties.get('resource_id')
    if resource_id:
        ctx.logger.info("Reused %s" % resource_id)
        return

    # credentials
    client_session = common.nsx_login(kwargs)

    resource_id = nsx_security_group.add_group_exclude_member(
        client_session,
        group_exclude_member['security_group_id'],
        group_exclude_member['objectId'],
    )

    ctx.instance.runtime_properties['resource_id'] = resource_id
    ctx.logger.info("created %s" % resource_id)


@operation
def delete(**kwargs):
    use_existing, group_exclude_member = common.get_properties(
        'group_exclude_member', kwargs
    )

    if use_existing:
        ctx.logger.info("Used existed")
        return

    resource_id = ctx.instance.runtime_properties.get('resource_id')
    if not resource_id:
        ctx.logger.info("Not fully created, skip")
        return

    # credentials
    client_session = common.nsx_login(kwargs)

    try:
        nsx_security_group.del_group_exclude_member(
            client_session, resource_id
        )
    except Exception as ex:
        ctx.logger.error("We have issue with remove: %s", str(ex))
        raise cfy_exc.RecoverableError(
            message="Retry to delete little later", retry_after=30
        )

    ctx.logger.info("delete %s" % resource_id)

    common.remove_properties('group_exclude_member')

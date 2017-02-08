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


@operation
def create(**kwargs):

    validation_rules = {
        "security_group_id": {
            "required": True
        },
        # dynamic member definition
        "dynamic_set": {
            "required": True
        }
    }

    use_existing, dynamic_member = common.get_properties_and_validate(
        'dynamic_member', kwargs, validation_rules
    )

    resource_id = ctx.instance.runtime_properties.get('resource_id')
    if resource_id:
        ctx.logger.info("Reused %s" % resource_id)
        return

    # credentials
    client_session = common.nsx_login(kwargs)

    resource_id = nsx_security_group.set_dynamic_member(
        client_session,
        dynamic_member['security_group_id'],
        dynamic_member['dynamic_set']
    )

    ctx.instance.runtime_properties['resource_id'] = resource_id
    ctx.logger.info("created %s" % (
        resource_id
    ))


@operation
def delete(**kwargs):
    use_existing, dynamic_member = common.get_properties(
        'dynamic_member', kwargs
    )

    if use_existing:
        common.remove_properties('dynamic_member')
        ctx.logger.info("Used existed")
        return

    resource_id = ctx.instance.runtime_properties.get('resource_id')
    if not resource_id:
        common.remove_properties('dynamic_member')
        ctx.logger.info("Not fully created, skip")
        return

    # credentials
    client_session = common.nsx_login(kwargs)

    common.attempt_with_rerun(
        nsx_security_group.del_dynamic_member,
        client_session=client_session,
        security_group_id=resource_id
    )

    ctx.logger.info("delete %s" % resource_id)

    common.remove_properties('dynamic_member')

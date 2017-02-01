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
import cloudify_nsx.library.nsx_security_policy as nsx_security_policy
import cloudify_nsx.library.nsx_common as common


@operation
def create(**kwargs):
    validation_rules = {
        "security_policy_id": {
            "required": True
        },
        "category": {
            "required": True
        },
        "action": {
            "required": True
        }
    }

    use_existing, policy_section = common.get_properties_and_validate(
        'policy_section', kwargs, validation_rules
    )

    resource_id = ctx.instance.runtime_properties.get('resource_id')
    if resource_id:
        ctx.logger.info("Reused %s" % resource_id)
        return

    # credentials
    client_session = common.nsx_login(kwargs)

    resource_id = nsx_security_policy.add_policy_section(
        client_session,
        policy_section['security_policy_id'],
        policy_section['category'],
        policy_section['action']
    )

    ctx.instance.runtime_properties['resource_id'] = resource_id
    ctx.logger.info("created %s" % (
        resource_id
    ))


@operation
def delete(**kwargs):
    use_existing, policy_section = common.get_properties(
        'policy_section', kwargs
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
        nsx_security_policy.del_policy_section(
            client_session, resource_id
        )
    except Exception as ex:
        ctx.logger.error("We have issue with remove: %s", str(ex))
        raise cfy_exc.RecoverableError(
            message="Retry to delete little later", retry_after=30
        )

    ctx.logger.info("delete %s" % resource_id)

    common.remove_properties('policy_section')

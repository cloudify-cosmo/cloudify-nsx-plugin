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


@operation
def create(**kwargs):
    kwargs = common.get_properties_update(
        'policy_section', "security_policy_id", kwargs,
        target_relationship="cloudify.nsx.relationships.contained_in",
        target_property="resource_id"
    )

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
    common.delete_object(
        nsx_security_policy.del_policy_section, 'policy_section',
        kwargs
    )

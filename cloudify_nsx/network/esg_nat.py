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
import cloudify_nsx.library.nsx_common as common
import cloudify_nsx.library.nsx_nat as nsx_nat


@operation
def create(**kwargs):
    validation_rules = {
        "esg_id": {
            "required": True
        },
        "action": {
            "required": True
        },
        "originalAddress": {
            "required": True
        },
        "translatedAddress": {
            "required": True
        },
        "vnic": {
            "set_none": True
        },
        "ruleTag": {
            "set_none": True
        },
        "loggingEnabled": {
            "default": False,
            "type": "boolean",
        },
        "enabled": {
            "default": True,
            "type": "boolean"
        },
        "description": {
            "set_none": True
        },
        "protocol": {
            "default": "any"
        },
        "translatedPort": {
            "default": "any"
        },
        "originalPort": {
            "default": "any"
        }
    }

    use_existing, nat_dict = common.get_properties_and_validate(
        'rule', kwargs, validation_rules
    )

    resource_id = ctx.instance.runtime_properties.get('resource_id')
    if resource_id:
        ctx.logger.info("Reused %s" % resource_id)
        return

    # credentials
    client_session = common.nsx_login(kwargs)

    resource_id = nsx_nat.add_nat_rule(
        client_session,
        nat_dict['esg_id'],
        nat_dict['action'],
        nat_dict['originalAddress'],
        nat_dict['translatedAddress'],
        nat_dict['vnic'],
        nat_dict['ruleTag'],
        nat_dict['loggingEnabled'],
        nat_dict['enabled'],
        nat_dict['description'],
        nat_dict['protocol'],
        nat_dict['translatedPort'],
        nat_dict['originalPort'])

    ctx.instance.runtime_properties['resource_id'] = resource_id
    ctx.logger.info("created %s " % resource_id)


@operation
def delete(**kwargs):
    use_existing, nat_dict = common.get_properties('rule', kwargs)

    if use_existing:
        common.remove_properties('rule')
        ctx.logger.info("Used existed")
        return

    resource_id = ctx.instance.runtime_properties.get('resource_id')
    if not resource_id:
        common.remove_properties('rule')
        ctx.logger.info("Not fully created, skip")
        return

    # credentials
    client_session = common.nsx_login(kwargs)

    common.attempt_with_rerun(
        nsx_nat.delete_nat_rule,
        client_session=client_session,
        esg_id=nat_dict['esg_id'],
        resource_id=resource_id
    )

    ctx.logger.info("delete %s" % resource_id)

    common.remove_properties('rule')

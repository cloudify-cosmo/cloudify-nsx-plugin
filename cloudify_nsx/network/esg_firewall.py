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
import cloudify_nsx.library.nsx_firewall as nsx_firewall
import cloudify_nsx.library.nsx_common as common


@operation
def create(**kwargs):
    validation_rules = {
        "esg_id": {
            "required": True
        },
        "ruleTag": {
            "set_none": True
        },
        "name": {
            "set_none": True
        },
        "source": {
            "set_none": True
        },
        "destination": {
            "set_none": True
        },
        "application": {
            "set_none": True
        },
        "matchTranslated": {
            "default": False,
            "type": "boolean"
        },
        "direction": {
            "values": [
                "in",
                "out"
            ],
            "set_none": True
        },
        "action": {
            "required": True,
            "values": [
                "accept",
                "deny",
                "reject"
            ]
        },
        "enabled": {
            "default": True,
            "type": "boolean"
        },
        "loggingEnabled": {
            "default": False,
            "type": "boolean"
        },
        "description": {
            "set_none": True
        }
    }

    use_existing, firewall_dict = common.get_properties_and_validate(
        'rule', kwargs, validation_rules
    )

    resource_id = ctx.instance.runtime_properties.get('resource_id')
    if resource_id:
        ctx.logger.info("Reused %s" % resource_id)
        return

    # credentials
    client_session = common.nsx_login(kwargs)

    rule_id, resource_id = nsx_firewall.add_firewall_rule(
        client_session,
        firewall_dict['esg_id'],
        firewall_dict['application'],
        firewall_dict["direction"],
        firewall_dict["name"],
        firewall_dict["loggingEnabled"],
        firewall_dict["matchTranslated"],
        firewall_dict["destination"],
        firewall_dict["enabled"],
        firewall_dict["source"],
        firewall_dict["action"],
        firewall_dict["ruleTag"],
        firewall_dict["description"]
    )

    if not resource_id:
        raise cfy_exc.NonRecoverableError(
            "Can't create firewall rule."
        )

    ctx.instance.runtime_properties['resource_id'] = resource_id
    ctx.instance.runtime_properties['rule_id'] = rule_id
    ctx.logger.info("created %s" % resource_id)


@operation
def delete(**kwargs):
    common.delete_object(
        nsx_firewall.delete_firewall_rule, 'rule',
        kwargs, ['rule_id']
    )

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

    use_existing, firewall_dict = common.get_properties_and_validate(
        'rule', kwargs
    )

    if use_existing:
        ctx.logger.info("Used existed")
        return

    # credentials
    client_session = common.nsx_login(kwargs)

    resource_id, location = nsx_firewall.add_firewall_rule(
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
    ctx.instance.runtime_properties['location'] = location
    ctx.logger.info("created %s | %s" % (resource_id, location))


@operation
def delete(**kwargs):
    use_existing, nat_dict = common.get_properties('rule', kwargs)

    if use_existing:
        ctx.logger.info("Used existed")
        return

    resource_id = ctx.instance.runtime_properties.get('resource_id')
    if not resource_id:
        ctx.logger.info("Not fully created, skip")
        return

    # credentials
    client_session = common.nsx_login(kwargs)

    result_raw = nsx_firewall.delete_firewall_rule(
        client_session,
        nat_dict['esg_id'],
        resource_id
    )
    if not result_raw:
        ctx.logger.error("Status %s" % result_raw['status'])
        raise cfy_exc.NonRecoverableError(
            "Can't delete interface."
        )

    ctx.logger.info("delete %s" % resource_id)

    ctx.instance.runtime_properties['resource_id'] = None

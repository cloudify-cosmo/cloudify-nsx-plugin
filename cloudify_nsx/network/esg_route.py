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
import cloudify_nsx.library.nsx_esg_dlr as nsx_esg
import cloudify_nsx.library.nsx_common as common


@operation
def create(**kwargs):
    validation_rules = {
        "esg_id": {
            "required": True
        },
        "network": {
            "required": True
        },
        "next_hop": {
            "set_none": True
        },
        "vnic": {
            "set_none": True,
            "type": "string"
        },
        "mtu": {
            "set_none": True,
            "type": "string"
        },
        "admin_distance": {
            "set_none": True,
            "type": "string"
        },
        "description": {
            "set_none": True
        }
    }

    use_existing, route = common.get_properties_and_validate(
        'route', kwargs, validation_rules
    )

    if use_existing:
        ctx.logger.info("Used existed")
        return

    resource_id = ctx.instance.runtime_properties.get('resource_id')
    if resource_id:
        ctx.logger.info("Reused %s" % resource_id)
        return

    # credentials
    client_session = common.nsx_login(kwargs)

    resource_id = route['next_hop']

    nsx_esg.esg_route_add(
        client_session,
        route['esg_id'],
        route['network'],
        resource_id,
        route['vnic'],
        route['mtu'],
        route['admin_distance'],
        route['description'])

    ctx.instance.runtime_properties['resource_id'] = resource_id
    ctx.logger.info("created %s" % resource_id)


@operation
def delete(**kwargs):
    use_existing, route = common.get_properties('route', kwargs)

    if use_existing:
        ctx.logger.info("Used existed")
        return

    resource_id = ctx.instance.runtime_properties.get('resource_id')
    if not resource_id:
        ctx.logger.info("Not fully created, skip")
        return

    client_session = common.nsx_login(kwargs)

    common.attempt_with_rerun(
        nsx_esg.esg_route_del,
        client_session=client_session,
        esg_id=route['esg_id'],
        network=route['network'],
        next_hop=resource_id
    )

    ctx.logger.info("delete %s" % resource_id)

    common.remove_properties('route')

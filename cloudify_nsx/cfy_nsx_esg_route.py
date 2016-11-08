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
import pynsxv.library.nsx_esg as nsx_esg
import library.nsx_common as common
from cloudify import exceptions as cfy_exc


@operation
def create(**kwargs):
    use_existed, route = common.get_properties('route', kwargs)

    if use_existed:
        ctx.logger.info("Used existed")
        return

    # credentials
    client_session = common.nsx_login(kwargs)

    resource_id = route['next_hop']

    result_raw = nsx_esg.esg_route_add(
        client_session,
        route['esg_name'],
        route['network'],
        resource_id,
        route['vnic'],
        route['mtu'],
        route['admin_distance'],
        route['description'])

    if not result_raw:
        raise cfy_exc.NonRecoverableError(
            "Can't set route."
        )

    location = route['esg_name'] + "/" + resource_id
    ctx.instance.runtime_properties['resource_id'] = resource_id
    ctx.instance.runtime_properties['location'] = location
    ctx.logger.info("created %s | %s" % (resource_id, location))


@operation
def delete(**kwargs):
    use_existed, route = common.get_properties('route', kwargs)

    if use_existed:
        ctx.logger.info("Used existed")
        return

    resource_id = ctx.instance.runtime_properties.get('resource_id')
    if not resource_id:
        ctx.logger.info("Not fully created, skip")
        return

    client_session = common.nsx_login(kwargs)

    result_raw = nsx_esg.esg_route_del(
        client_session,
        route['esg_name'],
        route['network'],
        resource_id
    )
    if not result_raw:
        ctx.logger.error("Status %s" % result_raw['status'])
        raise cfy_exc.NonRecoverableError(
            "Can't delete gateway."
        )

    ctx.logger.info("delete %s" % resource_id)

    ctx.instance.runtime_properties['resource_id'] = None
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
import library.nsx_esg_dlr as cfy_dlr
import library.nsx_common as common


@operation
def create(**kwargs):
    use_existing, neighbour_filter = common.get_properties_and_validate(
        'filter', kwargs
    )

    if use_existing:
        ctx.logger.info("Used existed, no changes made")
        return

    resource_id = ctx.instance.runtime_properties.get('resource_id')
    if resource_id:
        ctx.logger.info("Reused %s" % resource_id)
        return

    # credentials
    client_session = common.nsx_login(kwargs)

    resource_id = cfy_dlr.add_bgp_neighbour_filter(
        client_session,
        use_existing,
        neighbour_filter['neighbour_id'],
        neighbour_filter['action'],
        neighbour_filter['ipPrefixGe'],
        neighbour_filter['ipPrefixLe'],
        neighbour_filter['direction'],
        neighbour_filter['network']
    )

    ctx.instance.runtime_properties['resource_id'] = resource_id
    ctx.logger.info("created %s" % resource_id)


@operation
def delete(**kwargs):
    use_existing, neighbour = common.get_properties('neighbour', kwargs)

    if use_existing:
        ctx.logger.info("Used existed")
        return

    resource_id = ctx.instance.runtime_properties.get('resource_id')
    if not resource_id:
        ctx.logger.info("Not fully created, skip")
        return

    # credentials
    client_session = common.nsx_login(kwargs)

    cfy_dlr.del_bgp_neighbour_filter(
        client_session,
        resource_id
    )

    ctx.logger.info("delete %s" % resource_id)

    ctx.instance.runtime_properties['resource_id'] = None

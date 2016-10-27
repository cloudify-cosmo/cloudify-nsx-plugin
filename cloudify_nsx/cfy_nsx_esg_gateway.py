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
from cfy_nsx_common import nsx_login, get_properties
from cloudify import exceptions as cfy_exc


@operation
def create(**kwargs):
    use_existed, gateway = get_properties('gateway', kwargs)

    if use_existed:
        ctx.logger.info("Used existed")
        return

    # credentials
    client_session = nsx_login(kwargs)

    resource_id = gateway['dgw_ip']

    result_raw = nsx_esg.esg_dgw_set(client_session,
        gateway['esg_name'],
        resource_id,
        gateway['vnic'],
        gateway['mtu'],
        gateway['admin_distance']
    )

    if not result_raw:
        raise cfy_exc.NonRecoverableError(
            "Can't set gateway."
        )

    location = gateway['esg_name'] + "/" + resource_id
    ctx.instance.runtime_properties['resource_id'] = resource_id
    ctx.instance.runtime_properties['location'] = location
    ctx.logger.info("created %s | %s" % (resource_id, location))

@operation
def delete(**kwargs):
    use_existed, gateway = get_properties('gateway', kwargs)

    if use_existed:
        ctx.logger.info("Used existed")
        return

    resource_id = ctx.instance.runtime_properties.get('resource_id')
    if not resource_id:
        ctx.logger.info("Not fully created, skip")
        return

    # credentials
    client_session = nsx_login(kwargs)

    result_raw = nsx_esg.esg_dgw_clear(
        client_session,
        gateway['esg_name']
    )
    if not result_raw:
        ctx.logger.error("Status %s" % result_raw['status'])
        raise cfy_exc.NonRecoverableError(
            "Can't delete gateway."
        )

    ctx.logger.info("delete %s" % resource_id)

    ctx.instance.runtime_properties['resource_id'] = None

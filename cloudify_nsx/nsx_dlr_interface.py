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
import pynsxv.library.nsx_dlr as nsx_router
from nsx_common import nsx_login
from cloudify import exceptions as cfy_exc


@operation
def create(**kwargs):
    # credentials
    properties = ctx.node.properties
    nsx_auth = properties.get('nsx_auth', {})
    nsx_auth.update(kwargs.get('nsx_auth', {}))
    client_session = nsx_login(nsx_auth)

    interface = properties.get('interface', {})
    interface.update(kwargs.get('interface', {}))
    use_existed = interface.get('use_external_resource', False)

    if use_existed:
        ctx.logger.info("Used existed")
        return

    result_raw = nsx_router.dlr_add_interface(client_session,
        str(interface['dlr_id']),
        str(interface['interface_ls_id']),
        str(interface['interface_ip']),
        str(interface['interface_subnet'])
    )
    if result_raw['status'] < 200 and result_raw['status'] >= 300:
        ctx.logger.error("Status %s" % result_raw['status'])
        raise cfy_exc.NonRecoverableError(
            "Can't create interface."
        )
    resource_id = result_raw['body']['interfaces']['interface']['index']
    location = result_raw['body']['interfaces']['interface']['name']
    ctx.instance.runtime_properties['resource_dlr_id'] =  str(interface['dlr_id'])
    ctx.instance.runtime_properties['resource_id'] = resource_id
    ctx.instance.runtime_properties['location'] = location
    ctx.logger.info("created %s | %s" % (str(resource_id), str(location)))

@operation
def delete(**kwargs):
    # credentials
    properties = ctx.node.properties
    nsx_auth = properties.get('nsx_auth', {})
    nsx_auth.update(kwargs.get('nsx_auth', {}))
    client_session = nsx_login(nsx_auth)

    interface = properties.get('interface', {})
    interface.update(kwargs.get('interface', {}))
    use_existed = interface.get('use_external_resource', False)

    if use_existed:
        ctx.logger.info("Used existed")
        return

    if 'resource_id' not in ctx.instance.runtime_properties:
        ctx.logger.info("Nott fully created, skip")
        return
    result_raw = nsx_router.dlr_del_interface(
        client_session,
        ctx.instance.runtime_properties['resource_dlr_id'],
        ctx.instance.runtime_properties['resource_id']
    )

    if result_raw['status'] < 200 and result_raw['status'] >= 300:
        ctx.logger.error("Status %s" % result_raw['status'])
        raise cfy_exc.NonRecoverableError(
            "Can't create interface."
        )

    ctx.logger.info("delete %s" % ctx.instance.runtime_properties['resource_id'])

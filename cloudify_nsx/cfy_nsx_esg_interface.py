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
from cfy_nsx_common import nsx_login
from cloudify import exceptions as cfy_exc


@operation
def create(**kwargs):
    # credentials
    properties = ctx.node.properties
    nsx_auth = properties.get('nsx_auth', {})
    nsx_auth.update(kwargs.get('nsx_auth', {}))

    interface = ctx.instance.runtime_properties.get('interface', {})
    interface.update(properties.get('interface', {}))
    interface.update(kwargs.get('interface', {}))
    ctx.instance.runtime_properties['interface'] = interface

    use_existed = interface.get('use_external_resource', False)

    if use_existed:
        ctx.logger.info("Used existed")
        return

    client_session = nsx_login(nsx_auth)

    resource_id = str(interface['ifindex'])

    result_raw = nsx_esg.esg_cfg_interface(client_session,
        str(interface['esg_name']),
        str(resource_id),
        str(interface['ipaddr']),
        str(interface['netmask']),
        str(interface['prefixlen']),
        str(interface['name']),
        str(interface['mtu']),
        str(interface['is_connected']),
        str(interface['portgroup_id']),
        str(interface['vnic_type']),
        str(interface['enable_send_redirects']),
        str(interface['enable_proxy_arp']),
        str(interface['secondary_ips'])
    )

    if not result_raw:
        raise cfy_exc.NonRecoverableError(
            "Can't create interface."
        )

    location = str(interface['esg_name']) + "/" + resource_id
    ctx.instance.runtime_properties['resource_id'] = resource_id
    ctx.instance.runtime_properties['location'] = location
    ctx.logger.info("created %s | %s" % (str(resource_id), str(location)))

@operation
def delete(**kwargs):
    # credentials
    properties = ctx.node.properties
    nsx_auth = properties.get('nsx_auth', {})
    nsx_auth.update(kwargs.get('nsx_auth', {}))

    interface = ctx.instance.runtime_properties.get('interface', {})
    interface.update(properties.get('interface', {}))
    interface.update(kwargs.get('interface', {}))
    ctx.instance.runtime_properties['interface'] = interface

    use_existed = interface.get('use_external_resource', False)

    if use_existed:
        ctx.logger.info("Used existed")
        return

    resource_id = ctx.instance.runtime_properties.get('resource_id')
    if not resource_id:
        ctx.logger.info("Not fully created, skip")
        return

    client_session = nsx_login(nsx_auth)

    result_raw = nsx_esg.esg_clear_interface(
        client_session,
        str(interface['esg_name']),
        resource_id
    )
    if not result_raw:
        ctx.logger.error("Status %s" % result_raw['status'])
        raise cfy_exc.NonRecoverableError(
            "Can't delete interface."
        )

    ctx.logger.info("delete %s" % resource_id)

    ctx.instance.runtime_properties['resource_id'] = None

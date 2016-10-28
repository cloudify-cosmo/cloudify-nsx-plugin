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
from cfy_nsx_common import nsx_login, get_properties
from cloudify import exceptions as cfy_exc
import pynsxv.library.nsx_dhcp as nsx_dhcp


@operation
def create(**kwargs):
    # credentials
    client_session = nsx_login(kwargs)

    use_existed, bind_dict = get_properties('bind', kwargs)

    if use_existed:
        ctx.logger.info("Used pre existed!")
        return

    if 'mac' in bind_dict:
        resource_id = nsx_dhcp.add_mac_binding(client_session,
            bind_dict['esg_name'],
            bind_dict['mac'],
            bind_dict['hostname'],
            bind_dict['ip'],
            bind_dict['default_gateway'],
            bind_dict['subnet_mask'],
            bind_dict['domain_name'],
            bind_dict['dns_server_1'],
            bind_dict['dns_server_2'],
            bind_dict['lease_time'],
            bind_dict['auto_dns']
        )
    elif 'mac' in bind_dict and 'mac' in bind_dict:
        resource_id = nsx_dhcp.add_vm_binding(client_session,
            bind_dict['esg_name'],
            bind_dict['vm_id'],
            bind_dict['vnic_id'],
            bind_dict['hostname'],
            bind_dict['ip'],
            bind_dict['default_gateway'],
            bind_dict['subnet_mask'],
            bind_dict['domain_name'],
            bind_dict['dns_server_1'],
            bind_dict['dns_server_2'],
            bind_dict['lease_time'],
            bind_dict['auto_dns']
        )
    else:
        raise cfy_exc.NonRecoverableError(
            "Please fill vm_id/vnic_id or mac"
        )

    ctx.instance.runtime_properties['resource_id'] = resource_id

    ctx.logger.info("Binded %s | %s" % (resource_id, bind_dict))

@operation
def delete(**kwargs):
    use_existed, bind_dict = get_properties('bind', kwargs)

    if use_existed:
        ctx.logger.info("Used pre existed!")
        return

    resource_id = ctx.instance.runtime_properties.get('resource_id')
    if not resource_id:
        ctx.logger.info("We dont have resource_id")
        return

    # credentials
    client_session = nsx_login(kwargs)

    if not nsx_dhcp.delete_dhcp_binding(client_session,
        bind_dict['esg_name'], resource_id
    ):
        raise cfy_exc.NonRecoverableError(
            "Ca't drop dhcp bind"
        )

    ctx.instance.runtime_properties['resource_id'] = None

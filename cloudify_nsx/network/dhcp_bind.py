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
from cloudify import exceptions as cfy_exc
import cloudify_nsx.library.nsx_esg_dlr as nsx_dhcp


@operation
def create(**kwargs):
    validation_rules = {
        "esg_id": {
            "required": True
        },
        "vm_id": {
            "set_none": True
        },
        "vnic_id": {
            "set_none": True,
            "type": "string"
        },
        "mac": {
            "set_none": True
        },
        "hostname": {
            "required": True
        },
        "ip": {
            "required": True
        },
        "default_gateway": {
            "set_none": True
        },
        "subnet_mask": {
            "set_none": True
        },
        "domain_name": {
            "set_none": True
        },
        "dns_server_1": {
            "set_none": True
        },
        "dns_server_2": {
            "set_none": True
        },
        "lease_time": {
            "set_none": True
        },
        "auto_dns": {
            "set_none": True
        }
    }

    use_existing, bind_dict = common.get_properties_and_validate(
        'bind', kwargs, validation_rules
    )

    if use_existing:
        ctx.logger.info("Used pre existed!")
        return

    resource_id = ctx.instance.runtime_properties.get('resource_id')
    if resource_id:
        ctx.logger.info("Reused %s" % resource_id)
        return

    # credentials
    client_session = common.nsx_login(kwargs)

    if bind_dict.get('mac'):  # if NONE skip this part
        resource_id = nsx_dhcp.add_mac_binding(client_session,
                                               bind_dict['esg_id'],
                                               bind_dict['mac'],
                                               bind_dict['hostname'],
                                               bind_dict['ip'],
                                               bind_dict['default_gateway'],
                                               bind_dict['subnet_mask'],
                                               bind_dict['domain_name'],
                                               bind_dict['dns_server_1'],
                                               bind_dict['dns_server_2'],
                                               bind_dict['lease_time'],
                                               bind_dict['auto_dns'])
    elif bind_dict.get('vnic_id') is not None and bind_dict.get('vm_id'):
        resource_id = nsx_dhcp.add_vm_binding(client_session,
                                              bind_dict['esg_id'],
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
                                              bind_dict['auto_dns'])
    else:
        raise cfy_exc.NonRecoverableError(
            "Please fill vm_id/vnic_id or mac"
        )

    ctx.instance.runtime_properties['resource_id'] = resource_id

    ctx.logger.info("Binded %s | %s" % (resource_id, bind_dict))


@operation
def delete(**kwargs):
    use_existing, bind_dict = common.get_properties('bind', kwargs)

    if use_existing:
        common.remove_properties('bind')
        ctx.logger.info("Used pre existed!")
        return

    resource_id = ctx.instance.runtime_properties.get('resource_id')
    if not resource_id:
        common.remove_properties('bind')
        ctx.logger.info("We dont have resource_id")
        return

    # credentials
    client_session = common.nsx_login(kwargs)

    common.attempt_with_rerun(
        nsx_dhcp.delete_dhcp_binding,
        client_session=client_session,
        resource_id=resource_id
    )

    ctx.logger.info("deleted %s" % resource_id)

    common.remove_properties('bind')

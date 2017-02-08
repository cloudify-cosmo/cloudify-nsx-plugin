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
        "ifindex": {
            "required": True,
            "type": "string"
        },
        "ipaddr": {
            "set_none": True
        },
        "netmask": {
            "set_none": True
        },
        "prefixlen": {
            "set_none": True
        },
        "name": {
            "set_none": True
        },
        "mtu": {
            "set_none": True
        },
        "is_connected": {
            "set_none": True
        },
        "portgroup_id": {
            "set_none": True
        },
        "vnic_type": {
            "set_none": True,
            "values": [
                "uplink",
                "internal"
            ]
        },
        "enable_send_redirects": {
            "set_none": True
        },
        "enable_proxy_arp": {
            "set_none": True
        },
        "secondary_ips": {
            "set_none": True
        }
    }

    use_existing, interface = common.get_properties_and_validate(
        'interface', kwargs, validation_rules
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

    resource_id = interface['ifindex']

    nsx_esg.esg_cfg_interface(
        client_session,
        interface['esg_id'],
        interface['ifindex'],
        interface['ipaddr'],
        interface['netmask'],
        interface['prefixlen'],
        interface['name'],
        interface['mtu'],
        interface['is_connected'],
        interface['portgroup_id'],
        interface['vnic_type'],
        interface['enable_send_redirects'],
        interface['enable_proxy_arp'],
        interface['secondary_ips']
    )

    ctx.instance.runtime_properties['resource_id'] = resource_id
    ctx.logger.info("created %s" % resource_id)


@operation
def delete(**kwargs):
    use_existing, interface = common.get_properties('interface', kwargs)

    if use_existing:
        common.remove_properties('interface')
        ctx.logger.info("Used existed")
        return

    resource_id = ctx.instance.runtime_properties.get('resource_id')
    if not resource_id:
        common.remove_properties('interface')
        ctx.logger.info("Not fully created, skip")
        return

    # credentials
    client_session = common.nsx_login(kwargs)

    common.attempt_with_rerun(
        nsx_esg.esg_clear_interface,
        client_session=client_session,
        esg_id=interface['esg_id'],
        resource_id=resource_id
    )

    ctx.logger.info("delete %s" % resource_id)

    common.remove_properties('interface')

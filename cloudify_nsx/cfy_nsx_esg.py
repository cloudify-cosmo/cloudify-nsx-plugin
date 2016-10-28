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
import pynsxv.library.nsx_dhcp as nsx_dhcp
from cfy_nsx_common import nsx_login, get_properties
from cloudify import exceptions as cfy_exc
import library.nsx_nat as nsx_nat


@operation
def create(**kwargs):
    # credentials
    client_session = nsx_login(kwargs)

    use_existed, edge_dict = get_properties('edge', kwargs)

    ctx.logger.info("checking %s" % edge_dict["name"])

    resource_id, _ = nsx_esg.esg_read(client_session, edge_dict["name"])
    if use_existed:
        ctx.instance.runtime_properties['resource_id'] = resource_id
        ctx.logger.info("Used existed %s" % resource_id)
    elif resource_id:
        raise cfy_exc.NonRecoverableError(
            "We already have such router"
        )

    if not use_existed:
        resource_id, location = nsx_esg.esg_create(client_session,
            edge_dict['name'],
            edge_dict['esg_pwd'],
            edge_dict['esg_size'],
            edge_dict['datacentermoid'],
            edge_dict['datastoremoid'],
            edge_dict['resourcepoolid'],
            edge_dict['default_pg'],
            edge_dict['esg_username'],
            edge_dict['esg_remote_access']
        )
        ctx.instance.runtime_properties['resource_id'] = resource_id
        ctx.instance.runtime_properties['location'] = location
        ctx.logger.info("created %s | %s" % (resource_id, location))

    _, firewall = get_properties('firewall', kwargs)
    if firewall:
        if not nsx_esg.esg_fw_default_set(client_session,
            edge_dict['name'],
            firewall['action'],
            firewall['logging']
        ):
            raise cfy_exc.NonRecoverableError(
                "Can't change firewall rules"
            )
        ctx.logger.info("firewall %s | %s" % (
            firewall['action'], firewall['logging'])
        )

    _, dhcp = get_properties('dhcp', kwargs)
    if dhcp:
        if not nsx_dhcp.dhcp_server(client_session,
            edge_dict['name'],
            dhcp['enabled'],
            dhcp['syslog_enabled'],
            dhcp['syslog_level']
        ):
            raise cfy_exc.NonRecoverableError(
                "Can't change dhcp rules"
            )
        ctx.logger.info("dhcp %s | %s" % (
            dhcp['enabled'], dhcp['syslog_enabled'])
        )

    _, nat = get_properties('nat', kwargs)
    if nat:
        if not nsx_nat.nat_service(client_session,
            resource_id,
            nat['enabled']
        ):
            raise cfy_exc.NonRecoverableError(
                "Can't change nat rules"
            )
        ctx.logger.info("nat %s" % (
            nat['enabled'])
        )

@operation
def delete(**kwargs):
    use_existed, edge_dict = get_properties('edge', kwargs)

    if use_existed:
        ctx.logger.info("Used existed %s" % edge_dict.get('name'))
        return

    resource_id = ctx.instance.runtime_properties.get('resource_id')
    if not resource_id:
        ctx.logger.info("We dont have resource_id")
        return

    # credentials
    client_session = nsx_login(kwargs)

    ctx.logger.info("checking %s" % resource_id)

    client_session.delete('nsxEdge', uri_parameters={'edgeId': resource_id})

    ctx.logger.info("delete %s" % resource_id)

    ctx.instance.runtime_properties['resource_id'] = None

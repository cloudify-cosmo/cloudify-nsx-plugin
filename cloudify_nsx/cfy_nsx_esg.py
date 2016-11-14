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
import library.nsx_nat as nsx_nat
import library.nsx_esg_dlr as nsx_dlr


def update_edge(client_session, resource_id, kwargs):

    _, firewall = common.get_properties_and_validate('firewall', kwargs)

    if not nsx_dlr.esg_fw_default_set(
        client_session,
        resource_id,
        firewall['action'],
        firewall['logging']
    ):
        raise cfy_exc.NonRecoverableError(
            "Can't change firewall rules"
        )

    _, dhcp = common.get_properties_and_validate('dhcp', kwargs)

    if not nsx_dlr.dhcp_server(
        client_session,
        resource_id,
        dhcp['enabled'],
        dhcp['syslog_enabled'],
        dhcp['syslog_level']
    ):
        raise cfy_exc.NonRecoverableError(
            "Can't change dhcp rules"
        )

    _, routing = common.get_properties_and_validate('routing', kwargs)
    nsx_dlr.routing_global_config(
        client_session, resource_id,
        routing['enabled'], routing['routingGlobalConfig'],
        routing['staticRouting']
    )

    _, ospf = common.get_properties_and_validate('ospf', kwargs)

    nsx_dlr.ospf_create(
        client_session, resource_id,
        ospf['enabled'], ospf['defaultOriginate'],
        ospf['gracefulRestart'], ospf['redistribution']
    )

    _, nat = common.get_properties_and_validate('nat', kwargs)

    if not nsx_nat.nat_service(
        client_session,
        resource_id,
        nat['enabled']
    ):
        raise cfy_exc.NonRecoverableError(
            "Can't change nat rules"
        )


@operation
def create(**kwargs):

    use_existed, edge_dict = common.get_properties_and_validate('edge', kwargs)

    resource_id = ctx.instance.runtime_properties.get('resource_id')

    # credentials
    client_session = common.nsx_login(kwargs)

    if use_existed and resource_id:
        name = common.get_edgegateway(client_session, resource_id)['name']
        edge_dict['name'] = name
        ctx.instance.runtime_properties['edge']['name'] = name

    resource_id = ctx.instance.runtime_properties.get('resource_id')
    if resource_id:
        ctx.logger.info("Reused %s" % resource_id)

    if not resource_id:
        resource_id, _ = nsx_esg.esg_read(client_session, edge_dict["name"])
        if use_existed:
            ctx.instance.runtime_properties['resource_id'] = resource_id
            ctx.logger.info("Used existed %s" % resource_id)
        elif resource_id:
            raise cfy_exc.NonRecoverableError(
                "We already have such router"
            )

    if not resource_id:
        resource_id, location = nsx_esg.esg_create(
            client_session,
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

    update_edge(client_session, resource_id, kwargs)


@operation
def delete(**kwargs):
    use_existed, edge_dict = common.get_properties('edge', kwargs)

    resource_id = ctx.instance.runtime_properties.get('resource_id')
    if not resource_id:
        ctx.logger.info("We dont have resource_id")
        return

    # credentials
    client_session = common.nsx_login(kwargs)

    if use_existed:
        ctx.logger.info("Used existed %s" % edge_dict.get('name'))
        update_edge(client_session, resource_id, kwargs)
        return

    ctx.logger.info("checking %s" % resource_id)

    client_session.delete('nsxEdge', uri_parameters={'edgeId': resource_id})

    ctx.logger.info("delete %s" % resource_id)

    ctx.instance.runtime_properties['resource_id'] = None

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
import library.nsx_common as common
from cloudify import exceptions as cfy_exc
import library.nsx_dlr as nsx_dlr


@operation
def create(**kwargs):
    # credentials
    client_session = common.nsx_login(kwargs)

    use_existed, router_dict = common.get_properties('router', kwargs)

    ctx.logger.info("checking %s" % router_dict["name"])

    resource_id, _ = nsx_router.dlr_read(client_session, router_dict["name"])
    if use_existed:
        ctx.instance.runtime_properties['resource_id'] = resource_id
        ctx.logger.info("Used existed %s" % resource_id)
        return
    if resource_id:
        raise cfy_exc.NonRecoverableError(
            "We already have such router"
        )

    resource_id, location = nsx_router.dlr_create(
        client_session,
        router_dict['name'],
        router_dict['dlr_pwd'],
        router_dict['dlr_size'],
        router_dict['datacentermoid'],
        router_dict['datastoremoid'],
        router_dict['resourcepoolid'],
        router_dict['ha_ls_id'],
        router_dict['uplink_ls_id'],
        router_dict['uplink_ip'],
        router_dict['uplink_subnet'],
        router_dict['uplink_dgw'])
    ctx.instance.runtime_properties['resource_id'] = resource_id
    ctx.instance.runtime_properties['location'] = location
    ctx.logger.info("created %s | %s" % (resource_id, location))

    _, firewall = common.get_properties('firewall', kwargs)
    if firewall:
        _, validate = common.get_properties('validate_firewall', kwargs)
        firewall = common.validate(firewall, validate, False)

        ctx.logger.info("checking firewall:" + str(firewall))

        if not nsx_dlr.esg_fw_default_set(
            client_session,
            resource_id,
            firewall['action'],
            firewall['logging']
        ):
            raise cfy_exc.NonRecoverableError(
                "Can't change firewall rules"
            )


@operation
def delete(**kwargs):
    use_existed, router_dict = common.get_properties('router', kwargs)

    if use_existed:
        ctx.logger.info("Used pre existed!")
        return

    resource_id = ctx.instance.runtime_properties.get('resource_id')
    if not resource_id:
        ctx.logger.info("We dont have resource_id")
        return

    # credentials
    client_session = common.nsx_login(kwargs)

    ctx.logger.info("deleting %s" % resource_id)

    client_session.delete('nsxEdge', uri_parameters={'edgeId': resource_id})

    ctx.logger.info("deleted %s" % resource_id)

    ctx.instance.runtime_properties['resource_id'] = None
